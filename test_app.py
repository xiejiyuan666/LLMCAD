"""测试脚本 - 验证项目可运行"""
from __future__ import annotations

import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import Settings
from app.core.domain import CADRequest
from app.services.llm_service import MockCodeGenerator
from app.services.cad_service import CadQueryExecutor, CadModelExporter
from app.services.render_service import TrimeshRenderer


def test_config():
    """测试配置加载"""
    print("=" * 50)
    print("测试1: 配置加载")
    settings = Settings.from_env()
    print(f"  [OK] OpenAI模型: {settings.openai_model}")
    print(f"  [OK] API密钥已配置: {settings.has_api_key}")
    print(f"  [OK] 渲染尺寸: {settings.render_width}x{settings.render_height}")


def test_mock_generation():
    """测试Mock代码生成"""
    print("\n" + "=" * 50)
    print("测试2: Mock代码生成")

    generator = MockCodeGenerator()
    request = CADRequest(description="一个带腿的圆桌")
    code = generator.generate(request)

    print(f"  [OK] 生成代码长度: {len(code.code)} 字符")
    assert "import cadquery as cq" in code.code
    print("  [OK] 代码包含必要的import")
    assert "result =" in code.code
    print("  [OK] 代码定义了result变量")


def test_cad_execution():
    """测试CAD代码执行"""
    print("\n" + "=" * 50)
    print("测试3: CAD代码执行")

    generator = MockCodeGenerator()
    executor = CadQueryExecutor()

    request = CADRequest(description="测试")
    code = generator.generate(request)

    model = executor.execute(code)
    print(f"  [OK] 模型执行成功")
    print(f"  [OK] 模型体积: {model.volume:.2f} mm3")
    assert model.volume > 0
    print("  [OK] 体积大于0")


def test_rendering():
    """测试渲染功能"""
    print("\n" + "=" * 50)
    print("测试4: 渲染功能")

    generator = MockCodeGenerator()
    executor = CadQueryExecutor()
    renderer = TrimeshRenderer()

    request = CADRequest(description="测试")
    code = generator.generate(request)
    model = executor.execute(code)

    result = renderer.render(model, width=400, height=300)
    print(f"  [OK] 渲染成功")
    print(f"  [OK] 图片路径: {result.image_path}")
    assert Path(result.image_path).exists()
    print("  [OK] 图片文件存在")


def test_export():
    """测试导出功能"""
    print("\n" + "=" * 50)
    print("测试5: 导出功能")

    generator = MockCodeGenerator()
    executor = CadQueryExecutor()
    exporter = CadModelExporter()

    request = CADRequest(description="测试")
    code = generator.generate(request)
    model = executor.execute(code)

    result = exporter.export(model, "output/test_export")
    print(f"  [OK] STL导出: {result.stl_path}")
    print(f"  [OK] STEP导出: {result.step_path}")
    assert Path(result.stl_path).exists()
    assert Path(result.step_path).exists()
    print("  [OK] 导出文件存在")


def main():
    print("\n" + "=" * 50)
    print("LLMCAD 功能测试")
    print("=" * 50)

    try:
        test_config()
        test_mock_generation()
        test_cad_execution()
        test_rendering()
        test_export()

        print("\n" + "=" * 50)
        print("[SUCCESS] 所有测试通过!")
        print("=" * 50)
        print("\n运行 Streamlit 应用:")
        print("  streamlit run app/main.py")
        print()
        return 0

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
