from django.core import validators
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core import models as core_models

# Create your models here.
class Review(core_models.TimeStampedModel):
    """Review Model Definition"""

    review = models.TextField()
    accuracy = models.IntegerField(
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )
    communication = models.IntegerField(
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )
    cleanliness = models.IntegerField(
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )
    location = models.IntegerField(
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )
    check_in = models.IntegerField(
        validators=[MaxValueValidator(1), MaxValueValidator(5)]
    )
    value = models.IntegerField(validators=[MaxValueValidator(1), MaxValueValidator(5)])

    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="reviews"
    )
    room = models.ForeignKey(
        "rooms.Room", on_delete=models.CASCADE, related_name="reviews"
    )

    def __str__(self):
        return f"{self.review} - {self.room}"

    # admin 뿐만 아니라 나중에 프론트엔드 딴에서도 보여주기 위해서 모델 딴에 함수 정의
    def rating_average(self):
        avg = (
            self.accuracy
            + self.communication
            + self.cleanliness
            + self.location
            + self.check_in
            + self.value
        ) / 6
        return round(avg, 2)

    rating_average.short_description = "AVG"

    class Meta:
        ordering = ("-created",)
