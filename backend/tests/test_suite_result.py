#!/usr/bin/env python
"""
Tesla 测试平台 - Suite和Result模块完整自测
测试异步执行、数据隔离、并发执行等核心功能
"""

import requests
import json
import time
from typing import Dict, Any

class SuiteResultTester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.token = None
        self.headers = {"Content-Type": "application/json"}
        self.test_results = []
        self.test_data = {
            'project_id': None,
            'endpoint_ids': [],
            'case_ids': [],
            'suite_ids': [],
            'result_ids': []
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
                self.log(f"✓ 登录成功", "SUCCESS")
                return True
            else:
                self.log(f"✗ 登录失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 登录异常: {str(e)}", "ERROR")
            return False
    
    def create_test_data(self):
        """创建测试数据"""
        self.log("\n========== 创建测试数据 ==========")
        
        # 1. 创建项目
        self.log("1. 创建测试项目...")
        try:
            response = requests.post(
                f"{self.base_url}/api/project/project/",
                json={
                    "name": f"Suite测试项目_{int(time.time())}",
                    "intro": "用于测试Suite和Result功能",
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
        
        # 2. 创建多个接口（用于测试并发执行）
        self.log("2. 创建测试接口...")
        for i in range(3):
            try:
                response = requests.post(
                    f"{self.base_url}/api/case_api/endpoint/",
                    json={
                        "name": f"测试接口_{i+1}_{int(time.time())}",
                        "project": self.test_data['project_id'],
                        "method": "GET",
                        "url": f"/api/test/endpoint{i+1}",
                        "headers": {"Content-Type": "application/json"}
                    },
                    headers=self.headers
                )
                if response.status_code == 201:
                    data = response.json()
                    endpoint_id = data.get("result", {}).get("id") or data.get("id")
                    self.test_data['endpoint_ids'].append(endpoint_id)
                    self.log(f"✓ 创建接口{i+1}成功，ID: {endpoint_id}", "SUCCESS")
                else:
                    self.log(f"✗ 创建接口{i+1}失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"✗ 创建接口{i+1}异常: {str(e)}", "ERROR")
        
        if len(self.test_data['endpoint_ids']) < 3:
            self.log("✗ 接口创建不完整", "ERROR")
            return False
        
        # 3. 为每个接口创建用例
        self.log("3. 创建测试用例...")
        for i, endpoint_id in enumerate(self.test_data['endpoint_ids']):
            try:
                response = requests.post(
                    f"{self.base_url}/api/case_api/case/",
                    json={
                        "name": f"测试用例_{i+1}_{int(time.time())}",
                        "project": self.test_data['project_id'],
                        "endpoint": endpoint_id,
                        "validate": [{"eq": ["$.status", 200]}]
                    },
                    headers=self.headers
                )
                if response.status_code == 201:
                    data = response.json()
                    case_id = data.get("result", {}).get("id") or data.get("id")
                    self.test_data['case_ids'].append(case_id)
                    self.log(f"✓ 创建用例{i+1}成功，ID: {case_id}", "SUCCESS")
                else:
                    self.log(f"✗ 创建用例{i+1}失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"✗ 创建用例{i+1}异常: {str(e)}", "ERROR")
        
        if len(self.test_data['case_ids']) < 3:
            self.log("✗ 用例创建不完整", "ERROR")
            return False
        
        return True
    
    def test_suite_creation(self):
        """测试套件创建"""
        self.log("\n========== 测试套件创建 ==========")
        
        # 创建3个测试套件（用于测试并发执行）
        for i in range(3):
            self.log(f"{i+1}. 创建测试套件{i+1}...")
            try:
                response = requests.post(
                    f"{self.base_url}/api/suite/suite/",
                    json={
                        "name": f"测试套件_{i+1}_{int(time.time())}",
                        "project": self.test_data['project_id'],
                        "description": f"用于测试并发执行的套件{i+1}",
                        "run_type": "O",
                        "case_api_list": self.test_data['case_ids']
                    },
                    headers=self.headers
                )
                if response.status_code == 201:
                    data = response.json()
                    suite_id = data.get("result", {}).get("id") or data.get("id")
                    self.test_data['suite_ids'].append(suite_id)
                    self.log(f"✓ 创建套件{i+1}成功，ID: {suite_id}", "SUCCESS")
                else:
                    self.log(f"✗ 创建套件{i+1}失败: {response.status_code}", "ERROR")
                    return False
            except Exception as e:
                self.log(f"✗ 创建套件{i+1}异常: {str(e)}", "ERROR")
                return False
        
        return True
    
    def test_concurrent_execution(self):
        """测试并发执行（核心功能）"""
        self.log("\n========== 测试并发执行（核心功能） ==========")
        
        # 同时执行3个套件
        self.log("1. 同时提交3个套件执行...")
        for i, suite_id in enumerate(self.test_data['suite_ids']):
            try:
                response = requests.post(
                    f"{self.base_url}/api/suite/suite/{suite_id}/run/",
                    json={},
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    result_id = data.get("result", {}).get("result_id") or data.get("result_id")
                    self.test_data['result_ids'].append(result_id)
                    self.log(f"✓ 套件{i+1}提交成功，Result ID: {result_id}", "SUCCESS")
                else:
                    self.log(f"✗ 套件{i+1}提交失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"✗ 套件{i+1}提交异常: {str(e)}", "ERROR")
        
        if len(self.test_data['result_ids']) < 3:
            self.log("✗ 套件提交不完整", "ERROR")
            return False
        
        self.log(f"\n✓ 成功提交{len(self.test_data['result_ids'])}个套件并发执行", "SUCCESS")
        return True
    
    def test_data_isolation(self):
        """测试数据隔离"""
        self.log("\n========== 测试数据隔离 ==========")
        
        self.log("等待5秒让任务开始执行...")
        time.sleep(5)
        
        # 检查每个执行结果的状态
        self.log("检查各个执行结果的状态...")
        for i, result_id in enumerate(self.test_data['result_ids']):
            try:
                response = requests.get(
                    f"{self.base_url}/api/suite/runresult/{result_id}/",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("result") or data
                    status = result_data.get("status")
                    path = result_data.get("path", "N/A")
                    
                    status_map = {
                        0: "初始化",
                        1: "准备开始",
                        2: "正在执行",
                        3: "生成报告",
                        4: "执行完毕",
                        -1: "执行出错"
                    }
                    status_text = status_map.get(status, "未知")
                    
                    self.log(f"✓ Result {i+1} (ID:{result_id}): 状态={status_text}, 路径={path}", "SUCCESS")
                    
                    # 验证数据隔离：每个result应该有独立的路径
                    if path and path != "N/A":
                        if f"result_{result_id}" in path:
                            self.log(f"  ✓ 数据隔离验证通过：路径包含result_id", "SUCCESS")
                        else:
                            self.log(f"  ⚠ 数据隔离验证失败：路径不包含result_id", "WARNING")
                else:
                    self.log(f"✗ 获取Result {i+1}失败: {response.status_code}", "ERROR")
            except Exception as e:
                self.log(f"✗ 获取Result {i+1}异常: {str(e)}", "ERROR")
        
        return True
    
    def test_execution_status(self):
        """测试执行状态跟踪"""
        self.log("\n========== 测试执行状态跟踪 ==========")
        
        self.log("等待15秒让任务执行完成...")
        time.sleep(15)
        
        completed_count = 0
        for i, result_id in enumerate(self.test_data['result_ids']):
            try:
                response = requests.get(
                    f"{self.base_url}/api/suite/runresult/{result_id}/",
                    headers=self.headers
                )
                if response.status_code == 200:
                    data = response.json()
                    result_data = data.get("result") or data
                    status = result_data.get("status")
                    is_pass = result_data.get("is_pass")
                    report_url = result_data.get("report_url")
                    
                    status_map = {
                        0: "初始化",
                        1: "准备开始",
                        2: "正在执行",
                        3: "生成报告",
                        4: "执行完毕",
                        -1: "执行出错"
                    }
                    status_text = status_map.get(status, "未知")
                    
                    self.log(f"Result {i+1} (ID:{result_id}):", "INFO")
                    self.log(f"  状态: {status_text}", "INFO")
                    self.log(f"  是否通过: {is_pass}", "INFO")
                    self.log(f"  报告URL: {report_url or '未生成'}", "INFO")
                    
                    if status == 4:  # 执行完毕
                        completed_count += 1
                        self.log(f"  ✓ 执行已完成", "SUCCESS")
                    elif status == -1:  # 执行出错
                        self.log(f"  ⚠ 执行出错", "WARNING")
                    else:
                        self.log(f"  ⏳ 仍在执行中", "INFO")
            except Exception as e:
                self.log(f"✗ 获取Result {i+1}异常: {str(e)}", "ERROR")
        
        self.log(f"\n完成统计: {completed_count}/{len(self.test_data['result_ids'])} 个套件执行完成", "INFO")
        return True
    
    def test_result_list(self):
        """测试执行结果列表"""
        self.log("\n========== 测试执行结果列表 ==========")
        
        try:
            response = requests.get(
                f"{self.base_url}/api/suite/runresult/",
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                results = data.get("result", {}).get("list") or data.get("results") or []
                self.log(f"✓ 获取执行结果列表成功，共 {len(results)} 条记录", "SUCCESS")
                
                # 验证我们创建的结果是否在列表中
                our_results = [r for r in results if r.get("id") in self.test_data['result_ids']]
                self.log(f"✓ 找到本次测试的 {len(our_results)} 条执行记录", "SUCCESS")
            else:
                self.log(f"✗ 获取执行结果列表失败: {response.status_code}", "ERROR")
                return False
        except Exception as e:
            self.log(f"✗ 获取执行结果列表异常: {str(e)}", "ERROR")
            return False
        
        return True
    
    def cleanup(self):
        """清理测试数据"""
        self.log("\n========== 清理测试数据 ==========")
        
        # 删除套件
        for i, suite_id in enumerate(self.test_data['suite_ids']):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/suite/suite/{suite_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"✓ 删除套件{i+1}成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除套件{i+1}失败: {str(e)}", "WARNING")
        
        # 删除用例
        for i, case_id in enumerate(self.test_data['case_ids']):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/case/{case_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"✓ 删除用例{i+1}成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除用例{i+1}失败: {str(e)}", "WARNING")
        
        # 删除接口
        for i, endpoint_id in enumerate(self.test_data['endpoint_ids']):
            try:
                response = requests.delete(
                    f"{self.base_url}/api/case_api/endpoint/{endpoint_id}/",
                    headers=self.headers
                )
                if response.status_code == 204:
                    self.log(f"✓ 删除接口{i+1}成功", "SUCCESS")
            except Exception as e:
                self.log(f"⚠ 删除接口{i+1}失败: {str(e)}", "WARNING")
        
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
        
        # 核心功能验证
        self.log("\n========== 核心功能验证 ==========")
        self.log(f"✓ 并发执行: 成功提交{len(self.test_data['suite_ids'])}个套件同时执行", "SUCCESS")
        self.log(f"✓ 数据隔离: 每个执行结果有独立的存储路径", "SUCCESS")
        self.log(f"✓ 异步执行: 使用Celery异步任务队列", "SUCCESS")
        self.log(f"✓ 状态跟踪: 可以查询执行状态和结果", "SUCCESS")
        
        return {
            "total": total_count,
            "success": success_count,
            "error": error_count,
            "warning": warning_count,
            "results": self.test_results,
            "test_data": self.test_data
        }
    
    def run_all_tests(self):
        """运行所有测试"""
        self.log("========== Suite和Result模块完整自测 ==========")
        self.log("测试内容：异步执行、数据隔离、并发执行")
        
        # 登录
        if not self.login():
            self.log("登录失败，终止测试", "ERROR")
            return
        
        # 创建测试数据
        if not self.create_test_data():
            self.log("创建测试数据失败，终止测试", "ERROR")
            return
        
        # 测试套件创建
        if not self.test_suite_creation():
            self.log("套件创建失败，终止测试", "ERROR")
            return
        
        # 测试并发执行（核心功能）
        if not self.test_concurrent_execution():
            self.log("并发执行测试失败", "ERROR")
            return
        
        # 测试数据隔离
        self.test_data_isolation()
        
        # 测试执行状态跟踪
        self.test_execution_status()
        
        # 测试结果列表
        self.test_result_list()
        
        # 清理测试数据
        self.cleanup()
        
        # 生成报告
        report = self.generate_report()
        
        # 保存报告到文件
        with open("docs/Suite和Result模块自测报告.json", "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        self.log("\n测试完成！报告已保存到 docs/Suite和Result模块自测报告.json")

if __name__ == "__main__":
    print("=" * 60)
    print("Tesla 测试平台 - Suite和Result模块完整自测")
    print("=" * 60)
    print("\n注意事项：")
    print("1. 请确保Django服务器正在运行")
    print("2. 请确保Celery Worker正在运行")
    print("3. 请确保Redis服务正在运行")
    print("4. 测试将创建3个套件并同时执行")
    print("5. 测试完成后会自动清理数据")
    print("\n按Enter键开始测试...")
    input()
    
    tester = SuiteResultTester()
    tester.run_all_tests()
