# from math import ceil
# from django.core import paginator
from io import BufferedIOBase
from re import template
from django.http import Http404
from django.core import paginator
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

# from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
from django.views.generic import ListView, DetailView, View, UpdateView, CreateView
from django.views.generic.edit import FormView

from django_countries import countries
from . import models, forms
from users import mixins as user_mixins

# Create your views here.
# def all_rooms(request):
#     page = request.GET.get(
#         "page", 1
#     )  # get방법이니깐 url에 있음!! ?page=3 이런식으로 넘어올거임 그러므로 get("page"), 디폴트는 1
#     room_list = models.Room.objects.all()
#     paginator = Paginator(room_list, 10, orphans=3)  # orphans 3개 이하이면 직전페이지에 포함
#     try:
#         rooms = paginator.page(page)
#         return render(request, "rooms/home.html", context={"page": rooms})
#     except EmptyPage:  # EmptyPage라는 exception 잡아줌, 모든 예외 처리하려면 except Exception:
#         return redirect("/")


class HomeView(ListView):
    """HomeView Definition"""

    model = models.Room
    paginate_by = 12
    paginate_orphans = 3
    ordering = "created"
    page_kwarg = "page"
    # ListView를 상속받는 Class Based View는 무조건 rooms/room_list에서 템플릿을 찾고(모르겠으면 일단 실행시키고 접속해서 어디서 찾는지 확인하기)
    # 템플릿에 무조건 모델 결과는 object_list로, 페이지네이터 결과는 page_obj로 넘겨서 렌더링한다.
    context_object_name = "rooms"  # object_list로 넘어가는 걸 rooms란 이름으로 바꿔주기

    def get_context_data(self, **kwargs):  # 템플릿에 넘겨줄 context 추가해주는 부분
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        context["now"] = now
        return context


# def room_detail(request, pk):
#     try:
#         room = models.Room.objects.get(pk=pk)
#         return render(request, "rooms/detail.html", context={"room": room})
#     except models.Room.DoesNotExist:
#         raise Http404()  # 이렇게만 쓰면 자동으로 templates폴더에서 404.html 찾아서 렌더링... -> 실제로 작동 확인하려면 debug=false 설정해야함


class RoomDetail(DetailView):
    """RoomDetail Definition"""

    model = models.Room
    # DetailView 상속받고 모델 설정해두면 자동으로 템플릿은 templates/rooms/room_detail.html을 찾게 됨


class SearchView(View):
    def get(self, request):
        country = request.GET.get("country")

        # SearchForm()인에 request.GET 넣으면 url에서 GET정보 가져와서 검색한 걸 기억하게 해줌
        # 근데 만약 비어있는 필드가 있는 상태에서 검색하면 오류가 뜨게 됨
        # 맨처음 search페이지를 불러올때는 아무 데이터도 기억 안되어있는게 정상이므로 country가 없으면 search 첨 불러온거라 보고 진행
        if country:
            form = forms.SearchForm(request.GET)
            if form.is_valid():

                city = form.cleaned_data.get("city")
                price = form.cleaned_data.get("price")
                room_type = form.cleaned_data.get("room_type")
                guests = form.cleaned_data.get("guests")
                bedrooms = form.cleaned_data.get("bedrooms")
                beds = form.cleaned_data.get("beds")
                baths = form.cleaned_data.get("baths")
                instant_book = form.cleaned_data.get("instant_book")
                superhost = form.cleaned_data.get("superhost")
                amenities = form.cleaned_data.get("amenities")
                facilities = form.cleaned_data.get("facilities")

                filter_args = {}

                if city != "Anywhere":
                    filter_args["city__startswith"] = city

                filter_args["country"] = country

                if room_type is not None:
                    filter_args["room_type"] = room_type

                if price is not None:
                    filter_args["price__lte"] = price

                if guests is not None:
                    filter_args["guets__gte"] = guests

                if bedrooms is not None:
                    filter_args["bedrooms__gte"] = bedrooms

                if beds is not None:
                    filter_args["beds__gte"] = beds

                if baths is not None:
                    filter_args["baths__gte"] = baths

                if instant_book is True:
                    filter_args["instant_book"] = True

                if superhost is True:
                    filter_args["superhost"] = True

                for amenity in amenities:
                    filter_args["amenities"] = amenity

                for facility in facilities:
                    filter_args["facilities"] = facility

                qs = models.Room.objects.filter(**filter_args).order_by("-created")

                paginator = Paginator(qs, 10, orphans=5)
                page = request.GET.get("page", 1)

                rooms = paginator.get_page(page)

                return render(
                    request,
                    "rooms/search.html",
                    {"form": form, "rooms": rooms},
                )

        else:
            form = forms.SearchForm()
        return render(request, "rooms/search.html", {"form": form})


