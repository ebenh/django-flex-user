# This module is based on this blog entry:
# https://concisecoder.io/2018/10/27/case-insensitive-fields-in-django-models/
# Further reading:
# https://stackoverflow.com/questions/7773341/case-insensitive-unique-model-fields-in-django

try:
    from django.contrib.postgres.fields import CICharField as PGCICharField
    from django.db import connection

    if connection.vendor != 'postgresql':
        raise RuntimeError


    class CICharField(PGCICharField):
        pass

except (ModuleNotFoundError, RuntimeError):
    from django.db import models


    class CaseInsensitiveFieldMixin:
        """
        Field mixin that uses case-insensitive lookup alternatives if they exist.
        """

        LOOKUP_CONVERSIONS = {
            'exact': 'iexact',
            'contains': 'icontains',
            'startswith': 'istartswith',
            'endswith': 'iendswith',
            'regex': 'iregex',
        }

        def get_lookup(self, lookup_name):
            converted = self.LOOKUP_CONVERSIONS.get(lookup_name, lookup_name)
            return super().get_lookup(converted)


    class CICharField(CaseInsensitiveFieldMixin, models.CharField):
        pass
