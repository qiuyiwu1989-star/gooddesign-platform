# 081：小好右下角 Copilot 入口验收

日期：2026-11-04  
预览：`http://127.0.0.1:8892/inno/`

## 完成内容

- 小好从顶部导航迁移为右下角常驻入口，桌面显示头像与名称，移动端使用48px圆形头像。
- 点击后在入口上方打开研究导览面板，不再使用全高右侧抽屉。
- 保留找项目、读方法、核证据三个真实动作及当前项目ID，不增加模型对话或自动研究表述。
- 修复导航`backdrop-filter`导致fixed以导航为参照的问题，按钮已真正移出导航DOM。
- `replace_chrome`同步清理旧trigger/dialog，1238个构建页面均只有一个入口和一个面板。
- 移动端调整头像、标题与关闭按钮，360/390px下“你好，我是小好”完整单行显示。
- `aria-haspopup`、`aria-controls`、`aria-expanded`与真实状态同步，支持Escape、关闭按钮和焦点返回。

## 验证

```sh
python3 scripts/build_gooddesign_site.py
.runtime/pipeline/bin/python -m unittest tests.test_xiaohao_copilot_081 tests.test_ip_xiaohao_078 -v
python3 tests/browser/xiaohao_copilot_081.py
python3 tests/browser/ip_xiaohao_078.py
python3 tests/browser/home_refinement_080.py
python3 tests/browser/case_079.py
.runtime/pipeline/bin/python -m unittest discover -s tests -v
git diff --check
```

- 新旧小好静态测试：11项通过。
- 小好Copilot专项：43项浏览器检查通过。
- 旧小好交互：19项浏览器检查通过。
- 首页：86项浏览器检查通过。
- 079项目档案：33项浏览器检查通过。
- 全量：552项测试通过，`git diff --check`通过。
- 无浏览器脚本异常或角色资源加载失败。

## 证据与边界

桌面浅色/深色和移动端截图、报告位于`output/design-081/`。本次只改变统一角色入口与可访问状态，不改变业务数据、路由、研究内容或模型能力。未提交Git、未部署生产。
