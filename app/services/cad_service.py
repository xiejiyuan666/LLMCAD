from __future__ import annotations

import logging
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters

from app.core.domain import CADCode, CADModel, ExportResult

logger = logging.getLogger("llm_cad")


class CadQueryExecutor:
    """CadQuery代码执行器"""

    def execute(self, code: CADCode) -> CADModel:
        """执行CAD代码生成模型"""
        namespace = {
            "cadquery": cq,
            "cq": cq,
            "math": math,
            "pi": math.pi,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "radians": math.radians,
            "degrees": math.degrees,
            "sqrt": math.sqrt,
        }

        try:
            exec(code.code, namespace)
        except Exception as e:
            logger.error(f"Code execution failed: {e}")
            raise ValueError(f"代码执行失败: {e}") from e

        if "result" not in namespace:
            raise ValueError("代码必须定义 'result' 变量")

        workplane = namespace["result"]
        try:
            volume = workplane.val().Volume()
        except Exception as e:
            logger.error(f"Failed to calculate volume: {e}")
            volume = 0.0

        return CADModel(workplane=workplane, volume=volume)


class CadModelExporter:
    """CAD模型导出器"""

    def export(self, model: CADModel, base_path: str) -> ExportResult:
        """导出模型为STL和STEP格式"""
        Path(base_path).mkdir(parents=True, exist_ok=True)

        stl_path = f"{base_path}/model.stl"
        step_path = f"{base_path}/model.step"

        if model.workplane is None:
            logger.warning("No workplane to export")
            return ExportResult()

        try:
            exporters.export(model.workplane.val(), stl_path)
            exporters.export(model.workplane.val(), step_path)
            logger.info(f"Exported to {stl_path} and {step_path}")
        except Exception as e:
            logger.error(f"Export failed: {e}")
            raise

        return ExportResult(stl_path=stl_path, step_path=step_path)
