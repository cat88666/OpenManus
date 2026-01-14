#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Oracle - 机会感知引擎
"""

from .scrapers.upwork_scraper import UpworkScraper
from .analyzer.smart_filter import OpportunityAnalyzer
from .storage.opportunity_db import OpportunityDB
from .oracle_agent import OracleAgent

__all__ = [
    'UpworkScraper',
    'OpportunityAnalyzer',
    'OpportunityDB',
    'OracleAgent'
]

