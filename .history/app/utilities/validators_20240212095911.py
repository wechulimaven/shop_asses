from datetime import datetime

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from rest_framework import serializers

from utilities.utils import (
    _get_media_type,
    get_content_file_type,
    get_file_extension
)


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


def validate_amount(amount):
    try:
        amount = int(amount)
    except BaseException:
        raise ValidationError(
            {"amount": ["amount must be either type int or can be casted as one"]}
        )

    return amount


def validate_file(value):
    valid_media_type = _get_media_type(value)
    file_type = get_content_file_type(get_file_extension(value.name))

    if not valid_media_type or not file_type:
        raise serializers.ValidationError(_("File type is not supported."))

    if value.size > settings.CONTENT_FILE_MAX_SIZE[valid_media_type]:
        raise serializers.ValidationError(
            _(
                "{} size is bigger than allowed ({}bytes).".format(
                    valid_media_type.capitalize(),
                    settings.CONTENT_FILE_MAX_SIZE[valid_media_type],
                )
            )
        )
    return value


def validate_year(value):
    year = value.year
    today_year = datetime.now().year
    if today_year - year < 0:
        raise serializers.ValidationError("year cannot be greater {today_year}".format(today_year=today_year))
    if today_year - year < 18:
        raise serializers.ValidationError("must be greater than 18")


def phone_number_validator(code, phone):
    numb = settings.SUPPORTED_COUNTRY_CODES
    for numbers in numb:

        data, message, success = phone, "", None

        if numbers[code]:
            if phone.startswith("+"):
                data = phone[4:]
                if phone[:4] not in numbers.keys():
                    success, message = False, "Invalid country code with phone number"

            elif len(phone) > numbers[code]:
                if phone.startswith("0"):
                    data = phone[1:]
                elif len(phone[1:]) == numbers[code] and not phone.startswith("0"):
                    success, message = False, "Invalid number"
                elif len(phone[1:]) > numbers[code]:
                    success, message = False, "Invalid length of number"
            break

    res = {
        "success": (numbers[code] == len(data)) if success is None else success,
        "message": message
    }

    return res
