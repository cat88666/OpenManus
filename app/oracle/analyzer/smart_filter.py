#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机会分析器 - 使用LLM智能评分
"""

import json
import asyncio
from typing import Dict, List, Optional
from app.llm import LLM
from app.logger import logger


class OpportunityAnalyzer:
    """机会分析器 - 使用LLM智能评分"""

    def __init__(self, my_skills: Optional[List[str]] = None, min_budget: float = 300):
        """
        初始化分析器

        Args:
            my_skills: 我的技能列表
            min_budget: 最低预算要求
        """
        # 使用默认配置初始化LLM
        self.llm = LLM(config_name="default")

        # 我的技能配置(可以从config读取)
        self.my_skills = my_skills or [
            "React",
            "Vue.js",
            "JavaScript",
            "TypeScript",
            "Python",
            "FastAPI",
            "Django",
            "Node.js",
            "Express",
            "SQL",
            "MongoDB",
            "REST API",
            "GraphQL",
            "AWS",
            "Docker",
        ]

        # 最低预算要求
        self.min_budget = min_budget

    async def analyze_job(self, job: Dict) -> Dict:
        """
        分析单个职位

        Args:
            job: 职位数据

        Returns:
            分析结果
        """
        try:
            # 构建分析提示词
            prompt = self._build_analysis_prompt(job)

            # 调用LLM分析
            response = await self.llm.ask(
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.3,  # 低温度,更稳定的输出
            )

            # 解析LLM返回
            result = self._parse_llm_response(response)

            # 添加规则过滤
            result = self._apply_rule_filters(job, result)

            logger.info(
                f"[评分:{result['score']}] {job['title'][:50]}... - {result['reason'][:80]}"
            )

            return result

        except Exception as e:
            logger.error(f"分析失败: {e}")
            return {
                "score": 0,
                "reason": f"分析出错: {str(e)}",
                "recommended": False,
                "suggested_bid": 0,
                "match_score": 0,
                "budget_reasonable": False,
                "requirement_clear": False,
                "estimated_hours": 0,
                "risks": [],
                "strengths": [],
            }

    def _build_analysis_prompt(self, job: Dict) -> str:
        """
        构建分析提示词

        Args:
            job: 职位数据

        Returns:
            提示词字符串
        """
        tech_stack_str = ", ".join(job["tech_stack"]) if job["tech_stack"] else "未明确"
        description_preview = (
            job["description"][:800]
            if len(job["description"]) > 800
            else job["description"]
        )

        return f"""你是一个资深的外包接单专家。请评估以下项目是否值得申请。

项目信息:
- 标题: {job['title']}
- 预算: ${job['budget']}
- 技术栈: {tech_stack_str}
- 描述: {description_preview}...

我的技能:
{', '.join(self.my_skills)}

评估维度:
1. 预算合理性 (低于${self.min_budget}不推荐)
2. 技术栈匹配度 (我擅长的技术)
3. 需求明确度 (需求是否清晰)
4. 项目复杂度 (是否能在合理时间完成)
5. 竞争程度 (根据预算和需求判断)

请用以下JSON格式输出(只输出JSON,不要其他文字):
{{
    "score": 85,
    "reason": "一句话总结为什么值得/不值得申请",
    "match_score": 90,
    "budget_reasonable": true,
    "requirement_clear": true,
    "estimated_hours": 40,
    "suggested_bid": 1200,
    "risks": ["可能的风险点"],
    "strengths": ["项目优势"]
}}
"""

    def _parse_llm_response(self, response: str) -> Dict:
        """
        解析LLM返回的JSON

        Args:
            response: LLM返回的字符串

        Returns:
            解析后的字典
        """
        try:
            # 提取JSON部分
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            data = json.loads(response)

            # 添加推荐标志
            data["recommended"] = data.get("score", 0) >= 70

            # 确保所有必需字段存在
            defaults = {
                "score": 50,
                "reason": "无评估原因",
                "match_score": 50,
                "budget_reasonable": False,
                "requirement_clear": False,
                "estimated_hours": 0,
                "suggested_bid": 0,
                "risks": [],
                "strengths": [],
            }

            for key, default_value in defaults.items():
                if key not in data:
                    data[key] = default_value

            return data

        except Exception as e:
            logger.error(f"解析LLM响应失败: {e}, 原始响应: {response[:200]}")
            return {
                "score": 50,
                "reason": "解析失败,需人工审核",
                "recommended": False,
                "suggested_bid": 0,
                "match_score": 0,
                "budget_reasonable": False,
                "requirement_clear": False,
                "estimated_hours": 0,
                "risks": ["解析失败"],
                "strengths": [],
            }

    def _apply_rule_filters(self, job: Dict, analysis: Dict) -> Dict:
        """
        应用规则过滤

        Args:
            job: 职位数据
            analysis: 分析结果

        Returns:
            更新后的分析结果
        """
        # 预算过低,直接降分
        if job["budget"] < self.min_budget:
            analysis["score"] = min(analysis["score"], 40)
            analysis["reason"] = f"预算过低(${job['budget']}). " + analysis["reason"]
            analysis["recommended"] = False
            analysis["budget_reasonable"] = False

        # 技术栈完全不匹配,降分
        if job["tech_stack"] and analysis.get("match_score", 0) < 30:
            analysis["score"] = min(analysis["score"], 50)
            analysis["reason"] = "技术栈不匹配. " + analysis["reason"]
            analysis["recommended"] = False

        # 描述太短,需求不明确
        if len(job.get("description", "")) < 100:
            analysis["score"] = min(analysis["score"], 60)
            analysis["requirement_clear"] = False
            if "需求不明确" not in analysis["reason"]:
                analysis["reason"] = "需求描述过于简短. " + analysis["reason"]

        return analysis

    async def batch_analyze(
        self, jobs: List[Dict], max_concurrent: int = 3
    ) -> List[Dict]:
        """
        批量分析职位

        Args:
            jobs: 职位列表
            max_concurrent: 最大并发数

        Returns:
            带分析结果的职位列表
        """
        results = []

        # 分批处理,避免并发过高
        for i in range(0, len(jobs), max_concurrent):
            batch = jobs[i : i + max_concurrent]
            tasks = [self.analyze_job(job) for job in batch]
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            for job, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"分析职位失败: {job['title']}, 错误: {result}")
                    result = {
                        "score": 0,
                        "reason": f"分析异常: {str(result)}",
                        "recommended": False,
                    }

                results.append({**job, "analysis": result})

        # 按分数排序
        results.sort(key=lambda x: x["analysis"].get("score", 0), reverse=True)

        logger.info(f"批量分析完成: {len(results)}个职位")
        return results
