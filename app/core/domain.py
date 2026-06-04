from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Optional


class CADRequest(BaseModel):
    """CAD生成请求"""
    description: str = Field(..., description="用户自然语言描述")


class CADCode(BaseModel):
    """生成的CAD代码"""
    code: str = Field(..., description="Python/CadQuery代码")


class CADModel(BaseModel):
    """CAD模型结果"""
    workplane: Optional[Any] = Field(None, description="CadQuery Workplane对象", exclude=True)
    volume: float = Field(0.0, description="体积 (mm³)")


class RenderedImage(BaseModel):
    """渲染结果"""
    image_path: str = Field(..., description="图片文件路径")


class ExportResult(BaseModel):
    """导出结果"""
    stl_path: Optional[str] = Field(None, description="STL文件路径")
    step_path: Optional[str] = Field(None, description="STEP文件路径")


class CADResult(BaseModel):
    """完整CAD生成结果"""
    success: bool = Field(True, description="是否成功")
    code: str = Field("", description="生成的代码")
    image_path: Optional[str] = Field(None, description="渲染图路径")
    stl_path: Optional[str] = Field(None, description="STL路径")
    volume: float = Field(0.0, description="体积")
    error: Optional[str] = Field(None, description="错误信息")
