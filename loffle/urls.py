from django.urls import path, include
from rest_framework.routers import APIRootView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from loffle.views import TicketViewSet, ProductViewSet


class LoffleAPI(APIRootView):
    """
    로플의 로플 API
    """
    pass


router = ExtendedDefaultRouter(trailing_slash=False)
router.APIRootView = LoffleAPI

router.register('tickets', TicketViewSet, basename='tickets')
router.register('products', ProductViewSet, basename='products')

urlpatterns = [
    path('/', include(router.urls)),
]
