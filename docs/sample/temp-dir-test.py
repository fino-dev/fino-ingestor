import tempfile
from pathlib import Path

tmp = tempfile.TemporaryDirectory()

print(tmp.name)

path = Path(tmp.name) / "hoge_dir"
path.mkdir(parents=True, exist_ok=True)
print(path.exists())

_ = (path / "hoge.txt").write_text("hoge")
print(path / "hoge.txt")
print((path / "hoge.txt").read_text())
