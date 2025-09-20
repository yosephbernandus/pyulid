"""
PyULID
"""

# Import compiled Rust module
from . import pyulid as _pyulid_rust

from datetime import datetime
from typing import Union

# Re-export fast functions for high-performance use
ulid = _pyulid_rust.ulid
ulid_monotonic = _pyulid_rust.ulid_monotonic
ulid_with_timestamp = _pyulid_rust.ulid_with_timestamp
ulid_is_valid = _pyulid_rust.ulid_is_valid
ulid_timestamp = _pyulid_rust.ulid_timestamp
ulid_random = _pyulid_rust.ulid_random
ulid_to_uuid = _pyulid_rust.ulid_to_uuid
uuid_to_ulid = _pyulid_rust.uuid_to_ulid
encode_base32 = _pyulid_rust.encode_base32
decode_base32 = _pyulid_rust.decode_base32

__version__ = "0.1.0"
__all__ = [
    "ULID",
    "ulid",
    "ulid_monotonic",
    "ulid_with_timestamp",
    "ulid_is_valid",
    "ulid_timestamp",
    "ulid_random",
    "ulid_to_uuid",
    "uuid_to_ulid",
    "encode_base32",
    "decode_base32",
]


class ULID:
    """
    A ULID (Universally Unique Lexicographically Sortable Identifier) object.

    This is a wrapper around the Rust functions.
    For bulk operations, use the module-level functions directly.
    """

    def __init__(self, ulid_str: Union[str, None] = None):
        """
        Create a ULID instance.

        Args:
            ulid_str: ULID string, or None to generate a new ULID
        """
        if ulid_str is None:
            self._ulid = _pyulid_rust.ulid()
        else:
            if not _pyulid_rust.ulid_is_valid(ulid_str):
                raise ValueError(f"Invalid ULID string: {ulid_str}")
            self._ulid = ulid_str

    @classmethod
    def with_timestamp(cls, timestamp_ms: int) -> "ULID":
        """Create a ULID with a specific timestamp."""
        ulid_str = _pyulid_rust.ulid_with_timestamp(timestamp_ms)
        return cls(ulid_str)

    @classmethod
    def from_uuid(cls, uuid_str: str) -> "ULID":
        """Create a ULID from a UUID string."""
        ulid_str = _pyulid_rust.uuid_to_ulid(uuid_str)
        return cls(ulid_str)

    @property
    def timestamp(self) -> int:
        """Get the timestamp in milliseconds since Unix epoch."""
        return _pyulid_rust.ulid_timestamp(self._ulid)

    @property
    def datetime(self) -> datetime:
        """Get the timestamp as a datetime object."""
        timestamp_ms = self.timestamp
        return datetime.fromtimestamp(timestamp_ms / 1000.0)

    @property
    def random(self) -> int:
        """Get the random component as an integer."""
        return _pyulid_rust.ulid_random(self._ulid)

    @property
    def uuid(self) -> str:
        """Get the ULID as a UUID string."""
        return _pyulid_rust.ulid_to_uuid(self._ulid)

    def is_valid(self) -> bool:
        """Check if this ULID is valid."""
        return _pyulid_rust.ulid_is_valid(self._ulid)

    @classmethod
    def monotonic(cls) -> "ULID":
        """Generate a monotonic ULID (guaranteed ordering)."""
        ulid_str = _pyulid_rust.ulid_monotonic()
        return cls(ulid_str)

    def __str__(self) -> str:
        """Return the ULID as a string."""
        return self._ulid

    def __repr__(self) -> str:
        """Return a detailed representation."""
        return f"ULID('{self._ulid}')"

    # Comparisons (ULIDs are lexicographically sortable)
    def __eq__(self, other) -> bool:
        if isinstance(other, ULID):
            return self._ulid == other._ulid
        elif isinstance(other, str):
            return self._ulid == other
        return False

    def __lt__(self, other) -> bool:
        if isinstance(other, ULID):
            return self._ulid < other._ulid
        elif isinstance(other, str):
            return self._ulid < other
        return NotImplemented

    def __le__(self, other) -> bool:
        if isinstance(other, ULID):
            return self._ulid <= other._ulid
        elif isinstance(other, str):
            return self._ulid <= other
        return NotImplemented

    def __gt__(self, other) -> bool:
        if isinstance(other, ULID):
            return self._ulid > other._ulid
        elif isinstance(other, str):
            return self._ulid > other
        return NotImplemented

    def __ge__(self, other) -> bool:
        if isinstance(other, ULID):
            return self._ulid >= other._ulid
        elif isinstance(other, str):
            return self._ulid >= other
        return NotImplemented

    def __hash__(self) -> int:
        """Make ULID hashable (can be used in sets, dict keys)."""
        return hash(self._ulid)
