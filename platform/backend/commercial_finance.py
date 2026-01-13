"""
团队管理和财务系统
支持30人团队管理、分成计算、USDT支付
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from decimal import Decimal
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommissionRate(Enum):
    """分成比例"""
    LOW = 0.20  # 20%
    MEDIUM = 0.25  # 25%
    HIGH = 0.30  # 30%


class TransactionType(Enum):
    """交易类型"""
    INCOME = "income"  # 收入
    COMMISSION = "commission"  # 分成
    PAYMENT = "payment"  # 支付
    REFUND = "refund"  # 退款


class TransactionStatus(Enum):
    """交易状态"""
    PENDING = "pending"  # 待处理
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败
    CANCELLED = "cancelled"  # 已取消


class TeamMember:
    """团队成员"""
    
    def __init__(self, id: int, name: str, email: str, skills: List[str],
                 hourly_rate: float, commission_rate: float = 0.25,
                 usdt_wallet: str = None):
        self.id = id
        self.name = name
        self.email = email
        self.skills = skills
        self.hourly_rate = hourly_rate
        self.commission_rate = commission_rate
        self.usdt_wallet = usdt_wallet
        self.availability = "available"
        self.projects_completed = 0
        self.total_earned = Decimal('0')
        self.success_rate = 100.0
        self.created_at = datetime.now()
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'skills': self.skills,
            'hourly_rate': self.hourly_rate,
            'commission_rate': self.commission_rate,
            'usdt_wallet': self.usdt_wallet,
            'availability': self.availability,
            'projects_completed': self.projects_completed,
            'total_earned': float(self.total_earned),
            'success_rate': self.success_rate
        }


class Project:
    """项目"""
    
    def __init__(self, id: int, title: str, budget: Decimal, 
                 platform: str, assigned_to: int = None):
        self.id = id
        self.title = title
        self.budget = budget
        self.platform = platform
        self.assigned_to = assigned_to
        self.status = "new"
        self.created_at = datetime.now()
        self.completed_at = None
        self.team_cost = Decimal('0')
        self.platform_profit = Decimal('0')
    
    def calculate_profit(self, team_cost: Decimal) -> Decimal:
        """计算利润"""
        self.team_cost = team_cost
        self.platform_profit = self.budget - team_cost
        return self.platform_profit
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'title': self.title,
            'budget': float(self.budget),
            'platform': self.platform,
            'assigned_to': self.assigned_to,
            'status': self.status,
            'team_cost': float(self.team_cost),
            'platform_profit': float(self.platform_profit)
        }


class FinancialRecord:
    """财务记录"""
    
    def __init__(self, transaction_type: TransactionType, amount: Decimal,
                 currency: str = "USD", description: str = ""):
        self.id = None
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.usdt_amount = self._convert_to_usdt(amount)
        self.description = description
        self.status = TransactionStatus.PENDING
        self.created_at = datetime.now()
        self.completed_at = None
        self.project_id = None
        self.team_member_id = None
    
    def _convert_to_usdt(self, amount: Decimal) -> Decimal:
        """转换为USDT"""
        # 假设 1 USD = 1 USDT
        return amount
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'id': self.id,
            'transaction_type': self.transaction_type.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'usdt_amount': float(self.usdt_amount),
            'status': self.status.value,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class TeamManager:
    """团队管理器"""
    
    def __init__(self):
        self.members: Dict[int, TeamMember] = {}
        self.next_id = 1
    
    def add_member(self, name: str, email: str, skills: List[str],
                   hourly_rate: float, commission_rate: float = 0.25,
                   usdt_wallet: str = None) -> TeamMember:
        """添加团队成员"""
        member = TeamMember(
            id=self.next_id,
            name=name,
            email=email,
            skills=skills,
            hourly_rate=hourly_rate,
            commission_rate=commission_rate,
            usdt_wallet=usdt_wallet
        )
        self.members[self.next_id] = member
        self.next_id += 1
        logger.info(f"添加团队成员: {name}")
        return member
    
    def get_member(self, member_id: int) -> Optional[TeamMember]:
        """获取团队成员"""
        return self.members.get(member_id)
    
    def get_all_members(self) -> List[TeamMember]:
        """获取所有团队成员"""
        return list(self.members.values())
    
    def find_available_members(self, skills: List[str]) -> List[TeamMember]:
        """查找具有特定技能的可用成员"""
        available = []
        for member in self.members.values():
            if member.availability == "available":
                # 检查技能匹配
                if any(skill in member.skills for skill in skills):
                    available.append(member)
        
        # 按成功率排序
        return sorted(available, key=lambda m: m.success_rate, reverse=True)
    
    def set_member_availability(self, member_id: int, availability: str):
        """设置成员可用性"""
        member = self.get_member(member_id)
        if member:
            member.availability = availability
            logger.info(f"设置成员 {member.name} 可用性为: {availability}")
    
    def update_member_stats(self, member_id: int, project_completed: bool,
                           rating: float = 5.0):
        """更新成员统计"""
        member = self.get_member(member_id)
        if member:
            member.projects_completed += 1
            
            # 更新成功率
            if project_completed:
                current_success = (member.success_rate / 100) * (member.projects_completed - 1)
                member.success_rate = ((current_success + rating / 5) / member.projects_completed) * 100
            else:
                member.success_rate = (member.success_rate / 100) * (member.projects_completed - 1) / member.projects_completed * 100
            
            logger.info(f"更新成员 {member.name} 统计: 完成项目数={member.projects_completed}, 成功率={member.success_rate:.2f}%")


class FinanceManager:
    """财务管理器"""
    
    def __init__(self):
        self.projects: Dict[int, Project] = {}
        self.records: List[FinancialRecord] = []
        self.team_manager = TeamManager()
        self.next_project_id = 1
    
    def create_project(self, title: str, budget: Decimal, platform: str) -> Project:
        """创建项目"""
        project = Project(
            id=self.next_project_id,
            title=title,
            budget=budget,
            platform=platform
        )
        self.projects[self.next_project_id] = project
        self.next_project_id += 1
        logger.info(f"创建项目: {title}, 预算: ${budget}")
        return project
    
    def assign_project(self, project_id: int, member_id: int,
                      estimated_cost: Decimal) -> bool:
        """分配项目给团队成员"""
        project = self.projects.get(project_id)
        member = self.team_manager.get_member(member_id)
        
        if not project or not member:
            logger.error("项目或成员不存在")
            return False
        
        project.assigned_to = member_id
        project.status = "assigned"
        project.calculate_profit(estimated_cost)
        
        # 记录财务
        self._record_project_income(project)
        
        logger.info(f"项目 {project.title} 分配给 {member.name}")
        logger.info(f"项目预算: ${project.budget}, 团队成本: ${estimated_cost}, 平台利润: ${project.platform_profit}")
        
        return True
    
    def _record_project_income(self, project: Project):
        """记录项目收入"""
        record = FinancialRecord(
            transaction_type=TransactionType.INCOME,
            amount=project.budget,
            description=f"项目收入: {project.title}"
        )
        record.project_id = project.id
        record.status = TransactionStatus.COMPLETED
        record.completed_at = datetime.now()
        self.records.append(record)
    
    def calculate_commission(self, project_id: int) -> Dict:
        """计算分成"""
        project = self.projects.get(project_id)
        member = self.team_manager.get_member(project.assigned_to)
        
        if not project or not member:
            logger.error("项目或成员不存在")
            return {}
        
        # 团队成员分成
        member_commission = project.team_cost * Decimal(str(member.commission_rate))
        
        # 平台利润
        platform_profit = project.platform_profit
        
        logger.info(f"项目 {project.title} 分成计算:")
        logger.info(f"  团队成员 ({member.name}): ${member_commission} ({member.commission_rate*100:.0f}%)")
        logger.info(f"  平台利润: ${platform_profit} ({(1-member.commission_rate)*100:.0f}%)")
        
        return {
            'project_id': project_id,
            'member_id': member.id,
            'member_commission': float(member_commission),
            'platform_profit': float(platform_profit),
            'total_budget': float(project.budget)
        }
    
    def process_payment(self, member_id: int, amount: Decimal,
                       usdt_wallet: str) -> bool:
        """处理支付"""
        member = self.team_manager.get_member(member_id)
        
        if not member:
            logger.error("成员不存在")
            return False
        
        # 创建支付记录
        record = FinancialRecord(
            transaction_type=TransactionType.PAYMENT,
            amount=amount,
            description=f"支付给 {member.name}"
        )
        record.team_member_id = member_id
        record.status = TransactionStatus.PENDING
        self.records.append(record)
        
        # 更新成员收益
        member.total_earned += amount
        
        logger.info(f"创建支付记录: 支付给 {member.name} ${amount} USDT")
        logger.info(f"成员总收益: ${member.total_earned}")
        
        return True
    
    def get_monthly_stats(self, year: int, month: int) -> Dict:
        """获取月度统计"""
        total_income = Decimal('0')
        total_commission = Decimal('0')
        total_profit = Decimal('0')
        project_count = 0
        
        for record in self.records:
            if record.created_at.year == year and record.created_at.month == month:
                if record.transaction_type == TransactionType.INCOME:
                    total_income += record.amount
                elif record.transaction_type == TransactionType.COMMISSION:
                    total_commission += record.amount
        
        total_profit = total_income - total_commission
        
        # 统计项目数
        for project in self.projects.values():
            if project.created_at.year == year and project.created_at.month == month:
                project_count += 1
        
        return {
            'year': year,
            'month': month,
            'total_income': float(total_income),
            'total_commission': float(total_commission),
            'total_profit': float(total_profit),
            'profit_margin': float(total_profit / total_income * 100) if total_income > 0 else 0,
            'project_count': project_count,
            'average_project_value': float(total_income / project_count) if project_count > 0 else 0
        }
    
    def get_team_performance(self) -> List[Dict]:
        """获取团队绩效"""
        performance = []
        
        for member in self.team_manager.get_all_members():
            performance.append({
                'member_id': member.id,
                'name': member.name,
                'skills': member.skills,
                'projects_completed': member.projects_completed,
                'success_rate': member.success_rate,
                'total_earned': float(member.total_earned),
                'hourly_rate': member.hourly_rate,
                'commission_rate': member.commission_rate * 100
            })
        
        # 按成功率排序
        return sorted(performance, key=lambda x: x['success_rate'], reverse=True)


# 使用示例
def main():
    """主函数"""
    
    # 1. 初始化财务管理器
    fm = FinanceManager()
    
    # 2. 添加30人团队
    team_data = [
        ("Alice", "alice@example.com", ["Python", "Django", "PostgreSQL"], 50, 0.25, "wallet_alice"),
        ("Bob", "bob@example.com", ["Java", "Spring", "MySQL"], 55, 0.25, "wallet_bob"),
        ("Charlie", "charlie@example.com", ["Go", "Kubernetes", "Docker"], 60, 0.30, "wallet_charlie"),
        ("Diana", "diana@example.com", ["React", "Vue", "TypeScript"], 45, 0.20, "wallet_diana"),
        ("Eve", "eve@example.com", ["Node.js", "Express", "MongoDB"], 50, 0.25, "wallet_eve"),
        # ... 添加更多团队成员
    ]
    
    for name, email, skills, hourly_rate, commission_rate, wallet in team_data:
        fm.team_manager.add_member(name, email, skills, hourly_rate, commission_rate, wallet)
    
    logger.info(f"已添加 {len(fm.team_manager.get_all_members())} 个团队成员")
    
    # 3. 创建项目
    project1 = fm.create_project("Django REST API", Decimal('5000'), "upwork")
    project2 = fm.create_project("React Dashboard", Decimal('8000'), "toptal")
    project3 = fm.create_project("Go Microservice", Decimal('10000'), "linkedin")
    
    # 4. 分配项目
    fm.assign_project(project1.id, 1, Decimal('1500'))  # Alice
    fm.assign_project(project2.id, 4, Decimal('2400'))  # Diana
    fm.assign_project(project3.id, 3, Decimal('3000'))  # Charlie
    
    # 5. 计算分成
    logger.info("\n=== 分成计算 ===")
    for project_id in [project1.id, project2.id, project3.id]:
        commission = fm.calculate_commission(project_id)
        logger.info(f"项目 {project_id}: {commission}")
    
    # 6. 处理支付
    logger.info("\n=== 处理支付 ===")
    fm.process_payment(1, Decimal('375'), "wallet_alice")  # 1500 * 25%
    fm.process_payment(4, Decimal('480'), "wallet_diana")  # 2400 * 20%
    fm.process_payment(3, Decimal('900'), "wallet_charlie")  # 3000 * 30%
    
    # 7. 获取月度统计
    logger.info("\n=== 月度统计 ===")
    stats = fm.get_monthly_stats(datetime.now().year, datetime.now().month)
    logger.info(f"月收入: ${stats['total_income']}")
    logger.info(f"月支出: ${stats['total_commission']}")
    logger.info(f"月利润: ${stats['total_profit']}")
    logger.info(f"利润率: {stats['profit_margin']:.2f}%")
    logger.info(f"项目数: {stats['project_count']}")
    logger.info(f"平均项目价值: ${stats['average_project_value']}")
    
    # 8. 获取团队绩效
    logger.info("\n=== 团队绩效 ===")
    performance = fm.get_team_performance()
    for perf in performance[:5]:
        logger.info(f"{perf['name']}: 完成项目数={perf['projects_completed']}, 成功率={perf['success_rate']:.2f}%, 总收益=${perf['total_earned']}")


if __name__ == "__main__":
    main()
