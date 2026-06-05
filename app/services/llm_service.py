from __future__ import annotations

import json
import logging
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.domain import CADRequest, CADCode

logger = logging.getLogger("llm_cad")


class LLMCodeGenerator:
    """基于OpenAI的代码生成器"""

    SYSTEM_PROMPT = """你是专业的CAD建模工程师，使用CadQuery库创建参数化3D模型。

根据用户自然语言描述，生成完整可执行的Python代码。

规则：
1. 使用CadQuery库 (import cadquery as cq)
2. 最终模型变量必须命名为 `result`
3. 代码完整，包含import语句
4. 使用合理的默认参数值（单位：毫米）
5. 使用标准数学函数 math.sin, math.cos, math.radians
6. 合并多个实体时使用 .union() 方法，不要使用 .add()

示例 - 带腿的圆桌：
```python
import cadquery as cq
import math

# 参数
table_diameter = 80
table_thickness = 5
leg_height = 70
leg_diameter = 6
leg_offset = 25

# 桌面
result = cq.Workplane("XY").circle(table_diameter/2).extrude(table_thickness)

# 四条桌腿
for angle in [0, 90, 180, 270]:
    rad = math.radians(angle)
    x = leg_offset * math.cos(rad)
    y = leg_offset * math.sin(rad)
    leg = cq.Workplane("XY", origin=(x, y, -leg_height)).circle(leg_diameter/2).extrude(leg_height)
    result = result.union(leg)
```

输出必须是有效的Python代码，直接返回代码，不要解释。"""

    def __init__(self) -> None:
        self._client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url) if settings.has_api_key else None

    def generate(self, request: CADRequest) -> CADCode:
        """生成CAD代码"""
        if not self._client:
            logger.info("Using mock generator (no API key)")
            return CADCode(code=self._mock_code())

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": request.description}
        ]

        try:
            logger.info(f"Sending request to {settings.openai_model}")
            response = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                temperature=0.2
            )

            content = response.choices[0].message.content
            code = self._extract_code(content)
            logger.info(f"Generated code length: {len(code)} chars")
            return CADCode(code=code)

        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            raise

    def _extract_code(self, content: str) -> str:
        """从LLM响应中提取代码块"""
        if content.startswith("```python"):
            return content.replace("```python", "").replace("```", "").strip()
        elif content.startswith("```"):
            return content.replace("```", "").strip()
        return content.strip()

    def _mock_code(self) -> str:
        """Mock代码（无API密钥时使用）"""
        return '''import cadquery as cq
import math

# 参数
table_diameter = 80
table_thickness = 5
leg_height = 70
leg_diameter = 6
leg_offset = 25

# 桌面
result = cq.Workplane("XY").circle(table_diameter/2).extrude(table_thickness)

# 四条桌腿
for angle in [0, 90, 180, 270]:
    rad = math.radians(angle)
    x = leg_offset * math.cos(rad)
    y = leg_offset * math.sin(rad)
    leg = cq.Workplane("XY", origin=(x, y, -leg_height)).circle(leg_diameter/2).extrude(leg_height)
    result = result.union(leg)
'''


class MockCodeGenerator:
    """Mock代码生成器（用于测试）"""

    def generate(self, request: CADRequest) -> CADCode:
        """返回固定的示例代码"""
        code = '''import cadquery as cq
import math

# 参数
table_diameter = 80
table_thickness = 5
leg_height = 70
leg_diameter = 6
leg_offset = 25

# 桌面
result = cq.Workplane("XY").circle(table_diameter/2).extrude(table_thickness)

# 四条桌腿
for angle in [0, 90, 180, 270]:
    rad = math.radians(angle)
    x = leg_offset * math.cos(rad)
    y = leg_offset * math.sin(rad)
    leg = cq.Workplane("XY", origin=(x, y, -leg_height)).circle(leg_diameter/2).extrude(leg_height)
    result = result.union(leg)
'''
        return CADCode(code=code)
