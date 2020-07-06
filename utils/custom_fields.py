from django.db.models import CharField, TextField

from .utils import normalize_text

'''
set of custom filed to use in apps
'''


class FarsiCharField(CharField):
    """
    Farsi character field to change multi form characters reform to standard
    """

    def to_python(self, value):
        return super(FarsiCharField, self).to_python(normalize_text(value))


class FarsiTextField(TextField):
    """
        Farsi text field to change multi form characters reform to standard
    """

    def to_python(self, value):
        return super(FarsiTextField, self).to_python(normalize_text(value))
