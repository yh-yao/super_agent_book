
from pydantic import BaseModel
import os

class Settings(BaseModel):
    app_name: str = "Manus+ Demo"
    use_mock_models: bool = True if os.getenv("USE_MOCK","1")=="1" else False

settings = Settings()
