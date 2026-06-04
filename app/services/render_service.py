from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

import numpy as np
import trimesh
from cadquery import exporters

from app.core.domain import CADModel, RenderedImage

logger = logging.getLogger("llm_cad")


class TrimeshRenderer:
    """基于Trimesh的3D渲染器"""

    def render(self, model: CADModel, width: int = 800, height: int = 600) -> RenderedImage:
        """渲染CAD模型为图片"""
        if model.workplane is None:
            raise ValueError("模型为空")

        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 导出为STL临时文件
            exporters.export(model.workplane.val(), tmp_path)

            # 使用trimesh加载和渲染
            mesh = trimesh.load_mesh(tmp_path)
            scene = trimesh.Scene(mesh)

            # 设置相机
            scale = mesh.scale if mesh.scale > 0 else 100
            scene.set_camera(
                angles=(np.pi / 6, np.pi / 4, 0),
                distance=scale * 4
            )

            # 渲染图片
            png_bytes = scene.save_image(resolution=(width, height))

            # 保存到输出目录
            Path("output").mkdir(exist_ok=True)
            image_path = f"output/render_{id(model):08x}.png"
            Path(image_path).write_bytes(png_bytes)

            logger.info(f"Rendered image saved to {image_path}")
            return RenderedImage(image_path=image_path)

        except Exception as e:
            logger.error(f"Rendering failed: {e}")
            raise

        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
