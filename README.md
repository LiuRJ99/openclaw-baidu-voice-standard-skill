# 百度语音技能 (Baidu Voice Skill)

## 功能概述

此技能集成了百度云的语音服务，提供语音识别（ASR）和语音合成（TTS）功能。

### 核心功能

1. **语音识别 (ASR)**：
   - 将音频文件转换为文字
   - 支持多种音频格式自动转换
   - 最高支持60秒音频

2. **文本转语音 (TTS)**：
   - 将文字转换为自然语音
   - 支持多种发音人
   - 可调节语速、音调、音量

## 配置要求

### 环境变量

使用前需要配置以下环境变量：

```bash
export BAIDU_API_KEY="你的百度API密钥"
export BAIDU_SECRET_KEY="你的百度密钥"
```

### 系统依赖

- `ffmpeg`：用于音频格式转换
- `python >= 3.6`
- `requests >= 2.25.1`

## 使用方法

### 语音识别 (ASR)

```python
result = handle("asr", {
    "audio_path": "/path/to/audio.wav",
    "format": "wav",
    "rate": 16000,
    "dev_pid": 1537
}, config)
```

### 文本转语音 (TTS)

```python
result = handle("tts", {
    "text": "你好，这是一段测试文本",
    "save_path": "/path/to/output.mp3",
    "per": 0,  # 发音人
    "format": 3  # 输出格式 3=mp3
}, config)
```

## 配置文件

`config.json` 包含以下参数：

```json
{
  "cuid": "openclaw_raspberry_pi",  // 设备唯一标识
  "dev_pid": 1537,                  // 识别模型类型
  "per": 0,                         // 发音人
  "default_speed": 5,               // 默认语速
  "default_pitch": 5,               // 默认音调
  "default_volume": 5               // 默认音量
}
```

## 支持的音频格式

### ASR (语音识别)
- 输入：MP3, WAV, AMR, M4A 等常见格式
- 自动转换为：PCM 16kHz 单声道
- 限制：最长60秒

### TTS (语音合成)
- 输出：MP3, PCM, WAV
- 文本限制：每次最多60个中文字符