import requests
import json

def get_access_token(api_key, secret_key):
    """
    获取百度语音API的Access Token
    :param api_key: API Key
    :param secret_key: Secret Key
    :return: access_token 和过期时间
    """
    url = f"https://aip.baidubce.com/oauth/2.0/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": api_key,
        "client_secret": secret_key
    }
    response = requests.post(url, params=params)
    result = response.json()
    if "access_token" in result:
        return result["access_token"], result.get("expires_in", 2592000)
    else:
        raise Exception(f"Auth failed: {result}")