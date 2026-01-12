#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置加载模块

从 TOML 配置文件加载扫描器配置。
"""

import tomllib
from pathlib import Path
from typing import Optional

from app.config import PROJECT_ROOT
from app.jobs.models import JobConfig
from app.logger import logger


class ConfigLoader:
    """配置加载器"""

    @staticmethod
    def _get_config_path() -> Path:
        """
        获取配置文件路径

        Returns:
            Path: 配置文件路径

        Raises:
            FileNotFoundError: 如果配置文件不存在
        """
        config_path = PROJECT_ROOT / "config" / "job_scanner.toml"
        if not config_path.exists():
            raise FileNotFoundError(
                f"配置文件不存在: {config_path}\n请创建配置文件或参考示例配置。"
            )
        return config_path

    @staticmethod
    def load_config(config_path: Optional[Path] = None) -> JobConfig:
        """
        加载配置文件

        Args:
            config_path: 配置文件路径，如果为 None 则使用默认路径

        Returns:
            JobConfig: 配置对象

        Raises:
            FileNotFoundError: 如果配置文件不存在
            ValueError: 如果配置文件格式错误
        """
        if config_path is None:
            config_path = ConfigLoader._get_config_path()

        try:
            with config_path.open("rb") as f:
                raw_config = tomllib.load(f)

            # 构建配置对象
            config = JobConfig(**raw_config)
            logger.info(f"成功加载配置文件: {config_path}")
            return config

        except FileNotFoundError:
            logger.error(f"配置文件不存在: {config_path}")
            raise
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise ValueError(f"配置文件格式错误: {e}")
