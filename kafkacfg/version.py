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
