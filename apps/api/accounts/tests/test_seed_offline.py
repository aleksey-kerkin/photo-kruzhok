from pathlib import Path


def test_seed_demo_does_not_download():
    source = (
        Path(__file__).resolve().parents[1]
        / "management"
        / "commands"
        / "seed_demo.py"
    ).read_text(encoding="utf-8")
    assert "t.me" not in source
    assert "urlopen" not in source
