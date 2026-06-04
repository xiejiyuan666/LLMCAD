from __future__ import annotations

from typing import Protocol

from app.core.domain import CADRequest, CADCode, CADModel, RenderedImage, ExportResult


class CodeGenerator(Protocol):
    """代码生成器端口"""

    def generate(self, request: CADRequest) -> CADCode:
        """根据自然语言描述生成CAD代码"""
        ...


class CADExecutor(Protocol):
    """CAD执行器端口"""

    def execute(self, code: CADCode) -> CADModel:
        """执行代码生成3D模型"""
        ...


class ModelRenderer(Protocol):
    """模型渲染器端口"""

    def render(self, model: CADModel, width: int = 800, height: int = 600) -> RenderedImage:
        """渲染3D模型为图片"""
        ...


class ModelExporter(Protocol):
    """模型导出器端口"""

    def export(self, model: CADModel, base_path: str) -> ExportResult:
        """导出模型为STL/STEP格式"""
        ...
