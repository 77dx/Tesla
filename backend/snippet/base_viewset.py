"""
通用 ViewSet 基类

所有业务 ViewSet 继承此基类后，自动获得：
1. created_by / updated_by 自动写入
2. product_line 过滤（通过 ?product_line=1 参数）
3. search 搜索（通过 ?search=xxx 参数，子类配置 search_fields）
4. 批量删除（POST /{prefix}/delete/ body: {ids: [1,2,3]}）

用法：
    class MyViewSet(BaseViewSet):
        queryset = MyModel.objects.all().order_by('-id')
        serializer_class = MySerializer
        search_fields = ['name', 'description']       # 字符串搜索字段
        product_line_field = 'project__product_line_id'  # 产品线过滤路径（默认）
"""
from typing import Optional
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


class BaseViewSet(viewsets.ModelViewSet):
    """
    通用 ViewSet 基类。

    子类可覆盖的属性：
        search_fields (list[str]):
            字符串模糊搜索的字段列表，如 ['name', 'description']。
            若列表中有字段名为 'id'，当 search 为纯数字时会精确匹配 id。
            默认：['name']

        product_line_field (str | None):
            产品线过滤 ORM 路径。
            - 直属项目的资源（如 Endpoint）：'project__product_line_id'
            - 直属产品线的资源（如 Project）：'product_line_id'
            - 不需要产品线过滤：设为 None
            默认：'project__product_line_id'

        extra_filters (dict):
            额外的固定过滤条件（传给 filter()）。
            默认：{}
    """

    search_fields: list = ['name']
    product_line_field: Optional[str] = 'project__product_line_id'
    extra_filters: dict = {}

    # ------------------------------------------------------------------ #
    #  自动写入审计字段                                                     #
    # ------------------------------------------------------------------ #

    def _get_user_or_none(self):
        user = self.request.user
        return user if user and user.is_authenticated else None

    def perform_create(self, serializer):
        user = self._get_user_or_none()
        kwargs = {}
        model_fields = {f.name for f in serializer.Meta.model._meta.get_fields()}
        if 'created_by' in model_fields:
            kwargs['created_by'] = user
        if 'updated_by' in model_fields:
            kwargs['updated_by'] = user
        serializer.save(**kwargs)

    def perform_update(self, serializer):
        user = self._get_user_or_none()
        kwargs = {}
        model_fields = {f.name for f in serializer.Meta.model._meta.get_fields()}
        if 'updated_by' in model_fields:
            kwargs['updated_by'] = user
        serializer.save(**kwargs)

    # ------------------------------------------------------------------ #
    #  通用查询过滤                                                         #
    # ------------------------------------------------------------------ #

    def get_queryset(self):
        qs = super().get_queryset()

        # 1. 额外固定过滤
        if self.extra_filters:
            qs = qs.filter(**self.extra_filters)

        # 2. 产品线过滤
        if self.product_line_field:
            pl_id = self.request.query_params.get('product_line')
            if pl_id:
                qs = qs.filter(**{self.product_line_field: pl_id})

        # 3. 搜索
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = self._apply_search(qs, search)

        return qs

    def _apply_search(self, qs, search: str):
        """按 search_fields 做模糊搜索；若字段名为 'id' 且 search 为纯数字则精确匹配。"""
        from django.db.models import Q
        q = Q()
        for field in self.search_fields:
            if field == 'id' and search.isdigit():
                q |= Q(id=int(search))
            else:
                q |= Q(**{f'{field}__icontains': search})
        return qs.filter(q)

    # ------------------------------------------------------------------ #
    #  批量删除                                                             #
    # ------------------------------------------------------------------ #

    @action(detail=False, methods=['post'], url_path='delete')
    def batch_delete(self, request):
        """
        POST /{prefix}/delete/
        Body: {"ids": [1, 2, 3]}
        """
        ids = request.data.get('ids', [])
        if not ids or not isinstance(ids, list):
            return Response({'detail': 'ids 字段必须为非空列表'}, status=status.HTTP_400_BAD_REQUEST)
        deleted_count, _ = self.get_queryset().filter(id__in=ids).delete()
        return Response({'deleted': deleted_count})
