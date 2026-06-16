# index.html 完整示例

参考模板，生成教程时按实际主题替换内容。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python 进阶教程</title>
    <link rel="stylesheet" href="assets/style.css">
    <link rel="stylesheet" href="assets/theme-tech.css">
</head>
<body>
    <main>
        <h1>Python 进阶教程</h1>
        <p class="intro">深入掌握 Python 高级特性，包含生产环境实战经验、性能优化和最佳实践。</p>
        
        <div class="callout callout-info">
            <strong>关于本教程</strong>：
            <ul>
                <li><strong>前置知识</strong>：已掌握 Python 基础语法（变量、函数、类）</li>
                <li><strong>学习深度</strong>：系统掌握，包含生产实践和调试技巧</li>
                <li><strong>主题风格</strong>：技术蓝（适合编程类教程，代码高亮优化）</li>
            </ul>
        </div>

        <h2>课程目录</h2>
        
        <div class="chapter-list">
            <div class="chapter-item">
                <span class="chapter-badge basic">基础</span>
                <h3><a href="01-iterators-generators.html">01 - 迭代器与生成器</a></h3>
                <p>理解迭代协议、生成器表达式、yield 关键字和惰性求值</p>
            </div>
            
            <div class="chapter-item">
                <span class="chapter-badge basic">基础</span>
                <h3><a href="02-decorators.html">02 - 装饰器深入</a></h3>
                <p>函数装饰器、类装饰器、装饰器工厂和常见应用场景</p>
            </div>
            
            <div class="chapter-item">
                <span class="chapter-badge basic">基础</span>
                <h3><a href="03-context-managers.html">03 - 上下文管理器</a></h3>
                <p>with 语句原理、自定义上下文管理器、资源管理最佳实践</p>
            </div>
            
            <div class="chapter-item">
                <span class="chapter-badge intermediate">进阶</span>
                <h3><a href="04-exception-handling.html">04 - 异常处理最佳实践</a></h3>
                <p>异常链、重试策略、调试技巧和生产环境错误处理</p>
            </div>
            
            <div class="chapter-item">
                <span class="chapter-badge intermediate">进阶</span>
                <h3><a href="05-concurrency.html">05 - 并发编程</a></h3>
                <p>多线程、多进程、asyncio、GIL 和性能权衡</p>
            </div>
            
            <div class="chapter-item">
                <span class="chapter-badge advanced">高级</span>
                <h3><a href="06-metaclasses.html">06 - 元类与类型系统</a></h3>
                <p>元类、类型注解、Protocol 和运行时类型检查</p>
            </div>
        </div>

        <h2>学习资源</h2>
        <ul>
            <li><a href="https://docs.python.org/3/" target="_blank">Python 官方文档</a></li>
            <li><a href="https://peps.python.org/" target="_blank">Python 增强提案 (PEPs)</a></li>
        </ul>
    </main>
</body>
</html>
```

对应的 CSS 添加到 `style.css`：

```css
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
```