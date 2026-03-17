from django.core.management.base import BaseCommand
from system.models import Permission

# 预置权限码定义
# 格式: (code, name, module)
PERMISSIONS = [
    # 项目管理
    ('project:list',        '查看项目列表',   'project'),
    ('project:detail',      '查看项目详情',   'project'),
    ('project:create',      '新建项目',       'project'),
    ('project:update',      '修改项目',       'project'),
    ('project:delete',      '删除项目',       'project'),
    # 接口管理
    ('endpoint:list',       '查看接口列表',   'endpoint'),
    ('endpoint:detail',     '查看接口详情',   'endpoint'),
    ('endpoint:create',     '新建接口',       'endpoint'),
    ('endpoint:update',     '修改接口',       'endpoint'),
    ('endpoint:delete',     '删除接口',       'endpoint'),
    # 用例管理
    ('case:list',           '查看用例列表',   'case'),
    ('case:detail',         '查看用例详情',   'case'),
    ('case:create',         '新建用例',       'case'),
    ('case:update',         '修改用例',       'case'),
    ('case:delete',         '删除用例',       'case'),
    # 套件管理
    ('suite:list',          '查看套件列表',   'suite'),
    ('suite:detail',        '查看套件详情',   'suite'),
    ('suite:create',        '新建套件',       'suite'),
    ('suite:update',        '修改套件',       'suite'),
    ('suite:delete',        '删除套件',       'suite'),
    ('suite:run',           '执行套件',       'suite'),
    # 执行结果
    ('result:list',         '查看结果列表',   'result'),
    ('result:detail',       '查看结果详情',   'result'),
    ('result:delete',       '删除结果',       'result'),
    # 环境管理
    ('environment:list',    '查看环境列表',   'environment'),
    ('environment:create',  '新建环境',       'environment'),
    ('environment:update',  '修改环境',       'environment'),
    ('environment:delete',  '删除环境',       'environment'),
    # 用户管理
    ('user:list',           '查看用户列表',   'user'),
    ('user:update',         '修改用户信息',   'user'),
    # 系统管理
    ('system:manage',       '系统配置管理',   'system'),
    # 产品线管理
    ('product_line:list',   '查看产品线列表', 'product_line'),
    ('product_line:create', '新建产品线',     'product_line'),
    ('product_line:update', '修改产品线',     'product_line'),
    ('product_line:delete', '删除产品线',     'product_line'),
    ('product_line:manage_members', '管理产品线成员', 'product_line'),
]


class Command(BaseCommand):
    help = '初始化/同步预置权限码到数据库'

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0
        for code, name, module in PERMISSIONS:
            obj, created = Permission.objects.update_or_create(
                code=code,
                defaults={'name': name, 'module': module}
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        self.stdout.write(
            self.style.SUCCESS(
                f'权限初始化完成：新增 {created_count} 条，更新 {updated_count} 条，共 {len(PERMISSIONS)} 条。'
            )
        )
