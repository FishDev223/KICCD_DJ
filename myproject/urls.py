"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kiccd_app.urls', namespace='kiccd_app')),
]

# Serve media files during development. `static()` returns a list of URL
# patterns — concatenate it with `urlpatterns` instead of placing it as an
# element inside the list (that would create a nested list and cause errors).
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
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


admin.site.index_title = None
admin.site.site_header = None
admin.site.site_title = None
admin.site.name = None

# admin.site.site_header = ""
# admin.site.site_title = ""
# admin.site.index_title = ""
# admin.site.name = ""
# admin.site.site_brand = "KICCD"
# admin.site.site_footer = "Kentucky Invasive Carp Centralized Database (KICCD) - Developed by Chris Hickey (KDFWR)"
# admin.site.site_url = None 
# admin.site.enable_nav_sidebar = True