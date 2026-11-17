# 资源文件模板

四份资源的分工：

- `assets/style.css`：设计令牌 + 全部组件样式，浅色为默认值，`[data-theme="dark"]` 覆盖为深色
- `assets/script.js`：主题切换、代码复制、标签页
- `assets/theme-*.css`：只覆盖品牌色与字体气质，不重复写布局和组件
- Prism.js：代码高亮，两套主题共用 `prism-tomorrow`

> 硬性约束：组件规则里只能引用 CSS 变量，不能出现 `#fff`、`#333`、`#ddd` 这类字面色值。写死一个颜色，切换时就只换一半，出现白底白字。

## assets/style.css（主样式文件）

```css
/* ============================================================
   设计令牌
   浅色为默认；[data-theme="dark"] 提供完整的深色取值。
   深色块必须把全部颜色令牌都覆盖一遍，这样 theme-*.css
   只需管品牌色，任何主题都不会漏掉某个组件。
   ============================================================ */
:root {
    color-scheme: light;

    /* 品牌色：由 theme-*.css 覆盖 */
    --primary: #007acc;
    --primary-hover: #005a9e;
    --text-on-accent: #ffffff;

    /* 表面 */
    --bg-page: #f5f5f5;
    --bg-surface: #ffffff;
    --bg-soft: #fafafa;
    --bg-muted: #f0f0f0;
    --bg-inline: #eff2f7;
    --bg-code: #2d2d2d;
    --bg-code-terminal: #1e1e1e;
    --terminal-accent: #4caf50;
    --bg-note: #fffbea;
    --note-bar: #ffc107;

    /* 文字 */
    --text: #333333;
    --text-strong: #111111;
    --text-muted: #666666;
    --text-code: #f8f8f2;

    /* 线与阴影 */
    --border: #dddddd;
    --border-soft: #eeeeee;
    --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    /* 提示框 */
    --callout-info-bg: #e7f3ff;
    --callout-warning-bg: #fff4e5;
    --callout-tip-bg: #e8f5e9;
    --callout-danger-bg: #ffebee;
    --callout-info-bar: #007acc;
    --callout-warning-bar: #ff9800;
    --callout-tip-bar: #4caf50;
    --callout-danger-bar: #f44336;

    /* 徽章与好坏对照 */
    --badge-basic-bg: #e8f5e9;
    --badge-basic-fg: #2e7d32;
    --badge-mid-bg: #fff3e0;
    --badge-mid-fg: #b34700;
    --badge-adv-bg: #fce4ec;
    --badge-adv-fg: #c2185b;
    --compare-good-bg: #e8f5e9;
    --compare-bad-bg: #ffebee;
}

[data-theme="dark"] {
    color-scheme: dark;

    --primary: #4da3e0;
    --primary-hover: #6fb7ee;
    --text-on-accent: #0b1016;

    --bg-page: #0d1014;
    --bg-surface: #161a21;
    --bg-soft: #1b2028;
    --bg-muted: #1f242d;
    --bg-inline: #232936;
    --bg-code: #0b0e12;
    --bg-code-terminal: #070a0d;
    --terminal-accent: #5ecb6a;
    --bg-note: #2a2412;
    --note-bar: #ffca28;

    --text: #c8cfdb;
    --text-strong: #f2f5fa;
    --text-muted: #96a0b0;
    --text-code: #e8ecf3;

    --border: #2a313c;
    --border-soft: #222831;
    --shadow: 0 2px 10px rgba(0, 0, 0, 0.55);

    --callout-info-bg: #10283c;
    --callout-warning-bg: #33270f;
    --callout-tip-bg: #13291a;
    --callout-danger-bg: #33161a;
    --callout-info-bar: #4da3e0;
    --callout-warning-bar: #ffb74d;
    --callout-tip-bar: #66bb6a;
    --callout-danger-bar: #ef7b7b;

    --badge-basic-bg: #16301f;
    --badge-basic-fg: #6cc186;
    --badge-mid-bg: #33270f;
    --badge-mid-fg: #e2a95e;
    --badge-adv-bg: #331a26;
    --badge-adv-fg: #e884ac;
    --compare-good-bg: #13291a;
    --compare-bad-bg: #33161a;
}

/* ============================================================
   基础排版
   ============================================================ */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    line-height: 1.6;
    color: var(--text);
    background: var(--bg-page);
    transition: background-color 0.18s ease, color 0.18s ease;
}

main {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem;
    background: var(--bg-surface);
    box-shadow: var(--shadow);
    min-height: 100vh;
    transition: background-color 0.18s ease, box-shadow 0.18s ease;
}

h1, h2, h3, h4 { margin-top: 1.5em; margin-bottom: 0.5em; line-height: 1.3; }
h1 { font-size: 2.5rem; border-bottom: 3px solid var(--primary); padding-bottom: 0.3em; }
h2 { font-size: 2rem; border-bottom: 2px solid var(--border); padding-bottom: 0.2em; }
h3 { font-size: 1.5rem; }

p { margin-bottom: 1em; }
ul, ol { margin-left: 2em; margin-bottom: 1em; }
li { margin-bottom: 0.5em; }

a { color: var(--primary); }

/* 行内代码：代码块里的 code 不套这层底 */
code:not([class*="language-"]) {
    background: var(--bg-inline);
    color: var(--text-strong);
    padding: 0.12em 0.38em;
    border-radius: 4px;
    font-size: 0.92em;
}

/* ============================================================
   代码块
   两套主题都保持深色底，Prism 固定 prism-tomorrow，不换主题。
   ============================================================ */
pre,
pre[class*="language-"] {
    background: var(--bg-code);
    padding: 1.5em;
    border-radius: 8px;
    overflow-x: auto;
    position: relative;
    margin-bottom: 1.5em;
}
pre code,
pre[class*="language-"] > code {
    color: var(--text-code);
    font-family: "Courier New", Consolas, monospace;
    font-size: 0.9em;
}
pre.terminal { background: var(--bg-code-terminal); border-left: 4px solid var(--terminal-accent); }

.copy-button {
    position: absolute;
    top: 0.5em;
    right: 0.5em;
    background: var(--primary);
    color: var(--text-on-accent);
    border: none;
    padding: 0.3em 0.8em;
    border-radius: 4px;
    cursor: pointer;
    font-size: 0.85em;
}
.copy-button:hover { background: var(--primary-hover); }

/* ============================================================
   组件
   ============================================================ */
.callout {
    padding: 1em 1.5em;
    margin-bottom: 1.5em;
    border-left: 4px solid;
    border-radius: 4px;
}
.callout-info { background: var(--callout-info-bg); border-color: var(--callout-info-bar); }
.callout-warning { background: var(--callout-warning-bg); border-color: var(--callout-warning-bar); }
.callout-tip { background: var(--callout-tip-bg); border-color: var(--callout-tip-bar); }
.callout-danger { background: var(--callout-danger-bg); border-color: var(--callout-danger-bar); }

details { margin-bottom: 1.5em; border: 1px solid var(--border); border-radius: 4px; padding: 1em; }
summary { cursor: pointer; font-weight: bold; user-select: none; }
.details-content { margin-top: 1em; padding-top: 1em; border-top: 1px solid var(--border-soft); }

.tabs { margin-bottom: 1.5em; }
.tab-buttons { display: flex; gap: 0.5em; border-bottom: 2px solid var(--border); }
.tab-buttons button {
    padding: 0.5em 1em;
    border: none;
    background: transparent;
    color: var(--text);
    cursor: pointer;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
}
.tab-buttons button:hover { color: var(--primary); }
.tab-buttons button.active { border-bottom-color: var(--primary); color: var(--primary); font-weight: bold; }
.tab-content { display: none; padding-top: 1em; }
.tab-content.active { display: block; }

table { width: 100%; border-collapse: collapse; margin-bottom: 1.5em; }
th, td { padding: 0.8em; border: 1px solid var(--border); text-align: left; }
th { background: var(--bg-muted); font-weight: bold; }
.comparison .good { background: var(--compare-good-bg); }
.comparison .bad { background: var(--compare-bad-bg); }

.steps { margin-bottom: 1.5em; }
.step { display: flex; gap: 1em; margin-bottom: 1.5em; }
.step-number {
    flex-shrink: 0;
    width: 2em;
    height: 2em;
    background: var(--primary);
    color: var(--text-on-accent);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}
.step-content { flex: 1; }

.definition {
    background: var(--bg-soft);
    border: 2px solid var(--primary);
    border-radius: 8px;
    padding: 1.5em;
    margin-bottom: 1.5em;
}
.definition h4 { margin-top: 0; color: var(--primary); }

.sidebar-note {
    background: var(--bg-note);
    border-left: 4px solid var(--note-bar);
    padding: 1em;
    margin: 1.5em 0;
    font-size: 0.95em;
}

.chapter-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75em;
    padding: 1em 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 2em;
}
.chapter-nav a { color: var(--primary); text-decoration: none; font-weight: 500; }
.chapter-nav a:hover { text-decoration: underline; }

.chapter-footer {
    margin-top: 3em;
    padding-top: 2em;
    border-top: 2px solid var(--border);
}
.chapter-footer .chapter-nav { border: none; margin: 0; }

.intro { font-size: 1.1em; color: var(--text-muted); margin-bottom: 2em; }
.chapter-list { display: flex; flex-direction: column; gap: 1.5em; }
.chapter-item { border: 1px solid var(--border); border-radius: 8px; padding: 1.5em; background: var(--bg-soft); }
.chapter-item h3 { margin: 0.5em 0; }
.chapter-item a { text-decoration: none; color: var(--primary); }
.chapter-item a:hover { text-decoration: underline; }

.chapter-badge { display: inline-block; padding: 0.2em 0.8em; border-radius: 12px; font-size: 0.85em; font-weight: bold; margin-right: 0.5em; }
.chapter-badge.basic { background: var(--badge-basic-bg); color: var(--badge-basic-fg); }
.chapter-badge.intermediate { background: var(--badge-mid-bg); color: var(--badge-mid-fg); }
.chapter-badge.advanced { background: var(--badge-adv-bg); color: var(--badge-adv-fg); }

.version-info {
    background: var(--bg-muted);
    padding: 1em;
    border-radius: 4px;
    font-size: 0.9em;
    color: var(--text-muted);
    margin-bottom: 2em;
}

/* ============================================================
   主题切换控件
   .page-toolbar 用于 index.html；章节页把按钮直接放进 .chapter-nav
   ============================================================ */
.page-toolbar {
    max-width: 900px;
    margin: 0 auto;
    padding: 1rem 2rem 0;
    display: flex;
    justify-content: flex-end;
}

.theme-toggle {
    display: inline-flex;
    align-items: center;
    gap: 0.45em;
    padding: 0.35em 0.85em;
    font-size: 0.85rem;
    font-family: inherit;
    color: var(--text-muted);
    background: var(--bg-surface);
    border: 1px solid var(--border);
    border-radius: 999px;
    cursor: pointer;
    transition: color 0.18s ease, border-color 0.18s ease, background-color 0.18s ease;
}
.theme-toggle::before {
    content: "";
    width: 0.55em;
    height: 0.55em;
    border-radius: 50%;
    background: var(--primary);
}
.theme-toggle:hover { color: var(--primary); border-color: var(--primary); }
.theme-toggle:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }

/* ============================================================
   响应式
   ============================================================ */
@media (max-width: 768px) {
    main { padding: 1rem; margin: 0; }
    .page-toolbar { padding: 0.75rem 1rem 0; }
    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.5rem; }
    pre, pre[class*="language-"] { padding: 1em; font-size: 0.85em; }
    .chapter-nav { flex-direction: column; align-items: flex-start; gap: 0.5em; }
    .tabs { overflow-x: auto; }
    .tab-buttons { flex-wrap: nowrap; }
}
```

