"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/14 11:48
"""
import os
import subprocess
import time
from pathlib import Path

import pytest
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Process


def executor_cmd(cmd):
    subprocess.run(cmd, shell=True)


def create_process(test_dir):
    cmd = f"pytest -vs {test_dir}"
    print(cmd)
    p = Process(target=executor_cmd, args=(cmd, ))
    p.start()
    print(f"{cmd}已创建进程")
    p.join()
    print(f"{cmd}当前进程执行完成")


def parse(test_path):
    """
    1。创建多线程
    2。在线程中创建进程去执行tests中文件夹的用例
    :return:
    """
    futures = []
    with ThreadPoolExecutor() as executor:
        print(f"{executor}线程已创建")
        for item in test_path.iterdir():
            # 创建进程
            futures.append(executor.submit(create_process, item))
    for future in futures:
        future.result()
    print("所有线程执行结束")
    return 0


def main():
    current_path = Path(__file__)
    tests_path = current_path.parent / "testcases"
    parse(tests_path)


if __name__ == '__main__':
    main()

    # pytest.main()
    # time.sleep(3)
    # os.system("allure generate ./temps -o ./resports --clean")
