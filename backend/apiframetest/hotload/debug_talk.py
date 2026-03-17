"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/4 17:35
"""
import base64
import hashlib
import re
import os
import rsa
import yaml
from Tesla import settings
from apiframetest.commons.base_url import read_ini
from apiframetest.configs import setting
from apiframetest.configs.setting import current_url
import redis

# 这里面都是在yaml中可以调用的方法
class DebugTalk:
    def yaml_read(self, key):
        key = key.replace(' ', '')

        backend = os.getenv("APIFRAME_CONTEXT_BACKEND", "file").lower()
        if backend == "redis":
            redis_url = os.getenv("APIFRAME_REDIS_URL") or os.getenv("CELERY_BROKER_URL") or "redis://127.0.0.1:6379/0"
            prefix = os.getenv("APIFRAME_CONTEXT_PREFIX", "")
            redis_key = f"{prefix}:context" if prefix else "apiframe:context"

            r = redis.Redis.from_url(redis_url, decode_responses=True)
            return r.hget(redis_key, key)

        # file backend (默认)
        extract_path = getattr(setting, "extract_path", None) or str(settings.EXTRACT_PATH)
        with open(extract_path, encoding='utf-8', mode='r') as f:
            value = yaml.safe_load(f) or {}
            return value.get(key)
    def env(self, key):
        current_url = setting.current_url
        return current_url
        # current_env = setting.current_env
        # url = read_ini()[key]
        # url_1, url_2 = url.split("//")
        # if current_env == "test":
        #     current_base_url = f"{url_1}//test-{url_2}"
        # elif current_env == "dev":
        #     current_base_url = f"{url_1}//dev-{url_2}"
        # else:
        #     current_base_url = url
        # return current_base_url
    def md5_encode(self, data):
        # 把data数据转成utf-8格式
        data = str(data).encode("utf-8")
        # md5加密，用的是哈希算法
        md5_value = hashlib.md5(data).hexdigest()
        return md5_value
    def base64_encode(self, data):
        data = str(data).encoding("utf-8")
        base64_value = base64.b64encode(data).decode(encoding="utf-8")
        return base64_value
    # 生成公钥和私钥
    def create_key(self):
        (pub_key, private_key) = rsa.newkeys(1024)
        with open("./public.pem", 'w') as f:
            f.write(pub_key.save_pkcs1().decode())
        with open("./private.pem", 'w') as f:
            f.write(private_key.save_pkcs1().decode())
    def rsa_encode(self, data):
        # 加载公钥
        with open("./publish.pem") as f:
            pubkey = rsa.PublicKey.load_pkcs1(f.read().encode())
        data = str(data).encode("utf-8")
        byte_value = rsa.encrypt(data, pubkey)
        rsa_value = base64.b64encode(byte_value).decode("utf-8")
        return rsa_value



if __name__ == '__main__':
    d = DebugTalk()
    # d.create_key()
    print(d.env("user-site"))
