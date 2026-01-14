# -*- coding: utf-8 -*-
"""
ProjectHunterAgent - 专门负责"接单"的智能体

这是一个自定义的 Agent，专门用于：
1. 调用浏览器爬取职位
2. 自动调用数据库工具保存
3. 循环对每一个新条目进行逻辑推理评分

工作流程：
- 第一步：搜集 - 使用浏览器工具爬取职位信息
- 第二步：存入 - 调用数据库工具保存到MySQL
- 第三步：评估 - 对每个职位进行评分和分析
"""

from typing import Dict, List, Optional
from pydantic import Field

from app.agent.manus import Manus
from app.logger import logger
from app.tool import ToolCollection, DatabaseTool
from app.flow.planning import PlanningFlow, PlanStepStatus


class ProjectHunterAgent(Manus):
    """
    ProjectHunterAgent - 项目猎手智能体
    
    这是一个专门负责"接单"的智能体，继承自 Manus，提供了：
    
    核心功能：
    - 职位搜集：使用浏览器工具爬取职位信息
    - 数据存储：调用数据库工具保存职位到MySQL
    - 智能评分：对职位进行逻辑推理和评分
    
    工作流程：
    1. 初始化时添加DatabaseTool到可用工具
    2. 执行三步工作流：搜集 -> 存入 -> 评估
    3. 支持循环执行，持续监控新职位
    """
    
    # 智能体基本信息
    name: str = "ProjectHunter"
    description: str = "专门负责接单的智能体，可以搜集职位、保存到数据库、进行评分"
    
    # 工作流程跟踪
    planning_flow: Optional[PlanningFlow] = None
    current_workflow_step: str = "idle"  # idle, collecting, storing, evaluating
    collected_opportunities: List[Dict] = Field(default_factory=list)
    
    def __init__(self, **kwargs):
        """初始化ProjectHunterAgent"""
        super().__init__(**kwargs)
        
        # 添加DatabaseTool到可用工具
        if not any(isinstance(tool, DatabaseTool) for tool in self.available_tools.tools):
            self.available_tools.add_tool(DatabaseTool())
            logger.info("已添加DatabaseTool到ProjectHunterAgent的可用工具")
    
    async def run_workflow(self, task: str = "帮我搜集和评估新的工作机会") -> str:
        """
        执行完整的工作流程：搜集 -> 存入 -> 评估
        
        Args:
            task: 任务描述
            
        Returns:
            str: 工作流程执行结果
        """
        logger.info(f"ProjectHunterAgent 开始执行工作流程: {task}")
        
        # 初始化规划流程
        await self._initialize_planning_flow()
        
        # 第一步：搜集职位
        logger.info("【第一步】开始搜集职位...")
        self.current_workflow_step = "collecting"
        collect_result = await self._step_collect_opportunities()
        
        # 第二步：存入数据库
        logger.info("【第二步】开始存入数据库...")
        self.current_workflow_step = "storing"
        store_result = await self._step_store_opportunities()
        
        # 第三步：评估职位
        logger.info("【第三步】开始评估职位...")
        self.current_workflow_step = "evaluating"
        evaluate_result = await self._step_evaluate_opportunities()
        
        self.current_workflow_step = "idle"
        
        # 返回完整的工作流程结果
        workflow_summary = f"""
        ╔════════════════════════════════════════════════════════════╗
        ║           ProjectHunterAgent 工作流程完成                   ║
        ╠════════════════════════════════════════════════════════════╣
        ║ 【第一步】搜集职位:
        ║ {collect_result}
        ║
        ║ 【第二步】存入数据库:
        ║ {store_result}
        ║
        ║ 【第三步】评估职位:
        ║ {evaluate_result}
        ╚════════════════════════════════════════════════════════════╝
        """
        
        logger.info(workflow_summary)
        return workflow_summary
    
    async def _initialize_planning_flow(self) -> None:
        """初始化规划流程"""
        try:
            # 创建规划流程
            self.planning_flow = PlanningFlow(
                agents={"hunter": self},
                plan_id=f"hunt_{self.name}",
                executors=["hunter"]
            )
            
            # 定义工作流程的三个步骤
            steps = [
                {
                    "id": "collect",
                    "name": "搜集职位",
                    "description": "使用浏览器工具爬取职位信息",
                    "type": "collect"
                },
                {
                    "id": "store",
                    "name": "存入数据库",
                    "description": "调用数据库工具保存职位",
                    "type": "store"
                },
                {
                    "id": "evaluate",
                    "name": "评估职位",
                    "description": "对职位进行逻辑推理和评分",
                    "type": "evaluate"
                }
            ]
            
            # 创建计划
            plan = await self.planning_flow.planning_tool.create_plan(
                goal="搜集、存储和评估工作机会",
                steps=steps
            )
            
            logger.info(f"规划流程初始化完成，计划ID: {plan.get('id')}")
            
        except Exception as e:
            logger.error(f"规划流程初始化失败: {str(e)}")
            raise
    
    async def _step_collect_opportunities(self) -> str:
        """
        第一步：搜集职位
        
        使用浏览器工具爬取职位信息
        """
        try:
            # 使用Manus的run方法来执行搜集任务
            prompt = """
            请使用浏览器工具访问以下职位平台，搜集最新的工作机会：
            1. 访问 Upwork (https://www.upwork.com)
            2. 搜索相关的项目和职位
            3. 收集职位信息（标题、描述、预算、技能要求等）
            4. 返回搜集到的职位列表（JSON格式）
            
            请返回格式如下的JSON数据：
            {
                "opportunities": [
                    {
                        "title": "职位标题",
                        "description": "职位描述",
                        "budget": "预算",
                        "skills": ["技能1", "技能2"],
                        "url": "职位链接",
                        "platform": "平台名称"
                    }
                ]
            }
            """
            
            # 执行搜集任务
            result = await self.run(prompt, max_steps=5)
            
            # 解析结果并存储
            self.collected_opportunities = self._parse_opportunities(result)
            
            return f"✓ 成功搜集 {len(self.collected_opportunities)} 个职位"
            
        except Exception as e:
            logger.error(f"搜集职位失败: {str(e)}")
            return f"✗ 搜集职位失败: {str(e)}"
    
    async def _step_store_opportunities(self) -> str:
        """
        第二步：存入数据库
        
        调用数据库工具保存职位到MySQL
        """
        try:
            if not self.collected_opportunities:
                return "✓ 没有新职位需要存储"
            
            # 使用Manus的run方法来执行存储任务
            prompt = f"""
            请使用database工具将以下职位信息存入MySQL数据库：
            
            职位数据：
            {self.collected_opportunities}
            
            请执行以下步骤：
            1. 调用database工具的upsert操作
            2. 表名：opportunities
            3. 对每个职位执行upsert操作
            4. 返回存储结果
            """
            
            # 执行存储任务
            result = await self.run(prompt, max_steps=5)
            
            return f"✓ 成功存储 {len(self.collected_opportunities)} 个职位到数据库"
            
        except Exception as e:
            logger.error(f"存储职位失败: {str(e)}")
            return f"✗ 存储职位失败: {str(e)}"
    
    async def _step_evaluate_opportunities(self) -> str:
        """
        第三步：评估职位
        
        对每个职位进行逻辑推理和评分
        """
        try:
            if not self.collected_opportunities:
                return "✓ 没有职位需要评估"
            
            # 使用Manus的run方法来执行评估任务
            prompt = f"""
            请对以下职位进行逻辑推理和评分：
            
            职位列表：
            {self.collected_opportunities}
            
            评估标准：
            1. 技能匹配度（0-10分）
            2. 预算合理性（0-10分）
            3. 项目复杂度（0-10分）
            4. 时间投入评估（0-10分）
            
            请返回每个职位的评分结果，格式如下：
            {{
                "evaluations": [
                    {{
                        "title": "职位标题",
                        "scores": {{
                            "skill_match": 8,
                            "budget_reasonableness": 7,
                            "complexity": 6,
                            "time_investment": 5
                        }},
                        "total_score": 26,
                        "recommendation": "建议接单"
                    }}
                ]
            }}
            """
            
            # 执行评估任务
            result = await self.run(prompt, max_steps=5)
            
            return f"✓ 成功评估 {len(self.collected_opportunities)} 个职位"
            
        except Exception as e:
            logger.error(f"评估职位失败: {str(e)}")
            return f"✗ 评估职位失败: {str(e)}"
    
    def _parse_opportunities(self, result: str) -> List[Dict]:
        """
        解析搜集结果中的职位信息
        
        Args:
            result: 搜集结果字符串
            
        Returns:
            List[Dict]: 解析后的职位列表
        """
        try:
            import json
            import re
            
            # 尝试从结果中提取JSON
            json_match = re.search(r'\{.*"opportunities".*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
                return data.get("opportunities", [])
            
            return []
            
        except Exception as e:
            logger.warning(f"解析职位信息失败: {str(e)}")
            return []
