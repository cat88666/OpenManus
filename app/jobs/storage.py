#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
存储管理模块

管理已发送工作的记录，避免重复推送。
"""

import json
from pathlib import Path
from typing import Set

from app.config import PROJECT_ROOT
from app.logger import logger


class JobStorage:
    """工作存储管理器"""

    def __init__(self, storage_file: str):
        """
        初始化存储管理器

        Args:
            storage_file: 存储文件路径（相对于项目根目录）
        """
        self.storage_path = PROJECT_ROOT / storage_file
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sent_jobs: Set[str] = set()
        self._load()

    def _load(self) -> None:
        """从文件加载已发送工作记录"""
        if self.storage_path.exists():
            try:
                with self.storage_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    self._sent_jobs = set(data)
                logger.info(f"加载已发送工作记录: {len(self._sent_jobs)} 条")
            except Exception as e:
                logger.error(f"加载存储文件失败: {e}")
                self._sent_jobs = set()
        else:
            logger.info("存储文件不存在，创建新记录")

    def _save(self) -> None:
        """保存已发送工作记录到文件"""
        try:
            with self.storage_path.open("w", encoding="utf-8") as f:
                json.dump(list(self._sent_jobs), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存存储文件失败: {e}")

    def is_sent(self, job_id: str) -> bool:
        """
        检查工作是否已发送

        Args:
            job_id: 工作 ID

        Returns:
            bool: 是否已发送
        """
        return job_id in self._sent_jobs

    def mark_sent(self, job_id: str) -> None:
        """
        标记工作为已发送

        Args:
            job_id: 工作 ID
        """
        self._sent_jobs.add(job_id)
        self._save()

    def mark_sent_batch(self, job_ids: Set[str]) -> None:
        """
        批量标记工作为已发送

        Args:
            job_ids: 工作 ID 集合
        """
        self._sent_jobs.update(job_ids)
        self._save()

    def get_new_jobs(self, all_jobs: list) -> list:
        """
        过滤出未发送的工作

        Args:
            all_jobs: 所有工作列表

        Returns:
            list: 未发送的工作列表
        """
        new_jobs = [job for job in all_jobs if not self.is_sent(job.id)]
        return new_jobs

