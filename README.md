# 豆拼拼豆 · 推介页内容框架

这是 [spec.md](spec.md) 阶段 B 的独立静态网页。8 个章节、截图及阅读交互已接入，精细美化在结构审阅后进行。

线上预览：<https://showcase-html.vercel.app>

GitHub：<https://github.com/jiaoyunqin/pindou-showcase>

## 打开预览

直接打开 `index.html` 即可。移动或复制时，一起保留 `styles.css`、`interactions.js` 和 `assets/`。

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

## 阅读与审阅

- 导航和“查看使用步骤”跳转到真实章节。
- 点击截图打开大图，可切换原始尺寸、滚动查看，或在新标签页打开完整公开版。
- 大图支持 Esc、关闭按钮、点击遮罩；关闭后焦点返回原截图。Tab / Shift+Tab 在查看控件之间循环。
- “作品如何进入精选”默认收起，展开后显示投稿和审核中的实际状态。
- 禁用 JavaScript 后，正文、锚点、投稿展开和图片文件链接仍可用。
- 正式产品入口尚未配置；当前主动作是查看步骤。微信实际使用截图与 Web 演示版说明分别标注。

## 文件

| 文件 | 用途 |
| --- | --- |
| `spec.md` | 唯一规划来源及阶段验收记录 |
| `index.html` | 可编辑的 8 章节正文 |
| `styles.css` / `interactions.js` | 响应式布局与图片查看 |
| `assets/` | 24 张裁片（含备选）及 10 张完整公开版 |
| `assets-manifest.json` | 原图哈希、裁剪坐标、公开处理与章节对应 |
| `scripts/prepare-assets.py` | 从原 JPG 重建派生素材；需 Python + Pillow |
| `scripts/serve.cjs` | 本机预览，仅提供页面文件与派生素材 |
| `verification/` | 浏览器检查结果、素材核对结果及截图 |

原始 JPG 保持不变。分享卡片已裁去会话信息，投稿和审核截图已遮挡昵称等标识。预览服务和线上部署均不会提供原始 JPG、规划文件或验证截图。
