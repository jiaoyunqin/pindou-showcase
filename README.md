# 豆拼拼豆 · 产品推介页

这是 [spec.md](spec.md) v0.6 对应的独立静态网页。阶段 C 视觉优化已完成，最终页面包含 8 个章节、31 张正文图和 31 个灯箱入口。

## 打开预览

可直接打开 [index.html](index.html)。移动或复制时，需一起保留 `styles.css`、`styles-sections.css`、`styles-outcomes.css`、`styles-responsive.css`、`interactions.js` 和 `assets/`。

也可以在本目录执行：

```sh
node scripts/serve.cjs
```

默认打开 <http://127.0.0.1:4174/>。端口被占用时，可指定其他端口：

```sh
node scripts/serve.cjs 4180
```

脚本按自身位置定位文件，也可从任意目录执行它的完整路径。只需要 Node.js，无需安装依赖或构建。

在其他 AI IDE 或远程环境中，使用该环境提供的端口预览地址。网页根路径 `/` 对应本目录 `index.html`，`/assets/` 对应派生截图目录。无需启动原应用，也没有 `/app/` 路径。

## 页面与交互

- 导航和“查看使用步骤”跳转到真实章节。
- 点击截图打开大图，可切换原始尺寸、滚动查看，或在新标签页打开完整公开版。
- 大图支持 Esc、关闭按钮、点击遮罩；关闭后焦点返回原截图。Tab / Shift+Tab 在查看控件之间循环。
- “作品如何进入精选”默认收起，展开后显示投稿和审核中的实际状态。
- 禁用 JavaScript 后，正文、锚点、投稿展开和图片文件链接仍可用。
- `prefers-reduced-motion: reduce` 下不启用入场动画，`file://` 直接打开时仍可加载样式和图片。
- 首屏与体验章节展示用户提供的小程序码；发布前仍需用微信复核实际可达性。
- 当前站内主动作是查看步骤，不把本机地址作为公开体验入口。

## 样式与素材

| 文件 | 用途 |
| --- | --- |
| `spec.md` | 唯一规划来源及阶段验收记录 |
| `index.html` | 可编辑的 8 章节正文 |
| `styles.css` | 全局 token、基础排版与交互状态 |
| `styles-sections.css` | 各章节构图与视觉组件 |
| `styles-outcomes.css` | 原始图片与导出图纸的两层案例对照 |
| `styles-responsive.css` | 响应式布局与减少动效规则 |
| `interactions.js` | 灯箱与渐进增强交互 |
| `assets/` | 31 张展示图、18 张公开来源副本及 1 张小程序码 |
| `assets-manifest.json` | S01–S14、N01–N12、O01–O07 的哈希、尺寸、来源、授权限制及派生关系 |
| `scripts/prepare-assets.py` | 从原 JPG 重建派生素材；需 Python + Pillow |
| `scripts/serve.cjs` | 本机预览，仅提供页面文件与派生素材 |
| `verification/` | 浏览器检查结果、素材核对结果及截图 |

原始 S 系列文件保持不变。S13、S14 提供替换后的爱心手绘画布与红系色板。分享卡片已裁去会话信息，投稿和审核截图已遮挡昵称等标识。预览服务不会提供原始图片、规划文件或验证截图，路径穿越用例已验证为阻断。

`../new_photo/` 中 N01–N12 均已完成尺寸、SHA-256、来源和授权审计，仅 N04/N06/N09 作为导出图纸公开。`../new_photo/original_photo/` 中 O01–O07 也已完成审计，其中 O01/O03/O04 用于独立案例原图，O07 用于首屏猫咪主线；其余素材不生成公开副本或占位。用户授权范围为本次豆拼拼豆推介页，**对外使用前仍需确认第三方角色权利**。

## 最终验收

- [浏览器终验](verification/final-results.json)：`status=passed`，`failures=[]`；覆盖 4 个视口、8 个锚点、31 张正文图、31 个灯箱、无 JavaScript、减少动效和 `file://`。
- [素材终验](verification/final-asset-checks.json)：`status=passed`，`failures=[]`；4 份 CSS、49 个 WebP、正文图片和路径穿越检查均通过。

本文只记录本地交付与终验结果，不声明云端部署状态。
