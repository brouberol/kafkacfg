import re
from dataclasses import dataclass, field

from .exceptions import InvalidPredicateAttribute


@dataclass
class Filter:
    """A filter is simply a list of predicates"""

    predicates: list["Predicate"]

    @classmethod
    def from_str(cls, filter: str) -> "Filter":
        predicates = []
        for predicate_str in filter.split(";"):
            predicates.append(Predicate.from_str(predicate_str))
        return Filter(predicates=predicates)


@dataclass
class Predicate:
    """A predicate equates a field name to a list of values (or patterns)

    Examples:
    - name=log.dirs
    - name=log.dirs,broker.id
    - name=log.*.bytes
    - name=log.*.bytes,socket.*

    """

    attribute: str
    values: list[str] = field(default_factory=list)

    @classmethod
    def from_str(cls, predicate: str) -> "Predicate":
        attribute, values_str = predicate.split("=")
        values = values_str.split(",")
        return Predicate(attribute=attribute, values=values)

    def to_regex(self):
        """Generate a regex in charge of matching any value from self.values"""
        # we convert the human-readable * glob pattern into a regex .*
        values = [val.replace("*", ".*") for val in self.values]
        # we then generate a (x|y|z) regex that can match any of the valuies
        values_pattern = "|".join(values)
        return "(%s)" % (values_pattern)

    def matches(self, config: dict) -> bool:
        if self.attribute not in config:
            raise InvalidPredicateAttribute(
                f"The attribute '{self.attribute}' is not found. "
                f"Available attributes are: {', '.join(config.keys())}"
            )
        attribute_value = config[self.attribute]
        return bool(re.match(self.to_regex(), attribute_value))
