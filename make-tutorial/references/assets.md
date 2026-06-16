# 资源文件模板

## assets/style.css（主样式文件）

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background: #f5f5f5;
}

main {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
    background: white;
    min-height: 100vh;
}

h1, h2, h3, h4 { margin-top: 1.5em; margin-bottom: 0.5em; line-height: 1.3; }
h1 { font-size: 2.5rem; border-bottom: 3px solid #007acc; padding-bottom: 0.3em; }
h2 { font-size: 2rem; border-bottom: 2px solid #ddd; padding-bottom: 0.2em; }
h3 { font-size: 1.5rem; }

p { margin-bottom: 1em; }
ul, ol { margin-left: 2em; margin-bottom: 1em; }
li { margin-bottom: 0.5em; }

pre { background: #2d2d2d; padding: 1.5em; border-radius: 8px; overflow-x: auto; position: relative; margin-bottom: 1.5em; }
pre code { color: #f8f8f2; font-family: "Courier New", Consolas, monospace; font-size: 0.9em; }
pre.terminal { background: #1e1e1e; border-left: 4px solid #00ff00; }

.copy-button {
    position: absolute;
    top: 0.5em;
    right: 0.5em;
    background: #007acc;
    color: white;
    border: none;
    padding: 0.3em 0.8em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85em;
}
.copy-button:hover { background: #005a9e; }

.callout {
    padding: 1em 1.5em;
    margin-bottom: 1.5em;
    border-left: 4px solid;
    border-radius: 4px;
}
.callout-info { background: #e7f3ff; border-color: #007acc; }
.callout-warning { background: #fff4e5; border-color: #ff9800; }
.callout-tip { background: #e8f5e9; border-color: #4caf50; }
.callout-danger { background: #ffebee; border-color: #f44336; }

details { margin-bottom: 1.5em; border: 1px solid #ddd; border-radius: 4px; padding: 1em; }
summary { cursor: pointer; font-weight: bold; user-select: none; }
.details-content { margin-top: 1em; padding-top: 1em; border-top: 1px solid #eee; }

.tabs { margin-bottom: 1.5em; }
.tab-buttons { display: flex; gap: 0.5em; border-bottom: 2px solid #ddd; }
.tab-buttons button {
    padding: 0.5em 1em;
    border: none;
    background: transparent;
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.tab-buttons button.active { border-bottom-color: #007acc; font-weight: bold; }
.tab-content { display: none; padding-top: 1em; }
.tab-content.active { display: block; }

table { width: 100%; border-collapse: collapse; margin-bottom: 1.5em; }
th, td { padding: 0.8em; border: 1px solid #ddd; text-align: left; }
th { background: #f5f5f5; font-weight: bold; }
.comparison .good { background: #e8f5e9; }
.comparison .bad { background: #ffebee; }

.steps { margin-bottom: 1.5em; }
.step { display: flex; gap: 1em; margin-bottom: 1.5em; }
.step-number {
    flex-shrink: 0;
    width: 2em;
    height: 2em;
    background: #007acc;
    color: white;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}
.step-content { flex: 1; }

.definition {
    background: #f9f9f9;
    border: 2px solid #007acc;
    border-radius: 8px;
    padding: 1.5em;
    margin-bottom: 1.5em;
}
.definition h4 { margin-top: 0; color: #007acc; }

.sidebar-note {
    background: #fffbea;
    border-left: 4px solid #ffc107;
    padding: 1em;
    margin: 1.5em 0;
    font-size: 0.95em;
}

.chapter-nav {
    display: flex;
    justify-content: space-between;
    padding: 1em 0;
    border-bottom: 1px solid #ddd;
    margin-bottom: 2em;
}
.chapter-nav a { color: #007acc; text-decoration: none; font-weight: 500; }
.chapter-nav a:hover { text-decoration: underline; }

.chapter-footer {
    margin-top: 3em;
    padding-top: 2em;
    border-top: 2px solid #ddd;
}
.chapter-footer .chapter-nav { border: none; margin: 0; }

.intro { font-size: 1.1em; color: #555; margin-bottom: 2em; }
.chapter-list { display: flex; flex-direction: column; gap: 1.5em; }
.chapter-item { border: 1px solid #ddd; border-radius: 8px; padding: 1.5em; background: #fafafa; }
.chapter-item h3 { margin: 0.5em 0; }
.chapter-item a { text-decoration: none; color: #007acc; }
.chapter-item a:hover { text-decoration: underline; }
.chapter-badge { display: inline-block; padding: 0.2em 0.8em; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 0.5em; }
.chapter-badge.basic { background: #e8f5e9; color: #2e7d32; }
.chapter-badge.intermediate { background: #fff3e0; color: #e65100; }
.chapter-badge.advanced { background: #fce4ec; color: #c2185b; }

.version-info {
    background: #f0f0f0;
    padding: 1em;
    border-radius: 4px;
    font-size: 0.9em;
    color: #666;
    margin-bottom: 2em;
}

/* 响应式设计 */
@media (max-width: 768px) {
    main { padding: 1rem; margin: 0; }
    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.5rem; }
    pre { padding: 1em; font-size: 0.85em; }
    .chapter-nav { flex-direction: column; gap: 0.5em; }
    .tabs { overflow-x: auto; }
    .tab-buttons { flex-wrap: nowrap; }
}
```

## assets/script.js（交互脚本）

```javascript
// 代码块复制按钮
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('pre code').forEach(block => {
        const button = document.createElement('button');
        button.className = 'copy-button';
        button.textContent = '复制';
        button.addEventListener('click', () => {
            navigator.clipboard.writeText(block.textContent);
            button.textContent = '已复制!';
            setTimeout(() => button.textContent = '复制', 2000);
        });
        block.parentElement.appendChild(button);
    });

    // 标签页切换
    document.querySelectorAll('.tabs').forEach(tabGroup => {
        const buttons = tabGroup.querySelectorAll('.tab-buttons button');
        const contents = tabGroup.querySelectorAll('.tab-content');
        buttons.forEach((button, index) => {
            button.addEventListener('click', () => {
                buttons.forEach(b => b.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                button.classList.add('active');
                contents[index].classList.add('active');
            });
        });
    });
});
```

## Prism.js 代码高亮

**使用 CDN（推荐）：**

在 HTML `<head>` 中：
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
```

在 `</body>` 前：
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<!-- 根据需要添加其他语言 -->
```

## 主题样式文件

### theme-tech.css（技术类）
```css
:root {
    --primary: #007acc;
    --primary-dark: #005a9e;
    --bg-main: #ffffff;
    --bg-aside: #f8f9fa;
    --text: #1a1a1a;
}
body { background: var(--bg-aside); color: var(--text); }
main { background: var(--bg-main); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h1 { color: var(--primary); border-bottom-color: var(--primary); }
a { color: var(--primary); }
```

### theme-math.css（数学类）
```css
:root {
    --primary: #8b4513;
    --bg-main: #fffef8;
    --text: #2c2416;
}
body { background: #f5f3ed; color: var(--text); font-family: Georgia, serif; }
main { background: var(--bg-main); border: 1px solid #d4c9b0; }
h1 { color: var(--primary); font-family: "Palatino Linotype", Palatino, serif; }
```

### theme-science.css（科学类）
```css
:root {
    --primary: #2196f3;
    --accent: #00bcd4;
}
body { background: #eceff1; }
h1 { color: var(--primary); border-bottom: 3px solid var(--accent); }
th { background: #e3f2fd; color: #1976d2; }
```
