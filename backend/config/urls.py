from django.contrib import admin
from django.http import HttpResponseForbidden
from django.urls import include, path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny

def forbidden(_):
    return HttpResponseForbidden("Изменение логина/пароля запрещено. Обратитесь к администратору.")

schema_view = get_schema_view(
    openapi.Info(title="Silant API", default_version="v1"),
    public=True, permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Блокируем отдельные пути allauth
    path("accounts/password/change/", forbidden, name="account_change_password"),
    path("accounts/password/set/", forbidden, name="account_set_password"),
    path("accounts/password/reset/", forbidden, name="account_reset_password"),
    path("accounts/", include("allauth.urls")),

    path("", include("silant.urls")),

    # Swagger/Redoc
    re_path(r"^swagger(?P<format>\.json|\.yaml)$", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
