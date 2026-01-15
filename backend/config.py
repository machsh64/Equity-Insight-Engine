"""配置文件"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    database_url: str
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    grok_api_key: Optional[str] = None
    
    # AI服务配置
    ai_service_url: Optional[str] = None  # 自定义AI服务URL，如: https://api.openai.com/v1
    ai_service_model: Optional[str] = "gpt-4"  # AI模型名称，如: gpt-4, gpt-3.5-turbo等
    ai_service_api_key: Optional[str] = None  # AI服务API Key（如果与openai_api_key不同）
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False
    )


settings = Settings()

