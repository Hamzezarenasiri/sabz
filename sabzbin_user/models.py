# Create your models here.
from uuid import uuid4

import pyotp
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField

from utils.custom_fields import FarsiCharField, FarsiTextField
from utils.custom_models import BaseUUIDModel, TimestampedModel


class CustomUserManager(BaseUserManager):

    def create_user(self, phone_number, password=None, **extra_fields):
        """Creates and saves a new user"""
        if not phone_number:
            raise ValueError(_('Users must have a phone_number'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password):
        """Creates and saves a new super user"""
        user = self.create_user(phone_number, password)
        user.is_active = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

    def get_by_phone_number(self, phone_number):
        return self.get(**{'phone_number': phone_number})


class User(AbstractBaseUser, PermissionsMixin, BaseUUIDModel, TimestampedModel):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

   phone_number are required. Other fields are optional.
    """
    id = models.UUIDField(primary_key=True,
                          default=uuid4,
                          editable=False,
                          db_index=True, )
    first_name = FarsiCharField(_('first name'),
                                max_length=30,
                                blank=True, )
    last_name = FarsiCharField(_('last name'),
                               max_length=30,
                               blank=True, )
    phone_number = PhoneNumberField(_('mobile number'),
                                    unique=True,
                                    blank=False,
                                    null=False, )
    referral = models.OneToOneField('User',
                                    on_delete=models.DO_NOTHING,
                                    null=True,
                                    db_index=True)
    birth_date = models.DateField(_('birth date'),
                                  null=True,
                                  blank=True, )
    avatar = models.ImageField(verbose_name=_('Avatar'),
                               upload_to='users/avatars/%Y/%m/',
                               null=True,
                               blank=True, )
    avatar_thumbnail = models.ImageField(verbose_name=_("avatar thumbnail"),
                                         upload_to="users/avatars-thumbnails/%Y/%m/",
                                         blank=True,
                                         editable=False, )
    key = models.CharField(_('key'),
                           max_length=50,
                           unique=True,
                           blank=True, )
    is_staff = models.BooleanField(_('staff status'),
                                   default=False,
                                   help_text=_('Designates whether the user can log into this admin site.'), )
    is_active = models.BooleanField(_('active'),
                                    default=True,
                                    help_text=_('Designates whether this user should be treated as active. '
                                                'Unselected this instead of deleting accounts.'), )
    objects = CustomUserManager()
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return f'{self.first_name} {self.last_name}-{self.phone_number}'

    def authenticate(self, otp):
        """ This method authenticates the given otp"""
        provided_otp = otp
        # Here we are using Time Based OTP.
        # otp must be provided within this interval or it's invalid
        auth_otp = pyotp.TOTP(
            self.key, interval=settings.OTP_INTERVAL,
            digits=settings.SMS_VERIFY_CODE_LENGTH)
        return auth_otp.verify(provided_otp, valid_window=1)


class UserAddress(BaseUUIDModel, TimestampedModel):
    user = models.ForeignKey('User',
                             models.CASCADE,
                             related_name='user_addresses',
                             verbose_name=_('User'), )
    address = FarsiTextField(_('address'),
                             max_length=300, )
    # it's better to use postgis
    # from django.contrib.gis.db.models import PointField
    # coordinates = PointField(max_length=50, blank=True, verbose_name=_("Coordinates"), null=True,)
    coordinates = models.CharField(_("Coordinates"),
                                   max_length=50,
                                   blank=True,
                                   null=True, )

    def __str__(self):
        return f'{self.address} ({self.user.first_name} {self.user.last_name})'

    class Meta:
        verbose_name = _('user addresses')
        verbose_name_plural = _('users addresses')


class UserScoreBase(BaseUUIDModel, TimestampedModel):
    TYPE_CHOICES = (('Profile', _('Profile')),
                    ('Referral', _('Referral')),)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES,
                            null=False,
                            blank=False, )
    point = models.PositiveIntegerField(_('point'), default=0)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f'{self.point}-{self.type} ({self.user.first_name} {self.user.last_name})'

    class Meta:
        abstract = True


class UserScoreTransaction(UserScoreBase):
    user = models.ForeignKey('User',
                             models.CASCADE,
                             related_name='user_score_transactions',
                             verbose_name=_('User'),
                             null=False,
                             blank=False, )

    class Meta:
        verbose_name = _('user scores transaction')
        verbose_name_plural = _('users scores transactions')


class UserScore(UserScoreBase):
    user = models.ForeignKey('User',
                             models.CASCADE,
                             related_name='user_score',
                             verbose_name=_('User'),
                             null=False,
                             blank=False, )

    class Meta:
        verbose_name = _('user scores')
        verbose_name_plural = _('users scores')
        constraints = (models.UniqueConstraint(fields=['user', 'type'], name="user_score_type", ),)
