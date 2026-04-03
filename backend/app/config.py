from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "INFRAGRAPH_", "env_file": ".env"}

    database_url: str = "postgresql+asyncpg://infragraph:infragraph@localhost:5432/infragraph"
    debug: bool = False
    api_prefix: str = "/api"
    blast_radius_max_depth: int = 5


settings = Settings()
