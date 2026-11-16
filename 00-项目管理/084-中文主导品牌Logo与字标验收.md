# 084：中文主导品牌 Logo 与字标验收

日期：2026-11-04  
预览：`http://127.0.0.1:8892/inno/`

## 完成内容

- `brand-logo.svg`由字母G改为中文“好”主体，采用连续圆角和珊瑚色探索光点，与现有小好角色保持品牌关联。
- 字标改为中文“好设计”为主标题、GoodDesign为辅助英文，统一中文20px、英文10px。
- 导航、页脚、独立首页样板和动态档案使用同一结构，品牌首页无障碍名称同步。
- Logo URL增加`?v=084`避免旧缓存。
- SVG使用系统中文无衬线，无在线字体、图片或其他依赖。

## 验证

```sh
python3 scripts/build_gooddesign_site.py
.runtime/pipeline/bin/python -m unittest tests.test_brand_chinese_084 tests.test_gooddesign_chrome_072 -v
python3 tests/browser/brand_chinese_084.py
.runtime/pipeline/bin/python -m unittest discover -s tests -v
python3 tests/browser/home_refinement_080.py
python3 tests/browser/xiaohao_copilot_081.py
python3 tests/browser/museum_assets_083.py
git diff --check
```

- 品牌专项：40项浏览器检查通过。
- 导航/页脚/动态档案中文20px、英文10px一致。
- 1239构建页共享品牌检查通过，六档宽度无导航溢出，Logo实际加载成功。
- 深色、小好打开关闭、首页和展馆回归通过。
- 全量568项测试通过，`git diff --check`通过。

截图与报告位于`output/design-084/`。未提交Git、未部署生产。
