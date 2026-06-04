from __future__ import annotations

import sys
from pathlib import Path

# 保证以 streamlit run app/main.py 运行时，项目根目录在路径中
_LLMCAD_ROOT = Path(__file__).resolve().parent.parent
if str(_LLMCAD_ROOT) not in sys.path:
    sys.path.insert(0, str(_LLMCAD_ROOT))

import logging
import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from PIL import Image

from app.core.config import Settings
from app.core.domain import CADRequest, CADResult
from app.services.llm_service import LLMCodeGenerator, MockCodeGenerator
from app.services.cad_service import CadQueryExecutor, CadModelExporter
from app.services.render_service import TrimeshRenderer

logger = logging.getLogger("llm_cad.ui")


def _load_settings() -> Settings:
    """加载配置"""
    load_dotenv(Path(".env"))
    return Settings.from_env(os.environ)


@st.cache_resource
def get_services(settings: Settings):
    """
    Composition root: 组装服务实例
    Cached to reuse across Streamlit reruns
    """
    # 默认使用Mock
    generator = MockCodeGenerator()

    if settings.has_api_key:
        generator = LLMCodeGenerator()
    else:
        st.sidebar.warning("⚠️ API Key not found, using Mock Generator")

    return {
        "generator": generator,
        "executor": CadQueryExecutor(),
        "exporter": CadModelExporter(),
        "renderer": TrimeshRenderer(),
    }


def init_session_state():
    """初始化会话状态"""
    if "result" not in st.session_state:
        st.session_state.result = None
    if "history" not in st.session_state:
        st.session_state.history = []


def main():
    """主函数"""
    settings = _load_settings()
    services = get_services(settings)

    st.set_page_config(
        page_title="LLM CAD建模",
        page_icon="🎨",
        layout="wide"
    )

    init_session_state()

    # 页面标题
    st.title("🎨 LLM CAD建模系统")
    st.markdown("输入自然语言描述，AI自动生成3D模型")

    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 配置")
        st.info(f"模型: `{settings.openai_model}`")
        st.info(f"输出目录: `{settings.output_dir}`")

        if st.button("🗑️ 清除历史", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.divider()
        st.caption("💡 提示：输入越详细，生成的模型越准确")

    # 主界面 - 两列布局
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📝 输入描述")
        description = st.text_area(
            "描述你想要的3D模型：",
            placeholder="例如：\n生成一个带四个腿的圆桌\n创建一个长宽高为50,30,20的盒子，上面挖一个圆孔",
            height=150
        )

        generate_btn = st.button(
            "🚀 生成模型",
            type="primary",
            use_container_width=True,
            disabled=not description.strip()
        )

        if generate_btn:
            with st.spinner("正在生成..."):
                result = _generate_model(description, services, settings)
                st.session_state.result = result

                if result.success:
                    st.session_state.history.append({
                        "time": datetime.now().strftime("%H:%M:%S"),
                        "desc": description,
                        "volume": result.volume
                    })
                    st.success("✅ 生成成功！")
                else:
                    st.error(f"❌ 错误: {result.error}")

        # 显示生成的代码
        if st.session_state.result and st.session_state.result.code:
            st.subheader("📄 生成的代码")
            with st.expander("查看代码", expanded=True):
                st.code(st.session_state.result.code, language="python")

    with col2:
        st.subheader("🎨 渲染结果")

        result = st.session_state.result

        if result and result.success:
            if result.image_path and Path(result.image_path).exists():
                st.image(result.image_path, use_container_width=True)

            # 显示体积信息
            col_vol, col_stl = st.columns(2)
            with col_vol:
                st.metric("模型体积", f"{result.volume:,.2f} mm³")

            # 下载按钮
            if result.stl_path and Path(result.stl_path).exists():
                with col_stl:
                    with open(result.stl_path, "rb") as f:
                        st.download_button(
                            label="⬇️ STL",
                            data=f,
                            file_name="model.stl",
                            mime="application/octet-stream",
                            use_container_width=True
                        )
        else:
            st.info("👈 在左侧输入描述并点击生成")

        # 显示历史
        if st.session_state.history:
            st.divider()
            st.subheader("📚 历史记录")
            for item in reversed(st.session_state.history[-5:]):
                st.caption(f"{item['time']} | 体积: {item['volume']:,.0f} mm³")
                st.text(item['desc'][:50] + "..." if len(item['desc']) > 50 else item['desc'])


def _generate_model(
    description: str,
    services: dict,
    settings: Settings
) -> CADResult:
    """生成模型的完整流程"""
    try:
        # 1. 生成代码
        request = CADRequest(description=description)
        code_result = services["generator"].generate(request)

        # 2. 执行代码
        model = services["executor"].execute(code_result)

        # 3. 导出模型
        export_path = f"{settings.output_dir}/{hash(description) & 0xFFFFFFFF:08x}"
        export_result = services["exporter"].export(model, export_path)

        # 4. 渲染
        render_result = services["renderer"].render(
            model, settings.render_width, settings.render_height
        )

        return CADResult(
            success=True,
            code=code_result.code,
            image_path=render_result.image_path,
            stl_path=export_result.stl_path,
            volume=model.volume
        )

    except Exception as e:
        logger.exception("Model generation failed")
        return CADResult(
            success=False,
            error=str(e)
        )


if __name__ == "__main__":
    main()
