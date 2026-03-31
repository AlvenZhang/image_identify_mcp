import ollama
import base64
import sys


def analyze_image(image_path: str, prompt: str = "描述图片") -> str:
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    response = ollama.generate(
        model="qwen3-vl:8b-instruct-q4_K_M",
        prompt=prompt,
        images=[img_b64],
    )
    return response["response"]


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python analyze.py <图片路径> [提示词]")
        sys.exit(1)

    # image_path = sys.argv[1]
    image_path = "/tmp/flutter_test/test_outputs/1774937059066/07_result_page_loaded.png"
    prompt = sys.argv[2] if len(sys.argv) > 2 else "详细描述这张图片"

    try:
        result = analyze_image(image_path, prompt)
        print(result)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)
