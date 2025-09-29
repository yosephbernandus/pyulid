"""
PyULID - ULID Implementation

A Python library providing ULID (Universally Unique Lexicographically Sortable Identifier)
functionality implemented in Rust.

Example:
    >>> import pyulid
    >>> ulid_str = pyulid.ulid()
    >>> ulid_obj = pyulid.ULID(ulid_str)
    >>> print(f"Timestamp: {ulid_obj.datetime}")
"""

# Import compiled Rust module
from . import pyulid as _pyulid_rs

from datetime import datetime
from typing import Union, Optional, overload, TYPE_CHECKING
import sys

if sys.version_info >= (3, 10):
    from typing import TypeAlias
else:
    try:
        from typing_extensions import TypeAlias
    except ImportError:
        # Fallback for older Python without typing_extensions
        TypeAlias = type

if TYPE_CHECKING:
    from typing_extensions import Self
else:
    # Fallback for Python < 3.11
    try:
        from typing_extensions import Self
    except ImportError:
        from typing import TypeVar

        Self = TypeVar("Self", bound="ULID")

# Type aliases make it type safety
ULIDString: TypeAlias = str
"""Type alias for ULID string representation (26-character Base32 string)."""

ULIDUnion: TypeAlias = Union["ULID", str]
"""Type alias for values that can be compared with ULIDs (ULID objects or strings)."""

# Re-export fast functions for python use
ulid = _pyulid_rs.ulid
ulid_with_timestamp = _pyulid_rs.ulid_with_timestamp
ulid_is_valid = _pyulid_rs.ulid_is_valid
ulid_timestamp = _pyulid_rs.ulid_timestamp
ulid_random = _pyulid_rs.ulid_random
ulid_to_uuid = _pyulid_rs.ulid_to_uuid
uuid_to_ulid = _pyulid_rs.uuid_to_ulid
encode_base32 = _pyulid_rs.encode_base32
decode_base32 = _pyulid_rs.decode_base32
ulid_from_str = _pyulid_rs.ulid_from_str

__version__ = "1.0.1"
__all__ = [
    "ULID",
    "ULIDString",
    "ULIDUnion",
    "ulid",
    "ulid_with_timestamp",
    "ulid_is_valid",
    "ulid_timestamp",
    "ulid_random",
    "ulid_to_uuid",
    "uuid_to_ulid",
    "encode_base32",
    "decode_base32",
    "ulid_from_str",
    "parse",
]


def parse(ulid_str: str) -> "ULID":
    """
    Parse a ULID string into a ULID object.

    Args:
        ulid_str: A valid ULID string (26 characters)

    Returns:
        ULID object

    Raises:
        ValueError: If the ULID string is invalid

    Example:
        >>> ulid_obj = pyulid.parse("01ARZ3NDEKTSV4RRFFQ69G5FAV")
    """
    return ULID.from_str(ulid_str)


