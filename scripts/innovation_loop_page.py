"""ML024/076 enterprise workbench shell. Data and writes stay with the existing loop API."""
import json
from inno_site_chrome import navigation, footer
from gooddesign_assets import links as gooddesign_links

WORDS = {'proposed': '待确认提案', 'draft': '草稿', 'confirmed': '已记录确认', 'unknown': '未知', 'conflict': '存在冲突', 'supported': '有资料支持', 'pending': '待审核', 'required': '需要专业批准', 'approved': '已记录批准', 'not_required_with_reason': '已说明豁免理由', 'requires_evidence_and_preference_review': '需结合证据与偏好审查', 'source_statement': '来源陈述', 'inferred': '分析推断', 'hypothesized': '待验证假设', 'conditional_research_only': '满足条件后可继续研究', 'blocked_by_constraint_conflict': '约束冲突，暂不可推进', 'pending_review': '待审核'}
KEYS = {'conditions': '成立条件', 'key_unknowns': '关键未知', 'next_action': '下一步动作', 'route_ref': '路线', 'execution_authorized': '允许工程执行', 'status': '状态', 'reason': '理由', 'actor': '责任人', 'cost': '成本', 'budget': '预算', 'operating_context': '作业条件', 'acceptance_threshold': '验收条件', 'resources': '资源', 'responsible_actor': '责任人', 'value': '数值或内容', 'unit': '单位', 'nature': '内容性质', 'missing_reason': '待补充', 'id': '记录', 'revision': '版本'}


def friendly(value):
    if value is None:
        return '待确认'
    if isinstance(value, dict):
        if 'value' in value:
            content = friendly(value['value'])
            nature = WORDS.get(value.get('nature'), value.get('nature', ''))
            reason = value.get('missing_reason')
            return content + ('（' + nature + '）' if nature else '') + ('；' + str(reason) if reason else '')
        return '；'.join(KEYS.get(key, key) + '：' + friendly(item) for key, item in value.items())
    if isinstance(value, list):
        return '；'.join(friendly(item) for item in value) or '暂无记录'
    if isinstance(value, bool):
        return '是' if value else '否'
    return WORDS.get(str(value), str(value))


def page(bundle):
    if not isinstance(bundle, dict):
        raise ValueError('bundle object required')
    initial = json.dumps(bundle, ensure_ascii=False, allow_nan=False).replace('<', '\\u003c')
    return '''<!doctype html><html lang="zh-CN" data-theme="light" data-zw-mode="product"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light dark"><title>企业创新工作台 · GoodDesign</title><link rel="stylesheet" href="/inno/portal/system.css">''' + gooddesign_links() + '''<link rel="stylesheet" href="/inno/loop/workspace/enterprise-workbench.css"></head><body>''' + navigation('needs') + '''<main class="ew-shell" id="main"><header class="ew-header"><div class="ew-title"><span class="gd-kicker">GoodDesign 企业创新</span><h1>企业创新工作台</h1><p>把真实任务推进到可验证的下一步。</p></div><div class="ew-task-controls"><label for="task-select">当前研究任务</label><select id="task-select" aria-label="选择研究任务"></select><a class="gd-button" href="/inno/needs/">新建研究任务</a><button class="gd-button gd-button--quiet" id="reload" type="button">刷新数据</button></div></header><div class="ew-boundary"><span>授权内部试运行</span><span>需求、路线与行动均需核对，未授权工程执行</span></div><div class="ew-layout"><nav class="ew-nav" aria-label="工作台视图"><button type="button" data-view="overview" aria-current="page">研究概览</button><button type="button" data-view="requirement">需求与条件</button><button type="button" data-view="routes">路线与证据</button><button type="button" data-view="validation">验证计划</button><button type="button" data-view="feedback">反馈与回流</button></nav><section class="ew-workspace" id="workspace-view" aria-label="当前工作区"></section><aside class="ew-status" id="research-status" aria-label="当前研究判断"></aside></div><p class="ew-message" id="workspace-status" role="status" aria-live="polite"></p></main>''' + footer() + '''<dialog class="ew-evidence" id="evidence-panel" aria-labelledby="evidence-title"><div class="ew-dialog-head"><div><span class="gd-kicker">候选资料</span><h2 id="evidence-title">核对证据与适用边界</h2></div><button class="gd-button gd-button--quiet" type="button" id="evidence-close">关闭</button></div><p class="ew-dialog-note">这些资料可供研究，尚未证明与当前路线匹配。请核对项目对象、工况和原始出处。</p><div id="evidence-content"></div></dialog><script type="application/json" id="initial-bundle">''' + initial + '''</script><script src="/inno/loop/workspace/enterprise-workbench.js" defer></script></body></html>'''
