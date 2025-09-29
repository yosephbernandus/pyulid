# ULID Python

[![CI](https://github.com/yosephbernandus/ulid-python/workflows/CI/badge.svg)](https://github.com/yosephbernandus/ulid-python/actions)
[![PyPI](https://img.shields.io/pypi/v/ulid-python.svg)](https://pypi.org/project/ulid-python/)

A high-performance ULID (Universally Unique Lexicographically Sortable Identifier) implementation for Python.

ULID is a 128-bit identifier that is lexicographically sortable and encodes a timestamp. This implementation provides fast generation with monotonic ordering guarantees.

## Features

- **High Performance**: Rust-powered implementation with optimized Base32 encoding
- **Monotonic**: Guarantees lexicographic ordering within the same millisecond
- **Thread Safe**: Safe for concurrent use across multiple threads
- **Type Safe**: Full type hints for modern Python development
- **Multiple Formats**: Support for string, UUID, and binary representations

## Installation

```bash
# Using pip
pip install ulid-python

# Using uv (recommended for faster installs)
uv add ulid-python
```

## Usage

### Basic Usage

```python
import pyulid

# Generate a ULID
ulid_str = pyulid.ulid()
print(ulid_str)  # 01ARZ3NDEKTSV4RRFFQ69G5FAV

# Generate with specific timestamp
import time
timestamp = int(time.time() * 1000)  # milliseconds
ulid_str = pyulid.ulid_with_timestamp(timestamp)

# Validate a ULID
is_valid = pyulid.ulid_is_valid(ulid_str)
print(is_valid)  # True
```

### ULID Object

```python
import pyulid

# Create ULID object
ulid_obj = pyulid.ULID()
print(str(ulid_obj))        # 01ARZ3NDEKTSV4RRFFQ69G5FAV
print(ulid_obj.timestamp)   # 1547942611000
print(ulid_obj.datetime)    # 2019-01-19 22:10:11+00:00

# Create from string
ulid_obj = pyulid.ULID('01ARZ3NDEKTSV4RRFFQ69G5FAV')

# Create with specific timestamp
ulid_obj = pyulid.ULID.with_timestamp(timestamp)
```

### Component Access

```python
import pyulid

ulid_str = pyulid.ulid()

# Extract timestamp (48-bit, millisecond precision)
timestamp = pyulid.ulid_timestamp(ulid_str)
print(timestamp)  # 1547942611000

# Extract randomness (80-bit)
randomness = pyulid.ulid_random(ulid_str)
print(randomness)  # 12345678901234567890
```

### Format Conversion

```python
import pyulid

ulid_str = pyulid.ulid()

# Convert to UUID format
uuid_str = pyulid.ulid_to_uuid(ulid_str)
print(uuid_str)  # 01234567-89ab-cdef-0123-456789abcdef

# Convert UUID back to ULID
ulid_str = pyulid.uuid_to_ulid(uuid_str)
print(ulid_str)  # 01ARZ3NDEKTSV4RRFFQ69G5FAV
```

### Base32 Encoding

```python
import pyulid

# Encode integer to Base32
encoded = pyulid.encode_base32(12345)
print(encoded)  # Custom Crockford Base32 encoding

# Decode Base32 to integer
decoded = pyulid.decode_base32(encoded)
print(decoded)  # 12345
```

## Monotonic Support

PyULID provides monotonic ordering guarantees within the same millisecond by incrementing the random component:

```python
import pyulid

# Generate multiple ULIDs in quick succession
ulids = [pyulid.ulid() for _ in range(5)]

# They will be in lexicographic order
assert ulids == sorted(ulids)

# ULIDs generated in the same millisecond will have incremented randomness
for i in range(1, len(ulids)):
    if pyulid.ulid_timestamp(ulids[i-1]) == pyulid.ulid_timestamp(ulids[i]):
        assert pyulid.ulid_random(ulids[i]) > pyulid.ulid_random(ulids[i-1])
```

## Why not UUIDv4?

UUIDv4 (random UUIDs) are not lexicographically sortable and don't encode timestamp information:

- **Sortability**: ULIDs sort chronologically when generated sequentially, UUIDv4s are random
- **Timestamp**: ULIDs encode creation time for easy extraction, UUIDv4s don't
- **Compactness**: 26 characters vs 36 for UUID string representation  
- **Performance**: Faster generation and comparison than UUIDv4
- **Database Indexing**: Better for database performance due to sequential nature

## Specification

ULIDs are 128-bit identifiers consisting of:

```
 01AN4Z07BY      79KA1307SR9X4MV3
|----------|    |----------------|
 Timestamp          Randomness
   48bits             80bits
```

- **Timestamp**: 48-bit big-endian unsigned integer (milliseconds since Unix epoch)
- **Randomness**: 80-bit random number for uniqueness within the same millisecond
- **Encoding**: Crockford's Base32 (excludes I, L, O, U to avoid confusion)
- **Length**: 26 characters when encoded

## Requirements

- Python ≥ 3.8

## Contributing

Contributions are welcome! This project is actively maintained and we encourage:

- **Bug reports**: Open an issue if you find a bug
- **Feature requests**: Suggest new functionality 
- **Pull requests**: Submit code improvements
- **Documentation**: Help improve examples and docs
- **Testing**: Add test cases or improve coverage

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yosephbernandus/ulid-python.git
cd ulid-python

# Install development dependencies
uv sync --dev

# Build the extension in development mode
uv run maturin develop --release

# Run tests
uv run pytest tests/

# Run performance benchmarks
uv run pytest tests/test_performance.py -v -s
```

## License

[MIT License](LICENSE) - see the [LICENSE](LICENSE) file for details.
