import contextlib

from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.utils import timezone

from core.settings.base import RATE_LIMIT_ENABLED


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        import zoneinfo

        with contextlib.suppress(AttributeError):
            timezone.activate(zoneinfo.ZoneInfo(request.user.timezone))
        return self.get_response(request)


class AccountSetupMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_staff:
            return self.get_response(request)
        if user.is_authenticated and not user.account_setup:
            if (
                not request.path.startswith("/v4/auth")
                and not request.path.startswith(f"/v4/users/{user.username}/setup")
                and not request.path.startswith("/v4/crons")
                and not request.path.startswith("/v4/users/me")
                and not request.path.startswith("/v4/users/")
                and not request.path.startswith("/v4/invites")
            ):
                return HttpResponseForbidden("Account not setup")

        return self.get_response(request)


class LastOnlineMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            user.last_online = timezone.now()
            user.save()

        return self.get_response(request)


class RateLimitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.limit = 50
        self.window = 3600

    def __call__(self, request):
        if RATE_LIMIT_ENABLED:
            cache_key = f'ratelimit:{request.META["REMOTE_ADDR"]}:{request.path}'

            request_count = cache.get(cache_key, 0)

            if request_count >= self.limit:
                return HttpResponseForbidden("Rate limit exceeded")

            cache.set(cache_key, request_count + 1, self.window)

        response = self.get_response(request)
        return response
