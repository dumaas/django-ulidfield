import pytest
from django.db import connection


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    Override the default django_db_setup to create our test model tables.
    This ensures the tables exist before any tests run.
    """
    with django_db_blocker.unblock():
        # Create test model tables
        from tests.test_ulidfield import (
            BlankAllowedModel,
            MockModel,
            NonPrimaryKeyModel,
            NonPrimaryKeyModelNoDefault,
        )

        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(MockModel)
            schema_editor.create_model(NonPrimaryKeyModel)
            schema_editor.create_model(NonPrimaryKeyModelNoDefault)
            schema_editor.create_model(BlankAllowedModel)
