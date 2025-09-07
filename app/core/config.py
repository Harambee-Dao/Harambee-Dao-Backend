from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_ENV: str = Field(default="dev")
    LOG_LEVEL: str = Field(default="INFO")

    # Blockchain & Oracle Settings
    IPFS_API_URL: str = Field(default="http://localhost:5001")
    ORACLE_SIGNER: str = Field(default="0x0000000000000000000000000000000000000000")
    CELESTIA_ENDPOINT: str = Field(default="http://localhost:26658")

    # AI Settings
    GROQ_API_KEY: str | None = Field(default=None)
    GROQ_API_URL: str = Field(default="https://api.groq.com/openai/v1/chat/completions")

    # Twilio SMS Settings
    TWILIO_ACCOUNT_SID: str | None = Field(default=None)
    TWILIO_AUTH_TOKEN: str | None = Field(default=None)
    TWILIO_PHONE_NUMBER: str | None = Field(default=None)

    # Database Settings (for future use)
    DATABASE_URL: str = Field(default="sqlite:///./harambee_dao.db")

    # Security Settings
    SECRET_KEY: str = Field(default="dev-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = Field(default=60)
    OTP_RATE_LIMIT_PER_HOUR: int = Field(default=5)

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache

def get_settings() -> Settings:
    return Settings()


settings = get_settings()
