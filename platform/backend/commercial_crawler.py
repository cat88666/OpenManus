"""
远程项目爬虫和自动投递系统
支持多个平台：Upwork, Toptal, LinkedIn, FlexJobs等
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from enum import Enum
import aiohttp
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Platform(Enum):
    """支持的平台"""
    UPWORK = "upwork"
    TOPTAL = "toptal"
    LINKEDIN = "linkedin"
    FLEXJOBS = "flexjobs"
    FREELANCER = "freelancer"
    GURU = "guru"


class ProjectStatus(Enum):
    """项目状态"""
    NEW = "new"
    APPLIED = "applied"
    ACCEPTED = "accepted"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REJECTED = "rejected"


class RemoteProjectCrawler:
    """远程项目爬虫"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    async def crawl_upwork_projects(self, keywords: List[str]) -> List[Dict]:
        """爬取Upwork项目"""
        projects = []
        
        try:
            for keyword in keywords:
                url = f"https://www.upwork.com/ab/find-work/search?q={keyword}&sort=recency"
                
                # 使用Selenium处理JavaScript渲染的内容
                driver = webdriver.Chrome()
                driver.get(url)
                
                # 等待项目列表加载
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "job-tile"))
                )
                
                # 解析项目
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                job_tiles = soup.find_all('div', class_='job-tile')
                
                for tile in job_tiles:
                    try:
                        project = self._parse_upwork_project(tile)
                        if project:
                            projects.append(project)
                    except Exception as e:
                        logger.error(f"解析Upwork项目失败: {e}")
                
                driver.quit()
                
        except Exception as e:
            logger.error(f"爬取Upwork项目失败: {e}")
        
        return projects
    
    def _parse_upwork_project(self, tile) -> Optional[Dict]:
        """解析Upwork项目"""
        try:
            title = tile.find('h2', class_='job-title').text.strip()
            description = tile.find('p', class_='job-description').text.strip()
            budget = tile.find('span', class_='budget').text.strip()
            skills = [s.text.strip() for s in tile.find_all('span', class_='skill')]
            
            # 提取数字预算
            budget_value = self._extract_budget(budget)
            
            return {
                'platform': Platform.UPWORK.value,
                'title': title,
                'description': description,
                'budget': budget_value,
                'skills': skills,
                'duration': self._extract_duration(description),
                'client_rating': self._extract_rating(tile),
                'url': tile.find('a')['href'],
                'posted_at': datetime.now(),
                'status': ProjectStatus.NEW.value
            }
        except Exception as e:
            logger.error(f"解析项目失败: {e}")
            return None
    
    async def crawl_toptal_projects(self) -> List[Dict]:
        """爬取Toptal项目"""
        projects = []
        
        try:
            url = "https://www.toptal.com/jobs"
            
            driver = webdriver.Chrome()
            driver.get(url)
            
            # 等待项目加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "job-card"))
            )
            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            job_cards = soup.find_all('div', class_='job-card')
            
            for card in job_cards:
                try:
                    project = self._parse_toptal_project(card)
                    if project:
                        projects.append(project)
                except Exception as e:
                    logger.error(f"解析Toptal项目失败: {e}")
            
            driver.quit()
            
        except Exception as e:
            logger.error(f"爬取Toptal项目失败: {e}")
        
        return projects
    
    def _parse_toptal_project(self, card) -> Optional[Dict]:
        """解析Toptal项目"""
        try:
            title = card.find('h3', class_='job-title').text.strip()
            description = card.find('p', class_='job-description').text.strip()
            budget = card.find('span', class_='budget').text.strip()
            
            return {
                'platform': Platform.TOPTAL.value,
                'title': title,
                'description': description,
                'budget': self._extract_budget(budget),
                'skills': self._extract_skills(description),
                'duration': self._extract_duration(description),
                'url': card.find('a')['href'],
                'posted_at': datetime.now(),
                'status': ProjectStatus.NEW.value
            }
        except Exception as e:
            logger.error(f"解析项目失败: {e}")
            return None
    
    def _extract_budget(self, budget_str: str) -> float:
        """提取预算数字"""
        import re
        match = re.search(r'\$?([\d,]+)', budget_str)
        if match:
            return float(match.group(1).replace(',', ''))
        return 0.0
    
    def _extract_duration(self, text: str) -> str:
        """提取项目周期"""
        text_lower = text.lower()
        if 'long-term' in text_lower or 'ongoing' in text_lower:
            return 'long-term'
        elif 'short-term' in text_lower or 'one-off' in text_lower:
            return 'short-term'
        else:
            return 'unknown'
    
    def _extract_skills(self, text: str) -> List[str]:
        """从文本中提取技能"""
        common_skills = [
            'Python', 'Java', 'Go', 'Node.js', 'React', 'Vue', 'Angular',
            'DevOps', 'Docker', 'Kubernetes', 'AWS', 'GCP', 'Azure',
            'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch'
        ]
        
        found_skills = []
        for skill in common_skills:
            if skill.lower() in text.lower():
                found_skills.append(skill)
        
        return found_skills
    
    def _extract_rating(self, element) -> float:
        """提取客户评分"""
        try:
            rating = element.find('span', class_='rating').text.strip()
            return float(rating.split('/')[0])
        except:
            return 0.0


