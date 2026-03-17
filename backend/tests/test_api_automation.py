#!/usr/bin/env python
"""
Tesla 测试平台自动化测试脚本
测试所有主要功能模块的CRUD操作
"""

import requests
import json
import time
from typing import Dict, Any, Optional

class TeslaAPITester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        
    def log(self, message: str, status: str = "INFO"):
        """记录测试日志"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{status}] {message}"
        print(log_message)
        self.test_results.append({"time": timestamp, "status": status, "message": message})
        
    def login(self, username: str = "admin", password: str = "admin123"):
        """用户登录"""
        self.log("开始测试用户登录...")
        try:
            response = requests.post(
                f"{self.base_url}/api/account/profile/login/",
                json={"username": username, "password": password},
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.headers["Authorization"] = f"Token {self.token}"
                self.log(f"登录成功，Token: {self.token[:20]}...", "SUCCESS")
                return True
            else:
                self.log(f"登录失败: {response.status_code} - {response.text}", "ERROR")
                return False
        except Exception as e:
            self.log(f"登录异常: {str(e)}", "ERROR")
            return False
    
    def test_project_crud(self):
        """测试项目的CRUD操作"""
        self.log("\n========== 测试项目模块 ==========")
        project_id = None
        
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
                project_id = response.json().get("id")
                self.log(f"创建项目成功，ID: {project_id}", "SUCCESS")
            else:
                self.log(f"创建项目失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建项目异常: {str(e)}", "ERROR")
            return None
        
        # 获取项目列表
        self.log("2. 测试获取项目列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/project/project/",
                headers=self.headers
            )
            if response.status_code == 200:
                projects = response.json().get("results", [])
                self.log(f"获取项目列表成功，共 {len(projects)} 个项目", "SUCCESS")
            else:
                self.log(f"获取项目列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"获取项目列表异常: {str(e)}", "ERROR")
        
        # 获取项目详情
        self.log("3. 测试获取项目详情...")
        try:
            response = requests.get(
                f"{self.base_url}/api/project/project/{project_id}/",
                headers=self.headers
            )
            if response.status_code == 200:
                self.log(f"获取项目详情成功", "SUCCESS")
            else:
                self.log(f"获取项目详情失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"获取项目详情异常: {str(e)}", "ERROR")
        
        # 更新项目
        self.log("4. 测试更新项目...")
        try:
            response = requests.put(
                f"{self.base_url}/api/project/project/{project_id}/",
                json={
                    "name": f"更新后的测试项目_{int(time.time())}",
                    "intro": "这是更新后的项目描述",
                    "url": "http://updated.example.com"
                },
                headers=self.headers
            )
            if response.status_code == 200:
                self.log(f"更新项目成功", "SUCCESS")
            else:
                self.log(f"更新项目失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"更新项目异常: {str(e)}", "ERROR")
        
        return project_id
    
    def test_endpoint_crud(self, project_id: int):
        """测试接口的CRUD操作"""
        self.log("\n========== 测试接口模块 ==========")
        endpoint_id = None
        
        # 创建接口
        self.log("1. 测试创建接口...")
        try:
            response = requests.post(
                f"{self.base_url}/api/case_api/endpoint/",
                json={
                    "name": f"测试接口_{int(time.time())}",
                    "project": project_id,
                    "method": "POST",
                    "url": "/api/test/endpoint",
                    "headers": {"Content-Type": "application/json"},
                    "json": {"key": "value"}
                },
                headers=self.headers
            )
            if response.status_code == 201:
                endpoint_id = response.json().get("id")
                self.log(f"创建接口成功，ID: {endpoint_id}", "SUCCESS")
            else:
                self.log(f"创建接口失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建接口异常: {str(e)}", "ERROR")
            return None
        
        # 获取接口列表
        self.log("2. 测试获取接口列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/case_api/endpoint/",
                headers=self.headers
            )
            if response.status_code == 200:
                endpoints = response.json().get("results", [])
                self.log(f"获取接口列表成功，共 {len(endpoints)} 个接口", "SUCCESS")
            else:
                self.log(f"获取接口列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"获取接口列表异常: {str(e)}", "ERROR")
        
        # 更新接口
        self.log("3. 测试更新接口...")
        try:
            response = requests.put(
                f"{self.base_url}/api/case_api/endpoint/{endpoint_id}/",
                json={
                    "name": f"更新后的测试接口_{int(time.time())}",
                    "project": project_id,
                    "method": "GET",
                    "url": "/api/test/updated"
                },
                headers=self.headers
            )
            if response.status_code == 200:
                self.log(f"更新接口成功", "SUCCESS")
            else:
                self.log(f"更新接口失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"更新接口异常: {str(e)}", "ERROR")
        
        return endpoint_id
    
    def test_case_crud(self, project_id: int, endpoint_id: int):
        """测试用例的CRUD操作"""
        self.log("\n========== 测试用例模块 ==========")
        case_id = None
        
        # 创建用例
        self.log("1. 测试创建用例...")
        try:
            response = requests.post(
                f"{self.base_url}/api/case_api/case/",
                json={
                    "name": f"测试用例_{int(time.time())}",
                    "project": project_id,
                    "endpoint": endpoint_id,
                    "validate": [{"eq": ["$.status", 200]}]
                },
                headers=self.headers
            )
            if response.status_code == 201:
                case_id = response.json().get("id")
                self.log(f"创建用例成功，ID: {case_id}", "SUCCESS")
            else:
                self.log(f"创建用例失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建用例异常: {str(e)}", "ERROR")
            return None
        
        # 获取用例列表
        self.log("2. 测试获取用例列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/case_api/case/",
                headers=self.headers
            )
            if response.status_code == 200:
                cases = response.json().get("results", [])
                self.log(f"获取用例列表成功，共 {len(cases)} 个用例", "SUCCESS")
            else:
                self.log(f"获取用例列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"获取用例列表异常: {str(e)}", "ERROR")
        
        return case_id
    
    def test_suite_crud(self, project_id: int, case_id: int):
        """测试套件的CRUD操作"""
        self.log("\n========== 测试套件模块 ==========")
        suite_id = None
        
        # 创建套件
        self.log("1. 测试创建测试套件...")
        try:
            response = requests.post(
                f"{self.base_url}/api/suite/suite/",
                json={
                    "name": f"测试套件_{int(time.time())}",
                    "project": project_id,
                    "description": "自动化测试套件",
                    "run_type": "O",
                    "case_api_list": [case_id]
                },
                headers=self.headers
            )
            if response.status_code == 201:
                suite_id = response.json().get("id")
                self.log(f"创建测试套件成功，ID: {suite_id}", "SUCCESS")
            else:
                self.log(f"创建测试套件失败: {response.status_code}", "ERROR")
                return None
        except Exception as e:
            self.log(f"创建测试套件异常: {str(e)}", "ERROR")
            return None
        
        # 获取套件列表
        self.log("2. 测试获取测试套件列表...")
        try:
            response = requests.get(
                f"{self.base_url}/api/suite/suite/",
                headers=self.headers
            )
            if response.status_code == 200:
                suites = response.json().get("results", [])
                self.log(f"获取测试套件列表成功，共 {len(suites)} 个套件", "SUCCESS")
            else:
                self.log(f"获取测试套件列表失败: {response.status_code}", "ERROR")
        except Exception as e:
            self.log(f"获取测试套件列表异常: {str(e)}", "ERROR")
        
        return suite_id
    
    def cleanup(self, project_id: int, endpoint_id: int, case_id: int, suite_id: int):
        """清理测试数据"""
        self.log("\n========== 清理测试数据 ==========")
        
        # 删除套件
        if suite_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/suite/suite/{suite_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"删除测试套件成功", "SUCCESS")
                else:
                    self.log(f"删除测试套件失败: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"删除测试套件异常: {str(e)}", "WARNING")
        
        # 删除用例
        if case_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/case/{case_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"删除用例成功", "SUCCESS")
                else:
                    self.log(f"删除用例失败: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"删除用例异常: {str(e)}", "WARNING")
        
        # 删除接口
        if endpoint_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/endpoint/{endpoint_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"删除接口成功", "SUCCESS")
                else:
                    self.log(f"删除接口失败: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"删除接口异常: {str(e)}", "WARNING")
        
        # 删除项目
        if project_id:
            try:
                response = requests.delete(
                    f"{self.base_url}/api/project/project/{project_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"删除项目成功", "SUCCESS")
                else:
                    self.log(f"删除项目失败: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"删除项目异常: {str(e)}", "WARNING")
    
    def generate_report(self):
        """生成测试报告"""
        self.log("\n========== 测试报告 ==========")
        success_count = sum(1 for r in self.test_results if r["status"] == "SUCCESS")
        error_count = sum(1 for r in self.test_results if r["status"] == "ERROR")
        warning_count = sum(1 for r in self.test_results if r["status"] == "WARNING")
        total_count = len(self.test_results)
        
        self.log(f"总测试数: {total_count}")
        self.log(f"成功: {success_count}")
        self.log(f"失败: {error_count}")
        self.log(f"警告: {warning_count}")
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
        self.log("========== 开始自动化测试 ==========")
        
        # 登录
        if not self.login():
            self.log("登录失败，终止测试", "ERROR")
            return
        
        # 测试项目模块
        project_id = self.test_project_crud()
        if not project_id:
            self.log("项目模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试接口模块
        endpoint_id = self.test_endpoint_crud(project_id)
        if not endpoint_id:
            self.log("接口模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试用例模块
        case_id = self.test_case_crud(project_id, endpoint_id)
        if not case_id:
            self.log("用例模块测试失败，终止后续测试", "ERROR")
            return
        
        # 测试套件模块
        suite_id = self.test_suite_crud(project_id, case_id)
        
        # 清理测试数据
        self.cleanup(project_id, endpoint_id, case_id, suite_id)
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告到文件
        with open("docs/test_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log("\n测试完成！报告已保存到 docs/test_report.json")

if __name__ == "__main__":
    tester = TeslaAPITester()
    tester.run_all_tests()
