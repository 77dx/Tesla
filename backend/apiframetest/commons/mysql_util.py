"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/5 16:12
"""
import pymysql
from apiframetest.configs.setting import db_config

class MysqlUtil:

    def __init__(self):
        self.conn = pymysql.connect(
            user=db_config["username"],
            password=db_config["password"],
            host=db_config["host"],
            port=db_config["port"],
            database=db_config["database"]
        )

    def execute_sql(self, sql):
        cursor = self.conn.cursor()
        cursor.execute(sql)
        value = cursor.fetchone()
        cursor.close()
        self.conn.close()
        return value

if __name__ == '__main__':
    mysql = MysqlUtil().execute_sql("select * from student")
    print(mysql)
