from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from gymApi.throttling import LoginRateThrottle, TokenRefreshRateThrottle


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [TokenRefreshRateThrottle]
