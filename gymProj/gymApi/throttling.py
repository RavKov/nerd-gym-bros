from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """Limit anonymous login attempts per client IP."""

    scope = "login"

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            return None
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class RegisterRateThrottle(SimpleRateThrottle):
    """Limit account registration attempts per client IP."""

    scope = "register"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}


class TokenRefreshRateThrottle(SimpleRateThrottle):
    """Limit refresh token rotation per client IP."""

    scope = "token_refresh"

    def get_cache_key(self, request, view):
        return self.cache_format % {"scope": self.scope, "ident": self.get_ident(request)}
