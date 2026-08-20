import hashlib
import secrets

from django.utils import timezone

from .models import DailyVisitor


VISITOR_COOKIE = 'site_visitor'


class DailyVisitorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        visitor_cookie = request.COOKIES.get(VISITOR_COOKIE) or secrets.token_urlsafe(32)
        response = self.get_response(request)

        if self._should_count(request, response):
            visitor_id = hashlib.sha256(visitor_cookie.encode('utf-8')).hexdigest()
            DailyVisitor.objects.get_or_create(
                day=timezone.localdate(),
                visitor_id=visitor_id,
            )

        if VISITOR_COOKIE not in request.COOKIES:
            response.set_cookie(
                VISITOR_COOKIE,
                visitor_cookie,
                max_age=60 * 60 * 24 * 365,
                httponly=True,
                samesite='Lax',
                secure=request.is_secure(),
            )
        return response

    @staticmethod
    def _should_count(request, response):
        return (
            request.method in {'GET', 'HEAD'}
            and not request.path.startswith(('/admin/', '/static/', '/media/'))
            and response.status_code < 400
            and response.headers.get('Content-Type', '').startswith('text/html')
        )