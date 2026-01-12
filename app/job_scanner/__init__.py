#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程工作扫描器模块

提供多网站远程工作扫描和 Telegram 推送功能。
"""

from app.job_scanner.scanner import JobScanner
from app.job_scanner.scheduler import JobScannerScheduler

__all__ = ["JobScanner", "JobScannerScheduler"]

