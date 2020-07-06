from django.apps import AppConfig
from django.utils.translation import ugettext_lazy


class SabzbinUserConfig(AppConfig):
    name = 'sabzbin_user'
    verbose_name = ugettext_lazy('users')

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import signals
