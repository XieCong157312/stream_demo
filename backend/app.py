from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import subprocess
import shutil

app = FastAPI()

# 目录配置
UPLOAD_DIR = "uploads"
HLS_DIR = "hls"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(HLS_DIR, exist_ok=True)

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    # 保存上传的视频
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 转换为 HLS 格式
    output_dir = os.path.join(HLS_DIR, os.path.splitext(file.filename)[0])
    os.makedirs(output_dir, exist_ok=True)
    subprocess.run([
        "ffmpeg",
        "-i", file_path,
        "-c:v", "h264",
        "-c:a", "aac",
        "-hls_time", "5",
        "-hls_playlist_type", "event",
        "-hls_segment_filename", f"{output_dir}/segment_%03d.ts",
        f"{output_dir}/playlist.m3u8"
    ])
    
    return {"hls_url": f"/hls/{os.path.splitext(file.filename)[0]}/playlist.m3u8"}

@app.get("/hls/{path:path}")
async def serve_hls(path: str):
    return FileResponse(os.path.join(HLS_DIR, path))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)