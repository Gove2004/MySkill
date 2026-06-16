# 常见问题与解决方案

## CDN 资源加载失败

**问题**：Prism.js CDN 链接无法访问（国内网络环境、离线使用）

**解决方案**：
1. 使用国内镜像 CDN（如 BootCDN、字节跳动 CDN）
2. 下载到本地 `assets/prism/` 目录
3. 提供降级方案：CDN 失败时使用本地备份

```html
<link rel="stylesheet" href="https://cdn.bootcdn.net/ajax/libs/prism/1.29.0/themes/prism-tomorrow.min.css">
<link rel="stylesheet" href="assets/prism/prism.css">
```

## 代码块高亮不生效

**原因**：语言标注错误或 Prism.js 未加载对应语言模块

**检查**：
- 确认 `<code class="language-python">` 中的语言名正确
- 确认引入了对应语言的 JS 文件
- 打开浏览器控制台查看是否有加载错误

## 移动端显示异常

**原因**：忘记添加 viewport meta 标签或响应式 CSS 未生效

**解决**：
- 确认每个 HTML 都有 `<meta name="viewport" content="width=device-width, initial-scale=1.0">`
- 确认 `style.css` 包含 `@media` 查询
- 测试时使用浏览器开发者工具的移动设备模拟

## 练习题/思考题不够专业

**原因**：题目过于简单或脱离实际

**改进**：
- 基础练习：修改示例代码，添加新功能
- 进阶挑战：实现一个小型但完整的功能模块
- 思考题：引导思考设计权衡、性能影响、边界情况