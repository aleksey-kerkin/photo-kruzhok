from pathlib import Path


def repo_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "pnpm-workspace.yaml").is_file():
            return parent
    raise AssertionError("repository root was not found")


def test_readme_does_not_mention_passwords():
    text = (repo_root() / "README.md").read_text(encoding="utf-8")
    assert "password" not in text
