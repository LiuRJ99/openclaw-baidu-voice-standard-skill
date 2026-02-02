from scripts.asr import BaiduASR
from scripts.tts import BaiduTTS
from scripts.utils import get_access_token
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
    
    token, expires_in = get_access_token(config["api_key"], config["secret_key"])
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
        
        asr = BaiduASR(token, cuid, dev_pid)
        
        if audio_data:
            result = asr.recognize_raw(audio_data, format, rate)
        else:
            result = asr.recognize(audio_path, format, rate)
        
        return {"success": result is not None, "text": result}
    
    elif action == "tts":
        # 语音合成
        text = params.get("text")
        save_path = params.get("save_path", "output.mp3")
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