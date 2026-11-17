# HTML 组件使用指南

充分利用 HTML 的表现力增强教学效果。完整组件库和示例参考 `references/assets.md`。

## 核心组件

- **提示框**：`<div class="callout callout-info/warning/tip/danger">`
- **代码块**：`<pre><code class="language-python">` + Prism.js 自动高亮
- **可折叠内容**：`<details><summary>` 用于进阶内容
- **标签页**：`<div class="tabs">` 展示多语言对比
- **对比表格**：`<table class="comparison">` 好/坏写法对照
- **步骤流程**：`<div class="steps">` 操作指南
- **定义框**：`<div class="definition">` 关键概念
- **侧边注释**：`<aside class="sidebar-note">` 补充说明
- **主题切换**：`<button class="theme-toggle" data-theme-toggle>`（每页必带；index 放在 `.page-toolbar`，章节页放在 `.chapter-nav`）

## 无障碍要求

- 为交互组件添加 ARIA 属性（`role`, `aria-selected`, `aria-label`）
- 使用语义化标签（`<nav>`, `<main>`, `<article>`）
- 确保键盘导航可访问所有交互元素
- 文本与背景对比度 ≥ 4.5:1（**深浅两种模式都要检查**，深色下的提示框和徽章最容易不达标）
- **替代文本**：图片、图表必须有 `alt` 描述
- **主题切换按钮**必须有 `aria-pressed` 和 `aria-label`（`script.js` 会自动维护），并保留可见的 `:focus-visible` 焦点环

## 示例改进

```html
<!-- 标签页组件添加 ARIA -->
<div class="tabs" role="tablist">
    <button role="tab" aria-selected="true" aria-controls="panel-1">Python</button>
    <button role="tab" aria-selected="false" aria-controls="panel-2">JavaScript</button>
</div>
<div id="panel-1" role="tabpanel" class="tab-content active">...</div>
<div id="panel-2" role="tabpanel" class="tab-content">...</div>

<!-- 代码块复制按钮添加 aria-label -->
<button class="copy-button" aria-label="复制代码到剪贴板">复制</button>
```

## 响应式设计已包含

`style.css` 已包含基本响应式设计（`@media (max-width: 768px)`），移动端会自动调整布局、字体大小和导航结构。
