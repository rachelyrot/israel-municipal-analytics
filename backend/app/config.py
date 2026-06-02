from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/israel_municipal"
    app_name: str = "Israeli Municipal Analytics"
    debug: bool = False
    anthropic_api_key: str = ""
    allowed_origins: str = "http://localhost:5173,http://localhost:3000"
    disable_ssl_verify: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
