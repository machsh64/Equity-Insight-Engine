"""AI服务 - 调用外部LLM API"""
import json
import re
from typing import Optional, Dict
from openai import OpenAI
from config import settings


class AIService:
    """AI服务类"""
    
    def __init__(self):
        self.client = None
        self.model = settings.ai_service_model or "gpt-4"
        
        # 优先使用自定义AI服务配置
        api_key = settings.ai_service_api_key or settings.openai_api_key
        base_url = settings.ai_service_url
        if base_url:
            base_url = base_url.rstrip('/')
        
        
        if api_key:
            # 如果提供了自定义URL，使用自定义配置
            if base_url:
                self.client = OpenAI(
                    api_key=api_key,
                    base_url=base_url
                )
            else:
                # 否则使用默认OpenAI配置
                self.client = OpenAI(api_key=api_key)

        print(f"DEBUG: URL={self.client.base_url}, Key={self.client.api_key[:10]}..., Model={self.model}")
        
    
    def generate_analysis(self, prompt: str) -> str:
        """
        生成AI分析文本
        
        Args:
            prompt: 输入的prompt文本
            
        Returns:
            AI生成的分析文本
        """
        if not self.client:
            # 如果没有配置API key，返回占位文本
            return "AI分析功能需要配置API Key。请在.env文件中设置AI_SERVICE_API_KEY或OPENAI_API_KEY。"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一名专业的长期价值投资分析师，专注于客观分析和风险评估，从不给出买卖建议或目标价。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"API Error Detail: {type(e)} - {e}") 
            return f"AI分析生成失败: {str(e)}"
    
    def parse_comprehensive_analysis(self, text: str) -> Dict[str, Optional[str]]:
        """
        解析综合AI分析的输出
        
        Args:
            text: AI返回的文本
            
        Returns:
            包含analysis_text, main_label, risk_label的字典
        """
        result = {
            "analysis_text": None,
            "main_label": None,
            "risk_label": None
        }
        
        # 尝试解析格式化的输出
        analysis_match = re.search(r'分析[：:]\s*(.+?)(?=主标签|$)', text, re.DOTALL)
        if analysis_match:
            result["analysis_text"] = analysis_match.group(1).strip()
        
        main_label_match = re.search(r'主标签[：:]\s*(.+?)(?=风险标签|$)', text, re.DOTALL)
        if main_label_match:
            result["main_label"] = main_label_match.group(1).strip()
        
        risk_label_match = re.search(r'风险标签[：:]\s*(.+?)$', text, re.DOTALL)
        if risk_label_match:
            result["risk_label"] = risk_label_match.group(1).strip()
        
        # 如果解析失败，将整个文本作为analysis_text
        if not result["analysis_text"]:
            result["analysis_text"] = text.strip()
        
        return result

