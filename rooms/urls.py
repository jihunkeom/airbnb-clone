from django.urls import path
from . import views

app_name = "rooms"

urlpatterns = [
    path(
        "<int:pk>", views.RoomDetail.as_view(), name="detail"
    ),  # pk가 views.room_detail의 매개변수로 전달됨!
    # 그리고 다른 파일에서 detail이라는 네임스페이스 불러오려면 pk라는 매개변수 값 지정해줘야 함
    path("search/", views.SearchView.as_view(), name="search"),
]
