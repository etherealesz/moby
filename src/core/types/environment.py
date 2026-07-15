from typing import Literal

RuntimeEnvironment = Literal["fastapi-dev", "fastapi-run", "uvicorn", "unknown"]
ApplicationEnvironment = Literal["local", "development", "staging", "production"]
