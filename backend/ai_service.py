import json
import re
import time
import random
import logging
import requests
from typing import Optional, Dict, List
from config import settings

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService:
    """AI服务类 - 使用自定义 requests 方式调用"""
    
    def __init__(self):
        # 从配置中读取参数
        self.api_key = settings.ai_service_api_key or settings.openai_api_key
        self.base_url = settings.ai_service_url or "https://api.openai.com/v1"
        self.model = settings.ai_service_model or "gpt-4"
        
        # 预清理 URL
        if self.base_url:
            self.base_url = self.base_url.rstrip('/')
            
        print(f"DEBUG: URL={self.base_url}, Key={self.api_key[:10] if self.api_key else 'None'}..., Model={self.model}")

    def chat_with_openai(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 2500
    ) -> Optional[str]:
        """
        底层请求逻辑：Chat with OpenAI-compatible API
        """
        if not self.api_key:
            logger.error("API Key is missing.")
            return None

        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                # 额外添加 User-Agent 避免被 WAF 拦截
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            api_endpoint = f"{self.base_url}/chat/completions"
            logger.info(f"Calling API: {api_endpoint} (model: {self.model})")
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = requests.post(
                        api_endpoint,
                        headers=headers,
                        json=payload,
                        timeout=60,
                        verify=False  # 对应你需求中的禁用 SSL 验证
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result['choices'][0]['message']['content'].strip()
                    
                    elif response.status_code == 429:
                        wait_time = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Rate limited, retrying in {wait_time:.1f}s...")
                        time.sleep(wait_time)
                        continue
                    
                    else:
                        error_detail = response.text
                        logger.error(f"API Error {response.status_code}: {error_detail}")
                        return f"Error: {response.status_code} - {error_detail}"

                except requests.RequestException as req_err:
                    if attempt < max_retries - 1:
                        time.sleep((2 ** attempt) + 1)
                        continue
                    logger.error(f"Request failed: {req_err}")
                    return f"Request Error: {str(req_err)}"
            
            return None

        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    def generate_analysis(self, prompt: str) -> str:
        """生成AI分析文本（业务逻辑层）"""
        if not self.api_key:
            return "AI分析功能需要配置API Key。"

        messages = [
            {"role": "system", "content": "你是一名专业的长期价值投资分析师，专注于客观分析和风险评估，从不给出买卖建议或目标价。"},
            {"role": "user", "content": prompt}
        ]
        
        # 调用上面替换的请求方法
        result = self.chat_with_openai(
            messages=messages,
            temperature=0.7,
            max_tokens=500  # 根据业务调整
        )
        
        if result:
            return result
        return "AI分析生成失败，请检查后端日志。"

    def parse_comprehensive_analysis(self, text: str) -> Dict[str, Optional[str]]:
        """解析综合AI分析的输出（保持原样）"""
        result = {"analysis_text": None, "main_label": None, "risk_label": None}
        
        analysis_match = re.search(r'分析[：:]\s*(.+?)(?=主标签|$)', text, re.DOTALL)
        if analysis_match:
            result["analysis_text"] = analysis_match.group(1).strip()
        
        main_label_match = re.search(r'主标签[：:]\s*(.+?)(?=风险标签|$)', text, re.DOTALL)
        if main_label_match:
            result["main_label"] = main_label_match.group(1).strip()
        
        risk_label_match = re.search(r'风险标签[：:]\s*(.+?)$', text, re.DOTALL)
        if risk_label_match:
            result["risk_label"] = risk_label_match.group(1).strip()
        
        if not result["analysis_text"]:
            result["analysis_text"] = text.strip()
        
        return result