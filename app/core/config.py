from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# 加载环境变量
load_dotenv(Path(".env"))


@dataclass(frozen=True)
class Settings:
    """应用配置"""
    openai_api_key: str = ""
    openai_model: str = "deepseek-chat"
    openai_base_url: str = "https://api.deepseek.com"
    render_width: int = 800
    render_height: int = 600
    output_dir: str = "./output"

    @classmethod
    def from_env(cls, env: dict | None = None) -> "Settings":
        """从环境变量创建配置"""
        if env is None:
            env = os.environ
        return cls(
            openai_api_key=env.get("OPENAI_API_KEY", ""),
            openai_model=env.get("OPENAI_MODEL", "deepseek-chat"),
            openai_base_url=env.get("OPENAI_BASE_URL", "https://api.deepseek.com"),
            render_width=int(env.get("RENDER_WIDTH", "800")),
            render_height=int(env.get("RENDER_HEIGHT", "600")),
            output_dir=env.get("OUTPUT_DIR", "./output"),
        )

    @property
    def has_api_key(self) -> bool:
        """检查是否配置了API密钥"""
        key = self.openai_api_key.strip()
        return bool(key and key != "your_api_key_here")


# 全局配置实例
settings = Settings.from_env()
