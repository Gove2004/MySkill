# 教程维护与版本管理

## 版本标注

在 `index.html` 中添加版本和更新信息：

```html
<div class="version-info">
    <p><strong>版本：</strong>v1.2 | <strong>更新日期：</strong>2026-06-12</p>
    <p><strong>适用版本：</strong>Python 3.10+</p>
</div>
```

对应 CSS：

```css
.version-info {
    background: #f0f0f0;
    padding: 1em;
    border-radius: 4px;
    font-size: 0.9em;
    color: #666;
    margin-bottom: 2em;
}
```

## 更新策略

**小更新**（修正错误、补充说明）：
- 直接修改对应章节
- 更新 `index.html` 的更新日期
- 在章节顶部添加更新说明（可选）

**大更新**（新增章节、重构内容）：
- 升级版本号（v1.2 → v1.3）
- 在 `index.html` 添加更新日志链接
- 考虑创建 `CHANGELOG.md` 记录变更

## 系列教程组织

如果要创建多个相关教程（如"Python 基础" + "Python 进阶"），建议目录结构：

```
tutorials/
├── index.html                    # 总索引页
├── python-basics/                # 基础教程
│   ├── index.html
│   ├── 01-xxx.html
│   └── assets/
├── python-advanced/              # 进阶教程
│   ├── index.html
│   ├── 01-xxx.html
│   └── assets/
└── shared-assets/                # 共享资源（可选）
    └── common.css
```

总索引页 `tutorials/index.html` 列出所有系列教程，说明学习顺序和依赖关系。
