"""
LLM集成服务
"""
import json
import logging
from typing import Optional, Dict, Any, List
from config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务基类"""
    
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.claude_key = settings.CLAUDE_API_KEY
    
    async def analyze_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析机会"""
        raise NotImplementedError
    
    async def generate_proposal(self, opportunity_data: Dict[str, Any]) -> str:
        """生成申请信"""
        raise NotImplementedError
    
    async def generate_code(self, requirement: str, tech_stack: List[str]) -> str:
        """生成代码"""
        raise NotImplementedError


class OpenAIService(LLMService):
    """OpenAI服务"""
    
    def __init__(self):
        super().__init__()
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.openai_key)
        except ImportError:
            logger.warning("OpenAI库未安装")
            self.client = None
    
    async def analyze_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析机会
        
        评分维度：
        1. 预算合理性（0-20分）
        2. 技术栈匹配（0-25分）
        3. 需求明确度（0-20分）
        4. 客户质量（0-20分）
        5. 竞争程度（0-15分）
        """
        if not self.client:
            return self._default_analysis(opportunity_data)
        
        prompt = self._build_analysis_prompt(opportunity_data)
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的外包机会分析师。分析给定的机会并给出详细的评分和建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            result = json.loads(result_text)
            
            return {
                "score": result.get("score", 0),
                "reason": result.get("reason", ""),
                "recommended_budget": result.get("recommended_budget"),
                "risks": result.get("risks", []),
                "recommendations": result.get("recommendations", []),
                "analysis": result
            }
        except Exception as e:
            logger.error(f"OpenAI分析失败: {e}")
            return self._default_analysis(opportunity_data)
    
    async def generate_proposal(self, opportunity_data: Dict[str, Any]) -> str:
        """生成申请信"""
        if not self.client:
            return self._default_proposal(opportunity_data)
        
        prompt = self._build_proposal_prompt(opportunity_data)
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的自由职业者。根据机会信息生成一份专业的申请信。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=settings.OPENAI_TEMPERATURE,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"生成申请信失败: {e}")
            return self._default_proposal(opportunity_data)
    
    async def generate_code(self, requirement: str, tech_stack: List[str]) -> str:
        """生成代码"""
        if not self.client:
            return "# 代码生成失败"
        
        prompt = f"""
        根据以下需求生成代码：
        
        需求：{requirement}
        技术栈：{', '.join(tech_stack)}
        
        请生成完整、可运行的代码。
        """
        
        try:
            response = await self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的代码生成助手。生成高质量、可运行的代码。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"代码生成失败: {e}")
            return "# 代码生成失败"
    
    def _build_analysis_prompt(self, opportunity_data: Dict[str, Any]) -> str:
        """构建分析提示词"""
        return f"""
        分析以下外包机会，给出0-100分的评分：
        
        标题：{opportunity_data.get('title', '')}
        预算：${opportunity_data.get('budget', 'N/A')}
        技术栈：{', '.join(opportunity_data.get('tech_stack', []))}
        客户评价：{opportunity_data.get('client_rating', 'N/A')}/5
        当前申请数：{opportunity_data.get('proposal_count', 'N/A')}
        描述：{opportunity_data.get('description', '')[:200]}...
        
        我的技能：React, Python, FastAPI, Node.js, TypeScript
        
        请评估：
        1. 是否值得申请？
        2. 风险点？
        3. 建议出价？
        
        返回JSON格式：
        {{
            "score": 0-100,
            "reason": "简要理由",
            "recommended_budget": 建议出价,
            "risks": ["风险1", "风险2"],
            "recommendations": ["建议1", "建议2"]
        }}
        """
    
    def _build_proposal_prompt(self, opportunity_data: Dict[str, Any]) -> str:
        """构建申请信提示词"""
        return f"""
        根据以下机会信息生成一份专业的申请信：
        
        标题：{opportunity_data.get('title', '')}
        预算：${opportunity_data.get('budget', 'N/A')}
        技术栈：{', '.join(opportunity_data.get('tech_stack', []))}
        描述：{opportunity_data.get('description', '')}
        
        申请信应该：
        1. 简洁专业（150-300字）
        2. 突出相关经验
        3. 展示理解需求
        4. 提出合理报价
        5. 表达专业态度
        """
    
    def _default_analysis(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """默认分析结果"""
        budget = opportunity_data.get('budget', 0)
        proposal_count = opportunity_data.get('proposal_count', 0)
        
        # 简单的评分逻辑
        score = 50
        if budget and budget > 1000:
            score += 15
        if proposal_count and proposal_count < 10:
            score += 15
        
        return {
            "score": min(score, 100),
            "reason": "基础分析",
            "recommended_budget": budget,
            "risks": [],
            "recommendations": []
        }
    
    def _default_proposal(self, opportunity_data: Dict[str, Any]) -> str:
        """默认申请信"""
        return f"""
        Hi,
        
        I'm interested in your project: {opportunity_data.get('title', 'Your Project')}
        
        I have extensive experience with {', '.join(opportunity_data.get('tech_stack', ['web development']))}
        and I'm confident I can deliver high-quality results.
        
        I'm available to start immediately and committed to meeting your deadlines.
        
        Let's discuss the details.
        
        Best regards
        """


class ClaudeService(LLMService):
    """Claude服务"""
    
    def __init__(self):
        super().__init__()
        try:
            from anthropic import AsyncAnthropic
            self.client = AsyncAnthropic(api_key=self.claude_key)
        except ImportError:
            logger.warning("Anthropic库未安装")
            self.client = None
    
    async def analyze_opportunity(self, opportunity_data: Dict[str, Any]) -> Dict[str, Any]:
        """分析机会"""
        if not self.client:
            return OpenAIService()._default_analysis(opportunity_data)
        
        prompt = self._build_analysis_prompt(opportunity_data)
        
        try:
            response = await self.client.messages.create(
                model=settings.CLAUDE_MODEL,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            result_text = response.content[0].text
            # 尝试解析JSON
            try:
                result = json.loads(result_text)
            except:
                result = {"score": 60, "reason": result_text}
            
            return {
                "score": result.get("score", 60),
                "reason": result.get("reason", ""),
                "recommended_budget": result.get("recommended_budget"),
                "risks": result.get("risks", []),
                "recommendations": result.get("recommendations", []),
                "analysis": result
            }
        except Exception as e:
            logger.error(f"Claude分析失败: {e}")
            return OpenAIService()._default_analysis(opportunity_data)
    
    def _build_analysis_prompt(self, opportunity_data: Dict[str, Any]) -> str:
        """构建分析提示词"""
        return f"""
        分析以下外包机会，给出0-100分的评分：
        
        标题：{opportunity_data.get('title', '')}
        预算：${opportunity_data.get('budget', 'N/A')}
        技术栈：{', '.join(opportunity_data.get('tech_stack', []))}
        客户评价：{opportunity_data.get('client_rating', 'N/A')}/5
        当前申请数：{opportunity_data.get('proposal_count', 'N/A')}
        
        我的技能：React, Python, FastAPI, Node.js
        
        请评估这个机会的价值。
        """


def get_llm_service(provider: str = "openai") -> LLMService:
    """获取LLM服务"""
    if provider == "claude":
        return ClaudeService()
    else:
        return OpenAIService()
