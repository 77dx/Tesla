"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/16 11:31
"""
from django.urls import path, include
from rest_framework import routers
from .views import SnippetViewSet, FeedBackAllViewSet


router = routers.DefaultRouter()
router.register('snippet', SnippetViewSet, basename='snippet')
router.register('myfeedback', FeedBackAllViewSet, basename='myfeedback')

urlpatterns = router.urls

