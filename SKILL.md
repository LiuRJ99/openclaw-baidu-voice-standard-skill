---
name: baidu-voice
description: "Baidu Speech Recognition (ASR) and Text-to-Speech (TTS) services for OpenClaw. Provides 60s limit audio recognition and synthesis support for pcm/wav/amr formats. Use when Codex needs to work with voice services for: (1) Converting speech to text (ASR), (2) Converting text to speech (TTS), (3) Processing audio files with Baidu's speech APIs, or (4) Integrating voice capabilities into applications."
---

# Baidu Voice Skill

## Overview

This skill provides integration with Baidu's cloud speech services for both speech recognition (ASR) and text-to-speech (TTS) functionality. It enables converting audio to text and text to audio using Baidu's AI-powered APIs, supporting multiple audio formats and Chinese dialects.

## Core Capabilities

### 1. Speech Recognition (ASR)
- Convert audio files to text using Baidu's ASR API
- Automatic format conversion: Supports any common audio format (MP3, WAV, AMR, M4A, etc.), automatically converts to required format
- Up to 60-second audio files
- Multiple Chinese dialects: Mandarin (1537), English (1737), Cantonese (1637), Sichuan dialect (1837)

### 2. Text-to-Speech Synthesis (TTS)
- Convert text to natural-sounding speech
- Multiple voice options: Du Xiaomei (0), Du Xiaoyu (1), Du Xiaoyao (3), Du Yaya (4)
- Adjustable parameters: speed, pitch, volume
- Output formats: MP3, PCM, WAV

## Configuration

Before using the skill, ensure the following configuration is available:

```json
{
  "api_key": "your_baidu_api_key",
  "secret_key": "your_baidu_secret_key",
  "cuid": "unique_device_identifier",
  "dev_pid": 1537,
  "per": 0,
  "default_speed": 5,
  "default_pitch": 5,
  "default_volume": 5
}
```

## Usage Examples

### Speech Recognition
```python
result = handle("asr", {
    "audio_path": "/path/to/audio.pcm",
    "format": "pcm",
    "rate": 16000,
    "dev_pid": 1537
}, config)
```

### Text-to-Speech
```python
result = handle("tts", {
    "text": "Hello, this is a test",
    "save_path": "/path/to/output.mp3",
    "per": 4,  # Du Yaya voice
    "format": 3  # MP3 format
}, config)
```

## Audio Format Requirements

### For ASR (Speech Recognition)
- Original Format: Any common audio format (MP3, WAV, AMR, M4A, etc.)
- Converted Format: PCM (automatically converted), WAV, AMR, M4A
- Sample rate: 16000Hz (automatically converted), or 8000Hz (Mandarin only)
- Channels: 1 (mono, automatically converted from stereo)
- Duration: ≤60 seconds

### For TTS (Text Synthesis)
- Text length: ≤60 Chinese characters per request
- Text encoding: Must be properly encoded for transmission
- Output formats: MP3 (default), PCM, WAV

## Scripts

This skill includes Python implementations for:
- Authentication with Baidu API
- ASR (speech-to-text) processing
- TTS (text-to-speech) synthesis
- Audio format handling
