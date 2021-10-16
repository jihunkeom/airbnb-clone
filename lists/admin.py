from django.contrib import admin
from . import models

# Register your models here.
@admin.register(models.List)
class ListAdmin(admin.ModelAdmin):
    """List Admin Definition"""

    list_display = (
        "name",
        "user",
        "count_rooms",
    )

    search_fields = ("^name",)
    # 여러 개 선택할 수 있도록 해주기
    filter_horizontal = ("rooms",)
