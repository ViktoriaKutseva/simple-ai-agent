from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"
    
    openrouter_api_key: str = Field(default="")
    
    
settings = Settings()