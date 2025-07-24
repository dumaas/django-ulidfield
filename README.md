# django-ulidfield

A drop-in Django model field for storing sortable, time-encoded ULIDs as 26-character strings.

## What are ULIDs?

ULIDs (Universally Unique Lexicographically Sortable Identifiers) are a modern alternative to UUIDs that combine the benefits of both sequential integers and random UUIDs. They consist of:

- **48-bit timestamp** (milliseconds since Unix epoch)
- **80-bit randomness**

```
    01AN4Z07BY             79KA1307SR9X4MV3
|----------------|    |------------------------|
       time                   randomness
      48bits                    80bits
```

ULIDs are encoded in base-32 (Crockford's Base32) resulting in 26-character strings that are:
- **Sortable** by creation time
- **URL-safe** (no special characters)
- **Case-insensitive**
- **Compatible** with UUID storage (128-bit)

## Why ULIDs over UUIDs?

As explained in Brandur Leach's article ["Identity Crisis: Sequence v. UUID as Primary Key"](https://brandur.org/nanoglyphs/026-ids), ULIDs solve several problems with traditional UUID v4:

### Problems with Random UUIDs
- **Poor database performance**: Random UUIDs cause index fragmentation and cache misses
- **High WAL overhead**: More write-ahead log data due to scattered page updates
- **No temporal ordering**: Can't sort by creation time

### ULID Advantages
- **Time-ordered**: ULIDs sort naturally by creation time
- **Better database performance**: Sequential timestamp prefix reduces index fragmentation
- **Distributed generation**: No single point of failure like auto-incrementing integers
- **Opaque to users**: Prevents enumeration attacks and business intelligence leakage
- **UUID compatible**: Can be stored in UUID columns when needed

## Installation

```bash
pip install django-ulidfield
```

Or with Poetry:

```bash
poetry add django-ulidfield
```

## Usage

### Basic Usage

```python
from django.db import models
from django_ulidfield import ULIDField

class Article(models.Model):
    id = ULIDField(primary_key=True)
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# ULIDs are automatically generated
article = Article.objects.create(title="Hello World", content="...")
print(article.id)  # Output: 01AN4Z07BY79KA1307SR9X4MV3
```

### Non-Primary Key Usage

```python
class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_id = ULIDField()  # Unique by default
    customer_email = models.EmailField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
```

### Custom Configuration

```python
class Document(models.Model):
    # Allow null values
    doc_id = ULIDField(null=True, blank=True)

    # Custom default function
    tracking_id = ULIDField(default=None, null=True)

    # Allow duplicates (not recommended)
    reference_id = ULIDField(unique=False)
```

## Field Options

`ULIDField` inherits from Django's `CharField` and accepts all the same options, with these defaults:

- `max_length=26` (ULIDs are always 26 characters)
- `unique=True` (ULIDs should be unique)
- `editable=False` (ULIDs are typically auto-generated)
- `default=generate_ulid` (automatically generates new ULIDs)
- `blank=False` (ULIDs are required by default)

## Validation

The field automatically validates that values are proper ULIDs:

```python
# This will raise a ValidationError
invalid_article = Article(id=\"invalid-ulid\")
invalid_article.full_clean()  # ValidationError: 'invalid-ulid' is not a valid ULID
```

## Database Considerations

### Index Performance
ULIDs provide better database performance than random UUIDs because:
- The timestamp prefix keeps new insertions clustered together
- Reduces index page splits and cache misses
- Minimizes write-ahead log (WAL) overhead

### Storage
- **Database storage**: 26 characters (can be optimized to 16 bytes in UUID columns)
- **Memory/JSON**: 26-character string
- **URL-safe**: Can be used directly in URLs

## Migration from UUIDs

If you're migrating from UUIDs, you can:

1. **Direct replacement** (new records only):
```python
# Change this:
id = models.UUIDField(primary_key=True, default=uuid.uuid4)

# To this:
id = ULIDField(primary_key=True)
```

2. **Gradual migration** (with a new field):
```python
class MyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)  # Keep existing
    ulid = ULIDField(null=True, blank=True)  # Add new field
```

## Time Extraction

You can extract the timestamp from a ULID:

```python
from ulid import ULID

# Get timestamp from ULID
ulid_obj = ULID.from_str(article.id)
timestamp = ulid_obj.timestamp()
datetime_obj = ulid_obj.datetime()
```

## Development

### Setup
```bash
git clone https://github.com/your-username/django-ulidfield
cd django-ulidfield
poetry install
poetry run pre-commit install
```

### Running Tests
```bash
poetry run pytest
```

### Code Quality
This project uses:
- **Ruff** for linting and formatting
- **pytest** for testing
- **pre-commit** for code quality checks

## Requirements

- Python 3.9+
- Django 4.2+
- python-ulid 3.0.0+

## License

MIT License - see LICENSE file for details.

## Related Resources

- [ULID Specification](https://github.com/ulid/spec)
- [\"Identity Crisis: Sequence v. UUID as Primary Key\"](https://brandur.org/nanoglyphs/026-ids) - Deep dive on database identifier strategies
- [python-ulid library](https://pypi.org/project/python-ulid/)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