class EditRoomView(user_mixins.LoggedInOnlyView, UpdateView):
    model = models.Room
    template_name = "rooms/room_edit.html"
    fields = (
        "name",
        "description",
        "country",
        "city",
        "price",
        "address",
        "guests",
        "beds",
        "bedrooms",
        "baths",
        "check_in",
        "check_out",
        "instant_book",
        "room_type",
        "amenities",
        "facilities",
        "house_rules",
    )

    def get_object(self, queryset=None):
        # 다른 사람의 방을 url로 타고들어가서 수정할 수 없도록

        # 여기서 queryset은 위에서 정의한 model
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


class RoomPhotosView(user_mixins.LoggedInOnlyView, RoomDetail):
    # 방에 대한 사진들 다 처리하는 뷰 (수정, 삭제 등  RoomDetail이랑 거의 동일한 형태이지만 private함!!)
    model = models.Room
    template_name = "rooms/room_photos.html"

    def get_object(self, queryset=None):
        room = super().get_object(queryset=queryset)
        if room.host.pk != self.request.user.pk:
            raise Http404()
        return room


@login_required()
def delete_photo(request, room_pk, photo_pk):
    user = request.user

    try:
        room = models.Room.objects.get(pk=room_pk)
        if room.host.pk != user.pk:
            messages.error(request, "Can't delete that photo")
        else:
            models.Photo.objects.filter(pk=photo_pk).delete()
            messages.success(request, "Photo Deleted")
    except models.Room.DoesNotExist:
        return redirect(reverse("core:home"))

    return redirect(reverse("rooms:photos", kwargs={"pk": room_pk}))


class EditPhotoView(user_mixins.LoggedInOnlyView, SuccessMessageMixin, UpdateView):
    model = models.Photo
    template_name = "rooms/photo_edit.html"
    # UpdateView는 자동으로 항상 pk란 이름의 인자를 찾는데 우린 room_pk랑 photo_pk란 이름으로 인자 넘겨주므로 아래 코드 필요!
    pk_url_kwarg = "photo_pk"
    success_message = "Photo Updated!"
    fields = ("caption",)

    def get_success_url(self):
        room_pk = self.kwargs.get("room_pk")
        return reverse("rooms:photos", kwargs={"pk": room_pk})


class AddPhotoView(user_mixins.LoggedInOnlyView, FormView):
    template_name = "rooms/photo_create.html"

    # 사진을 저장하기 위해서는 사진에 해당되는 방을 정의해줘야 함. 따라서 커스텀 폼 사용해야함
    form_class = forms.CreatePhotoForm

    # form_valid 사용하면 SuccessMessageMixin 사용불가 -> 따로 직접 메세지 만들어줘야 함
    def form_valid(self, form):
        # 위에 form_class가 valid한지 판별하고, valid하면 pk 가져와서 form_class의 save란 메소드 실행시켜주기
        pk = self.kwargs.get("pk")
        form.save(pk)
        messages.success(self.request, "Photo Uploaded")
        return redirect(reverse("rooms:photos", kwargs={"pk": pk}))


class CreateRoomView(user_mixins.LoggedInOnlyView, FormView):

    form_class = forms.CreateRoomForm
    template_name = "rooms/room_create.html"

    def form_valid(self, form):
        # 이전 방법이랑 다르게 방의 유저 설정했는데 꼭 이렇게 안하고 원래 방법대로 해도 됨
        room = form.save()  # form의 save라 commit =False이구
        room.host = self.request.user
        room.save()  # form의 save가 아니라 commit True
        form.save_m2m()  # amenity, facility 등 manytomany 필드들은 이 함수 적용해야 저장됨!
        messages.success(self.request, "Room Created")
        return redirect(reverse("rooms:detail", kwargs={"pk": room.pk}))
