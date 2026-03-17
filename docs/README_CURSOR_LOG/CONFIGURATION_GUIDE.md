# 测试执行配置指南

## 配置文件位置

所有配置都在 `Tesla/settings.py` 文件中。

## 配置项说明

### 1. 基础路径配置

```python
# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 测试用例的路径
TEST_YAML_PATH = BASE_DIR / 'tests/test_case_yaml'
TEST_ALL_CASES = BASE_DIR / 'tests/test_all_cases.py'

# 中间变量的保存路径
EXTRACT_PATH = BASE_DIR / 'tests/extract.yaml'

# 测试报告的路径
REPORT_DIR = BASE_DIR / 'reports'
```

**说明**:
- `BASE_DIR`: 项目根目录,所有相对路径的基准
- `TEST_YAML_PATH`: 单个测试用例文件的存放目录
- `TEST_ALL_CASES`: 测试用例集合文件
- `EXTRACT_PATH`: 测试过程中提取的变量存储文件
- `REPORT_DIR`: 通过 API 接口执行的测试报告目录

### 2. 测试套件执行配置

```python
# 测试套件执行结果存储目录
# 每次执行会在此目录下创建 result_{result_id}_{timestamp}/ 子目录
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'
```

**说明**:
- 每次执行测试套件时,会在此目录下创建独立的子目录
- 子目录命名格式: `result_{result_id}_{timestamp}`
- 确保数据隔离,多个套件并发执行互不干扰

**目录结构示例**:
```
upload_yaml/
├── result_1_1709366400/
│   ├── test_login_1709366400.yaml
│   ├── results/
│   │   ├── xxx.json
│   │   └── xxx.xml
│   └── report/
│       ├── index.html
│       └── ...
└── result_2_1709366401/
    ├── test_register_1709366401.yaml
    ├── results/
    └── report/
```

### 3. 并发执行配置

```python
# 线程池配置 - 控制同时执行的测试套件数量
# 建议值: 4-8, 根据服务器性能调整
MAX_CONCURRENT_SUITES = 6
```

**说明**:
- 控制同时执行的测试套件数量
- 值越大,并发能力越强,但消耗资源也越多
- 建议根据服务器配置调整:
  - 低配置(2核4G): 2-4
  - 中等配置(4核8G): 4-6
  - 高配置(8核16G+): 6-8

**性能影响**:
| 配置值 | CPU 使用率 | 内存使用 | 响应速度 |
|--------|-----------|----------|----------|
| 2 | 低 | 低 | 慢 |
| 4 | 中 | 中 | 中 |
| 6 | 中高 | 中高 | 快 |
| 8 | 高 | 高 | 很快 |

### 4. 超时配置

```python
# pytest 执行超时时间(秒)
# 单个测试套件的最大执行时间,超时会被终止
PYTEST_EXECUTION_TIMEOUT = 300

# Allure 报告生成超时时间(秒)
ALLURE_GENERATION_TIMEOUT = 120
```

**说明**:
- `PYTEST_EXECUTION_TIMEOUT`: pytest 执行的最大时间
  - 默认 300 秒(5分钟)
  - 如果测试用例很多或执行很慢,可以适当增加
  - 建议值: 300-600 秒
  
- `ALLURE_GENERATION_TIMEOUT`: Allure 报告生成的最大时间
  - 默认 120 秒(2分钟)
  - 通常不需要修改
  - 建议值: 60-180 秒

**超时后的行为**:
- pytest 超时: 进程被终止,状态标记为 Error
- Allure 超时: 报告生成失败,但测试结果仍然保存

### 5. pytest 命令行参数

```python
# pytest 命令行参数
# 可以添加更多参数,如 '--maxfail=1', '--reruns=2' 等
PYTEST_ARGS = [
    '-v',           # 详细输出
    '--tb=short',   # 简洁的 traceback
]
```

**说明**:
- 自定义 pytest 的执行参数
- 常用参数:
  - `-v` / `-vv`: 详细输出
  - `--tb=short`: 简短的错误信息
  - `--tb=long`: 详细的错误信息
  - `--maxfail=N`: 失败 N 个后停止
  - `--reruns=N`: 失败后重试 N 次
  - `-x`: 第一个失败后停止
  - `-k EXPRESSION`: 只运行匹配的测试

**示例配置**:
```python
# 失败后重试2次
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '--reruns=2',
    '--reruns-delay=1',
]

# 第一个失败后停止
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '-x',
]

# 只运行特定标记的测试
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '-m', 'smoke',  # 只运行标记为 smoke 的测试
]
```

### 6. Allure 命令行参数

```python
# Allure 命令行参数
ALLURE_ARGS = [
    '--clean',      # 清理旧报告
]
```

**说明**:
- 自定义 Allure 报告生成的参数
- 常用参数:
  - `--clean`: 清理旧报告(推荐)
  - `--single-file`: 生成单文件报告

**示例配置**:
```python
# 生成单文件报告(便于分享)
ALLURE_ARGS = [
    '--clean',
    '--single-file',
]
```

## 完整配置示例

### 开发环境配置

