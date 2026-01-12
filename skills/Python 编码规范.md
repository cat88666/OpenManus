# Python 编码规范

## 1. 语言和注释
- **所有注释和文档字符串使用中文**
- 代码中的字符串提示信息使用中文
- 日志消息使用中文
- 变量和函数名使用英文，遵循 Python 命名规范

## 2. 异步编程
- 所有工具执行方法必须是 `async def`
- 使用 `await` 调用异步函数
- 智能体的主要方法都是异步的
- 使用 `asyncio.run()` 作为入口点

## 3. 类型提示
- 所有函数和方法必须包含类型提示
- 使用 `typing` 模块的类型（如 `Optional`, `Dict`, `List`）
- 使用 Pydantic 模型进行数据验证

## 4. 错误处理
- 使用 try-except 捕获异常
- 工具执行失败时返回 `ToolResult` 并设置 `error` 字段
- 记录错误日志使用 `logger.error()`
- 智能体应自动尝试替代方案

## 5. 日志记录
- 使用 `app.logger.logger` 进行日志记录
- 重要操作使用 `logger.info()`
- 警告使用 `logger.warning()`
- 错误使用 `logger.error()`
- 调试信息使用 `logger.debug()`

## 代码风格

### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地应用导入
4. 各组之间用空行分隔

### 类和方法
- 类名使用 PascalCase
- 方法名使用 snake_case
- 私有方法/属性使用单下划线前缀（`_`）
- 使用 Pydantic 的 `Field` 定义模型字段

### 文档字符串
- 所有公共类和方法必须有中文文档字符串
- 使用三引号格式
- 简要说明功能和参数


## 文件头规范
Python 文件应包含：
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
[模块描述]
"""
```
