import requests
from urllib.parse import quote

class BaiduTTS:
    def __init__(self, token, cuid, per=0, spd=5, pit=5, vol=5):
        """
        百度语音合成初始化
        :param token: Access Token
        :param cuid: 用户唯一标识
        :param per: 发音人
        :param spd: 语速
        :param pit: 音调
        :param vol: 音量
        """
        self.token = token
        self.cuid = cuid
        self.per = per
        self.spd = spd
        self.pit = pit
        self.vol = vol
        self.url = "https://tsn.baidu.com/text2audio"
    
    def synthesize(self, text, aue=3, filename="output.mp3"):
        """
        合成语音并保存到文件
        :param text: 待合成文本(≤60汉字/次，超长需分段)
        :param aue: 音频格式 3=mp3, 4=pcm-16k, 6=wav
        :param filename: 保存文件名
        :return: bool 成功/失败
        """
        # 2次 URL Encode (关键！)
        tex = quote(text)
        tex = quote(tex)  # 2次encode: %E4%B8%AD -> %25E4%25B8%25AD
        
        payload = {
            "tex": tex,
            "tok": self.token,
            "cuid": self.cuid,
            "ctp": 1,
            "lan": "zh",
            "spd": self.spd,
            "pit": self.pit,
            "vol": self.vol,
            "per": self.per,
            "aue": aue
        }
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        response = requests.post(self.url, data=payload, headers=headers)
        
        # 根据 Content-Type 判断结果
        content_type = response.headers.get("Content-Type", "")
        
        if content_type.startswith("audio"):
            with open(filename, "wb") as f:
                f.write(response.content)
            return True
        else:
            # JSON 错误
            try:
                error = response.json()
                print(f"TTS Error {error.get('err_no')}: {error.get('err_msg')}")
            except:
                print(f"TTS Error: {response.text}")
            return False
    
    def get_audio_bytes(self, text, aue=3):
        """
        返回音频字节(适合直接播放，不保存文件)
        :param text: 待合成文本
        :param aue: 音频格式
        :return: 音频字节数据或None
        """
        tex = quote(quote(text))
        payload = {
            "tex": tex, "tok": self.token, "cuid": self.cuid,
            "ctp": 1, "lan": "zh", "spd": self.spd, "pit": self.pit,
            "vol": self.vol, "per": self.per, "aue": aue
        }
        response = requests.post(self.url, data=payload)
        if response.headers.get("Content-Type", "").startswith("audio"):
            return response.content
        return None