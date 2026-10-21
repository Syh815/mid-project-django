from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('pages.urls')),
    # 強制支援靜態資源服務（即使透過反向代理或 Tunnel 訪問也能正確提供）
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.BASE_DIR / 'html'}),
]
