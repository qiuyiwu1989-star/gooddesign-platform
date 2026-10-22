# 047 历史素材登记与显式原件导入

`legacy_materials.py` 只扫描平台的 `01-原始资料/`（排除项目投递箱）和 `99-历史项目快照/`。不搬走原件、不执行代码、不按文件名确定项目、不批量解压。默认只登记或生成导入计划。

```sh
# 登记文件SHA、实际相对路径、扩展名、大小、重复组；生成私有不可覆盖快照
.runtime/pipeline/bin/python scripts/legacy_materials.py

# 根据明确复核的映射文件先检查计划，不写项目库
.runtime/pipeline/bin/python scripts/legacy_materials.py \
  --registry '04-知识库/历史素材登记/最新登记.json' --mapping '/外置盘路径/归属映射.json'

# 确认计划后才实际导入，保留逐条导入日志
.runtime/pipeline/bin/python scripts/legacy_materials.py \
  --registry '04-知识库/历史素材登记/最新登记.json' --mapping '/外置盘路径/归属映射.json' --apply
```

映射文件格式（每批最多50份，项目ID必须已经存在）：

```json
{
  "version": "legacy-map-1",
  "items": [{
    "relative_path": "01-原始资料/论文/某篇原件.pdf",
    "expected_sha256": "登记中对应文件的完整SHA256",
    "project_id": "2025-00",
    "scope": "project",
    "mapped_by": "复核操作者",
    "reason": "查阅对象后确认的归属依据；尚未完成内容核读"
  }]
}
```

`scope` 仅允许 `project` 或 `shared`。01来源默认 `unassigned`，99默认 `platform_reference`；这两种登记范围都不是已确认项目资料。历史代码/生成HTML明确标为参考素材，后续即使人工决定归档也保持 `unreviewed`，机器转换不等于事实审核。现有项目来源的明确或隐含范围冲突会拒绝导入，须另走归属治理，不通过同SHA重复导入偷偷改范围。

实际导入使用现有 `project_pipeline.ingest`：先将所选原件复制到外置登记区的临时文件并复核SHA，再保存真实原件及机器可读衍生件；不调用 `attach_legacy` 充当原件。成功或失败逐条写 `导入日志.jsonl`，重复原件幂等，不增加导入版本；重复尝试日志仍保留。错误发生前的已完成导入保留，不做破坏性回滚。共享来源先预约其明确范围，避免暂时成为项目专属；失败可能留下一条无实际来源的预约，日志可定位，不自动当成资料。

扫描不跟随符号链接，排除 node_modules、.git、构建和输出目录；默认最多30000文件/目录、单件512MiB、总哈希2GiB，超限明确记录或停止，不静默宣称完整。现有导入管线单件30MiB限制仍保留。

ZIP只读尾标记与受限中央目录元数据（默认3000项/8MiB中央目录），记录路径穿越、符号链接、重复名、加密、膨胀比、嵌套档案等风险。ZIP64/多卷/超限不继续解析；不打开嵌套压缩包、不解压成员、不把整个ZIP当项目文本导入。中央目录CRC与声明大小不等于实际内容已核验。

输出默认 `04-知识库/历史素材登记/`，应被 Git 忽略。最新指针与内容哈希命名的不可覆盖快照分开，同一素材集重复扫描应得到相同 `registry_id`。这些SHA证明字节身份，不证明来源真实性、归属、完整核读、专业审核或版权许可。
