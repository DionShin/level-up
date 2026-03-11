from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./level_up.db"
    CORS_ORIGINS: str = "http://localhost:3000"
    DEFAULT_USER_ID: str = "user_001"

    # VAPID 키 (pywebpush 푸시 알림용)
    # 생성: python -c "from py_vapid import Vapid; v=Vapid(); v.generate_keys(); print(v.public_key, v.private_key)"
    VAPID_PUBLIC_KEY: str = "YOUR_VAPID_PUBLIC_KEY"
    VAPID_PRIVATE_KEY: str = "YOUR_VAPID_PRIVATE_KEY"
    VAPID_EMAIL: str = "mailto:admin@levelup.app"

    # NewsAPI (https://newsapi.org — 무료 플랜으로 하루 100건)
    NEWS_API_KEY: str = "YOUR_NEWS_API_KEY"

    @property
    def news_api_key(self) -> str:
        return self.NEWS_API_KEY

    @property
    def vapid_public_key(self) -> str:
        return self.VAPID_PUBLIC_KEY

    @property
    def vapid_private_key(self) -> str:
        return self.VAPID_PRIVATE_KEY

    @property
    def vapid_email(self) -> str:
        return self.VAPID_EMAIL

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]


settings = Settings()
