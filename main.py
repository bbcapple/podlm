import os
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
import edge_tts
import asyncio
from bs4 import BeautifulSoup
import requests
from pytube import YouTube
import moviepy.editor as mp
import openai
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
import pathlib

# 加载环境变量
load_dotenv()

# 初始化应用
app = FastAPI(
    title="AI Podcast Generator",
    description="An AI-powered podcast generation system",
    version="1.0.0"
)

# 获取当前文件的目录
BASE_DIR = pathlib.Path(__file__).parent

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 确保必要的目录存在
for dir_path in [os.getenv("STATIC_DIR", "./static"), 
                 os.getenv("AUDIO_DIR", "./audio"),
                 os.getenv("OUTPUT_DIR", "./output"),
                 os.getenv("TEMP_DIR", "./temp")]:
    os.makedirs(dir_path, exist_ok=True)

# 配置静态文件
app.mount("/static", StaticFiles(directory=os.getenv("STATIC_DIR", "./static")), name="static")
app.mount("/audio", StaticFiles(directory=os.getenv("AUDIO_DIR", "./audio")), name="audio")

# 配置模型
class PodcastConfig(BaseModel):
    hosts: List[dict]  # 包含主持人信息的列表，每个主持人包含性别和风格
    background_music: bool = True
    
class ContentInput(BaseModel):
    text: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None

# 主持人声音选项
VOICE_STYLES = {
    "male": ["zh-CN-YunxiNeural", "zh-CN-YunjianNeural"],
    "female": ["zh-CN-XiaoxiaoNeural", "zh-CN-XiaoyiNeural"],
    "child": ["zh-CN-XiaoxuanNeural"],
}

async def text_to_speech(text: str, voice: str, output_file: str):
    """将文本转换为语音"""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)

def extract_text_from_url(url: str) -> str:
    """从URL提取文本内容"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def extract_audio_from_video(video_path: str, audio_path: str):
    """从视频提取音频"""
    video = mp.VideoFileClip(video_path)
    audio = video.audio
    audio.write_audiofile(audio_path)
    video.close()

def generate_title(content: str) -> str:
    """使用OpenAI生成播客标题"""
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"为以下内容生成一个吸引人的中文播客标题：\n{content[:500]}...",
        max_tokens=50
    )
    return response.choices[0].text.strip()

# 根路由
@app.get("/")
async def read_root():
    try:
        return FileResponse(os.path.join(os.getenv("STATIC_DIR", "./static"), "index.html"))
    except Exception as e:
        if os.getenv("DEBUG", "False").lower() == "true":
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/create_podcast")
async def create_podcast(
    config: PodcastConfig,
    content: ContentInput
):
    """创建AI播客的主要端点"""
    try:
        # 1. 处理输入内容
        final_text = ""
        if content.text:
            final_text += content.text
        if content.url:
            final_text += extract_text_from_url(content.url)
        
        if not final_text.strip():
            return {"status": "error", "message": "没有提供有效的内容"}
        
        # 2. 生成标题
        title = generate_title(final_text)
        
        # 3. 确保音频目录存在
        os.makedirs(os.getenv("AUDIO_DIR", "./audio"), exist_ok=True)
        
        # 4. 转换为语音
        audio_files = []
        segments = [seg for seg in final_text.split('\n\n') if seg.strip()]
        
        for i, segment in enumerate(segments):
            host = config.hosts[i % len(config.hosts)]
            voice = VOICE_STYLES[host['gender']][0]
            output_file = os.path.join(os.getenv("AUDIO_DIR", "./audio"), f"segment_{i}.mp3")
            await text_to_speech(segment, voice, output_file)
            audio_files.append(f"/audio/segment_{i}.mp3")
        
        # 5. 添加背景音乐（TODO）
        if config.background_music:
            pass
        
        return {
            "status": "success",
            "title": title,
            "audio_files": audio_files
        }
        
    except Exception as e:
        if os.getenv("DEBUG", "False").lower() == "true":
            raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
