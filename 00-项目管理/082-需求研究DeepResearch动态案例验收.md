# 082：需求研究 Deep Research 动态案例验收

日期：2026-11-04  
预览：`http://127.0.0.1:8892/inno/needs-v2/`

## 完成内容

新增“高功率工业泵电驱改造研究”动态案例。小好按五个阶段执行12个研究动作：拆解问题、规划检索、阅读证据、交叉核对、形成结论。

- 当前阶段、当前动作、研究日志、证据卡和实际完成动作数同步更新。
- 使用079真实资料：2017论文基本参数、结构设计、长宁H9现场记录和环球网媒体口径。
- 证据链接进入`2019-s19`具体档案记录，保留原始数值、单位、组态与来源边界。
- 完成后形成研究结论草案，明确待领域复核、非工程结论及专利/成本/现场补证任务。
- 支持暂停、继续、重播和关闭；减少动态偏好直接显示完整案例。
- 原需求填写、参考选择、草稿与导出逻辑未改变。

## 关键边界

页面明确标注“模拟演示 · 真实资料 · 0 次模型调用”。这是脚本化案例播放，不是实时联网、模型推理或企业工程验证。进度只表示已播放事件数，不能解释为真实模型进度。未来接入Agent须另建任务、事件和证据版本契约。

## 验证

```sh
python3 scripts/build_gooddesign_site.py
.runtime/pipeline/bin/python -m unittest tests.test_needs_live_demo_082 tests.test_needs_workspace_074 -v
python3 tests/browser/needs_live_demo_082.py
.runtime/pipeline/bin/python -m unittest discover -s tests -v
python3 tests/browser/home_refinement_080.py
python3 tests/browser/xiaohao_copilot_081.py
python3 tests/browser/case_079.py
git diff --check
```

- 新旧静态测试：11项通过。
- 动态案例浏览器：39项检查通过。
- 暂停冻结动作、继续不重复、重播归零、关闭焦点返回通过。
- 12动作、5阶段、4来源、报告与档案深链通过。
- 390/360px、深色、减少动态及原需求流程通过，无脚本或资源错误。
- 全量558项测试通过；首页86项、小好43项、079档案33项浏览器回归通过。
- `git diff --check`通过。

## 证据

工作过程、完成状态、深色和移动端截图及报告位于`output/design-082/`。未提交Git、未部署生产。
