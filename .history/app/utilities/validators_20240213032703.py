
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings



def validate_min_length(value):
    if value and len(value) < 2:
        raise ValidationError(
            _("Enter valid length of characters."), params={"value": value}
        )


def validate_description_min_length(value):
    if value and len(value) < 50:
        raise ValidationError(
            _("Enter valid length of characters. Atlist 50 characteers"), params={"value": value}
        )


def validate_isdigit(value):
    if value and not value.isdigit():
        raise ValidationError(_("Number must be numeric or number like"))


class OptionalSchemeURLValidator(URLValidator):
    def __call__(self, value):
        if '://' not in value:
            # Validate as if it were http://
            value = 'http://' + value
        super(OptionalSchemeURLValidator, self).__call__(value)


