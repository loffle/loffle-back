from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

from _config import settings


class CommunityPagination(PageNumberPagination):
    page_size = 5 # settings.REST_FRAMEWORK['PAGE_SIZE']
    page_size_query_param = 'page_size'
    # ordering = '-created_at'
