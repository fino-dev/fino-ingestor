# """Tests for LocalStorage implementation."""

# import pytest
# from fino_core.factory.storage import create_storage


# class TestLocalStorage:
#     """LocalStorageのテスト"""

#     def test_save_and_get(self, local_storage_config):
#         """データの保存と取得のテスト"""
#         storage = create_storage(local_storage_config)

#         # データを保存
#         test_data = b"test data"
#         storage.save(key="test/file.txt", data=test_data)

#         # データを取得
#         retrieved_data = storage.get(key="test/file.txt")
#         assert retrieved_data == test_data

#     def test_save_creates_directory(self, local_storage_config):
#         """保存時にディレクトリが作成されることを確認"""
#         storage = create_storage(local_storage_config)

#         # ネストされたパスで保存
#         test_data = b"nested data"
#         storage.save(key="nested/path/file.txt", data=test_data)

#         # データが正しく保存されていることを確認
#         retrieved_data = storage.get(key="nested/path/file.txt")
#         assert retrieved_data == test_data

#     def test_get_nonexistent_file_raises_error(self, local_storage_config):
#         """存在しないファイルを取得しようとするとエラーが発生することを確認"""
#         storage = create_storage(local_storage_config)

#         with pytest.raises(FileNotFoundError):
#             storage.get(key="nonexistent/file.txt")

#     def test_save_multiple_files(self, local_storage_config):
#         """複数のファイルを保存できることを確認"""
#         storage = create_storage(local_storage_config)

#         # 複数のファイルを保存
#         storage.save(key="file1.txt", data=b"content1")
#         storage.save(key="file2.txt", data=b"content2")
#         storage.save(key="subdir/file3.txt", data=b"content3")

#         # すべてのファイルが正しく保存されていることを確認
#         assert storage.get(key="file1.txt") == b"content1"
#         assert storage.get(key="file2.txt") == b"content2"
#         assert storage.get(key="subdir/file3.txt") == b"content3"
