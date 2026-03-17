import os, sys, django, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()
from case_api.models import Case
c = Case.objects.get(id=13)
print('当前:', json.dumps(c.api_args, ensure_ascii=False))
# 回滚：把嵌套的 data.data 展开
old = c.api_args
if 'data' in old and isinstance(old['data'], dict) and 'data' in old['data']:
    c.api_args = {'data': old['data']['data'], 'headers': old.get('headers', {})}
    c.save()
    print('回滚后:', json.dumps(c.api_args, ensure_ascii=False))
else:
    print('无需回滚，格式正确')
