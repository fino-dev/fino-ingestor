from dataclasses import dataclass

from fino_core.domain.model import Entity


@dataclass(eq=False, slots=True)
class DisclosureSource(Entity):
    source_id: str
    name: str

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")

    def __eq__(self, other: object) -> bool:
        if isinstance(other, DisclosureSource):
            return self.source_id == other.source_id
        return False

    def __hash__(self) -> int:
        return hash(self.source_id)
