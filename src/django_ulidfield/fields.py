from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.db import models
from ulid import ULID


def generate_ulid() -> str:
    """Generate a new ULID."""
    return str(ULID())


def validate_ulid(value):
    """Validate that a value is a valid ULID string."""
    if value is None:
        return  # Allow None values (handled by null=True/False)

    # Convert to string if it's not already
    str_value = str(value)

    # Allow empty strings - Django's blank=True/False handles this
    if str_value == "":
        return

    try:
        # Try to parse as ULID - this will raise an exception if invalid
        ULID.from_str(str_value)
    except Exception as e:
        raise ValidationError(
            f"'{str_value}' is not a valid ULID. ULIDs must be 26-character base32 strings.",
            code="invalid_ulid",
        ) from e


class ULIDField(models.CharField):
    """
    A Django model field that stores ULIDs (Universally Unique Lexicographically Sortable Identifiers)
    as 26-character base32 strings.

    This field behaves like a CharField but auto-generates a ULID value by default, enforces uniqueness,
    and is typically used as a primary key or unique identifier.
    """

    description = "A field for storing ULIDs (Universally Unique Lexicographically Sortable Identifiers)"

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 26)  # ULID is 26 characters long
        kwargs.setdefault("unique", True)  # ULIDs are unique
        kwargs.setdefault("editable", False)  # ULIDs are typically not editable
        kwargs.setdefault("default", generate_ulid)  # Generate a new ULID by default
        kwargs.setdefault("blank", False)  # Don't allow blank values by default

        # Add ULID validation
        validators = kwargs.setdefault("validators", [])
        if validate_ulid not in validators:
            validators.append(validate_ulid)

        super().__init__(*args, **kwargs)

    def to_python(self, value: Any) -> Optional[str]:
        """
        Convert the input value into a string, or return None.

        Django calls this during model deserialization or when loading from the database.
        We keep values as strings and let the validator handle ULID validation.
        """
        if value is None:
            return value
        if isinstance(value, ULID):
            return str(value)
        # Return as string - validation happens in validators
        return str(value)

    def get_prep_value(self, value: Any) -> Optional[str]:
        """
        Convert the value to a string before saving to the database.
        """
        if value is None:
            return None
        return str(value)
