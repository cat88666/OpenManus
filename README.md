# OpenManus

OpenManus 是一个简洁、开源的智能体实现方案，支持多种工具和 MCP（Model Context Protocol）集成。

## 特性

- 智能体系统：基于 ReAct 模式的智能体实现
- 丰富的工具集：文件操作、浏览器控制、Python 执行、网络搜索等
- MCP 集成：支持 Model Context Protocol，可连接远程工具服务
- 多智能体协作：支持规划流程，协调多个智能体完成任务
- 云沙箱支持：集成 Daytona 云沙箱，支持可视化调试
- 数据可视化：内置图表生成和可视化工具

## 必须遵守文档
- [01-项目架构](skills/01-项目架构.md)
- [02-快速开始](skills/02-快速开始.md)
- [03-禁止事项](skills/03-禁止事项.md)
- [04-开发规范](skills/04-开发规范.md)
- [05-编码规范](skills/05-编码规范.md)

## 开发指南

**添加新功能：**
1. 在 `app/` 修改或添加代码，参考 `app/tool/` 下的现有代码结构
2. 本地测试：`python main.py --prompt "测试您的新功能"`
3. 提交更改：`git add . && git commit -m "feat: 添加了新功能" && git push`

详细开发指南请参考：[开发规范文档](skills/04-开发规范.md)