## assets/script.js（交互脚本）

```javascript
(function () {
    'use strict';

    var THEME_KEY = 'tutorial-theme';

    function readTheme() {
        return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
    }

    function paintButtons(theme) {
        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            var next = theme === 'dark' ? '浅色' : '深色';
            btn.textContent = next;
            btn.setAttribute('aria-pressed', theme === 'dark' ? 'true' : 'false');
            btn.setAttribute('aria-label', '切换到' + next + '主题');
            btn.title = '切换到' + next + '主题';
        });
    }

    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        try { localStorage.setItem(THEME_KEY, theme); } catch (e) { /* 隐私模式下不可写，忽略 */ }
        paintButtons(theme);
    }

    // 兜底：某个页面漏写按钮时自动补一个，保证全站都能切换
    function ensureToggle() {
        if (document.querySelector('[data-theme-toggle]')) return;
        var bar = document.createElement('div');
        bar.className = 'page-toolbar';
        var btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'theme-toggle';
        btn.setAttribute('data-theme-toggle', '');
        bar.appendChild(btn);
        document.body.insertBefore(bar, document.body.firstChild);
    }

    document.addEventListener('DOMContentLoaded', function () {
        ensureToggle();
        paintButtons(readTheme());

        document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
            btn.addEventListener('click', function () {
                setTheme(readTheme() === 'dark' ? 'light' : 'dark');
            });
        });

        // 代码块复制按钮
        document.querySelectorAll('pre code').forEach(function (block) {
            var button = document.createElement('button');
            button.className = 'copy-button';
            button.type = 'button';
            button.textContent = '复制';
            button.setAttribute('aria-label', '复制代码到剪贴板');
            button.addEventListener('click', function () {
                navigator.clipboard.writeText(block.textContent);
                button.textContent = '已复制!';
                setTimeout(function () { button.textContent = '复制'; }, 2000);
            });
            block.parentElement.appendChild(button);
        });

        // 标签页切换
        document.querySelectorAll('.tabs').forEach(function (tabGroup) {
            var buttons = tabGroup.querySelectorAll('.tab-buttons button');
            var contents = tabGroup.querySelectorAll('.tab-content');
            buttons.forEach(function (button, index) {
                button.addEventListener('click', function () {
                    buttons.forEach(function (b) { b.classList.remove('active'); });
                    contents.forEach(function (c) { c.classList.remove('active'); });
                    button.classList.add('active');
                    contents[index].classList.add('active');
                });
            });
        });
    });
})();
```

