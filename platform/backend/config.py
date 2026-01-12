"""
配置管理模块
"""
import os
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本配置
    APP_NAME: str = "AI Digital Labor Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    
    # 数据库配置
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./ai_labor.db"
    )
    
    # Redis配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # CORS配置
    ALLOWED_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:8501",
        "http://localhost:8000",
    ]
    
    # LLM配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    
    CLAUDE_API_KEY: Optional[str] = os.getenv("CLAUDE_API_KEY")
    CLAUDE_MODEL: str = "claude-3-opus-20240229"
    CLAUDE_TEMPERATURE: float = 0.7
    
    # Upwork配置
    UPWORK_API_KEY: Optional[str] = os.getenv("UPWORK_API_KEY")
    UPWORK_API_SECRET: Optional[str] = os.getenv("UPWORK_API_SECRET")
    UPWORK_OAUTH_TOKEN: Optional[str] = os.getenv("UPWORK_OAUTH_TOKEN")
    
    # LinkedIn配置
    LINKEDIN_API_KEY: Optional[str] = os.getenv("LINKEDIN_API_KEY")
    LINKEDIN_EMAIL: Optional[str] = os.getenv("LINKEDIN_EMAIL")
    LINKEDIN_PASSWORD: Optional[str] = os.getenv("LINKEDIN_PASSWORD")
    
    # 邮件配置
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    SMTP_FROM: Optional[str] = os.getenv("SMTP_FROM")
    
    # Telegram配置
    TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID: Optional[str] = os.getenv("TELEGRAM_CHAT_ID")
    
    # 抓取配置
    SCRAPING_INTERVAL: int = 3600  # 1小时
    SCRAPING_TIMEOUT: int = 30  # 30秒
    SCRAPING_RETRIES: int = 3
    SCRAPING_PROXY_ROTATION: bool = True
    
    # 分析配置
    ANALYSIS_BATCH_SIZE: int = 10
    ANALYSIS_CACHE_TTL: int = 86400  # 24小时
    
    # 知识库配置
    KNOWLEDGE_BASE_PATH: str = os.getenv(
        "KNOWLEDGE_BASE_PATH",
        "./knowledge_base"
    )
    CHROMA_DB_PATH: str = os.getenv(
        "CHROMA_DB_PATH",
        "./chroma_db"
    )
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    
    # 日志配置
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "./logs/app.log")
    
    # 任务队列配置
    CELERY_BROKER_URL: str = os.getenv(
        "CELERY_BROKER_URL",
        "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND: str = os.getenv(
        "CELERY_RESULT_BACKEND",
        "redis://localhost:6379/1"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """获取配置实例（单例）"""
    return Settings()


# 全局配置实例
settings = get_settings()
