from django.urls import path, include
from rest_framework.routers import APIRootView
from rest_framework_extensions.routers import ExtendedDefaultRouter

from loffle.views import TicketViewSet, ProductViewSet, RaffleViewSet, ApplyUserViewSet, RaffleCandidateViewSet


class LoffleAPI(APIRootView):
    """
    로플의 로플 API
    """
    pass


router = ExtendedDefaultRouter(trailing_slash=False)
router.APIRootView = LoffleAPI

router.register('tickets', TicketViewSet, basename='ticket')
router.register('products', ProductViewSet, basename='product')

raffle = router.register('raffles', RaffleViewSet, basename='raffle')
raffle.register('users',
                ApplyUserViewSet,
                basename='apply-user',
                parents_query_lookups=('raffle',))
raffle.register('candidates',
                RaffleCandidateViewSet,
                basename='candidate',
                parents_query_lookups=('raffle',))

urlpatterns = [
    path('', include(router.urls)),
]
