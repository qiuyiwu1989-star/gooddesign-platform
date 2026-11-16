# 可直接改写的提示词

## 原图约束模板（推荐英文描述形态）

Create a premium 16:9 editorial illustration for GoodDesign's Pixel Industry Almanac. Use the supplied PROJECT REFERENCE as the authority for the actual object, not merely inspiration. First preserve its silhouette, proportions, component count and placement, connections, recognizable materials and colors. Do not redesign the machine.

Object: {project name and ID}. Visible identifying features: {observed features from the reference}. Reference viewpoint: {view}. Verified use context: {short supported purpose}. Preserve: {critical features}. Do not substitute: {known misleading generic machine}.

Render with crisp intentional 16-bit pixel clusters, clean stepped edges, restrained dithering, cobalt/cyan/navy environment, warm ivory highlights and small amber accents. Original object colors take priority over this palette. Keep the complete object readable with generous safe margins; simplify the background one level. Style sample, if supplied, controls brushwork and palette ONLY, never the object structure.

No invented labels, text, performance numbers, extra components, unsupported exposed internals, mascots or decorative brand marks. This is an editorial illustration, not a technical verification image.

## 偏差纠正模板

Compare with the supplied original, not the previous generated design. The last version incorrectly changed {specific feature}. Restore {observed actual shape, scale, placement and color}. Keep {correct parts}. Only adapt the pixel rendering and supported background; do not add mechanisms to make the image look more sophisticated. Keep enough margin to inspect the entire silhouette.

## 无原图模板

Create a conceptual usage-scene illustration of {supported activity}, not an exact depiction of the award-winning device. No reliable exterior reference is available. Use generic non-branded equipment and avoid asserting internal structure or specifications. {same pixel rendering paragraph}. Record the result as concept_scene and label it as such in presentation.

## 发给执行Agent的任务文本

请使用 gooddesign-pixel-illustrations Skill。处理项目{ID/name}；模式{reference_redraw/context_extension/concept_scene}。原图{path/URL}，用途依据{excerpt/source}。先看原图并列出识别特征，再绘制，输出并排对照和review.json。不得修改项目正文、奖项、评分或自行上线。交付位置由本项目落盘约定决定；旧图不覆盖。原图不足或工具不可用请列缺口，不伪造完成。
