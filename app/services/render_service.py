from __future__ import annotations

import io
import logging
import os
import tempfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from cadquery import exporters
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

from app.core.domain import CADModel, RenderedImage

logger = logging.getLogger("llm_cad")


class TrimeshRenderer:
    """基于matplotlib的3D渲染器（软件渲染，无需OpenGL）"""

    def render(self, model: CADModel, width: int = 800, height: int = 600) -> RenderedImage:
        """渲染CAD模型为图片"""
        if model.workplane is None:
            raise ValueError("模型为空")

        with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 导出为STL临时文件
            exporters.export(model.workplane.val(), tmp_path)

            # 使用trimesh加载
            mesh = trimesh.load_mesh(tmp_path)

            # 使用matplotlib渲染
            fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
            ax = fig.add_subplot(111, projection="3d")
            ax.set_facecolor("white")
            fig.patch.set_facecolor("white")

            # 绘制mesh面
            vertices = mesh.vertices
            faces = mesh.faces
            poly = Poly3DCollection(vertices[faces], alpha=0.9, linewidths=0.1)
            poly.set_facecolor((0.3, 0.5, 0.9))
            poly.set_edgecolor((0.2, 0.2, 0.2))
            ax.add_collection3d(poly)

            # 自动设置坐标轴范围
            bounds = mesh.bounds
            center = bounds.mean(axis=0)
            extent = np.ptp(bounds, axis=0).max() / 2
            ax.set_xlim(center[0] - extent, center[0] + extent)
            ax.set_ylim(center[1] - extent, center[1] + extent)
            ax.set_zlim(center[2] - extent, center[2] + extent)

            ax.set_box_aspect((1, 1, 1))
            ax.view_init(elev=25, azim=-60)
            ax.axis("off")

            # 保存到内存
            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight", pad_inches=0, dpi=100)
            plt.close(fig)
            png_bytes = buf.getvalue()

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