```python
# ==================== 测试套件执行配置 ====================

# 测试套件执行结果存储目录
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'

# 线程池配置 - 开发环境使用较小的值
MAX_CONCURRENT_SUITES = 2

# 超时配置 - 开发环境使用较短的超时时间
PYTEST_EXECUTION_TIMEOUT = 180  # 3分钟
ALLURE_GENERATION_TIMEOUT = 60   # 1分钟

# pytest 参数 - 开发环境使用详细输出
PYTEST_ARGS = [
    '-vv',          # 非常详细的输出
    '--tb=long',    # 详细的 traceback
    '-x',           # 第一个失败后停止
]

# Allure 参数
ALLURE_ARGS = [
    '--clean',
]
```

### 生产环境配置

```python
# ==================== 测试套件执行配置 ====================

# 测试套件执行结果存储目录
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'

# 线程池配置 - 生产环境使用较大的值
MAX_CONCURRENT_SUITES = 6

# 超时配置 - 生产环境使用较长的超时时间
PYTEST_EXECUTION_TIMEOUT = 600   # 10分钟
ALLURE_GENERATION_TIMEOUT = 180  # 3分钟

# pytest 参数 - 生产环境使用简洁输出
PYTEST_ARGS = [
    '-v',           # 详细输出
    '--tb=short',   # 简洁的 traceback
    '--reruns=2',   # 失败后重试2次
]

# Allure 参数
ALLURE_ARGS = [
    '--clean',
]
```

### 高性能环境配置

```python
# ==================== 测试套件执行配置 ====================

# 测试套件执行结果存储目录
SUITE_EXECUTION_BASE_DIR = BASE_DIR / 'upload_yaml'

# 线程池配置 - 高性能环境使用最大值
MAX_CONCURRENT_SUITES = 8

# 超时配置
PYTEST_EXECUTION_TIMEOUT = 300
ALLURE_GENERATION_TIMEOUT = 120

# pytest 参数 - 使用并行执行
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '-n', 'auto',   # 使用 pytest-xdist 并行执行
]

# Allure 参数
ALLURE_ARGS = [
    '--clean',
]
```

## 环境变量配置

也可以通过环境变量覆盖配置:

```bash
# 设置环境变量
export MAX_CONCURRENT_SUITES=8
export PYTEST_EXECUTION_TIMEOUT=600
```

在 `settings.py` 中读取:

```python
import os

# 从环境变量读取,如果没有则使用默认值
MAX_CONCURRENT_SUITES = int(os.environ.get('MAX_CONCURRENT_SUITES', 6))
PYTEST_EXECUTION_TIMEOUT = int(os.environ.get('PYTEST_EXECUTION_TIMEOUT', 300))
```

## 配置验证

创建一个验证脚本 `check_config.py`:

```python
from Tesla import settings
from pathlib import Path

print("=" * 60)
print("测试执行配置验证")
print("=" * 60)

# 检查目录配置
print(f"\n基础目录: {settings.BASE_DIR}")
print(f"  存在: {settings.BASE_DIR.exists()}")

print(f"\n执行结果目录: {settings.SUITE_EXECUTION_BASE_DIR}")
print(f"  存在: {settings.SUITE_EXECUTION_BASE_DIR.exists()}")

# 检查并发配置
print(f"\n最大并发数: {settings.MAX_CONCURRENT_SUITES}")

# 检查超时配置
print(f"\npytest 超时: {settings.PYTEST_EXECUTION_TIMEOUT} 秒")
print(f"Allure 超时: {settings.ALLURE_GENERATION_TIMEOUT} 秒")

# 检查参数配置
print(f"\npytest 参数: {' '.join(settings.PYTEST_ARGS)}")
print(f"Allure 参数: {' '.join(settings.ALLURE_ARGS)}")

print("\n" + "=" * 60)
```

运行验证:

```bash
python check_config.py
```

## 常见问题

### Q1: 如何增加并发数?

A: 修改 `MAX_CONCURRENT_SUITES` 的值:

```python
MAX_CONCURRENT_SUITES = 8  # 从 6 改为 8
```

### Q2: 测试经常超时怎么办?

A: 增加超时时间:

```python
PYTEST_EXECUTION_TIMEOUT = 600  # 从 300 改为 600
```

### Q3: 如何让失败的测试自动重试?

A: 添加 pytest-rerunfailures 参数:

```python
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '--reruns=2',        # 重试2次
    '--reruns-delay=1',  # 重试间隔1秒
]
```

### Q4: 如何更改报告存储位置?

A: 修改 `SUITE_EXECUTION_BASE_DIR`:

```python
SUITE_EXECUTION_BASE_DIR = Path('/data/test_reports')
```

### Q5: 如何使用并行执行加速测试?

A: 安装 pytest-xdist 并配置:

```bash
pip install pytest-xdist
```

```python
PYTEST_ARGS = [
    '-v',
    '--tb=short',
    '-n', 'auto',  # 自动使用所有CPU核心
    # 或指定核心数: '-n', '4'
]
```

## 性能调优建议

1. **根据服务器配置调整并发数**
   - CPU 核心数 × 1.5 是一个不错的起点
   - 监控 CPU 和内存使用率,适当调整

2. **合理设置超时时间**
   - 不要设置太短,避免正常测试被误杀
   - 不要设置太长,避免卡住的测试占用资源

3. **使用并行执行**
   - 对于独立的测试用例,使用 pytest-xdist 并行执行
   - 注意处理共享资源的冲突

4. **定期清理旧报告**
   - 使用定时任务清理过期的报告文件
   - 节省磁盘空间

## 更新日志

- **2026-03-02**: 初始版本,添加所有配置项说明
