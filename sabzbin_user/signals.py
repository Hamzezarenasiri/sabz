import logging
from io import BytesIO

import pyotp
from PIL import Image
from django.core.files.base import ContentFile
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import User, UserScoreTransaction, UserScore

logger = logging.getLogger(__name__)


def generate_key():
    """ User otp key generator """
    key = pyotp.random_base32()
    if is_unique(key):
        return key
    generate_key()


def is_unique(key):
    try:
        User.objects.get(key=key)
    except User.DoesNotExist:
        return True
    return False


@receiver(pre_save, sender=User)
def create_key(sender, instance, **kwargs):
    """This creates the key for users that don't have keys"""
    if not instance.key:
        instance.key = generate_key()


THUMBNAIL_SIZE = (100, 100)


@receiver(pre_save, sender=User)
def avatar_thumbnail(sender, instance, **kwargs):
    try:
        logger.info(f"Generating thumbnail for {instance.avatar_thumbnail}")
        image = Image.open(instance.avatar)
        image = image.convert("RGB")
        image.thumbnail(THUMBNAIL_SIZE, Image.ANTIALIAS)
        temp_thumb = BytesIO()
        image.save(temp_thumb, "JPEG")
        temp_thumb.seek(0)
        instance.avatar_thumbnail.save(instance.avatar.name, ContentFile(temp_thumb.read()), save=False, )
        temp_thumb.close()
    except ValueError:
        pass


@receiver(post_save, sender=UserScoreTransaction)
def user_score_transaction_point(sender, instance, created, **kwargs):
    if created:
        logger.info(f"add point for {instance}")
        user_score, stat = UserScore.objects.get_or_create(user=instance.user, type=instance.type)
        user_score.point += instance.point
        user_score.save()
