# coding: utf-8
"""051: read-only, conservative source triage for the gold acquisition task.

This module ranks *reading suggestions*, never approves ownership or facts. Source
text is untrusted data. No network, OCR, model, source execution, pipeline lock,
research recovery, or production writes occur here.
"""
import argparse, collections, contextlib, datetime, hashlib, json, re, sqlite3, unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIB = ROOT / '04-知识库/项目库'
DEFAULT_TASK_DB = ROOT / '04-知识库/历史素材登记/金奖全量采集任务/采集任务.sqlite3'
DEFAULT_OUTPUT = ROOT / 'output/research-051/triage'
MAX_JSON_BYTES = 64 * 1024 * 1024
MAX_ORIGINAL_BYTES = 64 * 1024 * 1024
ACQUIRED = {'downloaded', 'reused_existing', 'reused_duplicate'}
LIST_TITLE = re.compile(r'获奖(?:项目及颁发奖金项目|项目|作品)?名单|获奖项目(?:公示|汇总)|获奖名单|获奖目录')
CHALLENGE_TITLE = re.compile(r'^(?:403|404|500|502|503)\b|access denied|just a moment|robot check|bot verification|attention required|访问(?:安全)?验证|安全验证|人机验证', re.I)
CHALLENGE_BODY = re.compile(r'captcha|verify (?:that )?you are human|enable javascript and cookies|cookies must be enabled|enable cookies for|checking your browser|请完成(?:安全|人机)验证|请输入验证码|访问过于频繁|访问被拒绝|访问验证', re.I)
INSTRUCTION = re.compile(r'ignore (?:all )?(?:previous|prior) instructions|忽略(?:以上|之前|前面)(?:所有)?指令|<\s*system\s*>|system prompt', re.I)
LATER_MODEL = re.compile(r'后续型号|升级版|新一代|升级产品|二代|第二代|新型号|系列产品|next.generation|second.generation', re.I)
NAV_LINE = re.compile(r'^(?:首页|上一页|下一页|末页|返回|关于我们|联系我们|登录|注册|English|EN|搜索|网站地图|隐私政策|版权声明|首页\s*[>›].{0,70})$', re.I)
ID_RE = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{0,79}\Z')


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKC', str(value)).lower() if c.isalnum())


def _json(path):
    if not path.is_file():
        raise ValueError('登记文件不存在')
    if path.stat().st_size > MAX_JSON_BYTES:
        raise ValueError('登记JSON超出受控读取上限')
    return json.loads(path.read_text(encoding='utf-8'))


def _project(lib, project_id):
    if not isinstance(project_id, str) or not ID_RE.fullmatch(project_id):
        raise ValueError('项目ID无效')
    lib = Path(lib).resolve()
    p = lib / project_id
    if p.is_symlink() or not p.resolve().is_relative_to(lib):
        raise ValueError('项目目录不允许跨库或符号链接')
    if not (p / '数据/管道状态.json').is_file():
        raise ValueError('项目未建档')
    return p


