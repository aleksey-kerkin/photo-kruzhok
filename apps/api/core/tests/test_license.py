from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pnpm-workspace.yaml").is_file():
            return parent
    raise AssertionError("repository root was not found")


def test_license_is_polyform_strict():
    text = (repo_root() / "LICENSE").read_text(encoding="utf-8")
    assert text.startswith("Copyright (c) 2024-2026 Aleksey Kerkin\n")
    assert "PolyForm Strict License 1.0.0" in text
    assert "MIT License" not in text
