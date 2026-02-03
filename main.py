from scripts.asr import BaiduASR
from scripts.tts import BaiduTTS
from scripts.utils import get_access_token
from scripts.audio_utils import prepare_audio_for_asr
import os
import tempfile
import time

# 缓存 token
_token_cache = {
    "access_token": None,
    "expires_at": 0
}

def _get_token(config):
    """带缓存的 Token 获取"""
    global _token_cache
    now = time.time()
    
    if _token_cache["access_token"] and now < _token_cache["expires_at"]:
        return _token_cache["access_token"]
    
    # 从环境变量获取密钥
    api_key = os.getenv("BAIDU_API_KEY")
    secret_key = os.getenv("BAIDU_SECRET_KEY")
    
    if not api_key or not secret_key:
        raise ValueError("Missing BAIDU_API_KEY or BAIDU_SECRET_KEY environment variable")
    
    token, expires_in = get_access_token(api_key, secret_key)
    _token_cache["access_token"] = token
    _token_cache["expires_at"] = now + expires_in - 3600  # 提前1小时过期
    return token

def handle(action, params, config):
    """
    OpenClaw 调用入口
    action: "asr" | "tts"
    params: 参数字典
    """
    token = _get_token(config)
    cuid = config.get("cuid", "openclaw_pi")
    
    if action == "asr":
        # 语音识别
        audio_path = params.get("audio_path")
        audio_data = params.get("audio_data")  # bytes
        format = params.get("format", "pcm")
        rate = params.get("rate", 16000)
        dev_pid = params.get("dev_pid", config.get("dev_pid", 1537))
        
        if audio_data:
            # Raw audio data processing (already in correct format)
            asr = BaiduASR(token, cuid, dev_pid)
            result = asr.recognize_raw(audio_data, format, rate)
        elif audio_path:
            # File-based processing with automatic format conversion
            # First prepare the audio file for ASR
            prepared_audio_path = prepare_audio_for_asr(audio_path)
            if not prepared_audio_path:
                return {"success": False, "error": "Failed to prepare audio file for ASR. Unsupported format or invalid file."}
            
            # Use the prepared audio file for recognition
            asr = BaiduASR(token, cuid, dev_pid)
            result = asr.recognize(prepared_audio_path, "pcm", 16000)  # Always use PCM at 16kHz after conversion
            
            # Clean up temporary converted file if it was created in temp directory
            if prepared_audio_path != audio_path:
                try:
                    os.remove(prepared_audio_path)
                except:
                    pass  # Ignore cleanup errors
        else:
            return {"success": False, "error": "Either audio_path or audio_data must be provided"}
        
        return {"success": result is not None, "text": result}
    
    elif action == "tts":
        # 语音合成
        text = params.get("text")
        save_path = params.get("save_path", "output.mp3")
        # 如果save_path不是绝对路径，则保存到alist-mount/voice目录
        if not save_path.startswith('/'):
            save_path = f"/home/pihome/alist-mount/voice/{os.path.basename(save_path)}"
        else:
            # 确保目录存在
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        aue = params.get("format", 3)  # 3=mp3
        per = params.get("per", config.get("per", 0))
        
        tts = BaiduTTS(token, cuid, per, 
                      config.get("default_speed", 5),
                      config.get("default_pitch", 5),
                      config.get("default_volume", 5))
        
        success = tts.synthesize(text, aue, save_path)
        
        return {
            "success": success,
            "file_path": os.path.abspath(save_path) if success else None,
            "format": "mp3" if aue == 3 else "pcm" if aue == 4 else "wav"
        }
    
    return {"success": False, "error": "Unknown action"}