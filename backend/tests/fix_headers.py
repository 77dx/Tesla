import os, sys, django, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Tesla.settings')
django.setup()
from case_api.models import Endpoint
# 修复接口级 headers 里的 'Cookies' key -> 'cookie'
eps = Endpoint.objects.filter(headers__isnull=False)
fixed = 0
for ep in eps:
    h = ep.headers
    if h and 'Cookies' in h:
        h['cookie'] = h.pop('Cookies')
        ep.headers = h
        ep.save(update_fields=['headers'])
        fixed += 1
        print(f'修复接口 #{ep.id} [{ep.name}]: Cookies -> cookie')
print(f'共修复 {fixed} 条')
