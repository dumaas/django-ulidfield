# django-ulidfield

A custom Django model field for storing [ULID](https://github.com/ulid/spec) values as 26-character, lexicographically sortable strings.

## Features

- Stores ULIDs as 26-character base32 strings in a `CharField`
- Auto-generates ULIDs using the `ulid-py` library
- Provides built-in validation to ensure string conforms to ULID spec
- Supports use as primary key (`primary_key=True`)
- Drop-in replacement for `UUIDField` or `AutoField` when sortability is desired

## Installation

Install the package via PyPI:

```bash
pip install django-ulidfield
```

Or with Poetry:

```bash
poetry add django-ulidfield
```

## Usage

Add the `ULIDField` to your model like any Django field:

```python
from django.db import models
from django_ulidfield import ULIDField

class MyModel(models.Model):
    id = ULIDField(primary_key=True)
    name = models.CharField(max_length=100)
```

By default:
- The field is non-editable (`editable=False`)
- `max_length=26` is enforced
- It auto-generates new ULID values via `ulid.ULID()`

## When to Use This

Use `ULIDField` when:
- You need globally unique IDs
- You want time-sortable primary keys
- You're operating at high scale and want to avoid integer collisions or out-of-order UUIDs
- You want readable IDs that work in URLs

## How It Works

Internally:
- Values are stored as strings in the database
- On creation, `ulid.ULID()` generates a new identifier unless explicitly provided
- A custom validator ensures all values conform to ULID format

## Project Info

- **Source:** [GitHub](https://github.com/dumaas/django-ulidfield)
- **License:** MIT
- **PyPI:** [django-ulidfield](https://pypi.org/project/django-ulidfield/)
- **Python versions:** 3.9+
- **Django versions:** 4.2+

## Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you’d like to change.

To run tests:

```bash
poetry install
poetry run pytest
```

## License

MIT License
