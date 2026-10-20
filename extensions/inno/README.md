# /inno/ 本地网站预览（027）

源码：本目录CSS/JS及scripts/build_inno_preview.py。产物：output/inno-preview/inno/（忽略入Git）。

```sh
python3 scripts/build_inno_preview.py
python3 scripts/check_inno_preview.py
python3 -m http.server 8775 --bind 127.0.0.1 --directory output/inno-preview
```

项目库：http://127.0.0.1:8775/inno/projects/。

六导航、首页、560条目录、98原站封面，年份/奖种/状态/文本筛选、分页与URL恢复。普通详情只呈现既有公开字段，八模块留缺口；嫦娥复用现有5.0阅读HTML，不重算事实与评分。

馆/教育/企业页先建统一入口，现有资源通过标明的原站外链继续浏览；本轮无新增模型或企业提交API。

构建只读取公开原库字段及既有读者版HTML；不复制研究库全目录、原始附件、历史快照或私有配置。读者HTML内的本地研究文件下载不在此预览开放。所有输出属于可重建视图，禁止手改生成HTML作为新真源。

静态检查校对560项目、页面/资源链接和输出白名单；tests/browser/inno-library-027.js通过playwright-cli run-code检查交互。预览尚未部署opendesign.cc/inno/。
