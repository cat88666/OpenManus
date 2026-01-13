# -*- coding: utf-8 -*-
"""
机会数据库 - 使用MySQL openmanus库
"""

import json
from typing import List, Dict, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Float, Text, DateTime, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.logger import logger

# MySQL连接配置
DATABASE_URL = "mysql+pymysql://avnadmin:${DB_PASSWORD}@mysql-2e7c973-facenada1107-6e0b.h.aivencloud.com:23808/openmanus?ssl_mode=REQUIRED"

engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Opportunity(Base):
    """机会数据模型"""
    __tablename__ = "opportunities"

    id = Column(String(255), primary_key=True)
    platform = Column(String(50), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    budget = Column(Float)
    tech_stack = Column(Text)  # JSON格式
    url = Column(String(500))
    client_info = Column(Text)  # JSON格式
    posted_at = Column(String(50))
    scraped_at = Column(String(50))
    ai_score = Column(Float, default=0, index=True)
    ai_reason = Column(Text)
    analysis_data = Column(Text)  # JSON格式
    status = Column(String(50), default='new', index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OpportunityDB:
    """机会数据库 - 使用MySQL"""

    def __init__(self):
        """初始化数据库"""
        try:
            Base.metadata.create_all(bind=engine)
            logger.info("MySQL数据库连接成功: openmanus库")
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            raise

    def get_session(self) -> Session:
        """获取数据库会话"""
        return SessionLocal()

    def save(self, opportunity: Dict) -> bool:
        """
        保存机会

        Args:
            opportunity: 机会数据

        Returns:
            是否保存成功
        """
        session = self.get_session()
        try:
            opp = Opportunity(
                id=opportunity['id'],
                platform=opportunity['platform'],
                title=opportunity['title'],
                description=opportunity.get('description'),
                budget=opportunity.get('budget'),
                tech_stack=json.dumps(opportunity.get('tech_stack', [])),
                url=opportunity.get('url'),
                client_info=json.dumps(opportunity.get('client_info', {})),
                posted_at=opportunity.get('posted_at'),
                scraped_at=opportunity.get('scraped_at'),
                ai_score=opportunity.get('ai_score', 0),
                ai_reason=opportunity.get('ai_reason'),
                analysis_data=json.dumps(opportunity.get('analysis', {})),
                status=opportunity.get('status', 'new'),
                notes=opportunity.get('notes'),
            )
            session.merge(opp)
            session.commit()
            logger.info(f"机会保存成功: {opportunity['id']}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"保存机会失败: {e}")
            return False
        finally:
            session.close()

    def get_top_opportunities(self, limit: int = 10) -> List[Dict]:
        """
        获取评分最高的机会

        Args:
            limit: 返回数量

        Returns:
            机会列表
        """
        session = self.get_session()
        try:
            opportunities = session.query(Opportunity)\
                .filter(Opportunity.status != 'rejected')\
                .order_by(Opportunity.ai_score.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for opp in opportunities:
                result.append({
                    'id': opp.id,
                    'platform': opp.platform,
                    'title': opp.title,
                    'description': opp.description,
                    'budget': opp.budget,
                    'tech_stack': json.loads(opp.tech_stack) if opp.tech_stack else [],
                    'url': opp.url,
                    'client_info': json.loads(opp.client_info) if opp.client_info else {},
                    'posted_at': opp.posted_at,
                    'scraped_at': opp.scraped_at,
                    'ai_score': opp.ai_score,
                    'ai_reason': opp.ai_reason,
                    'analysis': json.loads(opp.analysis_data) if opp.analysis_data else {},
                    'status': opp.status,
                    'notes': opp.notes,
                    'created_at': opp.created_at.isoformat() if opp.created_at else None,
                    'updated_at': opp.updated_at.isoformat() if opp.updated_at else None,
                })
            return result
        except Exception as e:
            logger.error(f"获取机会失败: {e}")
            return []
        finally:
            session.close()

    def get_by_status(self, status: str, limit: int = 50) -> List[Dict]:
        """
        按状态获取机会

        Args:
            status: 状态
            limit: 返回数量

        Returns:
            机会列表
        """
        session = self.get_session()
        try:
            opportunities = session.query(Opportunity)\
                .filter(Opportunity.status == status)\
                .order_by(Opportunity.ai_score.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for opp in opportunities:
                result.append({
                    'id': opp.id,
                    'platform': opp.platform,
                    'title': opp.title,
                    'budget': opp.budget,
                    'ai_score': opp.ai_score,
                    'status': opp.status,
                })
            return result
        except Exception as e:
            logger.error(f"获取机会失败: {e}")
            return []
        finally:
            session.close()

    def update_status(self, opportunity_id: str, status: str, notes: str = None) -> bool:
        """
        更新机会状态

        Args:
            opportunity_id: 机会ID
            status: 新状态
            notes: 备注

        Returns:
            是否更新成功
        """
        session = self.get_session()
        try:
            opp = session.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
            if opp:
                opp.status = status
                if notes:
                    opp.notes = notes
                opp.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"机会状态更新成功: {opportunity_id} -> {status}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"更新机会状态失败: {e}")
            return False
        finally:
            session.close()

    def get_by_platform(self, platform: str, limit: int = 50) -> List[Dict]:
        """
        按平台获取机会

        Args:
            platform: 平台名称
            limit: 返回数量

        Returns:
            机会列表
        """
        session = self.get_session()
        try:
            opportunities = session.query(Opportunity)\
                .filter(Opportunity.platform == platform)\
                .order_by(Opportunity.ai_score.desc())\
                .limit(limit)\
                .all()
            
            result = []
            for opp in opportunities:
                result.append({
                    'id': opp.id,
                    'platform': opp.platform,
                    'title': opp.title,
                    'budget': opp.budget,
                    'ai_score': opp.ai_score,
                    'status': opp.status,
                })
            return result
        except Exception as e:
            logger.error(f"获取机会失败: {e}")
            return []
        finally:
            session.close()

    def get_stats(self) -> Dict:
        """
        获取统计信息

        Returns:
            统计数据
        """
        session = self.get_session()
        try:
            total = session.query(Opportunity).count()
            by_status = {}
            for status in ['new', 'applied', 'won', 'rejected']:
                count = session.query(Opportunity).filter(Opportunity.status == status).count()
                by_status[status] = count
            
            by_platform = {}
            platforms = session.query(Opportunity.platform).distinct().all()
            for (platform,) in platforms:
                count = session.query(Opportunity).filter(Opportunity.platform == platform).count()
                by_platform[platform] = count
            
            return {
                'total': total,
                'by_status': by_status,
                'by_platform': by_platform,
            }
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}
        finally:
            session.close()

    def close(self):
        """关闭数据库连接"""
        engine.dispose()
        logger.info("数据库连接已关闭")