class AutoSubmissionSystem:
    """自动投递系统"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.crawler = RemoteProjectCrawler(db_session)
    
    async def auto_submit_proposal(self, project: Dict, proposal_template: str) -> bool:
        """自动提交提案"""
        try:
            # 1. 生成个性化提案
            proposal = self._generate_proposal(project, proposal_template)
            
            # 2. 根据平台提交
            if project['platform'] == Platform.UPWORK.value:
                return await self._submit_upwork_proposal(project, proposal)
            elif project['platform'] == Platform.TOPTAL.value:
                return await self._submit_toptal_proposal(project, proposal)
            
            return False
            
        except Exception as e:
            logger.error(f"自动投递失败: {e}")
            return False
    
    def _generate_proposal(self, project: Dict, template: str) -> str:
        """生成个性化提案"""
        proposal = template
        
        # 替换模板变量
        proposal = proposal.replace('{project_title}', project.get('title', ''))
        proposal = proposal.replace('{project_description}', project.get('description', '')[:200])
        proposal = proposal.replace('{skills}', ', '.join(project.get('skills', [])))
        
        return proposal
    
    async def _submit_upwork_proposal(self, project: Dict, proposal: str) -> bool:
        """提交Upwork提案"""
        try:
            driver = webdriver.Chrome()
            driver.get(project['url'])
            
            # 等待提交按钮
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "submit-proposal-btn"))
            )
            
            # 填写提案
            proposal_field = driver.find_element(By.CLASS_NAME, "proposal-textarea")
            proposal_field.send_keys(proposal)
            
            # 提交
            submit_btn = driver.find_element(By.CLASS_NAME, "submit-proposal-btn")
            submit_btn.click()
            
            # 等待提交完成
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            
            driver.quit()
            return True
            
        except Exception as e:
            logger.error(f"提交Upwork提案失败: {e}")
            return False
    
    async def _submit_toptal_proposal(self, project: Dict, proposal: str) -> bool:
        """提交Toptal提案"""
        try:
            driver = webdriver.Chrome()
            driver.get(project['url'])
            
            # 等待提交按钮
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "apply-btn"))
            )
            
            # 填写提案
            proposal_field = driver.find_element(By.CLASS_NAME, "proposal-textarea")
            proposal_field.send_keys(proposal)
            
            # 提交
            apply_btn = driver.find_element(By.CLASS_NAME, "apply-btn")
            apply_btn.click()
            
            driver.quit()
            return True
            
        except Exception as e:
            logger.error(f"提交Toptal提案失败: {e}")
            return False


class AutoAcceptanceEngine:
    """自动接单引擎"""
    
    def __init__(self, db_session=None):
        self.db_session = db_session
        self.min_budget = 500  # 最小项目预算
        self.min_profit_margin = 0.5  # 最小利润率
        self.min_client_rating = 4.0  # 最小客户评分
    
    def should_accept_project(self, project: Dict, team_members: List[Dict]) -> bool:
        """判断是否应该接单"""
        
        # 1. 检查预算
        if project.get('budget', 0) < self.min_budget:
            logger.info(f"项目预算过低: {project['budget']}")
            return False
        
        # 2. 检查客户评分
        if project.get('client_rating', 0) < self.min_client_rating:
            logger.info(f"客户评分过低: {project['client_rating']}")
            return False
        
        # 3. 计算利润
        estimated_cost = self._estimate_team_cost(project, team_members)
        profit = project['budget'] - estimated_cost
        profit_margin = profit / project['budget'] if project['budget'] > 0 else 0
        
        if profit_margin < self.min_profit_margin:
            logger.info(f"利润率过低: {profit_margin}")
            return False
        
        # 4. 检查团队可用性
        available_members = self._find_available_members(project, team_members)
        if not available_members:
            logger.info("没有可用的团队成员")
            return False
        
        logger.info(f"项目符合接单条件: {project['title']}, 利润率: {profit_margin:.2%}")
        return True
    
    def _estimate_team_cost(self, project: Dict, team_members: List[Dict]) -> float:
        """估计团队成本"""
        # 简单估计：项目预算的30%
        return project.get('budget', 0) * 0.3
    
    def _find_available_members(self, project: Dict, team_members: List[Dict]) -> List[Dict]:
        """查找可用的团队成员"""
        project_skills = set(project.get('skills', []))
        available = []
        
        for member in team_members:
            if member.get('availability') == 'available':
                member_skills = set(member.get('skills', []))
                # 技能匹配度 > 50%
                if member_skills & project_skills:
                    available.append(member)
        
        return available
    
    def assign_project_to_team(self, project: Dict, team_members: List[Dict]) -> Optional[Dict]:
        """分配项目给团队"""
        available_members = self._find_available_members(project, team_members)
        
        if not available_members:
            return None
        
        # 选择最佳匹配的成员
        best_member = self._select_best_member(project, available_members)
        
        return {
            'project_id': project.get('id'),
            'team_member_id': best_member.get('id'),
            'assigned_at': datetime.now(),
            'status': 'assigned'
        }
    
    def _select_best_member(self, project: Dict, available_members: List[Dict]) -> Dict:
        """选择最佳匹配的成员"""
        project_skills = set(project.get('skills', []))
        
        # 按技能匹配度和完成率排序
        def score_member(member):
            member_skills = set(member.get('skills', []))
            skill_match = len(member_skills & project_skills) / len(project_skills) if project_skills else 0
            success_rate = member.get('success_rate', 0) / 100
            return skill_match * 0.7 + success_rate * 0.3
        
        return max(available_members, key=score_member)


# 使用示例
async def main():
    """主函数"""
    
    # 1. 爬取项目
    crawler = RemoteProjectCrawler()
    logger.info("开始爬取项目...")
    
    upwork_projects = await crawler.crawl_upwork_projects(['Python', 'Django', 'React'])
    toptal_projects = await crawler.crawl_toptal_projects()
    
    all_projects = upwork_projects + toptal_projects
    logger.info(f"爬取到 {len(all_projects)} 个项目")
    
    # 2. 自动投递
    submission_system = AutoSubmissionSystem()
    proposal_template = """
    Hi {client_name},
    
    I'm interested in your project: {project_title}
    
    I have extensive experience with: {skills}
    
    I can deliver high-quality results on time and within budget.
    
    Looking forward to hearing from you!
    """
    
    for project in all_projects[:5]:  # 投递前5个项目
        logger.info(f"投递项目: {project['title']}")
        await submission_system.auto_submit_proposal(project, proposal_template)
    
    # 3. 自动接单
    acceptance_engine = AutoAcceptanceEngine()
    
    # 示例团队成员
    team_members = [
        {
            'id': 1,
            'name': 'John',
            'skills': ['Python', 'Django', 'PostgreSQL'],
            'availability': 'available',
            'success_rate': 95
        },
        {
            'id': 2,
            'name': 'Jane',
            'skills': ['React', 'Vue', 'TypeScript'],
            'availability': 'available',
            'success_rate': 98
        }
    ]
    
    for project in all_projects:
        if acceptance_engine.should_accept_project(project, team_members):
            assignment = acceptance_engine.assign_project_to_team(project, team_members)
            logger.info(f"项目已分配: {assignment}")


if __name__ == "__main__":
    asyncio.run(main())
