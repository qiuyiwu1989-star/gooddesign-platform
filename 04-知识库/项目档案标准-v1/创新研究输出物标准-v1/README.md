# 创新研究输出物标准 V0.1

GDRP（GoodDesign Research Pack）规定每次产品创新、工程创新和 AI4S 概念研究任务的结构化交付。

完整规范：`specs/099-创新研究输出物标准.md`。

## 文件

- `research-pack.schema.json`：研究包 JSON Schema。
- `examples/rubber-research-pack.json`：割胶真实研究产物形成的标准主数据。
- `examples/report.html`：人类阅读报告（099 摘要版，manifest 指纹锁定）。
- `examples/report.md`：可编辑摘要。
- `examples/manifest.json`：上述文件的 SHA256。
- `templates/report.html`：102 可视化报告模板的割胶填充示例（设计参照，手工排布）。
- `examples/report-rendered.html`：由 `scripts/build_gdrp_report.py` 从 research-pack.json 自动生成的报告，不在 manifest 内。

## 渲染器

`scripts/build_gdrp_report.py`：先过 JSON Schema 再逐字段渲染九章报告；只搬运字段不发明事实，recommendations=[] 明示，未知与审核状态原样呈现，输出断言无破折号字符。用法：

```sh
# 只出 HTML
python3 scripts/build_gdrp_report.py <research-pack.json> <输出report.html>

# 四件套：report.html + report.md + manifest.json，源 pack 副本随目录交付
python3 scripts/build_gdrp_report.py <research-pack.json> <目录/report.html> --md <目录/report.md> --manifest <目录/manifest.json>
```

割胶四件套示例在 `output/gdrp/RUBBER-20261026-r1/`（不入 Git），manifest 指纹可在目录内直接复核。

## 核心原则

一个研究包包含统一任务身份、问题、功能、案例、迁移、候选、比较、验证、领域扩展、审核与边界。产品、工程和 AI4S 使用同一骨架，各自增加领域模块。

`recommendations=[]` 是合法完成状态。未知、待确认和未授权不得因字段完整而被忽略。

## 校验

在项目根目录执行：

```sh
.runtime/pipeline/bin/python - <<'PY'
from pathlib import Path
import json, hashlib
from jsonschema import Draft202012Validator
root = Path('04-知识库/项目档案标准-v1/创新研究输出物标准-v1')
schema = json.loads((root / 'research-pack.schema.json').read_text())
pack = json.loads((root / 'examples/rubber-research-pack.json').read_text())
Draft202012Validator(schema).validate(pack)
manifest = json.loads((root / 'examples/manifest.json').read_text())
for name, sha in manifest['files'].items():
    assert hashlib.sha256((root / 'examples' / name).read_bytes()).hexdigest() == sha
print('GDRP schema and manifest verified')
PY
```

该示例只用于标准验证与内部研究，不是客户批准方案、专家认证或工程结论。
