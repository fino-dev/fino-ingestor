from pathlib import Path

from fino_core.interface.port.document_storage import StoragePort
from fino_core.public.config.storage import LocalStorageConfig


class LocalStorage(StoragePort):
    def __init__(self, config: LocalStorageConfig) -> None:
        self.base_dir = Path(config.base_dir).expanduser().resolve()

    def exists(self, path: str) -> bool:
        target_path = self._resolve(path)
        return target_path.exists()

    def save(self, path: str, file: bytes) -> None:
        target_path = self._resolve(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        saved_bytes = target_path.write_bytes(file)

        if saved_bytes != len(file):
            raise IOError(
                f"Incomplete write detected: {saved_bytes} != {len(file)}: {path}"
            )

    def _resolve(self, path: str | Path) -> Path:
        p = Path(path)

        if p.is_absolute():
            raise ValueError("Absolute path is not allowed")

        full = (self.base_dir / p).resolve()

        if not full.is_relative_to(self.base_dir):
            raise ValueError("Path traversal detected")

        return full
