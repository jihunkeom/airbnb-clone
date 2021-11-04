from django.db import models
from core import models as core_models
from core import managers as core_managers

# Create your models here.
class Conversation(core_models.TimeStampedModel):
    """Conversation Model Definition"""

    participants = models.ManyToManyField(
        "users.User", blank=True, related_name="conversation"
    )

    def __str__(self):
        usernames = []
        for user in self.participants.all():
            usernames.append(user.username)
        return ", ".join(usernames)

    def count_messages(self):
        return self.messages.count()

    count_messages.short_description = "Number of Messages"

    def count_participants(self):
        return self.participants.count()

    count_participants.short_description = "Number of Participants"
    objects = core_managers.CustomModelManager()


class Message(core_models.TimeStampedModel):
    """Message Model Definition"""

    message = models.TextField()
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="messages"
    )
    conversation = models.ForeignKey(
        "Conversation", on_delete=models.CASCADE, related_name="messages"
    )

    def __str__(self):
        return f"{self.user} says: {self.message}"
