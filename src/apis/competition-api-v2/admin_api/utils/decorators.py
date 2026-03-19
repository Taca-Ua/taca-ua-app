"""
Authorization decorators and mixins for views protected by Keycloak JWT.

These helpers are a **second layer** that sit on top of ``KeycloakJWTMiddleware``.
The middleware validates the token and populates ``request.user_id`` /
``request.roles``; these decorators enforce the presence and content of those
attributes at the view level.

Usage
-----

Function-based views::

    from admin_api.decorators import require_auth, require_roles

    @api_view(["GET"])
    @require_auth
    def profile(request):
        return Response({"user_id": request.user_id, "roles": request.roles})


    @api_view(["DELETE"])
    @require_roles("admin-geral")
    def delete_resource(request, pk):
        ...


Class-based views (mixin)::

    from admin_api.decorators import RoleRequiredMixin

    class AdminOnlyView(RoleRequiredMixin, APIView):
        required_roles = ["admin-geral"]

        def get(self, request):
            ...

"""

from functools import wraps

from django.http import JsonResponse

# ---------------------------------------------------------------------------
# Function-based view decorators
# ---------------------------------------------------------------------------


def require_auth(view_func):
    """
    Require a valid, authenticated JWT.

    Returns ``401`` if ``request.user_id`` is not set (i.e. no valid Bearer
    token was provided).  Must be combined with ``KeycloakJWTMiddleware``;
    the middleware handles token *validation*, this decorator handles *enforcement*.
    """

    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not getattr(request, "user_id", None):
            return JsonResponse({"error": "Authentication required"}, status=401)
        return view_func(request, *args, **kwargs)

    return wrapper


def require_roles(*required_roles: str):
    """
    Require the authenticated user to possess **all** of the given realm roles.

    Returns:
    * ``401`` – no valid JWT (user not authenticated at all).
    * ``403`` – JWT valid but the user is missing one or more required roles.

    Example::

        @api_view(["POST"])
        @require_roles("general_admin")
        def create_tournament(request): ...

        @api_view(["DELETE"])
        @require_roles("general_admin", "nucleo_admin")  # must have BOTH
        def delete_resource(request, pk): ...

    """

    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not getattr(request, "user_id", None):
                return JsonResponse({"error": "Authentication required"}, status=401)

            user_roles: set[str] = set(getattr(request, "roles", []))
            missing: set[str] = set(required_roles) - user_roles

            if missing:
                return JsonResponse(
                    {
                        "error": "Insufficient permissions",
                        "required_roles": sorted(required_roles),
                        "missing_roles": sorted(missing),
                    },
                    status=403,
                )

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


# ---------------------------------------------------------------------------
# Class-based view mixin
# ---------------------------------------------------------------------------


class RoleRequiredMixin:
    """
    Mixin for ``APIView`` subclasses that enforces realm-role membership.

    Set ``required_roles`` on the subclass::

        class AdminDashboard(RoleRequiredMixin, APIView):
            required_roles = ["general_admin"]  # or ["nucleo_admin"]

            def get(self, request):
                ...

    Returns ``401`` if unauthenticated, ``403`` if roles are insufficient.
    """

    required_roles: list[str] = []

    def dispatch(self, request, *args, **kwargs):
        if not getattr(request, "user_id", None):
            return JsonResponse({"error": "Authentication required"}, status=401)

        user_roles: set[str] = set(getattr(request, "roles", []))
        missing: set[str] = set(self.required_roles) - user_roles

        if missing:
            return JsonResponse(
                {
                    "error": "Insufficient permissions",
                    "required_roles": sorted(self.required_roles),
                    "missing_roles": sorted(missing),
                },
                status=403,
            )

        return super().dispatch(request, *args, **kwargs)
