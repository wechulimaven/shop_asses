import logging

from accounts.models import User
from django.conf import settings
from django.core.management.base import BaseCommand
from utilities.utils import get_uuid

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates super user if no user is found"

    def handle(self, *args, **options):
        # check if admin doesn't exists
        if not User.objects.filter(is_staff=True).exists():
            logger.info("Prayer hub admin does not exist. Creating Prayer hub admin.....")
            logger.info(f"Admin email {settings.DJANGO_SU_EMAIL}")
            admin = User.objects.create_superuser(
                username=settings.DJANGO_SU_NAME,
                email=settings.DJANGO_SU_EMAIL,
                password=settings.DJANGO_SU_PASSWORD,
               
            )
            logger.info("Created Prayer hub admin {}".format(admin))
