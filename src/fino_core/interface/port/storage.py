from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    def exists(self, path: str) -> bool: ...

    @abstractmethod
    def save(self, path: str, file: bytes) -> None: ...
