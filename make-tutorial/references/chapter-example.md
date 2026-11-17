## 完整章节示例

以下是一个专业级章节的完整示例（Python 错误处理教程）。`<head>` 里的内联主题脚本和 `nav` 里的 `data-theme-toggle` 按钮是必留部分，不要删减。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <title>异常处理最佳实践 - Python 进阶教程</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
    <link rel="stylesheet" href="assets/style.css">
    <link rel="stylesheet" href="assets/theme-tech.css">
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
</head>
<body>
    <nav class="chapter-nav">
        <a href="index.html">目录</a>
        <a href="03-context-managers.html">← 上一章</a>
        <a href="05-concurrency.html">下一章 →</a>
        <button class="theme-toggle" type="button" data-theme-toggle aria-pressed="false">深色</button>
    </nav>

    <main>
        <h1>异常处理最佳实践</h1>
        
        <p>异常处理不仅是捕获错误，更是设计健壮系统的核心机制。本章探讨生产环境中的异常处理策略、常见陷阱和调试技巧。</p>

        <h2>为什么异常处理很重要</h2>
        
        <p>在生产环境中，未处理的异常会导致：</p>
        <ul>
            <li>服务崩溃，影响可用性</li>
            <li>数据不一致，破坏业务逻辑</li>
            <li>资源泄漏（文件句柄、数据库连接）</li>
            <li>难以调试的间歇性故障</li>
        </ul>

        <div class="callout callout-warning">
            <strong>常见误区</strong>：很多开发者认为 <code>try-except</code> 会降低性能。实际上，在正常路径下（无异常抛出），try 块的开销几乎为零。性能问题通常出在频繁抛出和捕获异常。
        </div>

        <h2>基本原则：精确捕获</h2>

        <p>永远捕获具体的异常类型，而不是使用裸 <code>except</code>：</p>

        <table class="comparison">
            <thead>
                <tr><th>推荐写法</th><th>不推荐写法</th></tr>
            </thead>
            <tbody>
                <tr>
                    <td class="good">
<pre><code class="language-python">try:
    data = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"Invalid JSON: {e}")
    return None
</code></pre>
                    </td>
                    <td class="bad">
<pre><code class="language-python">try:
    data = json.loads(response)
except:  # 捕获所有异常，包括 KeyboardInterrupt
    return None
</code></pre>
                    </td>
                </tr>
            </tbody>
        </table>

        <div class="callout callout-danger">
            <strong>陷阱</strong>：裸 <code>except</code> 会捕获 <code>KeyboardInterrupt</code> 和 <code>SystemExit</code>，导致程序无法正常退出。至少使用 <code>except Exception</code>。
        </div>

        <h2>真实场景：API 调用重试</h2>

        <p>生产代码通常需要处理网络不稳定、服务超时等问题。以下是一个带退避策略的重试实现：</p>

<pre><code class="language-python">import time
import requests
from requests.exceptions import Timeout, ConnectionError

def fetch_with_retry(url, max_retries=3, backoff=2):
    """
    带指数退避的 HTTP 请求
    
    Args:
        url: 目标 URL
        max_retries: 最大重试次数
        backoff: 退避倍数
    
    Returns:
        响应对象，失败时返回 None
    
    Raises:
        ValueError: URL 格式错误（不可恢复错误，不重试）
    """
    if not url.startswith(('http://', 'https://')):
        raise ValueError(f"Invalid URL: {url}")
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()  # 4xx/5xx 抛出异常
            return response
        
        except Timeout:
            wait = backoff ** attempt
            print(f"Timeout, retrying in {wait}s... (attempt {attempt + 1}/{max_retries})")
            time.sleep(wait)
        
        except ConnectionError as e:
            if attempt == max_retries - 1:
                print(f"Connection failed after {max_retries} attempts: {e}")
                return None
            time.sleep(backoff ** attempt)
        
        except requests.HTTPError as e:
            # 5xx 可重试，4xx 不可恢复
            if e.response.status_code >= 500:
                time.sleep(backoff ** attempt)
            else:
                print(f"Client error: {e.response.status_code}")
                return None
    
    return None
</code></pre>

        <div class="callout callout-tip">
            <strong>设计考量</strong>：
            <ul>
                <li><strong>区分可恢复与不可恢复错误</strong>：<code>ValueError</code> 直接抛出，<code>Timeout</code> 重试</li>
                <li><strong>指数退避</strong>：避免在服务故障时雪崩</li>
                <li><strong>明确返回值</strong>：成功返回 Response，失败返回 None（调用者可判断）</li>
            </ul>
        </div>

        <h2>异常链：保留上下文</h2>

        <p>在转换异常时，使用 <code>raise ... from</code> 保留原始异常：</p>

<pre><code class="language-python">class DataValidationError(Exception):
    """业务层异常"""
    pass

def parse_user_data(raw_data):
    try:
        return json.loads(raw_data)
    except json.JSONDecodeError as e:
        # 保留原始异常，方便调试
        raise DataValidationError(f"Invalid user data format") from e

# 调试时可以看到完整异常链
try:
    parse_user_data("not json")
except DataValidationError:
    import traceback
    traceback.print_exc()  # 会打印 JSONDecodeError 和 DataValidationError
</code></pre>

        <h2>常见陷阱与调试</h2>

        <details>
            <summary>点击展开：异常被静默吞噬</summary>
            <div class="details-content">
                <p><strong>现象</strong>：代码执行后没有任何错误提示，但结果不对。</p>
                <p><strong>原因</strong>：<code>except</code> 块捕获了异常但没有记录日志。</p>
                <p><strong>解决</strong>：至少记录日志，或者重新抛出：</p>
<pre><code class="language-python">try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")  # 自动记录堆栈
    raise  # 重新抛出原始异常
</code></pre>
            </div>
        </details>

        <h2>练习与思考</h2>

        <div class="steps">
            <div class="step">
                <span class="step-number">1</span>
                <div class="step-content">
                    <h4>基础练习</h4>
                    <p>修改上面的 <code>fetch_with_retry</code>，添加对 DNS 解析失败的处理（提示：捕获 <code>requests.exceptions.InvalidURL</code>）。</p>
                </div>
            </div>
            <div class="step">
                <span class="step-number">2</span>
                <div class="step-content">
                    <h4>进阶挑战</h4>
                    <p>实现一个上下文管理器，自动记录代码块的执行时间和异常信息。</p>
                </div>
            </div>
            <div class="step">
                <span class="step-number">3</span>
                <div class="step-content">
                    <h4>思考题</h4>
                    <p>为什么不建议在循环中频繁抛出和捕获异常？如何重构成性能更好的版本？</p>
                </div>
            </div>
        </div>

        <h2>本章小结</h2>
        <ul>
            <li>精确捕获异常类型，避免裸 <code>except</code></li>
            <li>区分可恢复错误（重试）和不可恢复错误（快速失败）</li>
            <li>使用 <code>raise ... from</code> 保留异常链</li>
            <li>生产代码必须记录日志，便于事后排查</li>
        </ul>

        <div class="callout callout-info">
            <strong>延伸阅读</strong>：
            <ul>
                <li><a href="https://docs.python.org/3/library/exceptions.html" target="_blank">Python 官方文档：内置异常</a></li>
                <li><a href="https://peps.python.org/pep-3134/" target="_blank">PEP 3134：异常链机制</a></li>
            </ul>
        </div>
    </main>

    <footer class="chapter-footer">
        <nav class="chapter-nav bottom">
            <a href="03-context-managers.html">← 上一章：上下文管理器</a>
            <a href="05-concurrency.html">下一章：并发编程 →</a>
        </nav>
