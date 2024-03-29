"""CHRDITools URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from CHRDITools.settings import SITE_NAME
from CHRDITools import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.tasks.urls', namespace='tasks')),
    path('risk/', include('apps.risks.urls', namespace='risks')),
]

# 为文件下载提供路径
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = SITE_NAME
admin.site.site_title = SITE_NAME
admin.site.index_title = SITE_NAME
