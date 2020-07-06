import random
import re

import factory.fuzzy
from django.contrib.auth import get_user_model

from sabzbin_user import models

USER = get_user_model()
RAW_PASS_FAKER = factory.Faker("password", locale='fa_IR')
PATTERN = re.compile(r'\W')


class UserFactory(factory.django.DjangoModelFactory):
    """
    Fake factory for USER Model
    """

    first_name = factory.Faker("first_name", locale='fa_IR')
    last_name = factory.Faker("last_name", locale='fa_IR')
    is_active = factory.fuzzy.FuzzyChoice([True, False, True, True])
    avatar = factory.django.ImageField(
        color=random.choice(['blue', 'green', 'orange', 'yellow', 'red', 'pink']))
    phone_number = factory.Faker('phone_number', locale='fa_IR')
    password = RAW_PASS_FAKER

    class Meta:
        model = USER
        django_get_or_create = ('phone_number',)


class FuzzyPoint(factory.fuzzy.BaseFuzzyAttribute):
    def fuzz(self):
        # return Point(random.uniform(48, 49), random.uniform(33, 34))
        return [random.uniform(50.50, 51.50), random.uniform(34.5, 35.5)]


class UserAddressFactory(factory.django.DjangoModelFactory):
    """
     Fake factory for UseAddress Model
     """
    user = factory.Iterator(USER.objects.all())
    address = factory.Faker('address', locale='fa_IR')
    coordinates = FuzzyPoint()

    class Meta:
        model = models.UserAddress


class TestUserAddressFactory(UserAddressFactory):  # Tests have problem with  factory.Iterator
    user = factory.SubFactory(UserFactory)


class UserScoreFactory(factory.django.DjangoModelFactory):
    """
     Fake factory for UseScore Model
     """
    user = factory.Iterator(USER.objects.all())
    type = factory.fuzzy.FuzzyChoice(('Profile', 'Referral'))
    point = factory.fuzzy.FuzzyChoice(range(1, 20))

    class Meta:
        model = models.UserScoreTransaction
