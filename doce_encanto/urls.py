from django.contrib import admin
from django.templatetags.static import static
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("favicon.ico", RedirectView.as_view(url=static("images/favicon.svg"), permanent=True)),
    path("admin/", admin.site.urls),
    path("", include("shop.urls")),
]
