import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest

from fino_core.infrastructure.adapter.storage.local import LocalStorage
from fino_core.interface.config.storage import LocalStorageConfig
from fino_core.interface.port.storage import StoragePort


class TestLocalStorage:
    @pytest.fixture
    def temp_dir(self) -> Generator[Path, None, None]:
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.fixture
    def storage(self, temp_dir: Path) -> LocalStorage:
        return LocalStorage(config=LocalStorageConfig(base_dir=str(temp_dir)))

    ########## instance check ##########
    def test_instance_success(self, storage: LocalStorage) -> None:
        assert isinstance(storage, StoragePort)

    def test_base_dir_absolute(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            absolute_path = Path(tmpdir) / "absolute" / "path"
            storage = LocalStorage(
                config=LocalStorageConfig(base_dir=str(absolute_path))
            )
            assert storage.base_dir == absolute_path.resolve()
            assert storage.base_dir.exists()
            assert storage.base_dir.is_dir()

    def test_base_dir_tilde(self) -> None:
        storage = LocalStorage(config=LocalStorageConfig(base_dir="~/tmp"))
        assert storage.base_dir == Path("~/tmp").expanduser().resolve()

    def test_base_dir_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                relative_path = "relative/path"
                storage = LocalStorage(
                    config=LocalStorageConfig(base_dir=relative_path)
                )
                expected = Path(tmpdir) / relative_path
                assert storage.base_dir == expected.resolve()
                assert storage.base_dir.exists()
                assert storage.base_dir.is_dir()
            finally:
                os.chdir(original_cwd)

    def test_base_dir_relative_with_trailing_slash(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_cwd = os.getcwd()
            try:
                os.chdir(tmpdir)
                relative_path = "relative/path/"
                storage = LocalStorage(
                    config=LocalStorageConfig(base_dir=relative_path)
                )
                expected = Path(tmpdir) / "relative/path"
                assert storage.base_dir == expected.resolve()
            finally:
                os.chdir(original_cwd)

    ########## normalize method ERROR ##########
    def test_normalize_raises_error_on_empty_string(self) -> None:
        with pytest.raises(ValueError, match="Base directory is required"):
            _ = LocalStorage(config=LocalStorageConfig(base_dir=""))

    def test_normalize_raises_error_when_path_is_file(self, temp_dir: Path) -> None:
        test_file = temp_dir / "test_not_dir.txt"
        _ = test_file.write_text("test")
        with pytest.raises(
            NotADirectoryError, match="Base directory is not a directory"
        ):
            _ = LocalStorage(config=LocalStorageConfig(base_dir=str(test_file)))

    ########## exists method ##########

    def test_exists_returns_true_when_file_exists(
        self, storage: LocalStorage, temp_dir: Path
    ) -> None:
        test_file = temp_dir / "test.txt"
        _ = test_file.write_text("test content")
        assert storage.exists("test.txt") is True

    def test_exists_returns_false_when_file_not_exists(
        self, storage: LocalStorage
    ) -> None:
        assert storage.exists("nonexistent.txt") is False

    def test_exists_returns_false_when_directory_exists(
        self, storage: LocalStorage, temp_dir: Path
    ) -> None:
        _ = (temp_dir / "subdir").mkdir()
        assert storage.exists("subdir") is True

    ########## exists method ERRORR ##########
    def test_exists_raises_error_on_absolute_path(self, storage: LocalStorage) -> None:
        with pytest.raises(ValueError, match="Absolute path is not allowed"):
            _ = storage.exists("/absolute/path.txt")

    def test_exists_raises_error_on_path_traversal(self, storage: LocalStorage) -> None:
        with pytest.raises(ValueError, match="Path traversal detected"):
            _ = storage.exists("../outside.txt")

    ########## save method ##########
    def test_save_creates_file(self, storage: LocalStorage, temp_dir: Path) -> None:
        content = b"test save file content"
        storage.save("test-save.txt", content)
        saved_file = temp_dir / "test-save.txt"
        assert saved_file.exists()
        assert saved_file.read_bytes() == content

    def test_save_creates_directories_recursively(
        self, storage: LocalStorage, temp_dir: Path
    ) -> None:
        content = b"test content"
        storage.save("subdir/nested/test.txt", content)
        saved_file = temp_dir / "subdir" / "nested" / "test.txt"
        assert saved_file.exists()
        assert saved_file.read_bytes() == content

    def test_save_overwrites_existing_file(
        self, storage: LocalStorage, temp_dir: Path
    ) -> None:
        initial_content = b"initial"
        updated_content = b"updated"
        storage.save("test-override.txt", initial_content)
        storage.save("test-override.txt", updated_content)
        saved_file = temp_dir / "test-override.txt"
        assert saved_file.read_bytes() == updated_content

    ########## save method ERRORR ##########
    def test_save_raises_error_on_absolute_path(self, storage: LocalStorage) -> None:
        with pytest.raises(ValueError, match="Absolute path is not allowed"):
            storage.save("/absolute/path.txt", b"content")

    def test_save_raises_error_on_path_traversal(
        self, storage: LocalStorage, temp_dir: Path
    ) -> None:
        # with relative path
        with pytest.raises(ValueError, match="Path traversal detected"):
            storage.save("../outside.txt", b"content")

        # with nested path
        with pytest.raises(ValueError, match="Path traversal detected"):
            storage.save("subdir/../../outside.txt", b"content")
