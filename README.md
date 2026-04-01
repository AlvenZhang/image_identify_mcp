# Image Identify MCP

使用 Ollama vision 模型进行图像识别的 MCP 服务器，支持 OpenCode、Claude Code 等所有 MCP 客户端。

## 环境要求

- Python 3.10+
- [Ollama](https://ollama.ai/) 已安装并运行
- Vision 模型：`qwen3-vl:8b-instruct-q4_K_M`

## 安装

```bash
# 创建虚拟环境
uv venv .venv
source .venv/bin/activate

# 安装依赖
uv pip install -r requirements.txt

# 安装 Vision 模型（如果还没有）
ollama pull qwen3-vl:8b-instruct-q4_K_M
```

## 测试

```bash
source .venv/bin/activate
python server.py
```

## MCP 客户端配置

在 OpenCode 的配置文件中添加 MCP 服务器。配置文件通常位于：
- `~/.config/opencode/opencode.json`

在配置文件中添加：

```json
{
  "mcpServers": {
    "image-identify": {
      "command": "uv",
      "args": [
        "--directory",
        "/Users/alven/code/image_identify_mcp",
        "run",
        "python",
        "server.py"
      ]
    }
  }
}
```

或者使用完整路径的虚拟环境：

```json
{
  "mcpServers": {
    "image-identify": {
      "command": "/Users/alven/code/image_identify_mcp/.venv/bin/python",
      "args": ["/Users/alven/code/image_identify_mcp/server.py"]
    }
  }
}
```

## 使用工具

### describe_image

描述图像内容并检测乱码文本。

**参数：**
- `image_path` (string): 图片路径（本地路径或 HTTP/HTTPS URL）

**返回：**
详细的图像内容描述，包括：
- 图像概述
- 各元素的详细描述
- 乱码文本检测结果（如有）

**示例：**
```
describe_image("/path/to/screenshot.png")
describe_image("https://example.com/image.png")
```
