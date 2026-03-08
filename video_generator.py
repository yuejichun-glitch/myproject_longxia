# -*- coding: utf-8 -*-
"""
农产品 AI 图文转视频工具
使用本地 FFmpeg + ComfyUI
"""
from flask import Flask, request, jsonify, render_template
import os
import subprocess
import uuid
import requests

app = Flask(__name__)

# 视频输出目录
OUTPUT_DIR = "static/outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def generate_video_from_images(images, text, audio_text, duration_per_image=5):
    """生成视频"""
    try:
        # 创建临时文件列表
        image_list = "imagelist.txt"
        with open(image_list, "w", encoding="utf-8") as f:
            for img in images:
                f.write(f"file '{img}'\n")
                f.write(f"duration {duration_per_image}\n")
        
        # 生成文件名
        video_id = str(uuid.uuid4())[:8]
        output_video = f"{OUTPUT_DIR}/video_{video_id}.mp4"
        
        # 使用 FFmpeg 合成视频
        # 这里是一个简化版本，实际需要更复杂的处理
        cmd = [
            "ffmpeg", "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", image_list,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-vf", f"scale=1280:720",
            output_video
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 清理临时文件
        os.remove(image_list)
        
        if result.returncode == 0:
            return f"/static/outputs/video_{video_id}.mp4"
        else:
            return f"Error: {result.stderr}"
            
    except Exception as e:
        return f"Error: {str(e)}"

def generate_voice(text, output_file):
    """使用 Edge TTS 生成语音"""
    try:
        # 使用 Edge TTS (免费)
        cmd = [
            "edge-tts",
            "--voice", "zh-CN-XiaoxiaoNeural",
            "--text", text,
            "--write-file", output_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0
    except:
        return False

@app.route("/")
def index():
    return render_template("video.html")

@app.route("/api/generate", methods=["POST"])
def generate():
    data = request.json
    images = data.get("images", [])  # 图片URL列表
    text = data.get("text", "")      # 文案文本
    duration = data.get("duration", 5)  # 每张图时长
    
    if not images:
        return jsonify({"error": "请上传图片"})
    
    # 生成语音
    audio_file = f"static/outputs/audio_{uuid.uuid4().hex[:8]}.mp3"
    if text:
        generate_voice(text, audio_file)
    
    # 生成视频
    video_url = generate_video_from_images(images, text, audio_file, duration)
    
    return jsonify({
        "video": video_url,
        "audio": audio_file if os.path.exists(audio_file) else None
    })

@app.route("/api/extract_images", methods=["POST"])
def extract_images():
    """从网页提取图片"""
    url = request.json.get("url", "")
    if not url:
        return jsonify({"error": "请输入URL"})
    
    try:
        import re
        from bs4 import BeautifulSoup
        
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        
        # 提取所有图片
        img_tags = soup.find_all("img")
        images = []
        for img in img_tags:
            src = img.get("src")
            if src and src.startswith("http"):
                images.append(src)
        
        return jsonify({"images": images[:10]})  # 最多10张
        
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print("=" * 50)
    print("🎬 农产品 AI 图文转视频")
    print("=" * 50)
    print("本地运行：http://localhost:5002")
    print()
    
    app.run(host="0.0.0.0", port=5002, debug=True)
