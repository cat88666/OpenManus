#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse  # 用于解析命令行参数
import asyncio  # 用于异步编程支持

from app.agent.manus import Manus
from app.logger import logger

async def main():
    parser = argparse.ArgumentParser(description="使用提示运行Manus智能体")
    parser.add_argument( "--prompt",type=str,required=False,help="智能体的输入提示")
    args = parser.parse_args()
    agent = await Manus.create()

    try:
        prompt = args.prompt if args.prompt else input("请输入您的提示: ")
        if not prompt.strip():
            logger.warning("提供的提示为空，程序退出。")
            return
        logger.warning("正在处理您的请求...")
        await agent.run(prompt)
        logger.info("请求处理完成。")
    except KeyboardInterrupt:
        logger.warning("操作已中断（用户按下了 Ctrl+C）。")
    finally:
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
