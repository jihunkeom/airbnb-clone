from django.shortcuts import render, redirect, reverse
from django.views.generic import TemplateView
from rooms import models as room_models
from . import models

# Create your views here.
def toggle_room(request, room_pk):
    action = request.GET.get("action", None)
    room = room_models.Room.objects.get_or_none(pk=room_pk)
    if room is not None and action is not None:
        # get_or_create는 이미 존재하는 리스트가 여러 개 있으면 에러 뜸!! 그래서 한번만 일어난다(?)
        the_list, _ = models.List.objects.get_or_create(
            user=request.user, name="My Favourite Houses"
        )
        if action == "add":
            the_list.rooms.add(room)
        elif action == "remove":
            the_list.rooms.remove(room)
    return redirect(reverse("rooms:detail", kwargs={"pk": room_pk}))


class SeeFavsView(TemplateView):
    template_name = "lists/list_detail.html"
