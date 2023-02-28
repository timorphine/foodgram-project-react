from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import CustomUserViewSet, FollowReadView, FollowViewSet

router = DefaultRouter()

router.register('users', CustomUserViewSet, basename='users')
# router.register(
#     r'users/subscriptions',
#     FollowReadView,
#     basename='subscriptions'
# )

urlpatterns = [
    path('', include(router.urls)),
    path('users/<user_id>/subscribe/', FollowViewSet.as_view(),
         name='subscribe'),
    path('users/subscriptions/', FollowReadView.as_view(),
         name='subscriptions'),
]
