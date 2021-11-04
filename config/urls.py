"""config URL Configuration

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("rooms/", include("rooms.urls", namespace="rooms")),
    path("users/", include("users.urls", namespace="users")),
    path("reservations/", include("reservations.urls", namespace="reservations")),
    path("reviews", include("reviews.urls", namespace="reviews")),
    path("", include("core.urls", namespace="core")),
]

# 개발환경에서만 이런식으로 사진 가져오도록!
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# static 파일은 아마존이나 다른 저장소에 의해 제공! static 파일이나 업로드된 파일들을 본인 서버에 사용하면 안됨!!!
# 이유는 만약에 사용자들이 많이 접속하면 결국 코드 서버에서 더 많은 디스크 공간을 소비하게 되므로
