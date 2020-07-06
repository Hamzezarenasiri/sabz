from django.core.management.base import BaseCommand

from sabzbin_user import factories
from sabzbin_user.factories import UserFactory


class Command(BaseCommand):
    help = 'make fake data in db for test'

    def handle(self, *args, **options):
        factories.UserFactory.create_batch(50)
        self.stdout.write("50 Fake Users Added :)")
        factories.UserAddressFactory.create_batch(100)
        self.stdout.write("100 Fake UserAddresses Added :)")
        factories.UserScoreFactory.create_batch(100)
        self.stdout.write("100 Fake UserScores Added :)")
