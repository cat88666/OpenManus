#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenManus 主程序入口

这个文件是 OpenManus 智能体系统的启动入口，负责：
1. 解析命令行参数（获取用户提示）
2. 创建并初始化 Manus 智能体
3. 执行用户任务
4. 清理资源并退出

使用方法：
    # 方式一：通过命令行参数传入提示
    python main.py --prompt "你好"

    # 方式二：交互式输入（不提供 --prompt 参数）
    python main.py
    # 然后根据提示输入您的需求

注意：运行前请确保已激活 conda 环境
    conda activate open_manus
"""
import argparse  # 用于解析命令行参数
import asyncio  # 用于异步编程支持

from app.agent.manus import Manus  # 导入 Manus 智能体类
from app.logger import logger  # 导入日志记录器


async def main():
    """
    主函数 - 异步函数，负责整个程序的执行流程

    执行步骤：
    1. 解析命令行参数，获取用户提示（如果有）
    2. 创建并初始化 Manus 智能体实例
    3. 获取用户提示（从命令行参数或交互式输入）
    4. 运行智能体处理用户任务
    5. 清理资源并退出
    """
    # ========== 第一步：解析命令行参数 ==========
    # 创建参数解析器，用于处理命令行输入
    parser = argparse.ArgumentParser(description="使用提示运行 Manus 智能体")

    # 添加 --prompt 参数
    # required=False 表示该参数是可选的（可以不提供）
    # 如果提供了 --prompt，则使用该值；否则会进入交互式输入模式
    parser.add_argument(
        "--prompt",
        type=str,
        required=False,
        help="智能体的输入提示（可选，如果不提供则进入交互式输入模式）"
    )

    # 解析命令行参数，将结果存储在 args 对象中
    args = parser.parse_args()

    # ========== 第二步：创建并初始化智能体 ==========
    # 使用 Manus.create() 工厂方法创建智能体实例
    # await 关键字表示这是一个异步操作，需要等待完成
    # create() 方法会：
    #   - 初始化工具集合（文件操作、浏览器、Python 执行等）
    #   - 连接 MCP 服务器（如果配置了）
    #   - 设置系统提示词和工作空间路径
    agent = await Manus.create()

    try:
        # ========== 第三步：获取用户提示 ==========
        # 如果命令行提供了 --prompt 参数，则使用它
        # 否则，使用 input() 函数交互式地询问用户输入
        prompt = args.prompt if args.prompt else input("请输入您的提示: ")

        # 检查提示是否为空（去除首尾空格后）
        # 如果为空，记录警告并直接返回，不执行任务
        if not prompt.strip():
            logger.warning("提供的提示为空，程序退出。")
            return

        # ========== 第四步：执行任务 ==========
        # 记录开始处理请求的日志
        logger.warning("正在处理您的请求...")

        # 调用智能体的 run() 方法执行任务
        # await 表示等待任务完成（这是一个异步操作）
        # run() 方法会：
        #   - 分析用户需求
        #   - 选择合适工具
        #   - 执行多步骤任务（最多 20 步）
        #   - 返回执行结果
        await agent.run(prompt)

        # 任务完成后记录成功日志
        logger.info("请求处理完成。")

    except KeyboardInterrupt:
        # ========== 异常处理：用户中断 ==========
        # 当用户按下 Ctrl+C 时，会触发 KeyboardInterrupt 异常
        # 这里捕获该异常，记录中断日志，然后正常退出
        # 不会抛出错误，而是优雅地处理中断
        logger.warning("操作已中断（用户按下了 Ctrl+C）。")

    finally:
        # ========== 第五步：清理资源 ==========
        # finally 块确保无论是否发生异常，都会执行清理操作
        # 这是资源管理的最佳实践，防止资源泄漏

        # 清理智能体资源：
        #   - 关闭浏览器上下文（如果使用了浏览器工具）
        #   - 断开所有 MCP 服务器连接
        #   - 释放其他占用的资源
        await agent.cleanup()


if __name__ == "__main__":
    """
    程序入口点

    当直接运行此文件时（而不是作为模块导入），会执行以下代码：
    1. 调用 asyncio.run(main()) 启动异步事件循环
    2. 运行 main() 异步函数
    3. 等待所有异步操作完成
    4. 程序退出

    这是 Python 异步程序的标准启动方式。
    """
    # 启动异步事件循环并运行 main() 函数
    # asyncio.run() 是 Python 3.7+ 推荐的异步程序入口方式
    # 它会：
    #   1. 创建新的事件循环
    #   2. 运行传入的协程（main()）
    #   3. 等待所有任务完成
    #   4. 关闭事件循环
    asyncio.run(main())
