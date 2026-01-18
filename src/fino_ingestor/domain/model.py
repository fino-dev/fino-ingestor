from abc import ABC, abstractmethod
from dataclasses import field
from typing import Any


class Entity:
    id: int = field(init=False)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.id == other.id
        return False

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(Entity):
    """
    An entry point of aggregate.
    """

    pass


class ValueObject(ABC):
    """
    An VO Abstruct Object
    Need to be extends with @dataclass annotation to correctory validate states
    """

    def __post_init__(self) -> None:
        self._validate()

    @abstractmethod
    def _validate(self) -> None: ...
