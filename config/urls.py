from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from ucsb.repository.user_repository import getAllUsers, edit_user, register_user
from ucsb.repository.asset_repository import add_asset, update_asset, delete_asset, get_all_assets, get_single_asset
from ucsb.repository.asset_data_repository import add_asset_data, delete_asset_data, get_asset_data

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "about/", TemplateView.as_view(template_name="pages/about.html"), name="about"
    ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("agmonitor.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# API URLS
urlpatterns += [
    # API base url
    path("api/", include("config.api_router")),
    # DRF auth token
    path("auth-token/", obtain_auth_token),
    path("getUser", getAllUsers),
    path("editUser", edit_user),
    path("registerUser", register_user),
    path("addUserAsset", add_asset),
    path("deleteUserAsset", delete_asset),
    path("updateUserAsset", update_asset),
    path("getAllAssets", get_all_assets),
    path("getSingleAsset", get_single_asset),
    path("createAssetData", add_asset_data),
    path("updateAssetData", update_asset),
    path("deleteAssetData", delete_asset_data),
    path("getAssetData", get_asset_data),
    path("getUser/", getAllUsers),
    path("editUser/", edit_user),
]

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
