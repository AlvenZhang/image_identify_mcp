# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Image Identify MCP is a Model Context Protocol server that provides image analysis tools using Ollama's vision models. It is designed to be used with OpenCode.

## Commands

```bash
# Install dependencies
uv pip install -r requirements.txt

# Run the MCP server (for development/testing)
source .venv/bin/activate
python server.py

# Run the standalone image analyzer
source .venv/bin/activate
python analyze.py <image_path> [prompt]
```

## Architecture

Single-file MCP server (`server.py`) built with FastMCP. The server provides two tools:

1. **`describe_image`** - Analyzes images for content description and detects garbled/corrupted text
2. **`analyze_image`** - Sends custom instructions to the vision model for focused analysis

Key components:
- `load_image()` - Handles both local paths and HTTP/HTTPS URLs
- `encode_image_to_base64()` - Converts PIL Images to base64 for Ollama
- `describe_image_with_ollama()` - Core function that sends images to Ollama vision model

Configuration via environment variables:
- `OLLAMA_HOST` - Ollama server address (default: `http://localhost:11434`)
- `VISION_MODEL` - Vision model name (default: `qwen3-vl:8b-instruct-q4_K_M`)
- `OLLAMA_TIMEOUT` - Request timeout in seconds (default: `120`)

The server performs a warmup call to the Ollama model on startup to avoid first-request timeouts.

## Dependencies

- **fastmcp** - MCP server framework
- **ollama** - Ollama client library
- **requests** - HTTP requests for remote image loading
- **Pillow** - Image processing
