from django.core.management.base import BaseCommand
from rooms.models import Amenity


class Command(BaseCommand):

    help = "This command creates amenities"

    # def add_arguments(self, parser):
    # parser.add_argument(
    #     # times라는 옵션 추가
    #     "--times",
    #     help="How many times do you want me to tell you that I love you?",
    # )

    def handle(self, *args, **options):
        """# print(args, options)
        # 위 코드 실행시 args는 비어있음... -> times는 결국 딕셔너리 형태로 입력되므로 options.get 사용!
        times = options.get("times")
        for t in range(int(times)):
            # print("I love you") 해도 되자만 아래처럼하면 SUCCESS, WARNING, ... 등 별로 다른 결과 나옴
            self.stdout.write(self.style.SUCCESS("I love you"))"""

        amenities = [
            "Kitchen",
            "Heating",
            "Washer",
            "Wifi",
            "Indoor fireplace",
            "Iron",
            "Laptop friendly workspace",
            "Crib",
            "Self check-in",
            "Carbon monoxide detector",
            "Shampoo",
            "Air conditioning",
            "Dryer",
            "Breakfast",
            "Hangers",
            "Hair dryer",
            "TV",
            "High chair",
            "Smoke detector",
            "Private bathroom",
        ]

        for a in amenities:
            # name은 Amenity 모델의 필드명
            Amenity.objects.create(name=a)

        self.stdout.write(self.style.SUCCESS("Amenities created!"))