class ULID:
    """
    A ULID (Universally Unique Lexicographically Sortable Identifier) object.

    ULIDs are 128-bit identifiers that are:
    - Lexicographically sortable
    - Encoded as 26-character Crockford Base32 strings
    - Contain timestamp + random components
    - URL-safe and case-insensitive

    This is a wrapper around Rust functions.
    For bulk operations, use the module-level functions directly.

    Example:
        >>> ulid = ULID()  # Generate new ULID
        >>> ulid = ULID.from_str("01ARZ3NDEKTSV4RRFFQ69G5FAV")  # Parse string
        >>> print(ulid.datetime)  # Get creation time
    """

    def __init__(self, ulid_str: Optional[str] = None) -> None:
        """
        Create a ULID instance.

        Args:
            ulid_str: ULID string, or None to generate a new ULID

        Raises:
            ValueError: If ulid_str is provided but invalid
        """
        if ulid_str is None:
            self._ulid = _pyulid_rs.ulid()
        else:
            if not _pyulid_rs.ulid_is_valid(ulid_str):
                raise ValueError(f"Invalid ULID string: {ulid_str}")
            self._ulid = _pyulid_rs.ulid_from_str(ulid_str)

    @classmethod
    def from_str(cls, ulid_str: str) -> Self:
        """
        Parse a ULID string into a ULID object.

        Args:
            ulid_str: A valid ULID string (26 characters)

        Returns:
            ULID object

        Raises:
            ValueError: If the ULID string is invalid
        """
        normalized = _pyulid_rs.ulid_from_str(ulid_str)
        instance = cls.__new__(cls)
        instance._ulid = normalized
        return instance

    @overload
    @classmethod
    def with_timestamp(cls, timestamp: int) -> Self: ...

    @overload
    @classmethod
    def with_timestamp(cls, timestamp: float) -> Self: ...

    @overload
    @classmethod
    def with_timestamp(cls, timestamp: datetime) -> Self: ...

    @classmethod
    def with_timestamp(cls, timestamp: Union[int, float, datetime]) -> Self:
        """
        Create a ULID with a specific timestamp.

        Args:
            timestamp: Timestamp as:
                - int: milliseconds since Unix epoch
                - float: seconds since Unix epoch
                - datetime: datetime object

        Returns:
            ULID object with specified timestamp
        """
        if isinstance(timestamp, datetime):
            timestamp_ms = int(timestamp.timestamp() * 1000)
        elif isinstance(timestamp, float):
            timestamp_ms = int(timestamp * 1000)
        else:
            timestamp_ms = timestamp

        ulid_str = _pyulid_rs.ulid_with_timestamp(timestamp_ms)
        instance = cls.__new__(cls)
        instance._ulid = ulid_str
        return instance

    @classmethod
    def from_uuid(cls, uuid_str: str) -> Self:
        """
        Create a ULID from a UUID string.

        Args:
            uuid_str: UUID string (with or without dashes)

        Returns:
            ULID object equivalent to the UUID
        """
        ulid_str = _pyulid_rs.uuid_to_ulid(uuid_str)
        instance = cls.__new__(cls)
        instance._ulid = ulid_str
        return instance

    @property
    def timestamp(self) -> int:
        """
        Get the timestamp in milliseconds since Unix epoch.

        Returns:
            Timestamp as integer milliseconds
        """
        return _pyulid_rs.ulid_timestamp(self._ulid)

    @property
    def datetime(self) -> datetime:
        """
        Get the timestamp as a datetime object.

        Returns:
            datetime object representing ULID creation time
        """
        timestamp_ms = self.timestamp
        return datetime.fromtimestamp(timestamp_ms / 1000.0)

    @property
    def random(self) -> int:
        """
        Get the random component as an integer.

        Returns:
            80-bit random component as integer
        """
        return _pyulid_rs.ulid_random(self._ulid)

    @property
    def uuid(self) -> str:
        """
        Get the ULID as a UUID string.

        Returns:
            UUID string representation (with dashes)
        """
        return _pyulid_rs.ulid_to_uuid(self._ulid)

    def is_valid(self) -> bool:
        """
        Check if this ULID is valid.

        Returns:
            True if valid, False otherwise
        """
        return _pyulid_rs.ulid_is_valid(self._ulid)

    def __str__(self) -> str:
        """Return the ULID as a string."""
        return self._ulid

    def __repr__(self) -> str:
        """Return a detailed representation."""
        return f"ULID('{self._ulid}')"

    def __bytes__(self) -> bytes:
        """Return the ULID as UTF-8 bytes."""
        return self._ulid.encode("utf-8")

    # Comparisons (ULIDs are lexicographically sortable)
    def __eq__(self, other: object) -> bool:
        """
        Check equality with another ULID or string.

        Args:
            other: ULID object or string to compare with

        Returns:
            True if equal, False otherwise
        """
        if isinstance(other, ULID):
            return self._ulid == other._ulid
        elif isinstance(other, str):
            return self._ulid == other
        return False

    def __lt__(self, other: ULIDUnion) -> bool:
        """Check if this ULID is less than another (lexicographically)."""
        if isinstance(other, ULID):
            return self._ulid < other._ulid
        elif isinstance(other, str):
            return self._ulid < other
        return NotImplemented

    def __le__(self, other: ULIDUnion) -> bool:
        """Check if this ULID is less than or equal to another."""
        if isinstance(other, ULID):
            return self._ulid <= other._ulid
        elif isinstance(other, str):
            return self._ulid <= other
        return NotImplemented

    def __gt__(self, other: ULIDUnion) -> bool:
        """Check if this ULID is greater than another (lexicographically)."""
        if isinstance(other, ULID):
            return self._ulid > other._ulid
        elif isinstance(other, str):
            return self._ulid > other
        return NotImplemented

    def __ge__(self, other: ULIDUnion) -> bool:
        """Check if this ULID is greater than or equal to another."""
        if isinstance(other, ULID):
            return self._ulid >= other._ulid
        elif isinstance(other, str):
            return self._ulid >= other
        return NotImplemented

    def __hash__(self) -> int:
        """Make ULID hashable (can be used in sets, dict keys)."""
        return hash(self._ulid)
