from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite+pysqlite:///:memory:"
    sec_user_agent: str = "edgar-ownership-etl/test"
    sec_requests_per_second: int = 5
    sec_force_high_rate_limit: bool = False
    watchlist_tickers: str = ""
    watchlist_ciks: str = ""
    raw_document_storage: str = "database"
    scheduler_timezone: str = "America/New_York"
    log_level: str = "INFO"

    def validate_rate(self) -> None:
        if self.sec_requests_per_second > 10 and not self.sec_force_high_rate_limit:
            raise ValueError("SEC_REQUESTS_PER_SECOND above 10 requires SEC_FORCE_HIGH_RATE_LIMIT=true")


settings = Settings()
settings.validate_rate()
