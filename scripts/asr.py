import requests
import base64
import json

class BaiduASR:
    def __init__(self, token, cuid, dev_pid=1537):
        """
        百度语音识别初始化
        :param token: Access Token
        :param cuid: 用户唯一标识
        :param dev_pid: 识别模型类型
        """
        self.token = token
        self.cuid = cuid
        self.dev_pid = dev_pid
        self.url = "http://vop.baidu.com/server_api"
    
    def recognize(self, audio_path, format="pcm", rate=16000):
        """
        识别本地音频文件
        :param audio_path: 音频文件路径
        :param format: 音频格式 pcm/wav/amr/m4a
        :param rate: 采样率 16000/8000
        :return: 识别文本或None
        """
        with open(audio_path, "rb") as f:
            audio_data = f.read()
        
        # JSON方式上传
        payload = {
            "format": format,
            "rate": rate,
            "channel": 1,
            "cuid": self.cuid,
            "token": self.token,
            "dev_pid": self.dev_pid,
            "speech": base64.b64encode(audio_data).decode("utf-8"),
            "len": len(audio_data)
        }
        
        headers = {"Content-Type": "application/json"}
        response = requests.post(self.url, data=json.dumps(payload), headers=headers)
        result = response.json()
        
        if result.get("err_no") == 0:
            return result["result"][0]  # 返回最优候选
        else:
            print(f"ASR Error {result.get('err_no')}: {result.get('err_msg')}")
            return None
    
    def recognize_raw(self, audio_data, format="pcm", rate=16000):
        """
        RAW方式上传(更快，适合内存中的音频数据)
        :param audio_data: 音频二进制数据
        :param format: 音频格式
        :param rate: 采样率
        :return: 识别结果
        """
        headers = {
            "Content-Type": f"audio/{format};rate={rate}"
        }
        params = {
            "cuid": self.cuid,
            "token": self.token,
            "dev_pid": self.dev_pid
        }
        
        response = requests.post(
            self.url, 
            params=params,
            headers=headers,
            data=audio_data  # 直接二进制
        )
        return response.json()