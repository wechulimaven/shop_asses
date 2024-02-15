from django.db.models import TextChoices


class AUTH_PROVIDER(TextChoices):
    DEFAULT = "email"
    GMAIL = "gmail"