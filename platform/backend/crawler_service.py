"""
爬虫服务 - 定时爬取远程工作机会
每5秒自动搜索一次新的工作机会
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CrawlerService:
    """爬虫服务 - 定时爬取工作机会"""
    
    def __init__(self, db_manager=None):
        self.db_manager = db_manager
        self.is_running = False
        self.last_crawl_time = None
        self.opportunities_cache = []
        
        # 模拟数据 - 真实场景中应该爬取真实网站
        self.mock_opportunities = [
            {
                "title": "React前端开发 - 电商平台",
                "description": "需要开发一个现代化的电商平台前端，使用React和TypeScript",
                "platform": "upwork",
                "budget": 3500,
                "skills": ["React", "TypeScript", "Tailwind CSS"],
                "duration": "3-6个月",
                "client_rating": 4.8,
                "url": "https://upwork.com/job/react-ecommerce-1"
            },
            {
                "title": "Python后端API开发",
                "description": "构建高性能的REST API，处理大量并发请求",
                "platform": "toptal",
                "budget": 4200,
                "skills": ["Python", "FastAPI", "PostgreSQL"],
                "duration": "2-4个月",
                "client_rating": 4.9,
                "url": "https://toptal.com/job/python-api-2"
            },
            {
                "title": "Go微服务开发",
                "description": "开发微服务架构，支持Kubernetes部署",
                "platform": "linkedin",
                "budget": 5000,
                "skills": ["Go", "Docker", "Kubernetes"],
                "duration": "长期",
                "client_rating": 4.7,
                "url": "https://linkedin.com/job/go-microservices-3"
            },
            {
                "title": "全栈开发 - Node.js + React",
                "description": "开发完整的Web应用，包括前后端",
                "platform": "upwork",
                "budget": 4800,
                "skills": ["Node.js", "React", "MongoDB"],
                "duration": "4-8个月",
                "client_rating": 4.6,
                "url": "https://upwork.com/job/fullstack-nodejs-4"
            },
            {
                "title": "DevOps工程师 - 云基础设施",
                "description": "管理AWS基础设施，配置CI/CD流程",
                "platform": "toptal",
                "budget": 4500,
                "skills": ["AWS", "Docker", "Jenkins"],
                "duration": "3-6个月",
                "client_rating": 4.8,
                "url": "https://toptal.com/job/devops-aws-5"
            },
            {
                "title": "Java企业应用开发",
                "description": "开发Spring Boot企业应用",
                "platform": "flexjobs",
                "budget": 3800,
                "skills": ["Java", "Spring Boot", "MySQL"],
                "duration": "6-12个月",
                "client_rating": 4.5,
                "url": "https://flexjobs.com/job/java-spring-6"
            }
        ]
        
        self.crawl_interval = 5  # 爬取间隔（秒）
    
    def start(self):
        """启动爬虫服务"""
        if self.is_running:
            logger.warning("爬虫服务已在运行")
            return
        
        self.is_running = True
        logger.info("爬虫服务已启动，每5秒搜索一次新机会")
        
        # 启动异步爬虫任务
        asyncio.create_task(self._crawl_loop())
    
    def stop(self):
        """停止爬虫服务"""
        self.is_running = False
        logger.info("爬虫服务已停止")
    
    async def _crawl_loop(self):
        """爬虫主循环 - 每5秒执行一次"""
        while self.is_running:
            try:
                await self.crawl_opportunities()
                await asyncio.sleep(self.crawl_interval)
            except Exception as e:
                logger.error(f"爬虫循环出错: {e}")
                await asyncio.sleep(self.crawl_interval)
    
    async def crawl_opportunities(self) -> List[Dict]:
        """爬取工作机会"""
        try:
            self.last_crawl_time = datetime.now()
            
            # 模拟爬取 - 随机返回一些机会
            new_opportunities = self._generate_opportunities()
            
            # 保存到缓存
            self.opportunities_cache = new_opportunities
            
            # 保存到数据库（如果有）
            if self.db_manager:
                for opp in new_opportunities:
                    await self._save_opportunity(opp)
            
            logger.info(f"✅ 成功爬取 {len(new_opportunities)} 个新机会")
            return new_opportunities
            
        except Exception as e:
            logger.error(f"❌ 爬取机会失败: {e}")
            return []
    
    def _generate_opportunities(self) -> List[Dict]:
        """生成机会列表（模拟爬取）"""
        # 随机选择2-4个机会
        count = random.randint(2, 4)
        selected = random.sample(self.mock_opportunities, count)
        
        # 为每个机会添加时间戳
        for opp in selected:
            opp['crawled_at'] = datetime.now().isoformat()
            opp['id'] = f"opp_{int(time.time())}_{random.randint(1000, 9999)}"
            opp['status'] = 'new'
        
        return selected
    
    async def _save_opportunity(self, opportunity: Dict):
        """保存机会到数据库"""
        try:
            # 这里应该调用数据库管理器保存
            logger.debug(f"保存机会: {opportunity['title']}")
        except Exception as e:
            logger.error(f"保存机会失败: {e}")
    
    def get_latest_opportunities(self, limit: int = 10) -> List[Dict]:
        """获取最新的机会"""
        return self.opportunities_cache[:limit]
    
    def get_crawler_status(self) -> Dict:
        """获取爬虫状态"""
        return {
            "is_running": self.is_running,
            "last_crawl_time": self.last_crawl_time.isoformat() if self.last_crawl_time else None,
            "crawl_interval": self.crawl_interval,
            "cached_opportunities": len(self.opportunities_cache),
            "status": "运行中" if self.is_running else "已停止"
        }


# 全局爬虫实例
crawler_service = None


def init_crawler_service(db_manager=None):
    """初始化爬虫服务"""
    global crawler_service
    crawler_service = CrawlerService(db_manager)
    return crawler_service


def get_crawler_service() -> CrawlerService:
    """获取爬虫服务实例"""
    global crawler_service
    if crawler_service is None:
        crawler_service = CrawlerService()
    return crawler_service


def start_crawler():
    """启动爬虫"""
    service = get_crawler_service()
    service.start()


def stop_crawler():
    """停止爬虫"""
    service = get_crawler_service()
    service.stop()
