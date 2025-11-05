"""
@ Title:
@ Author: Cathy
@ Time: 2024/12/16 11:31
"""
from django.urls import path
from rest_framework.routers import DefaultRouter

from snippet import views

# 第二版 ViewSet版
router = DefaultRouter()
router.register('snippets', views.SnippetViewSet, basename='snippet')
urlpatterns = [
    path('snippets/get_by_id/', views.SnippetViewSet.as_view({'post': 'get_by_id'})),
    # path('snippets/update_title/', views.SnippetViewSet.as_view({'post': 'update_title'})),
]
urlpatterns += router.urls



# 第一版ApiView版
# urlpatterns = [
#     path('snippets/', views.snippet_list),
#     path('snippets/snippet_create/', views.snippet_create),
#     path('snippets/snippet_update/', views.snippet_update),
#     path('snippets/snippet_delete/', views.snippet_delete),
# ]

# urlpatterns = [
#     path('snippets/', views.Snippetlist.as_view()),
#     path('snippets/<int:pk>/', views.SnippetDetail.as_view())
# ]

# urlpatterns = [
#     path('snippets/', views.snippet_list),
#     path('snippets/<int:pk>/', views.snippet_detail),
#     path('snippets/get_snippet/', views.get_snippet),
#     path('snippets/update_snippet/', views.update_snippet),
#     path('snippets/create_snippet/', views.create_snippet),
# ]






# from django.urls import path, include
# from rest_framework import routers
# from .views import SnippetViewSet, FeedBackAllViewSet
#
#
# router = routers.DefaultRouter()
# router.register('snippet', SnippetViewSet, basename='snippet')
# router.register('myfeedback', FeedBackAllViewSet, basename='myfeedback')
#
# urlpatterns = router.urls