## 主题色与首屏脚本

每个页面的 `<head>` 里必须有这段内联脚本，**位置放在所有 CSS 之后、`</head>` 之前**。它在首屏绘制前就把 `data-theme` 写进 `<html>`，避免深色用户看到一帧白底：

```html
<meta name="color-scheme" content="light dark">
<script>
    (function () {
        try {
            var saved = localStorage.getItem('tutorial-theme');
            var theme = saved || (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
            document.documentElement.setAttribute('data-theme', theme);
        } catch (e) {
            document.documentElement.setAttribute('data-theme', 'light');
        }
    })();
</script>
```

- 无用户选择时跟随系统 `prefers-color-scheme`
- 手动切换后写入 `localStorage`，键名固定 `tutorial-theme`，值只能是 `light` / `dark`
- 所有页面读同一个键，所以翻页不会跳回默认主题

## Prism.js 代码高亮

**使用 CDN（推荐）：**

在 HTML `<head>` 中，放在 `assets/style.css` 之前：
```html
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
```

在 `</body>` 前：
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/prism.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/components/prism-python.min.js"></script>
<!-- 根据需要添加其他语言 -->
```

**深色模式不要换 Prism 主题。** 代码块在两套主题下都是深底（`--bg-code` / `--bg-code-terminal` 控制），换了浅色 Prism 主题反而会出现浅底浅字。

国内网络或离线场景见 `references/troubleshooting.md` 的 CDN 降级方案。

## 主题样式文件

`theme-*.css` 只覆盖品牌色和字体气质。表面、文字、边框、提示框、徽章等令牌已经在 `style.css` 的深色块里配好，主题文件不必重复。

### theme-tech.css（技术类）

```css
:root {
    --primary: #007acc;
    --primary-hover: #005a9e;
    --text-on-accent: #ffffff;
    --font-stack: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
}
:root[data-theme="dark"] {
    --primary: #4da3e0;
    --primary-hover: #6fb7ee;
    --text-on-accent: #0b1016;
}
body { font-family: var(--font-stack); }
```

### theme-math.css（数学类）

```css
:root {
    --primary: #8b4513;
    --primary-hover: #6d360f;
    --bg-page: #f5f3ed;
    --bg-surface: #fffef8;
    --bg-soft: #f9f7f0;
    --bg-muted: #efece2;
    --text: #2c2416;
    --text-strong: #1b1509;
    --text-muted: #5d5140;
    --border: #d4c9b0;
    --border-soft: #e5dcc7;
    --shadow: 0 1px 3px rgba(60, 45, 20, 0.12);
    --font-stack: Georgia, "Songti SC", serif;
}
:root[data-theme="dark"] {
    --primary: #d2a06a;
    --primary-hover: #e2b882;
    --text-on-accent: #1b1509;
    --bg-page: #14110c;
    --bg-surface: #1d1913;
    --bg-soft: #221d16;
    --bg-muted: #2a2319;
    --bg-inline: #2a2319;
    --text: #e8ddc9;
    --text-strong: #f7efdf;
    --text-muted: #b3a68f;
    --border: #3a3125;
    --border-soft: #2e271d;
    --shadow: 0 1px 4px rgba(0, 0, 0, 0.5);
}
body { font-family: var(--font-stack); }
```

### theme-science.css（科学类）

```css
:root {
    --primary: #1976d2;
    --primary-hover: #145fa8;
    --bg-page: #eceff1;
    --bg-surface: #ffffff;
    --badge-mid-bg: #e3f2fd;
    --badge-mid-fg: #0b5394;
}
:root[data-theme="dark"] {
    --primary: #5eb8f7;
    --primary-hover: #82c9fa;
    --bg-page: #0b1013;
    --bg-surface: #131a20;
    --bg-soft: #18222a;
    --bg-muted: #1c2730;
}
```

### theme-art.css（设计/艺术类）

```css
:root {
    --primary: #c2185b;
    --primary-hover: #a01349;
    --bg-page: #f7f4f6;
    --bg-surface: #ffffff;
}
:root[data-theme="dark"] {
    --primary: #ff7aa8;
    --primary-hover: #ff9dbf;
    --text-on-accent: #110b0e;
    --bg-page: #110b0e;
    --bg-surface: #1a1216;
    --bg-soft: #201619;
    --bg-muted: #251a1e;
}
```

### theme-humanities.css（人文/语言类）

```css
:root {
    --primary: #8a5a2b;
    --primary-hover: #6f4520;
    --bg-page: #f7f2ea;
    --bg-surface: #fffdf7;
    --text: #35291d;
    --text-strong: #211810;
    --border: #ded2bf;
    --font-stack: "Iowan Old Style", Georgia, "Songti SC", serif;
}
:root[data-theme="dark"] {
    --primary: #d9a273;
    --primary-hover: #e8bb92;
    --text-on-accent: #211810;
    --bg-page: #131010;
    --bg-surface: #1d1815;
    --bg-soft: #231d19;
    --bg-muted: #2a231e;
    --text: #eadfce;
    --text-strong: #f8f0e3;
    --text-muted: #b6a690;
    --border: #3b322a;
    --border-soft: #2e2721;
}
body { font-family: var(--font-stack); }
```

### theme-business.css（商业/职场类）

```css
:root {
    --primary: #1f3a5f;
    --primary-hover: #16283f;
    --bg-page: #f4f6f8;
    --bg-surface: #ffffff;
}
:root[data-theme="dark"] {
    --primary: #7fb0dd;
    --primary-hover: #9cc6ee;
    --text-on-accent: #0c1420;
    --bg-page: #0b0f14;
    --bg-surface: #121821;
    --bg-soft: #17202a;
    --bg-muted: #1b2530;
}
```

**取色规则：** 深色的 `--primary` 一定比浅色的更亮、饱和度更低，才能在深底上达到 4.5:1 对比度。不要直接把浅色 `--primary` 搬到深色块里。
