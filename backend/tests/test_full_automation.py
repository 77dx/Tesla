#!/usr/bin/env python
"""
Tesla 测试平台完整自测脚本
包含所有模块的接口测试
"""

import requests
import json
import time
from typing import Dict, Any

class TeslaFullTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.test_data = {
            'project_id': None,
            'endpoint_id': None,
            'case_id': None,
            'suite_id': None,
            'role_id': None,
            'department_id': None,
            'position_id': None
        }
        
    def log(self, message: str, status: str = "INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{status}] {message}"
        print(log_message)
        self.test_results.append({"time": timestamp, "status": status, "message": message})
        
    def login(self, username: str = "keke", password: str = "123456"):
        """用户登录"""
        self.log("========== 测试用户登录 ==========")
        try:
            response = requests.post(
                f"{self.base_url}/api/account/profile/login/",
                json={"username": username, "password": password},
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("result", {}).get("token")
                self.headers["Authorization"] = f"Token {self.token}"
                self.log(f"✓ 登录成功，Token: {self.token[:20]}...", "SUCCESS")
                return True
            else:
                self.log(f"✗ 登录失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 登录异常: {str(e)}", "ERROR")
            return False
    
    def test_account_module(self):
        """测试账户模块"""
        self.log("\n========== 测试账户模块 ==========")
        
        # 获取用户信息
        self.log("1. 测试获取用户信息...")
        try:
            response = requests.get(
                f"{self.base_url}/api/account/profile/profile/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取用户信息成功", "SUCCESS")
            else:
                self.log(f"✗ 获取用户信息失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取用户信息异常: {str(e)}", "ERROR")
        
        # 获取所有用户
        self.log("2. 测试获取所有用户...")
        try:
            response = requests.get(
                f"{self.base_url}/api/account/profile/get_all_users/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取所有用户成功", "SUCCESS")
            else:
                self.log(f"✗ 获取所有用户失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取所有用户异常: {str(e)}", "ERROR")
    
    def test_system_module(self):
        """测试系统模块"""
        self.log("\n========== 测试系统模块 ==========")
        
        # 测试角色管理
        self.log("1. 测试角色管理...")
        try:
            # 创建角色
            response = requests.post(
                f"{self.base_url}/api/system/role/",
                json={"name": f"测试角色_{int(time.time())}"},
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['role_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建角色成功，ID: {self.test_data['role_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建角色失败: {response.status_code}", "ERROR")
            
            # 获取角色列表
            response = requests.get(
                f"{self.base_url}/api/system/role/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取角色列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取角色列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 角色管理测试异常: {str(e)}", "ERROR")
        
        # 测试部门管理
        self.log("2. 测试部门管理...")
        try:
            # 创建部门
            response = requests.post(
                f"{self.base_url}/api/system/department/",
                json={
                    "name": f"测试部门_{int(time.time())}",
                    "intro": "这是一个测试部门"
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['department_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建部门成功，ID: {self.test_data['department_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建部门失败: {response.status_code}", "ERROR")
            
            # 获取部门列表
            response = requests.get(
                f"{self.base_url}/api/system/department/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取部门列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取部门列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 部门管理测试异常: {str(e)}", "ERROR")
        
        # 测试职位管理
        self.log("3. 测试职位管理...")
        try:
            # 创建职位
            response = requests.post(
                f"{self.base_url}/api/system/position/",
                json={
                    "name": f"测试职位_{int(time.time())}",
                    "is_leader": False
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['position_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建职位成功，ID: {self.test_data['position_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建职位失败: {response.status_code}", "ERROR")
            
            # 获取职位列表
            response = requests.get(
                f"{self.base_url}/api/system/position/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取职位列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取职位列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 职位管理测试异常: {str(e)}", "ERROR")
    
    def test_project_module(self):
        """测试项目模块"""
        self.log("\n========== 测试项目模块 ==========")
        
        # 创建项目
        self.log("1. 测试创建项目...")
        try:
            response = requests.post(
                f"{self.base_url}/api/project/project/",
                json={
                    "name": f"测试项目_{int(time.time())}",
                    "intro": "这是一个自动化测试项目",
                    "url": "http://test.example.com"
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['project_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建项目成功，ID: {self.test_data['project_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建项目失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 创建项目异常: {str(e)}", "ERROR")
            return False
        
        # 获取项目列表
        self.log("2. 测试获取项目列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/project/project/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取项目列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取项目列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取项目列表异常: {str(e)}", "ERROR")
        
        return True
    
    def test_endpoint_module(self):
        """测试接口模块"""
        self.log("\n========== 测试接口模块 ==========")
        
        if not self.test_data['project_id']:
            self.log("✗ 跳过接口测试：缺少项目ID", "WARNING")
            return False
        
        # 创建接口
        self.log("1. 测试创建接口...")
        try:
            response = requests.post(
                f"{self.base_url}/api/case_api/endpoint/",
                json={
                    "name": f"测试接口_{int(time.time())}",
                    "project": self.test_data['project_id'],
                    "method": "POST",
                    "url": "/api/test/endpoint",
                    "headers": {"Content-Type": "application/json"},
                    "json": {"key": "value"}
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['endpoint_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建接口成功，ID: {self.test_data['endpoint_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建接口失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 创建接口异常: {str(e)}", "ERROR")
            return False
        
        # 获取接口列表
        self.log("2. 测试获取接口列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/case_api/endpoint/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取接口列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取接口列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取接口列表异常: {str(e)}", "ERROR")
        
        return True
    
    def test_case_module(self):
        """测试用例模块"""
        self.log("\n========== 测试用例模块 ==========")
        
        if not self.test_data['endpoint_id']:
            self.log("✗ 跳过用例测试：缺少接口ID", "WARNING")
            return False
        
        # 创建用例
        self.log("1. 测试创建用例...")
        try:
            response = requests.post(
                f"{self.base_url}/api/case_api/case/",
                json={
                    "name": f"测试用例_{int(time.time())}",
                    "project": self.test_data['project_id'],
                    "endpoint": self.test_data['endpoint_id'],
                    "validate": [{"eq": ["$.status", 200]}]
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['case_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建用例成功，ID: {self.test_data['case_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建用例失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 创建用例异常: {str(e)}", "ERROR")
            return False
        
        # 获取用例列表
        self.log("2. 测试获取用例列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/case_api/case/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取用例列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取用例列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取用例列表异常: {str(e)}", "ERROR")
        
        return True
    
    def test_suite_module(self):
        """测试套件模块"""
        self.log("\n========== 测试套件模块 ==========")
        
        if not self.test_data['case_id']:
            self.log("✗ 跳过套件测试：缺少用例ID", "WARNING")
            return False
        
        # 创建套件
        self.log("1. 测试创建测试套件...")
        try:
            response = requests.post(
                f"{self.base_url}/api/suite/suite/",
                json={
                    "name": f"测试套件_{int(time.time())}",
                    "project": self.test_data['project_id'],
                    "description": "自动化测试套件",
                    "run_type": "O",
                    "case_api_list": [self.test_data['case_id']]
                },
                headers=self.headers
            )
            if response.status_code == 201:
                data = response.json()
                self.test_data['suite_id'] = data.get("result", {}).get("id") or data.get("id")
                self.log(f"✓ 创建测试套件成功，ID: {self.test_data['suite_id']}", "SUCCESS")
            else:
                self.log(f"✗ 创建测试套件失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 创建测试套件异常: {str(e)}", "ERROR")
            return False
        
        # 获取套件列表
        self.log("2. 测试获取测试套件列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/suite/suite/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log("✓ 获取测试套件列表成功", "SUCCESS")
            else:
                self.log(f"✗ 获取测试套件列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"✗ 获取测试套件列表异常: {str(e)}", "ERROR")
        
        return True
    
    def cleanup(self):
        """清理测试数据"""
        self.log("\n========== 清理测试数据 ==========")
        
        # 删除套件
        if self.test_data['suite_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/suite/suite/{self.test_data['suite_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除测试套件成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除测试套件失败: {str(e)}", "WARNING")
        
        # 删除用例
        if self.test_data['case_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/case/{self.test_data['case_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除用例成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除用例失败: {str(e)}", "WARNING")
        
        # 删除接口
        if self.test_data['endpoint_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/endpoint/{self.test_data['endpoint_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除接口成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除接口失败: {str(e)}", "WARNING")
        
        # 删除项目
        if self.test_data['project_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/project/project/{self.test_data['project_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除项目成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除项目失败: {str(e)}", "WARNING")
        
        # 删除角色
        if self.test_data['role_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/system/role/{self.test_data['role_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除角色成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除角色失败: {str(e)}", "WARNING")
        
        # 删除部门
        if self.test_data['department_id']:
            try:
                response = requests.post(
                    f"{self.base_url}/api/system/department/delete/",
                    json={"id": self.test_data['department_id']},
                    headers=self.headers
                )
                if response.status_code == 200:
                    self.log("✓ 删除部门成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除部门失败: {str(e)}", "WARNING")
        
        # 删除职位
        if self.test_data['position_id']:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/system/position/{self.test_data['position_id']}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log("✓ 删除职位成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除职位失败: {str(e)}", "WARNING")
    
    def generate_report(self):
        """生成测试报告"""
        self.log("\n========== 测试报告 ==========")
        success_count = sum(1 for r in self.test_results if r["status"] == "SUCCESS")
        error_count = sum(1 for r in self.test_results if r["status"] == "ERROR")
        warning_count = sum(1 for r in self.test_results if r["status"] == "WARNING")
        total_count = len([r for r in self.test_results if r["status"] in ["SUCCESS", "ERROR"]])
        
        self.log(f"总测试数: {total_count}")
        self.log(f"成功: {success_count}")
        self.log(f"失败: {error_count}")
        self.log(f"警告: {warning_count}")
        if total_count > 0:
            self.log(f"成功率: {success_count/total_count*100:.2f}%")
        
        return {
            "total": total_count,
            "success": success_count,
            "error": error_count,
            "warning": warning_count,
            "results": self.test_results
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("========== 开始完整自动化测试 ==========")
        
        # 登录
        if not self.login():
            self.log("登录失败，终止测试", "ERROR")
            return
        
        # 测试账户模块
        self.test_account_module()
        
        # 测试系统模块
        self.test_system_module()
        
        # 测试项目模块
        if not self.test_project_module():
            self.log("项目模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试接口模块
        if not self.test_endpoint_module():
            self.log("接口模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试用例模块
        if not self.test_case_module():
            self.log("用例模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试套件模块
        self.test_suite_module()
        
        # 清理测试数据
        self.cleanup()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告到文件
        with open("docs/完整自测报告.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log("\n测试完成！报告已保存到 docs/完整自测报告.json")

if __name__ == "__main__":
    tester = TeslaFullTester()
    tester.run_all_tests()
