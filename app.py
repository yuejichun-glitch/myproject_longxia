# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

"""
农产品 AI 文案生成器
使用本地 Ollama 模型
"""
from flask import Flask, request, jsonify, render_template
import requests
import os

app = Flask(__name__)

OLLAMA_URL = "http://localhost:11434"

# 预设农产品类型
PRODUCT_TYPES = {
    "水果": ["苹果", "橙子", "草莓", "葡萄", "西瓜", "桃子"],
    "蔬菜": ["白菜", "萝卜", "土豆", "番茄", "黄瓜", "辣椒"],
    "粮油": ["大米", "面粉", "玉米", "花生", "大豆", "菜籽油"],
    "干货": ["红枣", "枸杞", "香菇", "木耳", "核桃", "板栗"],
    "禽蛋": ["鸡蛋", "鸭蛋", "鹅蛋", "土鸡", "乌鸡"],
    "水产": ["鱼", "虾", "蟹", "黄鳝", "泥鳅"]
}

def call_ollama(prompt, model="qwen2.5-coder:7b"):
    """调用本地 Ollama 模型"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120
        )
        return response.json().get("response", "").strip()
    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/")
def index():
    return render_template("index.html", product_types=PRODUCT_TYPES)

@app.route("/video")
def video():
    return render_template("simple_video.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    product_name = data.get("product_name", "")
    product_type = data.get("product_type", "")
    tone = data.get("tone", "热情")
    platform = data.get("platform", "抖音")
    
    # 构建 Prompt
    prompt = f"""你是一个农产品带货文案专家。请为以下农产品生成营销文案。

农产品信息：
- 产品名称：{product_name}
- 产品类型：{product_type}
- 风格：{tone}
- 平台：{platform}

请生成以下内容：
1. 短视频标题（3个，吸引眼球）
2. 商品描述（卖点突出，让人想买）
3. 直播话术（开场白 + 促单 + 结尾）
4. 评论区回复（常见问题回复）

要求：
- 语言生动、有感染力
- 适合四五线城市消费者
- 突出绿色、健康、实惠"""

    result = call_ollama(prompt)
    return jsonify({"result": result})

@app.route("/api/models")
def get_models():
    """获取可用模型列表"""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
        models = response.json().get("models", [])
        return jsonify({"models": [m["name"] for m in models]})
    except:
        return jsonify({"models": []})

if __name__ == "__main__":
    # 创建 templates 目录
    os.makedirs("templates", exist_ok=True)
    
    print("=" * 50)
    print("🌾 农产品 AI 文案生成器")
    print("=" * 50)
    print("本地运行：http://localhost:5001")
    print("按 Ctrl+C 停止服务")
    print()
    
    app.run(host="0.0.0.0", port=5001, debug=True)
