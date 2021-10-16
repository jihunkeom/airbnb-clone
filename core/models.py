from django.db import models

# Create your models here.
class TimeStampedModel(models.Model):
    """Time Stamped Model"""

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    # 지금 이 모델은 데이터베이스에 넣기 위한 모델이 아님
    # 공통된 부분들을 다른 앱의 모델들에서 상속받게 하기 위해 만든거
    # 따라서 데이터베이스에 추가하지 않기위해 아래와 같은 조치
    class Meta:
        abstract = True  # abstract model
