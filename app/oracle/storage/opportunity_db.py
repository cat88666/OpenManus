#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机会数据库 - 使用SQLite
"""

import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
from app.logger import logger


class OpportunityDB:
    """机会数据库 - 使用SQLite"""

    def __init__(self, db_path: str = "workspace/opportunities.db"):
        """
        初始化数据库

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = None
        self._connect()
        self._create_tables()

    def _connect(self):
        """连接数据库"""
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # 返回字典格式
        logger.info(f"数据库连接成功: {self.db_path}")

    def _create_tables(self):
        """创建表"""
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS opportunities (
            id TEXT PRIMARY KEY,
            platform TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            budget REAL,
            tech_stack TEXT,
            url TEXT,
            client_info TEXT,
            posted_at TEXT,
            scraped_at TEXT,
            ai_score REAL DEFAULT 0,
            ai_reason TEXT,
            analysis_data TEXT,
            status TEXT DEFAULT 'new',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_score ON opportunities(ai_score DESC)
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_status ON opportunities(status)
        """)

        self.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_platform ON opportunities(platform)
        """)

        self.conn.commit()
        logger.info("数据表创建成功")

    def save(self, opportunity: Dict) -> bool:
        """
        保存机会

        Args:
            opportunity: 机会数据

        Returns:
            是否保存成功
        """
        try:
            analysis = opportunity.get('analysis', {})

            self.conn.execute("""
            INSERT OR REPLACE INTO opportunities
            (id, platform, title, description, budget, tech_stack, url,
             client_info, posted_at, scraped_at, ai_score, ai_reason,
             analysis_data, status, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                opportunity['id'],
                opportunity['platform'],
                opportunity['title'],
                opportunity['description'],
                opportunity['budget'],
                json.dumps(opportunity.get('tech_stack', []), ensure_ascii=False),
                opportunity.get('url', ''),
                json.dumps(opportunity.get('client_info', {}), ensure_ascii=False),
                opportunity.get('posted_at', ''),
                opportunity.get('scraped_at', ''),
                analysis.get('score', 0),
                analysis.get('reason', ''),
                json.dumps(analysis, ensure_ascii=False),
                'new'
            ))

            self.conn.commit()
            return True

        except Exception as e:
            logger.error(f"保存失败: {e}")
            return False

    def batch_save(self, opportunities: List[Dict]) -> int:
        """
        批量保存

        Args:
            opportunities: 机会列表

        Returns:
            成功保存的数量
        """
        count = 0
        for opp in opportunities:
            if self.save(opp):
                count += 1
        logger.info(f"批量保存完成: {count}/{len(opportunities)}")
        return count

    def get_top_opportunities(self, limit: int = 10, status: str = 'new', min_score: float = 0) -> List[Dict]:
        """
        获取Top机会

        Args:
            limit: 返回数量
            status: 状态过滤
            min_score: 最低分数

        Returns:
            机会列表
        """
        cursor = self.conn.execute("""
        SELECT * FROM opportunities
        WHERE status = ? AND ai_score >= ?
        ORDER BY ai_score DESC, created_at DESC
        LIMIT ?
        """, (status, min_score, limit))

        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_dict(row))

        return results

    def get_by_id(self, opp_id: str) -> Optional[Dict]:
        """
        根据ID获取

        Args:
            opp_id: 机会ID

        Returns:
            机会数据或None
        """
        cursor = self.conn.execute("""
        SELECT * FROM opportunities WHERE id = ?
        """, (opp_id,))

        row = cursor.fetchone()
        return self._row_to_dict(row) if row else None

    def update_status(self, opp_id: str, status: str, notes: str = "") -> bool:
        """
        更新状态

        Args:
            opp_id: 机会ID
            status: 新状态
            notes: 备注

        Returns:
            是否更新成功
        """
        try:
            self.conn.execute("""
            UPDATE opportunities
            SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (status, notes, opp_id))

            self.conn.commit()
            return True
        except Exception as e:
            logger.error(f"更新状态失败: {e}")
            return False

    def get_statistics(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计数据字典
        """
        cursor = self.conn.execute("""
        SELECT
            COUNT(*) as total,
            COUNT(CASE WHEN status = 'new' THEN 1 END) as new_count,
            COUNT(CASE WHEN status = 'applied' THEN 1 END) as applied_count,
            COUNT(CASE WHEN ai_score >= 80 THEN 1 END) as high_score_count,
            AVG(ai_score) as avg_score,
            MAX(ai_score) as max_score,
            MIN(ai_score) as min_score
        FROM opportunities
        """)

        row = cursor.fetchone()
        return dict(row) if row else {}

    def search(self, keyword: str = "", min_score: float = 0, limit: int = 50) -> List[Dict]:
        """
        搜索机会

        Args:
            keyword: 搜索关键词
            min_score: 最低分数
            limit: 返回数量

        Returns:
            机会列表
        """
        if keyword:
            cursor = self.conn.execute("""
            SELECT * FROM opportunities
            WHERE (title LIKE ? OR description LIKE ?) AND ai_score >= ?
            ORDER BY ai_score DESC
            LIMIT ?
            """, (f'%{keyword}%', f'%{keyword}%', min_score, limit))
        else:
            cursor = self.conn.execute("""
            SELECT * FROM opportunities
            WHERE ai_score >= ?
            ORDER BY ai_score DESC
            LIMIT ?
            """, (min_score, limit))

        results = []
        for row in cursor.fetchall():
            results.append(self._row_to_dict(row))

        return results

    def _row_to_dict(self, row) -> Dict:
        """
        SQLite Row转Dict

        Args:
            row: SQLite Row对象

        Returns:
            字典格式数据
        """
        data = dict(row)

        # 解析JSON字段
        if data.get('tech_stack'):
            try:
                data['tech_stack'] = json.loads(data['tech_stack'])
            except:
                data['tech_stack'] = []

        if data.get('client_info'):
            try:
                data['client_info'] = json.loads(data['client_info'])
            except:
                data['client_info'] = {}

        if data.get('analysis_data'):
            try:
                data['analysis'] = json.loads(data['analysis_data'])
            except:
                data['analysis'] = {}

        return data

    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")

