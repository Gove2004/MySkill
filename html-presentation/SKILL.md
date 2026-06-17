---
name: html-presentation
description: Create presentations as self-contained HTML files instead of PPTX. AI-editable plain HTML with SVG icons, CSS variables, dark/light themes, fullscreen presentation mode with keyboard navigation. Use when the user asks to make a presentation, slides, 演示文稿, PPT, 幻灯片, or needs to present content visually. Generates a single .html file with no external dependencies.
---

# HTML Presentation

Generate self-contained HTML presentations — one `.html` file = one complete slide deck. No external dependencies, double-click to open.

## Why HTML instead of PPTX

- **AI-editable**: plain text, Edit tool works directly — no binary format
- **Instant preview**: double-click opens in browser
- **Fullscreen mode**: click ▶ to enter presentation mode, keyboard navigation
- **Theme toggle**: dark/light via CSS variables, SVG sun/moon icon
- **Responsive**: works on any screen, no zoom issues
- **No tooling**: zero install, zero dependencies

## Quick Reference: How to Generate

The template (`references/template.html`) is a two-layer file:

**Framework layer** (copy as-is, never modify):
- `<style>` block — all CSS including presentation mode
- Toolbar HTML — theme button (`id="themeBtn"`) + play button
- Exit button + slide counter HTML
- `<script>` block — theme toggle + presentation mode logic

**Content layer** (replace with your slides):
- Everything between `<!-- CONTENT -->` and the framework elements at the bottom
- Replace the hero placeholder and end placeholder with actual slides
- Each slide is `.hero`, `.section`, or `.end`

### How to generate a new presentation

1. Read `references/template.html` for the framework code
2. Write a new `.html` file, copying the framework layer verbatim
3. Fill the content layer with 8-12 slides relevant to the user's topic
4. Customize the accent color to match the topic

## No Emojis

Use inline SVG icons for all UI elements. Never use emoji (🌓 ▶ ✕ ☀️ 🔥 💧 etc.) — they render inconsistently across platforms and look unprofessional.

If you need content icons in cards, use plain text or simple Unicode symbols (→, ×, ∞, ≤, ≥).

## Presentation Mode

Click ▶ (top-right) or tell the user to press it. Fullscreen + keyboard navigation.

| Key | Action |
|---|---|
| `→` `↓` `PageDown` `Space` | Next slide |
| `←` `↑` `PageUp` | Previous slide |
| `Home` | First slide |
| `End` | Last slide |
| `Esc` | Exit presentation |
| Click X (top-right) | Exit presentation |

Slide counter ("3 / 12") displayed bottom-right. Exiting browser fullscreen auto-exits presentation mode.

## Design Patterns

### Hero Slide (always first)

```html
<div class="hero">
  <h1>Title</h1>
  <p>Subtitle or one-line summary</p>
</div>
```

Full-viewport landing. Title has gradient text (see accent customization below).

### Section with h2

Every section has an `<h2>` title with an automatic underline decoration:

```html
<div class="section">
  <h2>Section Title</h2>
  ...
</div>
```

The `h2:after` pseudo-element draws a small accent-colored line under every heading.

### Subtitle below h2

```html
<p class="sub">Supplementary description — context, caveat, or joke</p>
```

Place immediately after `<h2>`. Muted, centered, constrained width. Useful for adding context without cluttering the heading.

### Card Grid

```html
<div class="grid">
  <div class="card"><h3>Title</h3><p>1-2 sentence description.</p></div>
  ...
</div>
```

3-6 cards per grid. Best for: tech stacks, features, comparisons, team members.

### Flow / Steps

```html
<div class="flow">
  <div class="flow-item">
    <div class="num">1</div>
    <div class="text"><h4>Step Name</h4><p>Description. Can use <code>inline code</code>.</p></div>
  </div>
  ...
</div>
```

Best for: workflows, pipelines, timelines, how-to sequences.

### Stats

```html
<div class="stats">
  <div class="stat"><div class="value">100K</div><p>Label</p></div>
  ...
</div>
```

Best for: metrics, achievements, data snapshots.

### Tip / Callout Box

```html
<div class="tip-box">
  <h4>Tip Title</h4>
  <p>Content...</p>
</div>
```

Left-bordered accent box. Add `.tip-box` CSS to `<style>` when using this pattern.

### Code

```html
<code>inline code</code>
<pre><code>multi-line block</code></pre>
```

### Ending Slide

```html
<div class="end">
  <h1>Thanks / Q&A</h1>
  <p>Link, contact, or call to action</p>
</div>
```

## Accent Color Customization

Change 6 values to recolor the entire presentation. Find-and-replace in the `<style>` block:

| What | Where | Example (green) |
|---|---|---|
| Primary accent | `--accent` in `:root` | `#4ade80` |
| Light mode accent | `--accent` in `[data-theme="light"]` | `#16a34a` |
| Hero gradient partner | second color in `.hero h1` `linear-gradient` | `#06b6d4` |
| Flow num gradient partner | second color in `.flow-item .num` `linear-gradient` | same as above |
| Code background | `rgba()` in `code` | `rgba(74,222,128,0.12)` |
| Card hover background | `rgba()` in `.card:hover` | `rgba(74,222,128,0.05)` |

## Content Tips

1. **One topic per slide** — don't mix unrelated content in one grid
2. **3-6 cards per grid** — more than 6 is unreadable
3. **Use flow for sequential content** — numbered steps beat paragraphs
4. **Put real data in cards** — specific numbers, temperatures, names > vague descriptions
5. **End with a link** — repo URL, wiki, contact, or call to action
6. **Card titles are labels** — short and scannable (1-4 words)
7. **Card descriptions are evidence** — facts, not fluff

## Modifying Existing Presentations

Plain HTML = Edit tool works directly:
- "Change the accent to blue"
- "Add a slide about X between slide 3 and 4"
- "Update the hero subtitle"
- "Fix the typo in card 2"

No conversion, no export, no round-trip.