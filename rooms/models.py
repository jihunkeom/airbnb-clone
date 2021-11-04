from django.utils import timezone
from django.db import models
from django_countries.fields import CountryField
from django.urls import reverse
from core import models as core_models
from users import models as user_models
from cal import Calendar

# Create your models here.

# many to many위한 새로운 모델 만들기
class AbstractItem(core_models.TimeStampedModel):
    """Abstract Item"""

    name = models.CharField(max_length=80)

    class Meta:
        abstract = True

    def __str__(self):
        return self.name


class RoomType(AbstractItem):
    """RoomType Object Definition"""

    class Meta:
        verbose_name = "Room Type"
        ordering = ["name"]


class Amenity(AbstractItem):
    """Amenities Object Definition"""

    class Meta:
        verbose_name_plural = "Amenities"


class Facility(AbstractItem):
    "Facility model Definition"

    class Meta:
        verbose_name_plural = "Facilities"


class HouseRule(AbstractItem):
    """HouseRule Model Definition"""

    class Meta:
        verbose_name = "House Rule"


class Photo(core_models.TimeStampedModel):
    """Photo Modle Definition"""

    caption = models.CharField(max_length=80)
    file = models.ImageField(upload_to="room_photos")
    room = models.ForeignKey("Room", on_delete=models.CASCADE, related_name="photos")

    def __str__(self):
        return self.caption


class Room(AbstractItem):
    """Room Model Definition"""

    name = models.CharField(max_length=140)
    description = models.TextField()
    country = CountryField()
    city = models.CharField(max_length=80)
    price = models.IntegerField()
    address = models.CharField(max_length=140)
    guests = models.IntegerField()
    beds = models.IntegerField()
    bedrooms = models.IntegerField()
    baths = models.IntegerField()
    check_in = models.TimeField()
    check_out = models.TimeField()
    instant_book = models.BooleanField(default=False)
    # related name : 역으로 유저에서 해당 유저가 만든 방이나 리뷰등 접근할 때 사용하는 이름
    # related name is the name for the target !!!
    host = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="rooms"
    )
    room_type = models.ForeignKey(
        "RoomType", on_delete=models.SET_NULL, null=True, related_name="rooms"
    )
    amenities = models.ManyToManyField("Amenity", blank=True, related_name="rooms")
    facilities = models.ManyToManyField("Facility", blank=True, related_name="rooms")
    house_rules = models.ManyToManyField("HouseRule", blank=True, related_name="rooms")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.city = str.capitalize(self.city)
        super().save()

    def total_rating(self):
        all_reviews = self.reviews.all()
        all_ratings = 0

        if len(all_reviews) > 0:
            for review in all_reviews:
                all_ratings += review.rating_average()

            all_ratings = round(all_ratings / len(all_reviews), 2)

            return all_ratings

    def get_absolute_url(self):
        return reverse("rooms:detail", kwargs={"pk": self.pk})  # 첫인자는 namespace

    def first_photo(self):
        try:
            (photo,) = self.photos.all()[:1]
            return photo.file.url
        except ValueError:
            return None

    def get_next_four_photos(self):
        photos = self.photos.all()[1:5]

        return photos

    def get_calendars(self):
        now = timezone.now()
        this_year = now.year
        this_month = now.month
        next_month = this_month + 1
        if this_month == 12:
            next_month = 1
        this_month_cal = Calendar(this_year, this_month)
        next_month_cal = Calendar(this_year, next_month)
        return [this_month_cal, next_month_cal]
