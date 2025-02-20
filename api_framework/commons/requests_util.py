"""
@ Title:
@ Author: Cathy
@ Time: 2024/11/20 14:56
"""
import requests

class Requestutil:

    sess = requests.session()

    def send_all_request(self, **kwargs):
        # 处理公共参数
        total_params = {
            "application": "app",
            "content_type": "application/json"
        }
        for k,v in kwargs.item():
            if k == "params":
                kwargs["params"].update(total_params)

        res = Requestutil.sess.request(**kwargs)
        return res




if __name__ == '__main__':

    def modify(**kwargs):
        total_headers = {
            "content_type": "application/json",
            "accept":"aaaa",
        }
        for k, v in kwargs.items():
            if k == "headers":
                kwargs["headers"].update(total_headers)

        print(total_headers)

    modify(headers={"token": "28473hdjkhwjkfdhs"}, data={"username": "zhangsan"})

