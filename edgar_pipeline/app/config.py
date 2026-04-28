from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    database_url: str
    sec_user_agent: str
    sec_contact_email: str
    qlik_tenant_url: str
    qlik_api_key: str
    qlik_app_id: str
    run_mode: str = "hourly"
    log_level: str = "INFO"
    sec_rate_limit_per_second: float = 5.0

    @property
    def full_user_agent(self) -> str:
        return f"{self.sec_user_agent} ({self.sec_contact_email})"


def load_settings() -> Settings:
    return Settings(
        database_url=os.environ["DATABASE_URL"],
        sec_user_agent=os.environ["SEC_USER_AGENT"],
        sec_contact_email=os.environ["SEC_CONTACT_EMAIL"],
        qlik_tenant_url=os.environ.get("QLIK_TENANT_URL", ""),
        qlik_api_key=os.environ.get("QLIK_API_KEY", ""),
        qlik_app_id=os.environ.get("QLIK_APP_ID", ""),
        run_mode=os.environ.get("RUN_MODE", "hourly"),
        log_level=os.environ.get("LOG_LEVEL", "INFO"),
    )
