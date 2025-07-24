import pytest
from django.core.exceptions import ValidationError
from django.db import models
from ulid import ULID

from django_ulidfield import ULIDField


class MockModel(models.Model):
    id = ULIDField(primary_key=True)

    class Meta:
        app_label = "tests"


class NonPrimaryKeyModel(models.Model):
    id = models.AutoField(primary_key=True)
    ulid_field = ULIDField()

    class Meta:
        app_label = "tests"


class NonPrimaryKeyModelNoDefault(models.Model):
    id = models.AutoField(primary_key=True)
    ulid_field = ULIDField(default=None, null=True)

    class Meta:
        app_label = "tests"


class BlankAllowedModel(models.Model):
    id = models.AutoField(primary_key=True)
    ulid_field = ULIDField(blank=True, default="")

    class Meta:
        app_label = "tests"


@pytest.mark.django_db
def test_ulid_field():
    """Test that ULID field generates a valid ULID."""
    obj = MockModel.objects.create()
    assert obj.id is not None
    assert len(obj.id) == 26
    assert isinstance(obj.id, str)


@pytest.mark.django_db
def test_ulid_field_persistence():
    """Test that ULID field persists correctly in the database."""
    obj = MockModel.objects.create()
    res = MockModel.objects.get(id=obj.id)
    assert res.id == obj.id


@pytest.mark.django_db
def test_ulid_field_validation_valid_ulid():
    """Test that valid ULID strings are accepted."""
    valid_ulid = str(ULID())
    obj = NonPrimaryKeyModel.objects.create(ulid_field=valid_ulid)
    assert obj.ulid_field == valid_ulid


@pytest.mark.django_db
def test_ulid_field_validation_invalid_string():
    """Test that invalid ULID strings are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        obj = NonPrimaryKeyModel(ulid_field="invalid-ulid-string")
        obj.full_clean()  # This triggers field validation

    assert "not a valid ULID" in str(exc_info.value)


@pytest.mark.django_db
def test_ulid_field_validation_wrong_length():
    """Test that strings with wrong length are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        obj = NonPrimaryKeyModel(ulid_field="TOO_SHORT")
        obj.full_clean()

    assert "not a valid ULID" in str(exc_info.value)


@pytest.mark.django_db
def test_ulid_field_validation_invalid_characters():
    """Test that strings with invalid characters are rejected."""
    with pytest.raises(ValidationError) as exc_info:
        # Use a 26-character string with invalid base32 characters (I, L, O, U)
        obj = NonPrimaryKeyModel(
            ulid_field="01ILOU567890123456789012IL"
        )  # Contains I, L, O, U
        obj.full_clean()

    assert "not a valid ULID" in str(exc_info.value)


@pytest.mark.django_db
def test_ulid_field_empty_string_with_blank_false():
    """Test that empty strings are handled when blank=False (default)."""
    # Note: Django's blank=False means "required in forms" but doesn't automatically
    # replace explicitly-set empty strings with defaults during validation.
    # This is standard Django behavior.
    obj = NonPrimaryKeyModel(ulid_field="")

    # Since we explicitly set an empty string AND our validator allows empty strings
    # (leaving blank validation to Django), this should pass validation
    obj.full_clean()

    # The empty string should remain as-is since we explicitly set it
    assert obj.ulid_field == ""


@pytest.mark.django_db
def test_ulid_field_uses_default_when_not_specified():
    """Test that default ULID is generated when no value is specified."""
    # When we don't specify a value, the default should be used
    obj = NonPrimaryKeyModel()  # No ulid_field specified

    # The default should have been applied
    assert obj.ulid_field is not None
    assert len(obj.ulid_field) == 26
    assert obj.ulid_field != ""


@pytest.mark.django_db
def test_ulid_field_empty_string_with_blank_true():
    """Test that empty strings are allowed when blank=True."""
    obj = BlankAllowedModel(ulid_field="")
    obj.full_clean()  # Should not raise ValidationError

    # The field should accept the empty string
    assert obj.ulid_field == ""


def test_ulid_field_allows_null_if_configured():
    """Test that null values are allowed when null=True."""

    class NullableULIDModel(models.Model):
        nullable_ulid = ULIDField(null=True, blank=True)

        class Meta:
            app_label = "tests"

    # This should not raise an exception
    NullableULIDModel(nullable_ulid=None)
    # Note: We can't test full_clean() without creating the table,
    # but we can test that the validator allows None
    from django_ulidfield.fields import validate_ulid

    validate_ulid(None)  # Should not raise


def test_validate_ulid_function():
    """Test the validate_ulid function directly."""
    from django_ulidfield.fields import validate_ulid

    # Valid ULID should not raise
    valid_ulid = str(ULID())
    validate_ulid(valid_ulid)

    # Invalid ULID should raise ValidationError
    with pytest.raises(ValidationError):
        validate_ulid("invalid")

    # None should not raise (handled by field's null/blank settings)
    validate_ulid(None)

    # Empty string should not raise (handled by field's blank setting)
    validate_ulid("")
