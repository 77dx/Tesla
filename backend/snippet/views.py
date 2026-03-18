"""
snippet/views.py

此模块为学习练习代码，保留最简实现供参考。
业务逻辑请参考各 app 的 views.py。
"""
from rest_framework import viewsets
from .models import Snippet
from .serializers import SnippetSerializer


class SnippetViewSet(viewsets.ModelViewSet):
    """Snippet 练习 ViewSet（仅供学习参考）"""
    queryset = Snippet.objects.all().order_by('-id')
    serializer_class = SnippetSerializer
