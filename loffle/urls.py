from django.urls import path, include
from rest_framework.routers import APIRootView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from loffle.views import TicketViewSet


class LoffleAPI(APIRootView):
    """
    로플의 로플 API
    """
    pass


router = ExtendedDefaultRouter(trailing_slash=False)
router.APIRootView = LoffleAPI

router.register('ticket', TicketViewSet, basename='ticket')

urlpatterns = [
    path('/', include(router.urls)),
]
