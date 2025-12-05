import os
import json
from pydantic import BaseModel, AnyHttpUrl
from typing import List



class Settings(BaseModel):
    # Database
    INSTANCE_CONNECTION_NAME: str
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    # JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # default 24 hours

    # App config
    BACKEND_ORIGINS: List[AnyHttpUrl] | list[str] = ["*"]
    RATE_LIMIT_PER_MINUTE: int = 30

    EMAIL_HOST:str
    EMAIL_PORT:str
    EMAIL_USER:str
    EMAIL_PASS:str
    EMAIL_FROM:str
    FRONTEND_VERIFY_URL:str

    BASIC_AUTH_USER:str
    BASIC_AUTH_PASSWORD:str
    BASIC_AUTH_HASH_PASSWORD:str

    REST_COUNTRIES_API_URL: str
    REST_COUNTRIES_STATES_API_URL: str

def load_properties(filepath: str) -> Settings:
    """Load key=value pairs from server.properties."""
    props = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Missing configuration file: {filepath}")

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                props[key.strip()] = value.strip()

    # Split comma-separated BACKEND_ORIGINS
    if "BACKEND_ORIGINS" in props:
        try:
            props["BACKEND_ORIGINS"] = json.loads(props["BACKEND_ORIGINS"])
        except json.JSONDecodeError:
            # fallback: comma-separated
            props["BACKEND_ORIGINS"] = [url.strip() for url in props["BACKEND_ORIGINS"].split(",")]

    return Settings(**props)

def get_config_filepath() -> str:
    """Get the configuration file path based on the environment."""
    env = os.getenv("ENV", "dev")  # Default to "dev" if ENV is not set
    if env == "dev":
        return "server.dev.properties"
    elif env == "uat":
        return "server.uat.properties"
    elif env == "prod":
        return "server.prod.properties"
    elif env == "local":
        return "server.local.properties"
    else:
        raise ValueError(f"Unsupported environment: {env}")

# Load the configuration
settings = load_properties(get_config_filepath())
