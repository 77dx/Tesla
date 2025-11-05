from django.contrib import admin
from .models import Department, Role, Position

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'intro', 'leader']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']

@admin.register(Position)
class PositionmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']