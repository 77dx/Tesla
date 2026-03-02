import time
from concurrent.futures.thread import ThreadPoolExecutor
from pathlib import Path
from django.db import models
from django_q.humanhash import uuid
from django_q.models import Schedule
from django_q.tasks import schedule
from project.models import Project
from case_api.models import Case as CaseAPI
from case_ui.models import Case as CaseUI
from suite.task import run_pytest

class Suite(models.Model):
    """ 测试套件 """
    objects: models.QuerySet

    # 这个是老师的写法
    class RunType(models.TextChoices):
        ONCE = 'O', '单次执行'
        CRON = 'C', '计划任务'
        WebHook = 'W', 'webhook'

    # 以下是Django风格写法
    # CHOICES= [
    #     ('0', '单次执行'),
    #     ('C', '计划任务'),
    #     ('W', 'webhook'),

    name = models.CharField("套件名称", max_length=32)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    description = models.CharField('套件描述', max_length=250, blank=True)

    case_api_list = models.ManyToManyField(CaseAPI, blank=True)
    case_ui_list = models.ManyToManyField(CaseUI, blank=True)

    run_type = models.CharField("运行类型", choices=RunType.choices, default=RunType.ONCE, max_length=30)
    # run_type = models.CharField("运行类型", choices=CHOICES, default='0', max_length=30)
    cron = models.CharField("cron表达式", max_length=30, blank=True)
    hook_key = models.CharField("webhook密钥", max_length=255, blank=True)
    schedule = models.ForeignKey(Schedule, null=True, on_delete=models.SET_NULL)

    # 重新梳理：此处应该是根据suite_id进行筛选然后统计总数
    def case_api_count(self):
        """ API用例数量 """
        return self.case_api_list.all().count()

    def case_ui_count(self):
        """ UI用例数量 """
        return self.case_ui_list.all().count()

    def save(self, *args, **kwargs):
        if self.run_type == self.RunType.CRON:
            self.schedule = schedule('suite.task.run_by_cron', self.id, cron=self.cron, schedule_type="C")
        else:
            if self.schedule:
                self.schedule.delete()
                self.schedule = None

        if self.run_type == self.RunType.WebHook:
            if not self.hook_key:
                self.hook_key = uuid()[0]
        return super().save(*args, **kwargs)

    def run(self):
        """ 
        执行测试套件
        
        这是测试套件执行的入口方法,负责协调整个执行流程。
        
        执行流程:
        1. 创建 RunResult 记录和独立的执行目录(保证数据隔离)
        2. 生成 YAML 和 Excel 测试用例文件到独立目录
        3. 使用线程池异步执行测试(支持多套件并发)
        4. 测试结果和报告都保存在各自的独立目录中
        
        数据隔离机制:
        - 每次执行创建唯一目录: {base_dir}/result_{result_id}_{timestamp}/
        - 目录名包含 result_id(数据库主键)和 timestamp(Unix时间戳)
        - 确保多个套件并发执行时,数据完全隔离,互不干扰
        
        并发执行:
        - 使用 ThreadPoolExecutor 实现异步执行
        - 默认最多同时执行 6 个套件(可在 settings.py 中配置)
        - 主线程立即返回,不阻塞后续操作
        - 适合 Web 接口调用,提供良好的响应速度
        
        Returns:
            RunResult: 执行结果对象,包含以下重要字段:
                - id: 执行记录的唯一标识
                - path: 测试文件和报告的存储路径
                - status: 执行状态(Init/Running/Reporting/Done/Error)
                - is_pass: 测试是否通过(仅在执行完成后有效)
                - suite: 关联的测试套件
                - project: 关联的项目
        
        示例:
            # 执行测试套件
            suite = Suite.objects.get(id=1)
            result = suite.run()
            
            # 立即返回,可以查询初始状态
            print(f"执行ID: {result.id}")
            print(f"状态: {result.get_status_display()}")  # 初始化
            
            # 等待一段时间后查询最终结果
            import time
            time.sleep(10)
            result.refresh_from_db()
            print(f"最终状态: {result.get_status_display()}")  # Done/Error
            print(f"是否通过: {result.is_pass}")
        
        注意:
        - 此方法是异步的,立即返回 RunResult 对象
        - 实际的测试执行在后台线程中进行
        - 需要通过 result.refresh_from_db() 获取最新状态
        - 如果没有生成任何测试用例,会直接标记为 Error 状态
        """
        from Tesla import settings
        
        # ========== 步骤1: 创建执行结果记录 ==========
        # 先创建数据库记录,获取唯一的 result_id
        result: RunResult = RunResult.objects.create(
            suite = self,
            project = self.project,
            path = "todo"  # 临时值,稍后会更新为实际路径
        )
        
        # ========== 步骤2: 创建独立的执行目录 ==========
        # 从配置读取基础目录,默认为 'upload_yaml'
        base_dir = getattr(settings, 'SUITE_EXECUTION_BASE_DIR', Path('upload_yaml'))
        
        # 生成唯一的目录名: result_{result_id}_{timestamp}
        # - result_id: 数据库主键,确保不同执行记录的目录不同
        # - timestamp: Unix时间戳,确保同一记录多次执行的目录不同
        dir_name = f"result_{result.id}_{int(time.time())}"
        path = Path(base_dir) / dir_name
        
        # 创建目录,parents=True 会创建所有必要的父目录
        path.mkdir(parents=True, exist_ok=True)

        # 更新数据库记录中的路径
        result.path = str(path)
        result.save()

        # ========== 步骤3: 生成测试用例文件 ==========
        # 标记是否成功生成了至少一个测试用例
        test_cases_generated = False
        
        # 生成 API 测试用例(YAML 格式)
        case_api: CaseAPI
        for case_api in self.case_api_list.all():
            yaml_file = case_api.to_yaml(path)
            if yaml_file:
                test_cases_generated = True

        # 生成 UI 测试用例(Excel 格式)
        case_ui: CaseUI
        for case_ui in self.case_ui_list.all():
            case_ui.to_xlsx(path)

        # ========== 步骤4: 提交到线程池执行 ==========
        if test_cases_generated:
            # 从配置读取线程池大小,默认为 6
            max_workers = getattr(settings, 'MAX_CONCURRENT_SUITES', 6)
            
            # 创建线程池
            # 注意: 这里每次都创建新的线程池,也可以考虑使用全局线程池
            pool = ThreadPoolExecutor(max_workers=max_workers)
            
            # 提交任务到线程池
            # run_pytest 函数会在后台线程中执行,不阻塞当前线程
            # 参数说明:
            #   - str(path): 测试文件所在目录
            #   - result.id: RunResult 的 ID,用于更新状态
            #   - self.case_api_count(): API 用例数量(用于兼容性)
            pool.submit(run_pytest, str(path), result.id, self.case_api_count())
            
            # 注意: 这里没有调用 pool.shutdown(),线程池会在任务完成后自动清理
            # 如果需要等待任务完成,可以使用: pool.shutdown(wait=True)
        else:
            # 如果没有生成任何测试用例,直接标记为错误
            # 这通常表示配置有问题或者套件中没有用例
            result.status = result.RunStatus.Error
            result.save()
            
        # ========== 返回执行结果对象 ==========
        # 注意: 此时测试可能还在执行中,status 可能是 Init 或 Running
        # 需要通过 result.refresh_from_db() 获取最新状态
        return result

class RunResult(models.Model):
    """ 执行结果 """
    objects: models.QuerySet

    class RunStatus(models.IntegerChoices):
        Init = 0, "初始化"
        Ready = 1, "准备开始"
        Running = 2, "正在执行"
        Reporting = 3, "正在生成报告"
        Done = 4, "执行完毕"
        Error = -1, "执行出错"

    suite = models.ForeignKey(Suite, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    path = models.CharField("用例路径", max_length=255)
    is_pass = models.BooleanField("测试通过", default=False)

    status = models.IntegerField("执行状态", choices=RunStatus.choices, default=RunStatus.Init)
