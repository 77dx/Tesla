"""
@ Title: 测试执行服务
@ Author: Cathy
@ Time: 2026/3/2
@ Description: 提供测试套件执行的核心功能,支持多进程并发执行

本模块是测试执行的核心服务层,负责:
1. 执行 pytest 测试用例
2. 生成 Allure 测试报告
3. 管理测试执行状态
4. 提供多进程/线程安全的执行环境

主要类和函数:
- TestExecutionService: 测试执行服务类,封装完整的执行流程
- run_suite_tests: 便捷函数,用于在多进程/线程中调用

使用示例:
    # 方式1: 直接使用服务类
    service = TestExecutionService(result_id=1, yaml_files_dir='/path/to/yaml', report_base_dir='/path/to/report')
    result = service.execute_tests()
    
    # 方式2: 使用便捷函数(推荐用于多进程)
    result = run_suite_tests(result_id=1, yaml_files_dir='/path/to/yaml', report_base_dir='/path/to/report')
"""
import logging
import os
import subprocess
import time
import pytest
from pathlib import Path
from Tesla import settings

logger = logging.getLogger(__name__)


class TestExecutionService:
    """
    测试执行服务类
    
    职责:
    1. 管理测试执行的完整生命周期
    2. 执行 pytest 测试用例
    3. 生成 Allure 测试报告
    4. 更新数据库中的执行状态
    
    设计特点:
    - 线程安全: 每个实例独立管理自己的目录和状态
    - 数据隔离: 使用独立的目录存储每次执行的结果
    - 错误处理: 完善的异常捕获和状态回滚机制
    - 日志记录: 详细的执行日志,便于问题排查
    
    状态流转:
    Init → Running → Reporting → Done/Error
    """
    
    def __init__(self, result_id, yaml_files_dir, report_base_dir):
        """
        初始化测试执行服务
        
        Args:
            result_id (int): RunResult 模型的主键 ID,用于关联数据库记录
            yaml_files_dir (str|Path): YAML 测试文件所在目录的绝对路径
                                       该目录应包含所有需要执行的测试用例文件
            report_base_dir (str|Path): 报告输出的基础目录
                                        会在此目录下创建 results/ 和 report/ 子目录
        
        目录结构:
            report_base_dir/
            ├── test_*.yaml          # 测试用例文件(由外部生成)
            ├── results/             # pytest 执行结果(本类创建)
            │   ├── *.json          # Allure 结果文件
            │   └── *.xml           # JUnit XML 结果
            └── report/              # Allure HTML 报告(本类创建)
                ├── index.html
                └── ...
        
        Raises:
            无 - 初始化过程中的错误会被记录但不会抛出异常
        """
        self.result_id = result_id
        self.yaml_files_dir = Path(yaml_files_dir)
        self.report_base_dir = Path(report_base_dir)
        
        # 创建结果和报告目录
        # results: 存储 pytest 执行的原始结果数据
        # report: 存储 Allure 生成的 HTML 报告
        self.results_dir = self.report_base_dir / "results"
        self.report_dir = self.report_base_dir / "report"
        
        # 确保目录存在,parents=True 会创建所有必要的父目录
        # exist_ok=True 避免目录已存在时抛出异常
        self.results_dir.mkdir(parents=True, exist_ok=True)
        self.report_dir.mkdir(parents=True, exist_ok=True)
        
        # 记录初始化信息,便于追踪和调试
        logger.info(f"=" * 60)
        logger.info(f"初始化测试执行服务")
        logger.info(f"  - Result ID: {result_id}")
        logger.info(f"  - YAML 文件目录: {self.yaml_files_dir}")
        logger.info(f"  - 报告基础目录: {self.report_base_dir}")
        logger.info(f"  - 结果目录: {self.results_dir}")
        logger.info(f"  - 报告目录: {self.report_dir}")
        logger.info(f"=" * 60)
    
    def execute_tests(self):
        """
        执行测试用例的主方法
        
        执行流程:
        1. 更新状态为 Running
        2. 验证测试文件目录
        3. 执行 pytest 测试
        4. 更新测试结果(通过/失败)
        5. 生成 Allure 报告
        6. 更新最终状态(Done/Error)
        
        状态转换:
            Init → Running → Reporting → Done (成功)
                                      ↘ Error (失败)
        
        Returns:
            dict: 执行结果字典,包含以下字段:
                success (bool): 整个执行流程是否成功完成
                is_pass (bool): 测试用例是否全部通过(仅当 success=True 时有效)
                returncode (int): pytest 的返回码
                    0: 所有测试通过
                    1: 有测试失败
                    2: 测试执行被中断
                    3: 内部错误
                    4: pytest 使用错误
                    5: 没有收集到测试
                report_path (str): Allure 报告的目录路径
                status (int): 最终的执行状态(RunStatus 枚举值)
                error (str): 错误信息(仅当 success=False 时存在)
        
        异常处理:
            所有异常都会被捕获并记录,不会向外抛出
            发生异常时会将 RunResult 状态设置为 Error
        """
        from suite.models import RunResult
        
        try:
            # ========== 步骤1: 获取并更新执行状态 ==========
            logger.info(f"[步骤1] 获取 RunResult 对象 (ID: {self.result_id})")
            result = RunResult.objects.get(id=self.result_id)
            
            # 更新状态为 Running,表示测试开始执行
            result.status = result.RunStatus.Running
            result.save()
            logger.info(f"  ✓ 状态已更新为: {result.get_status_display()}")
            
            # ========== 步骤2: 验证测试文件目录 ==========
            logger.info(f"[步骤2] 验证测试文件目录")
            if not self.yaml_files_dir.exists():
                error_msg = f"YAML 文件目录不存在: {self.yaml_files_dir}"
                logger.error(f"  ✗ {error_msg}")
                result.status = result.RunStatus.Error
                result.save()
                return {
                    "success": False,
                    "error": error_msg
                }
            
            # 检查目录中是否有测试文件
            yaml_files = list(self.yaml_files_dir.glob("*.yaml")) + list(self.yaml_files_dir.glob("*.yml"))
            logger.info(f"  ✓ 找到 {len(yaml_files)} 个测试文件")
            if yaml_files:
                for yaml_file in yaml_files[:5]:  # 只显示前5个
                    logger.info(f"    - {yaml_file.name}")
                if len(yaml_files) > 5:
                    logger.info(f"    - ... 还有 {len(yaml_files) - 5} 个文件")
            
            # ========== 步骤3: 构造并执行 pytest 命令 ==========
            logger.info(f"[步骤3] 执行 pytest 测试")

            # 为每次运行设置独立的 extract.yaml,避免并行任务相互污染
            os.environ["APIFRAME_EXTRACT_PATH"] = str(self.report_base_dir / "extract.yaml")
            
            # 确保项目根目录在 sys.path 中,以便 conftest.py 能导入项目模块
            import sys
            project_root = str(settings.BASE_DIR)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
                logger.info(f"  ✓ 已将项目根目录添加到 sys.path: {project_root}")
            
            # 从配置文件读取 pytest 参数,支持灵活配置
            pytest_args = getattr(settings, 'PYTEST_ARGS', ['-v', '--tb=short'])
            
            # 构造完整的命令参数
            test_args = [
                str(self.yaml_files_dir),  # 测试文件目录
                f"--alluredir={self.results_dir}",  # Allure 结果输出目录
            ] + pytest_args  # 添加配置的额外参数
            
            logger.info(f"  pytest 命令参数: {' '.join(test_args)}")
            
            # 执行 pytest.main(),这是同步调用,会阻塞直到测试完成
            import time
            start_time = time.time()
            ret_code = pytest.main(test_args)
            elapsed_time = time.time() - start_time
            
            logger.info(f"  ✓ pytest 执行完成")
            logger.info(f"    - 返回码: {ret_code}")
            logger.info(f"    - 耗时: {elapsed_time:.2f} 秒")
            
            # ========== 步骤4: 根据返回码更新测试结果 ==========
            logger.info(f"[步骤4] 更新测试结果")
            
            # pytest 返回码说明:
            # 0: 所有测试通过
            # 1: 有测试失败
            # 其他: 执行过程中出现问题
            if ret_code == 0:
                result.is_pass = True
                logger.info(f"  ✓ 测试通过")
            else:
                result.is_pass = False
                logger.info(f"  ✗ 测试未通过 (返回码: {ret_code})")
            
            # 更新状态为 Reporting,准备生成报告
            result.status = result.RunStatus.Reporting
            result.save()
            logger.info(f"  ✓ 状态已更新为: {result.get_status_display()}")
            
            # ========== 步骤5: 生成 Allure 报告 ==========
            logger.info(f"[步骤5] 生成 Allure 报告")
            report_success = self._generate_allure_report()
            
            # ========== 步骤6: 更新最终状态 ==========
            logger.info(f"[步骤6] 更新最终状态")
            if report_success:
                result.status = result.RunStatus.Done
                logger.info(f"  ✓ 报告生成成功")
                logger.info(f"  ✓ 最终状态: {result.get_status_display()}")
            else:
                result.status = result.RunStatus.Error
                logger.error(f"  ✗ 报告生成失败")
                logger.error(f"  ✗ 最终状态: {result.get_status_display()}")
            
            result.save()
            
            # ========== 返回执行结果 ==========
            logger.info(f"=" * 60)
            logger.info(f"测试执行完成总结:")
            logger.info(f"  - Result ID: {self.result_id}")
            logger.info(f"  - 执行成功: True")
            logger.info(f"  - 测试通过: {result.is_pass}")
            logger.info(f"  - 返回码: {ret_code}")
            logger.info(f"  - 报告路径: {self.report_dir}")
            logger.info(f"  - 最终状态: {result.get_status_display()}")
            logger.info(f"=" * 60)
            
            return {
                "success": True,
                "is_pass": result.is_pass,
                "returncode": ret_code,
                "report_path": str(self.report_dir),
                "status": result.status
            }
            
        except Exception as e:
            # ========== 异常处理 ==========
            logger.error(f"=" * 60)
            logger.error(f"执行测试时发生异常:")
            logger.error(f"  - Result ID: {self.result_id}")
            logger.error(f"  - 异常类型: {type(e).__name__}")
            logger.error(f"  - 异常信息: {str(e)}")
            logger.error(f"=" * 60, exc_info=True)
            
            # 尝试更新数据库状态为 Error
            try:
                result = RunResult.objects.get(id=self.result_id)
                result.status = result.RunStatus.Error
                result.save()
                logger.info(f"  ✓ 已将状态更新为 Error")
            except Exception as db_error:
                logger.error(f"  ✗ 更新状态失败: {str(db_error)}")
            
            return {
                "success": False,
                "error": str(e)
            }
    
    def _generate_allure_report(self):
        """
        生成 Allure HTML 测试报告(私有方法)
        
        工作流程:
        1. 检查 results 目录中是否有测试结果文件
        2. 调用 allure 命令行工具生成 HTML 报告
        3. 验证报告是否成功生成
        
        依赖:
        - allure 命令行工具必须已安装并在 PATH 中
        - results 目录中必须有 pytest-allure 插件生成的结果文件
        
        Returns:
            bool: 报告是否成功生成
                True: 报告生成成功,index.html 存在
                False: 生成失败或没有结果文件
        
        注意:
        - 此方法不会抛出异常,所有错误都会被捕获并返回 False
        - 超时时间可通过 settings.ALLURE_GENERATION_TIMEOUT 配置
        """
        try:
            logger.info(f"  开始生成 Allure 报告")
            
            # ========== 检查结果文件 ==========
            # Allure 结果文件通常是 .json 格式,JUnit 结果是 .xml 格式
            json_files = list(self.results_dir.glob("*.json"))
            xml_files = list(self.results_dir.glob("*.xml"))
            result_files = json_files + xml_files
            
            logger.info(f"    - JSON 文件: {len(json_files)} 个")
            logger.info(f"    - XML 文件: {len(xml_files)} 个")
            
            if not result_files:
                logger.warning(f"    ✗ 未找到测试结果文件: {self.results_dir}")
                logger.warning(f"    提示: 确保 pytest 使用了 --alluredir 参数")
                return False
            
            logger.info(f"    ✓ 找到 {len(result_files)} 个结果文件")
            
            # ========== 构造 allure 命令 ==========
            # 从配置文件读取 allure 参数,支持灵活配置
            allure_args = getattr(settings, 'ALLURE_ARGS', ['--clean'])
            
            allure_cmd = [
                "allure",           # allure 命令
                "generate",         # 生成报告子命令
                str(self.results_dir),  # 输入: 结果文件目录
                "-o",               # 输出参数
                str(self.report_dir),   # 输出: 报告目录
            ] + allure_args  # 添加配置的额外参数
            
            logger.info(f"    执行命令: {' '.join(allure_cmd)}")
            
            # ========== 执行 allure 命令 ==========
            # 从配置读取超时时间,默认 120 秒
            timeout = getattr(settings, 'ALLURE_GENERATION_TIMEOUT', 120)
            
            import time
            start_time = time.time()
            
            allure_result = subprocess.run(
                allure_cmd,
                capture_output=True,  # 捕获标准输出和错误输出
                text=True,            # 以文本模式处理输出
                timeout=timeout,      # 设置超时时间
                cwd=settings.BASE_DIR  # 工作目录
            )
            
            elapsed_time = time.time() - start_time
            logger.info(f"    ✓ 命令执行完成 (耗时: {elapsed_time:.2f} 秒)")
            
            # ========== 检查执行结果 ==========
            if allure_result.returncode == 0:
                # 验证报告文件是否真的生成了
                report_index = self.report_dir / "index.html"
                if report_index.exists():
                    logger.info(f"    ✓ Allure 报告生成成功")
                    logger.info(f"    ✓ 报告入口: {report_index}")
                    
                    # 输出 allure 的标准输出(通常包含报告统计信息)
                    if allure_result.stdout:
                        logger.debug(f"    Allure 输出: {allure_result.stdout}")
                    
                    return True
                else:
                    logger.error(f"    ✗ 命令执行成功但未找到 index.html")
                    return False
            else:
                # 命令执行失败,记录错误信息
                logger.error(f"    ✗ Allure 报告生成失败")
                logger.error(f"    返回码: {allure_result.returncode}")
                if allure_result.stderr:
                    logger.error(f"    错误输出: {allure_result.stderr}")
                if allure_result.stdout:
                    logger.error(f"    标准输出: {allure_result.stdout}")
                return False
                
        except subprocess.TimeoutExpired:
            # 超时异常
            timeout = getattr(settings, 'ALLURE_GENERATION_TIMEOUT', 120)
            logger.error(f"    ✗ Allure 报告生成超时 (超过 {timeout} 秒)")
            logger.error(f"    提示: 可以在 settings.py 中调整 ALLURE_GENERATION_TIMEOUT")
            return False
            
        except FileNotFoundError:
            # allure 命令未找到
            logger.error(f"    ✗ 未找到 allure 命令")
            logger.error(f"    提示: 请确保 allure 已安装并在 PATH 中")
            logger.error(f"    安装方法: brew install allure (macOS) 或访问 https://docs.qameta.io/allure/")
            return False
            
        except Exception as e:
            # 其他异常
            logger.error(f"    ✗ 生成 Allure 报告时发生异常")
            logger.error(f"    异常类型: {type(e).__name__}")
            logger.error(f"    异常信息: {str(e)}", exc_info=True)
            return False


