__version__ = "0.7.0"

from dataclasses import dataclass

KAFKA_VERSIONS = (
    "0.7",
    "0.8",
    "0.8.1",
    "0.8.2",
    "0.9.0",
    "0.10.0",
    "0.10.1",
    "0.10.2",
    "0.11.0",
    "1.0",
    "1.1",
    "2.0",
    "2.1",
    "2.2",
    "2.3",
    "2.4",
    "2.5",
    "2.6",
    "2.7",
    "2.8",
    "3.0",
    "3.1",
    "3.2",
    "3.3",
    "3.4",
    "3.5",
    "3.6",
)

LIBRDKAFKA_VERSIONS = (
    "0.8.0",
    "0.8.1",
    "0.8.2",
    "0.8.3",
    "0.8.4",
    "0.8.5",
    "0.8.6",
    "0.9.0",
    "0.9.0.99",
    "0.9.0.100",
    "0.9.0.101",
    "0.9.1",
    "0.9.0",
    "0.9.2",
    "0.9.3",
    "0.9.4",
    "0.9.5",
    "1.0.0",
    "1.0.1",
    "1.1.0",
    "1.2.0",
    "1.2.1",
    "1.2.2",
    "1.3.0",
    "1.4.0",
    "1.4.2",
    "1.4.4",
    "1.5.0",
    "1.5.2",
    "1.5.3",
    "1.6.0",
    "1.6.1",
    "1.6.2",
    "1.7.0",
    "1.8.0",
    "1.8.2",
    "1.9.0",
    "1.9.1",
    "1.9.2",
    "2.0.0",
    "2.0.1",
    "2.0.2",
    "2.1.0",
    "2.1.1",
    "2.2.0",
    "2.3.0",
)


@dataclass
class KafkaVersion:
    """A dataclass allowing to compare the precedence of multiple kafka versions"""

    major: int
    minor: int
    patch: int
    full_repr: bool = True

    def __ge__(self, other):
        return (self.major, self.minor, self.patch) >= (
            other.major,
            other.minor,
            other.patch,
        )

    def __str__(self) -> str:
        if self.full_repr:
            return f"{self.major}.{self.minor}.{self.patch}"
        return f"{self.major}.{self.minor}"

    @classmethod
    def from_str(cls, version: str):
        if version.count(".") == 2:
            return cls(*map(int, version.split(".")))
        else:
            major, minor = version.split(".")
            return cls(int(major), int(minor), 0, full_repr=False)

    def to_url_fragment(self):
        return str(self).replace(".", "")
