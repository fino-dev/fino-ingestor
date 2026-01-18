from pathlib import Path

from fino_ingestor.interface.config.storage import LocalStorageConfig
from fino_ingestor.interface.port.storage import StoragePort


class LocalStorage(StoragePort):
    def __init__(self, config: LocalStorageConfig) -> None:
        self.base_dir = self._normalize_base_dir(config.base_dir)

    def exists(self, path: str) -> bool:
        target_path = self._resolve_path(path)
        return target_path.exists()

    def save(self, path: str, file: bytes) -> None:
        target_path = self._resolve_path(path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        saved_bytes = target_path.write_bytes(file)

        if saved_bytes != len(file):
            raise IOError(
                f"Incomplete write detected: {saved_bytes} != {len(file)}: {path}"
            )

    def _normalize_base_dir(self, base_dir: str) -> Path:
        if not base_dir:
            raise ValueError("Base directory is required")

        base = Path(base_dir.rstrip("/")).expanduser().resolve()  # type: ignore[reportUnknownMemberType]

        if base.exists():
            # pathが存在する場合はディレクトリかどうかをチェック
            if not base.is_dir():
                raise NotADirectoryError(f"Base directory is not a directory: {base}")
        else:
            # ディレクトリが存在しない場合は作成
            base.mkdir(parents=True, exist_ok=True)

        return base

    def _resolve_path(self, path: str) -> Path:
        p = Path(path)

        if p.is_absolute():
            raise ValueError("Absolute path is not allowed")

        full = (self.base_dir / p).resolve()

        if not full.is_relative_to(self.base_dir):
            raise ValueError("Path traversal detected")

        return full