def run_suite_tests(result_id, yaml_files_dir, report_base_dir):
    """
    执行测试套件的便捷函数
    
    这是一个封装函数,专门用于在多进程/线程环境中调用。
    它会自动处理 Django 环境的初始化,确保在子进程中也能正常工作。
    
    使用场景:
    1. ThreadPoolExecutor 中提交任务
    2. multiprocessing.Pool 中执行
    3. Celery 异步任务
    4. 任何需要独立进程/线程执行测试的场景
    
    Args:
        result_id (int): RunResult 模型的主键 ID
            用于关联数据库中的执行记录,更新状态和结果
        
        yaml_files_dir (str|Path): YAML 测试文件所在目录的绝对路径
            该目录应包含所有需要执行的测试用例文件(.yaml 或 .yml)
            
        report_base_dir (str|Path): 报告输出的基础目录
            测试结果和报告都会输出到这个目录下的子目录中
            - results/: pytest 执行结果
            - report/: Allure HTML 报告
    
    Returns:
        dict: 执行结果字典,包含以下字段:
            success (bool): 整个执行流程是否成功
            is_pass (bool): 测试是否全部通过(仅当 success=True 时有效)
            returncode (int): pytest 返回码
            report_path (str): 报告目录路径
            status (int): 最终执行状态
            error (str): 错误信息(仅当 success=False 时存在)
    
    示例:
        # 在线程池中使用
        from concurrent.futures import ThreadPoolExecutor
        
        pool = ThreadPoolExecutor(max_workers=6)
        future = pool.submit(
            run_suite_tests,
            result_id=123,
            yaml_files_dir='/path/to/yaml',
            report_base_dir='/path/to/report'
        )
        result = future.result()  # 获取执行结果
        
        # 在 Celery 任务中使用
        @app.task
        def execute_test_suite(result_id, yaml_dir, report_dir):
            return run_suite_tests(result_id, yaml_dir, report_dir)
    
    注意:
    - 此函数会自动处理 Django 环境初始化,无需手动调用 django.setup()
    - 在主进程中调用时,Django 环境已存在,不会重复初始化
    - 在子进程中调用时,会自动初始化 Django 环境
    - 函数是线程安全的,可以并发调用
    """
    import django
    import os
    import sys
    
    # ========== Django 环境初始化 ==========
    # 在子进程/线程中,Django 环境可能未初始化
    # 检查环境变量,如果未设置则进行初始化
    if not os.environ.get("DJANGO_SETTINGS_MODULE"):
        logger.info(f"检测到 Django 环境未初始化,开始初始化...")
        
        # 添加项目根目录到 Python 路径
        sys.path.append(str(settings.BASE_DIR))
        
        # 设置 Django 配置模块
        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Tesla.settings")
        
        # 初始化 Django
        django.setup()
        
        logger.info(f"Django 环境初始化完成")
    
    # ========== 创建服务实例并执行测试 ==========
    logger.info(f"开始执行测试套件 (Result ID: {result_id})")
    service = TestExecutionService(result_id, yaml_files_dir, report_base_dir)
    return service.execute_tests()
