# !pip install transformers
# !pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118


import os
import torch
import gc
from transformers import pipeline
import utils.decorator_utils
# from importlib import reload
# reload(utils.decorator_utils)
from utils.decorator_utils import persistent_cache
print("GPU is available:", torch.cuda.is_available())

try:
    gc.collect()
    torch.cuda.empty_cache()
except:
    pass

# 1. 加载模型到 GPU 或 CPU
asr = None  # 定义全局变量
from transformers import pipeline


model = "openai/whisper-large-v3-turbo"

def load_model():
    global asr  # 使用全局变量
    if asr is None:  # 如果模型还没有加载，则加载模型
        device = 0 if torch.cuda.is_available() else -1
        asr = pipeline("automatic-speech-recognition", model=model, device=device)
    return asr

# 2. 准备音频文件及输出目录
def prepare_audio_files(set_dir_name, audio_ext, audio_dir):
    output_dir = os.path.join(audio_dir, set_dir_name, "audio_text")
    os.makedirs(output_dir, exist_ok=True)

    audio_file_list = [
        os.path.join(audio_dir, set_dir_name, filename)
        for filename in os.listdir(os.path.join(audio_dir, set_dir_name))
        if filename.endswith(audio_ext)
    ]

    return output_dir, audio_file_list

# 3. 识别音频文本
@persistent_cache("drive/MyDrive/temp/transcribe_audio")
def transcribe_audio(audio_path):
    asr = load_model()  # 加载模型
    with torch.no_grad():  # 禁用梯度计算以减少内存使用
        result = asr(audio_path, return_timestamps=True)  # 返回时间戳

    return result

# 4. 处理结果并生成 SRT 文件
def process_srt(result, audio_path, output_dir):
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    output_srt_path = os.path.join(output_dir, f"{filename}.srt")

    chunk_length_s = result.get("chunk_length_s", 30)  # 默认分块长度
    chunk_index = 0
    last_start_time = 0

    # SRT 文件内容准备
    srt_content = []
    for i, chunk in enumerate(result["chunks"]):
        start_time, end_time = chunk["timestamp"]

        if start_time < last_start_time:
            chunk_index += 1
        last_start_time = start_time

        # 计算偏移量
        offset = chunk_length_s * chunk_index
        start_time += offset
        end_time += offset

        # SRT 格式化
        srt_content.append(f"{i + 1}")
        srt_content.append(f"{format_timestamp(start_time)} --> {format_timestamp(end_time)}")
        srt_content.append(chunk["text"].strip())
        srt_content.append("")  # 添加空行分隔

    # 将 SRT 内容保存到文件
    with open(output_srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_content))

    print(f"转录完成：{output_srt_path}")

# 5. 格式化时间戳
def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{int(seconds):02},{milliseconds:03}"

# 6. 主处理函数
def main(set_dir_name, audio_ext, audio_dir):
    output_dir, audio_file_list = prepare_audio_files(set_dir_name, audio_ext, audio_dir)

    for audio_path in audio_file_list:
        print(f"处理音频文件：{audio_path}")

        result = transcribe_audio(audio_path)  # 识别音频内容

        process_srt(result, audio_path, output_dir)  # 处理并生成 SRT 文件

        # 清理 GPU 显存
        del result  # 删除结果对象
        torch.cuda.empty_cache()  # 释放未使用的显存

    # 清理 GPU 显存
    gc.collect()  # 垃圾回收

# 配置参数并运行主函数
if __name__ == "__main__":
    set_dir_name = "2022 最新 Android 基础教程，从开发入门到项目实战，看它就够了，更新中"
    audio_ext = ".aac"
    audio_dir = "/content/drive/MyDrive/audios"  # 设置你的音频文件夹路径

    main(set_dir_name, audio_ext, audio_dir)
