from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/israel_municipal"
    app_name: str = "Israeli Municipal Analytics"
    debug: bool = False

    model_config = {"env_file": ".env"}


settings = Settings()
