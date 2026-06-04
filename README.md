# LLM CAD建模系统

基于LLM的对话式参数化CAD建模系统。用户通过自然语言描述，系统自动生成3D模型。

## 功能特性

- 🗣️ **自然语言输入** - 无需编程知识，描述即可生成
- 🤖 **AI自动生成代码** - 使用OpenAI GPT生成CadQuery代码
- 🎨 **3D模型渲染** - 自动渲染预览图
- 📦 **多格式导出** - 支持STL和STEP格式
- 🌐 **Streamlit界面** - 现代化Web交互界面

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

```bash
cp .env.example .env
# 编辑 .env 文件，填入你的OpenAI API密钥
```

### 3. 运行应用

```bash
streamlit run app/main.py
```

访问 `http://localhost:8501`

## 使用示例

**输入：**
```
生成一个带四个腿的圆桌
```

**输出：**
- ✅ 自动生成的CadQuery Python代码
- 🎨 3D模型渲染图
- ⬇️ 可下载的STL文件（用于3D打印）

## 项目结构

```
LLMCAD/
├── app/
│   ├── core/                    # 核心领域
│   │   ├── domain.py           # Pydantic数据模型
│   │   ├── ports.py            # 端口接口定义
│   │   └── config.py           # 配置管理
│   ├── services/               # 服务实现
│   │   ├── llm_service.py      # LLM代码生成
│   │   ├── cad_service.py      # CAD执行与导出
│   │   └── render_service.py   # 3D渲染
│   └── main.py                 # Streamlit主入口
├── requirements.txt
├── .env.example
└── README.md
```

## 架构说明

采用**端口适配器架构**（参考LayoutGenerator）：

1. **Core (核心层)** - 定义领域模型和端口接口
2. **Services (服务层)** - 实现具体业务逻辑
3. **UI (界面层)** - Streamlit交互界面

### 数据流

```
用户输入 (自然语言)
    ↓
LLMCodeGenerator.generate() → CADCode
    ↓
CadQueryExecutor.execute() → CADModel
    ↓
TrimeshRenderer.render() → RenderedImage
    ↓
CadModelExporter.export() → STL/STEP文件
```

## 支持的描述示例

- "生成一个长宽高为50,30,20的盒子"
- "创建一个带四个腿的圆桌，桌面直径80mm"
- "设计一个六角螺母，边长10mm，厚度5mm，中间有直径5mm的孔"
- "生成一个圆柱形杯子，外径30mm，高度40mm，壁厚3mm"

## 依赖库

- **CadQuery** - 参数化CAD建模库
- **OpenAI** - LLM API客户端
- **Trimesh** - 3D网格处理和渲染
- **Streamlit** - Web应用框架
- **Pydantic** - 数据验证和序列化
