"""
@ Title:
@ Author: Cathy
@ Time: 2025/3/11 14:22
"""
from iniconfig import IniConfig


def read_ini():
    ini = IniConfig('../pytest.ini')
    if "base_url" not in ini:
        return {}
    else:
        return dict(ini["base_url"].items())



if __name__ == '__main__':
    print(read_ini())