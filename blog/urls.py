"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path,re_path
from posts.views import home_view, detail_view, tagged_view, upload_view, image_view, rawupload_view, delimage_view, auth_view, login_view, logout_view, qrgen_view,qr_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name="home"),
    path('post/<slug:slug>/', detail_view, name="detail"),
#     path('q/<slug:slug>/', detail_view, name="detail"),
    re_path(r'^q/(?P<ws>[^0-9]*?)(?P<slug>[0-9]+?)/$', detail_view, name='detail'),
    #re_path(r'^q/([\w]*)(?P<slug>.+?)/$',detail_view,name='detail'),
    path('img/', image_view, name="images"),
    path('upload/<slug:slug>', upload_view, name="upload"),
    path('rawupload/<slug:slug>', rawupload_view, name="rawupload"),
    path('tag/<slug:slug>/', tagged_view, name="tagged"),
    path('accounts/login/', login_view,name="login"),
    path('accounts/auth', auth_view, name="auth"),
    path('accounts/logout', logout_view, name="logout"),
    path('delimage/<slug:slug>', delimage_view, name="delimage"),
    path('qr/', qr_view, name="qr"),
    path('qrgen', qrgen_view, name="qrgen"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