def _safe_file(p, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute():
        raise ValueError('来源必须使用项目内相对路径')
    candidate = p / relative
    resolved = candidate.resolve()
    if not resolved.is_relative_to(p.resolve()):
        raise ValueError('来源路径越过项目边界')
    # Even in-project symlinks are not necessary for registered source originals.
    for part in [candidate, *candidate.parents]:
        if part == p.parent:
            break
        if part.is_symlink():
            raise ValueError('来源路径含符号链接')
    if not resolved.is_file():
        raise ValueError('来源文件不存在')
    return resolved


def _sha_file(path):
    before = path.stat()
    if before.st_size > MAX_ORIGINAL_BYTES:
        raise ValueError('原件超过64MB，本轮不做完整指纹读取')
    digest = hashlib.sha256()
    with path.open('rb') as source:
        while block := source.read(1024 * 1024):
            digest.update(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('读取期间文件变化，请重新扫描')
    return digest.hexdigest(), before.st_size


def _ownership(p, sid, sources, reg, seen=None):
    seen = set() if seen is None else seen
    if sid in seen:
        raise ValueError('来源归属继承循环')
    seen.add(sid)
    if sid in reg.get('assignments', {}):
        value = reg['assignments'][sid]
    else:
        origin = sources[sid].get('origin') or {}
        parent = origin.get('parent_source_id')
        if parent in sources:
            if parent in reg.get('image_parent_rules', {}):
                value = reg['image_parent_rules'][parent]
            else:
                return _ownership(p, parent, sources, reg, seen)
        else:
            url = origin.get('url') or origin.get('requested_url')
            value = reg.get('url_rules', {}).get(url, {'scope': 'project', 'relation': 'project_submission_unreviewed'})
    if not isinstance(value, dict) or value.get('scope') not in {'project', 'pending', 'shared', 'reassigned'}:
        raise ValueError('来源归属登记无效')
    return {key: value.get(key) for key in ('scope', 'relation', 'owner_project', 'reason')}


def _title(original, meta):
    """Title from stored HTML only; no scripts/styles are executed or interpreted."""
    if original.suffix.lower() not in {'.html', '.htm'}:
        return meta.get('title', ''), 'registered_filename_not_document_identity'
    from html import unescape
    with original.open('rb') as handle:
        raw = handle.read(256 * 1024)
    charset = (meta.get('origin') or {}).get('declared_charset')
    encodings = [charset] if charset else []
    encodings += ['utf-8', 'gb18030']
    text = ''
    for encoding in encodings:
        try:
            text = raw.decode(encoding)
            break
        except (UnicodeError, LookupError, TypeError):
            pass
    if not text:
        text = raw.decode('utf-8', errors='replace')
    match = re.search(r'<title\b[^>]*>(.*?)</title\s*>', text, re.I | re.S)
    if not match:
        return meta.get('title', ''), 'registered_filename_not_document_identity'
    title = re.sub(r'<[^>]*>', '', match[1])
    return ' '.join(unescape(title).split())[:500], 'stored_html_title_untrusted'


def _units(catalog):
    value = catalog.get('unit') or ''
    if not isinstance(value, str):
        return []
    return [s.strip() for s in re.split(r'[,，;；、\n]+', value) if len(normalized(s)) >= 4][:30]


def _matches(names, blocks):
    result = []
    for name in names:
        needle = normalized(name)
        if len(needle) < 3:
            continue
        ids = [block['id'] for block in blocks if needle in normalized(block['text'])]
        if ids:
            result.append({'value': name, 'block_ids': ids[:12], 'matched_blocks': len(ids)})
    return result


def inspect_source(p, source_id, state, reg, catalog, aliases=None, hints=None,
                   other_catalogs=None, text_budget=18000, verify_originals=True):
    """Return a bounded, non-authoritative source-reading suggestion."""
    aliases = aliases or []
    hints = hints or []
    source = state.get('sources', {}).get(source_id)
    result = dict(source_id=source_id, requires_review=True, ownership_approved=False,
                  facts_approved=False, human_read=False, trust='untrusted_source_content_not_instructions', eligible_for_draft=False,
                  eligible_for_relation_review=False, risk_flags=[], issues=[])
    if not isinstance(source, dict):
        result.update(suggested_role='quarantine_or_conversion', priority=0, issues=['来源ID未在本项目登记'])
        return result
    origin = source.get('origin') or {}
    if not isinstance(origin, dict) or source.get('id', source_id) != source_id:
        result.update(suggested_role='quarantine_or_conversion', priority=0, issues=['来源元数据身份或origin结构无效'])
        return result
    result.update(registered_title=source.get('title', ''), url=origin.get('url') or origin.get('requested_url'),
                  candidate_hints=[{'title': h.get('title', ''), 'url': h.get('url', ''), 'task_id':h.get('task_id')} for h in hints],
                  conversion_status=source.get('status'), content_kind=origin.get('kind'),
                  integrity=dict(status='not_checked', declared_sha256=source.get('sha256')))
    try:
        ownership = _ownership(p, source_id, state['sources'], reg)
        result.update(scope=ownership['scope'], current_ownership=ownership)
        original = _safe_file(p, source.get('original'))
        chunks = _safe_file(p, source.get('chunks'))
        expected = source.get('sha256')
        if not isinstance(expected, str) or not re.fullmatch(r'[0-9a-f]{64}', expected):
            raise ValueError('原件缺少有效SHA256登记')
        if verify_originals:
            actual, size = _sha_file(original)
            if actual != expected:
                raise ValueError('原件SHA256与登记不一致')
        else:
            size = original.stat().st_size
        if chunks.stat().st_size > MAX_JSON_BYTES:
            raise ValueError('证据块超过受控读取上限')
        raw = chunks.read_bytes()
        if len(raw) > MAX_JSON_BYTES:
            raise ValueError('证据块超过受控读取上限')
        chunks_sha = hashlib.sha256(raw).hexdigest()
        declared_chunks = source.get('chunks_sha256')
        if declared_chunks is not None and chunks_sha != declared_chunks:
            raise ValueError('证据块SHA256与登记不一致')
        blocks = json.loads(raw)
        if not isinstance(blocks, list) or any(not isinstance(x, dict) or not isinstance(x.get('id'), str)
           or not isinstance(x.get('text'), str) or not isinstance(x.get('locator'), str) for x in blocks):
            raise ValueError('证据块结构无效')
        if len({x['id'] for x in blocks}) != len(blocks):
            raise ValueError('证据块ID重复')
        result['integrity'].update(status='verified' if verify_originals else 'original_not_verified',
                                   original_bytes=size, chunks_sha256=chunks_sha,
                                   chunks_binding='registered_sha256' if declared_chunks else 'computed_only_missing_registered_sha256')
        title, title_basis = _title(original, source)
        result.update(title=title, title_basis=title_basis)
    except (OSError, ValueError, TypeError, KeyError, AttributeError, json.JSONDecodeError) as exc:
        result.update(suggested_role='quarantine_or_conversion', priority=0)
        result['integrity']['status'] = 'blocked'
        result['issues'].append(str(exc))
        return result

    selected, used = [], 0
    for block in blocks:
        if used + len(block['text']) > text_budget:
            break
        selected.append(block)
        used += len(block['text'])
    text = '\n'.join(block['text'] for block in selected)
    all_chars = sum(len(block['text']) for block in blocks)
    result['reading_scope'] = dict(kind='bounded_machine_triage_not_human_read', text_budget=text_budget,
        sampled_chars=used, total_chars=all_chars, sampled_block_ids=[x['id'] for x in selected],
        total_blocks=len(blocks), all_chunks_scanned=len(selected) == len(blocks),
        meaning='扫描证据块不代表全文核读、语义正确或资料归属审核')
    lines = [x.strip() for x in text.splitlines() if x.strip()]
    nav_lines = sum(bool(NAV_LINE.fullmatch(x)) for x in lines)
    nonnav_chars = sum(len(x) for x in lines if not NAV_LINE.fullmatch(x))
    challenge = bool(CHALLENGE_TITLE.search(title)) or (len(text) < 3500 and bool(CHALLENGE_BODY.search(text)))
    navigation = bool(lines) and nav_lines / len(lines) >= .55 and nonnav_chars < 400
    low_text = used < 120
    catalog_candidate = bool(LIST_TITLE.search(title)) or (bool(LIST_TITLE.search(text[:700])) and
        (len(re.findall(r'\b1?20\d{7,12}\b', text)) >= 3 or ('银奖' in text and '金奖' in text)))
    full = _matches([catalog.get('name', '')], selected)
    alias_hits = _matches([x for x in aliases if isinstance(x, str)], selected)
    unit_hits = _matches(_units(catalog), selected)
    full_in_title = bool(normalized(catalog.get('name', ''))) and normalized(catalog.get('name', '')) in normalized(title)
    alias_in_title = [name for name in aliases if isinstance(name, str) and len(normalized(name)) >= 3 and normalized(name) in normalized(title)]
    hint_title_match = any(normalized(catalog.get('name', '')) in normalized(x.get('title', '')) for x in hints) if catalog.get('name') else False
    cross = []
    for other in other_catalogs or []:
        if other.get('id') == catalog.get('id') or len(normalized(other.get('name', ''))) < 6:
            continue
        hits = _matches([other['name']], selected)
        if hits:
            cross.append(dict(project_id=other['id'], name=other['name'], block_ids=hits[0]['block_ids']))
    result['identity_clues'] = dict(full_project_name_in_body=full, supplied_aliases_in_body=alias_hits,
        full_project_name_in_stored_title=full_in_title, supplied_aliases_in_stored_title=alias_in_title,
        unit_mentions=unit_hits, project_name_in_search_title_only=hint_title_match and not(full or alias_hits or full_in_title or alias_in_title),
        other_project_titles=cross[:20], other_project_title_count=len(cross),
        meaning='字符串线索不是项目身份、成果归属、论文采用或专利权属的证明')
    risks = result['risk_flags']
    generic_portal = bool(cross) and not full_in_title and ('好设计' in title and '作品详情' not in title or len(cross) >= 2)
    if generic_portal:risks.append('multi_project_portal_requires_project_excerpt')
    if challenge:risks.append('possible_access_challenge_not_article')
    if navigation:risks.append('navigation_dominates_sample')
    if low_text:risks.append('insufficient_machine_readable_text')
    if catalog_candidate:risks.append('whole_award_catalog_requires_exact_project_excerpt')
    if cross:risks.append('multiple_project_names_in_sample')
    if unit_hits and not(full or alias_hits or full_in_title or alias_in_title):risks.append('unit_only_relation_not_project_identity')
    if result['identity_clues']['project_name_in_search_title_only']:risks.append('search_title_not_confirmed_by_stored_content')
    if LATER_MODEL.search(title + '\n' + text):risks.append('possible_later_model_or_series_boundary')
    if INSTRUCTION.search(text):risks.append('instruction_like_text_untrusted_ignore_as_instructions')
    years = sorted(set(re.findall(r'\b(?:19|20)\d{2}\b', text)))
    result['year_clues'] = dict(catalog_year=catalog.get('year'), years_in_sample=years,
                               meaning='出现的年份不自动作为资料发表年、获奖年或型号年代')
    derived = origin.get('kind') in {'legacy_archive', 'project_json_row', 'project_source_excerpt'}
    if derived:risks.append('derived_or_legacy_source_not_independent_original')
    if ownership['scope'] == 'reassigned':risks.append('source_reassigned_do_not_read_as_this_project')
    foreign_owner=ownership.get('owner_project') not in (None,p.name) and ownership['scope'] in {'project','pending'}
    if foreign_owner:risks.append('registered_owner_conflicts_with_project_directory')
    if not declared_chunks:risks.append('chunks_hash_not_previously_registered')
    blockers = challenge or navigation or low_text or ownership['scope'] == 'reassigned' or foreign_owner
    if blockers:
        role = 'quarantine_or_conversion'
    elif generic_portal and not catalog_candidate:
        role = 'shared_overview_requires_project_excerpt'
    elif catalog_candidate:
        role = 'shared_catalog_requires_project_excerpt'
    elif full or alias_hits or full_in_title or alias_in_title:
        role = 'project_specific_candidate_requires_review'
    elif unit_hits:
        role = 'related_team_or_background_unverified'
    else:
        role = 'relation_unclear'
    result['suggested_role'] = role
    result['readability'] = dict(machine_readable=bool(selected) and not(challenge or navigation or low_text),
        navigation_lines=nav_lines, sampled_nonempty_lines=len(lines), nonnavigation_chars=nonnav_chars,
        content_check='heuristic_not_article_authenticity_certification')
    # This ordering is not a quality score, similarity, expert judgment or semantic proof.
    score = 60 if role == 'project_specific_candidate_requires_review' else 30 if role in {'shared_catalog_requires_project_excerpt', 'shared_overview_requires_project_excerpt'} else 15 if role == 'related_team_or_background_unverified' else 5
    if full:score += 15
    if full_in_title:score += 10
    if alias_hits:score += 5
    if 'possible_later_model_or_series_boundary' in risks:score -= 10
    if derived:score -= 20
    if blockers or not verify_originals:score = 0
    result['priority'] = max(0, score)
    result['priority_meaning'] = 'reading_order_only_not_quality_or_similarity'
    result['eligible_for_relation_review'] = not blockers and verify_originals
    result['eligible_for_draft'] = not blockers and verify_originals and bool(full or alias_hits or full_in_title or alias_in_title) and not derived and bool(declared_chunks)
    if role in {'shared_catalog_requires_project_excerpt', 'shared_overview_requires_project_excerpt'}:
        result['draft_constraints'] = ['仅在准确选录本项目条目后提炼；整届名单不得当成本项目专属原件', '题录年份、名单年份、个人/单位/编号字段须逐列核对']
    else:
        result['draft_constraints'] = ['每条候选仍须精确原文证据与对象/工况/时间边界', 'pending可读草稿但不可因此批准归属或事实；型号采用、权属、效果另核']
    return result


def triage_project(lib=DEFAULT_LIB, project_id=None, source_ids=None, aliases=None,
                   text_budget=18000, verify_originals=True, source_hints=None, other_catalogs=None):
    """Pure read-only inspection; aliases are supplied grounded labels, never inferred."""
    if not isinstance(text_budget, int) or not 1200 <= text_budget <= 100000:
        raise ValueError('text_budget须在1200–100000之间')
    p = _project(lib, project_id)
    state = _json(_safe_file(p, '数据/管道状态.json'))
    if not isinstance(state, dict) or not isinstance(state.get('sources'), dict) or not isinstance(state.get('project'),dict):raise ValueError('项目状态结构无效')
    catalog = dict(state.get('project', {}))
    if catalog.get('id') not in (None,project_id):raise ValueError('项目状态身份不一致')
    if aliases is not None and(not isinstance(aliases,list) or not all(isinstance(x,str)for x in aliases)):raise ValueError('别名须为显式字符串数组')
    if isinstance(source_ids,str):raise ValueError('来源ID须为数组')
    if other_catalogs is None:
        index=Path(lib)/'项目索引.json'
        other_catalogs=_json(index).get('projects',[]) if index.is_file() else []
    catalog.setdefault('id', project_id)
    regpath = p / '资料归属.json'
    reg = _json(_safe_file(p, '资料归属.json')) if regpath.exists() else {'version': 0, 'assignments': {}, 'url_rules': {}}
    if not isinstance(reg,dict):raise ValueError('项目归属登记结构无效')
    ids = list(state.get('sources', {})) if source_ids is None else list(dict.fromkeys(source_ids))
    if not all(isinstance(sid, str) for sid in ids):raise ValueError('来源ID列表无效')
    hints = source_hints or {}
    sources = [inspect_source(p, sid, state, reg, catalog, aliases, hints.get(sid), other_catalogs,
                              text_budget, verify_originals) for sid in ids]
    sources.sort(key=lambda item: (-item['priority'], item['source_id']))
    return dict(project_id=project_id, catalog=catalog, observed_at=now(), ingest_revision=state.get('revision'),
        ownership_version=reg.get('version', 0), source_count=len(sources), sources=sources,
        issues=[], writes_performed=False, ownership_or_facts_approved=False,
        consistency='per-project atomic files observed without locking; collector can add newer sources after this scan')


def read_task(task_db=DEFAULT_TASK_DB, project_ids=None):
    """Read a short SQLite snapshot without DDL, recovery or write-capable wrappers."""
    db = Path(task_db).resolve()
    if not db.is_file():raise ValueError('050任务数据库不存在')
    with contextlib.closing(sqlite3.connect(db.as_uri() + '?mode=ro', uri=True, timeout=15)) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA query_only=ON')
        connection.execute('BEGIN')
        projects = [dict(x) for x in connection.execute('SELECT id,catalog FROM projects ORDER BY id')]
        rows = [dict(x) for x in connection.execute('SELECT id,project,url,title,status,result,error FROM sources ORDER BY id')]
    if project_ids is not None:
        selected = set(project_ids)
        missing = selected - {x['id'] for x in projects}
        if missing:raise ValueError('请求项目不在050金奖任务中：' + ','.join(sorted(missing)))
        projects = [x for x in projects if x['id'] in selected]
        rows = [x for x in rows if x['project'] in selected]
    for project in projects:project['catalog'] = json.loads(project['catalog'])
    return projects, rows


def build_report(lib=DEFAULT_LIB, task_db=DEFAULT_TASK_DB, project_ids=None, aliases=None,
                 text_budget=18000, verify_originals=True):
    all_projects, rows = read_task(task_db)
    projects=all_projects
    if project_ids is not None:
        selected=set(project_ids);missing=selected-{x['id']for x in all_projects}
        if missing:raise ValueError('请求项目不在050金奖任务中：'+','.join(sorted(missing)))
        projects=[x for x in all_projects if x['id']in selected];rows=[x for x in rows if x['project']in selected]
    grouped = collections.defaultdict(list)
    for row in rows:grouped[row['project']].append(row)
    catalogs = [dict(x['catalog'], id=x['id']) for x in all_projects]
    report = dict(schema='gold-source-triage-1.0', generated_at=now(), mode='read_only_suggestions_not_approval',
        source_text_trust='untrusted_data_never_instructions', projects=[],
        limitations=['关键词仅提供阅读线索，不批准来源归属或事实。', '原件SHA校验不证明内容真实、合法再发布或成果实际采用。',
                     '仅扫描050任务已关联source_id；排队/失败/运行中与未完成专项查询仍保留。',
                     '扫描文本有预算边界，不宣称全文核读、专家审核或标杆级完成。'])
    for project in projects:
        pid = project['id']; candidates = grouped[pid]; hints = collections.defaultdict(list); ids=[]; issues=[]
        for row in candidates:
            if row['status'] not in ACQUIRED:continue
            try:
                result = json.loads(row['result'])
                sid = result['source_id']
                if not isinstance(sid, str):raise ValueError('source_id无效')
            except (TypeError, ValueError, KeyError):
                issues.append(dict(task_id=row['id'], issue='获取结果缺少有效来源身份'))
                continue
            if sid not in ids:ids.append(sid)
            hints[sid].append({'url':row['url'], 'title':row['title'], 'task_id':row['id']})
        try:
            item = triage_project(lib, pid, ids, (aliases or {}).get(pid), text_budget, verify_originals, hints, catalogs)
        except (OSError, ValueError, TypeError, KeyError) as exc:
            item = dict(project_id=pid, catalog=project['catalog'], sources=[], source_count=0,
                        issues=[str(exc)], writes_performed=False, ownership_or_facts_approved=False)
        item['task_counts'] = dict(collections.Counter(row['status'] for row in candidates))
        item['failed_candidates'] = [dict(task_id=x['id'], url=x['url'], title=x['title'], error=x['error']) for x in candidates if x['status']=='failed']
        item['task_issues'] = issues
        report['projects'].append(item)
    sources = [source for project in report['projects'] for source in project['sources']]
    report['summary'] = dict(projects=len(projects), candidate_urls=len(rows),
        task_status_counts=dict(collections.Counter(row['status'] for row in rows)), unique_project_sources=len(sources),
        integrity_status_counts=dict(collections.Counter(x['integrity']['status'] if 'integrity' in x else 'missing' for x in sources)),
        suggested_role_counts=dict(collections.Counter(x['suggested_role'] for x in sources)),
        eligible_for_relation_review=sum(x['eligible_for_relation_review'] for x in sources),
        eligible_for_draft=sum(x['eligible_for_draft'] for x in sources),
        ownership_approved=0, facts_published=0, human_full_reads=0)
    return report


def write_report(report, output=DEFAULT_OUTPUT):
    output = Path(output); output.mkdir(parents=True, exist_ok=True)
    path = output / '资料筛选建议.json'
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    lines=['# 金奖采集资料筛选建议', '', '只读阅读排序，**不批准归属、不发布事实、不代表全文核读**。', '',
           '生成：'+report['generated_at'], '', '```json', json.dumps(report['summary'],ensure_ascii=False,indent=2), '```', '',
           '| 项目 | 来源 | 可供草稿候选 | 关联待核 | 整届目录候选 | 阻断/转换 | 失败链接 |', '|---|---:|---:|---:|---:|---:|---:|']
    for item in report['projects']:
        src=item['sources']; role=collections.Counter(x['suggested_role'] for x in src)
        title=str(item['catalog'].get('name','')).replace('|','／').replace('\n',' ')
        lines.append(f"| {item['project_id']} {title} | {len(src)} | {sum(x['eligible_for_draft'] for x in src)} | {role['relation_unclear']+role['related_team_or_background_unverified']} | {role['shared_catalog_requires_project_excerpt']+role['shared_overview_requires_project_excerpt']} | {role['quarantine_or_conversion']} | {len(item['failed_candidates'])} |")
    lines += ['', '## 使用边界', '', *['- '+text for text in report['limitations']], '',
              '完整逐来源的指纹、范围、线索、风险和读取优先级见同目录JSON。所有来源继续保留原审核状态。']
    (output/'资料筛选建议.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return path


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--library',type=Path,default=DEFAULT_LIB)
    parser.add_argument('--task-db',type=Path,default=DEFAULT_TASK_DB)
    parser.add_argument('--project',action='append',dest='projects')
    parser.add_argument('--aliases',type=Path,help='显式项目ID→已核别名数组；不在本工具中推断别名')
    parser.add_argument('--text-budget',type=int,default=18000)
    parser.add_argument('--skip-original-hash',action='store_true',help='只诊断；跳过原件SHA时所有来源均不能供草稿')
    parser.add_argument('--output',type=Path,default=DEFAULT_OUTPUT)
    args=parser.parse_args()
    aliases=_json(args.aliases) if args.aliases else None
    if aliases is not None and not isinstance(aliases,dict):raise ValueError('别名文件须为项目ID对象')
    report=build_report(args.library,args.task_db,args.projects,aliases,args.text_budget,not args.skip_original_hash)
    path=write_report(report,args.output)
    print(json.dumps(dict(path=str(path),summary=report['summary']),ensure_ascii=False,indent=2))

if __name__=='__main__':main()
