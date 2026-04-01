#!/usr/bin/env python3
"""
Image Identify MCP Server

A Model Context Protocol server for image recognition using Ollama's vision models.
Provides tools to describe images and detect garbled/corrupted text.
"""

import base64
import os
from contextlib import contextmanager
from io import BytesIO
from pathlib import Path

import ollama
import requests
from fastmcp import FastMCP
from PIL import Image

mcp = FastMCP("image-identify-mcp")

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
VISION_MODEL = os.environ.get("VISION_MODEL", "qwen3-vl:8b-instruct-q4_K_M")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "120"))

ollama_client = ollama.Client(host=OLLAMA_HOST, timeout=OLLAMA_TIMEOUT)


def warmup():
    """Warmup Ollama model to avoid timeout on first request."""
    print(f"Warming up model: {VISION_MODEL}...")
    try:
        ollama_client.generate(
            model=VISION_MODEL,
            prompt="warmup",
            images=[],
            options={"temperature": 0},
        )
        print("Warmup complete.")
    except Exception as e:
        print(f"Warmup warning: {e}")


def load_image(image_path: str) -> Image.Image:
    """Load image from file path or URL."""
    if image_path.startswith(("http://", "https://")):
        response = requests.get(image_path, timeout=10)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    else:
        path = Path(image_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        return Image.open(path)


@contextmanager
def open_image(image_path: str):
    """Context manager for proper PIL Image resource cleanup."""
    image = load_image(image_path)
    try:
        yield image
    finally:
        image.close()


def encode_image_to_base64(image: Image.Image) -> str:
    """Encode PIL Image to base64 string."""
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


def describe_image_with_ollama(image_path: str, prompt: str) -> str:
    """Send image to Ollama vision model and get description."""
    with open_image(image_path) as image:
        image_base64 = encode_image_to_base64(image)

    try:
        response = ollama_client.generate(
            model=VISION_MODEL,
            prompt=prompt,
            images=[image_base64],
            options={"temperature": 0.3},
        )
        return response["response"]
    except ollama.Error as e:
        raise RuntimeError(f"Ollama error: {e}") from e


@mcp.tool()
def describe_image(image_path: str, custom_prompt: str = None) -> str:
    """
    Describe the content of an image and detect any garbled/corrupted text.

    This tool analyzes images to provide:
    - A detailed description of the image content
    - Detection of any garbled, corrupted, or unreadable text
    - Specific location information for any garbled text found

    Args:
        image_path: Path to the image file (local path or HTTP/HTTPS URL)
        custom_prompt: Optional custom prompt to guide the image analysis.
                      If not provided, a default comprehensive analysis will be performed.

    Returns:
        A detailed text description including any detected garbled text locations
    """
    default_prompt = """You are an expert at analyzing images and detecting text issues.

Please examine this image and provide a detailed description following these guidelines:

1. OVERVIEW: Briefly describe what the image shows (e.g., a UI screenshot, photograph, diagram, etc.)

2. DETAILED DESCRIPTION: List and describe all visible elements in the image, including:
   - Text elements (buttons, labels, headings, body text, placeholders)
   - Interactive elements (input fields, checkboxes, dropdowns, menus)
   - Visual elements (images, icons, dividers, backgrounds)
   - Layout structure (header, sidebar, main content area, footer)

3. TEXT ANALYSIS: For each text element you identified, assess whether it appears normal or garbled/corrupted:
   - If text appears normal: note what it says
   - If text appears garbled: describe exactly what is wrong and which specific element has the issue

4. GARBLED TEXT REPORT (if any found):
   For each garbled text element, provide:
   - The element name/location (e.g., "Search box placeholder text", "Navigation menu item #3")
   - What you see instead of normal text (e.g., "Shows as '����ynthetic test'", "Displays random symbols like '%#@!'")
   - The specific location in the image (e.g., "top-left corner", "center of the page", "right side of the header")

If no garbled text is found, clearly state "No garbled text detected in this image."

Be specific and detailed in your descriptions. Use exact quotes when describing visible text."""

    prompt = custom_prompt if custom_prompt else default_prompt
    description = describe_image_with_ollama(image_path, prompt)
    return description


@mcp.tool()
def analyze_image(image_path: str, instruction: str) -> str:
    """
    Analyze an image with a custom instruction.

    This tool sends both the image and a specific instruction to the vision model,
    allowing you to ask focused questions or give specific analysis tasks.

    Args:
        image_path: Path to the image file (local path or HTTP/HTTPS URL)
        instruction: Custom instruction for what to look for or what analysis to perform.
                    Examples:
                    - "Is there a red error message in this screenshot?"
                    - "Count the number of buttons in this UI"
                    - "Describe only the text elements that are visible"
                    - "Is this a legitimate login page or a phishing attempt?"

    Returns:
        Analysis result based on your instruction
    """
    prompt = f"""You are an AI assistant tasked with analyzing an image based on a specific instruction.

INSTRUCTION: {instruction}

Please analyze the image carefully and respond to the instruction above. Be specific and thorough in your analysis."""
    result = describe_image_with_ollama(image_path, prompt)
    return result


if __name__ == "__main__":
    warmup()
    mcp.run()
