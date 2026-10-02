import subprocess
from pathlib import Path


def test_gitignore_excludes_local_environment_files() -> None:
    root = Path(__file__).resolve().parents[1]
    gitignore = (root / ".gitignore").read_text(encoding="utf-8").splitlines()
    for pattern in (".env", ".env.*", "!.env.example", ".envrc"):
        assert pattern in gitignore

    def matching_pattern(path: str) -> str:
        result = subprocess.run(
            ["git", "check-ignore", "-v", path],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, path
        # "<source>:<line>:<pattern>\t<path>" — a leading "!" means the path is re-included.
        pattern = result.stdout.split(":", 2)[-1].split("\t", 1)[0]
        return pattern

    assert matching_pattern(".env") == ".env"
    assert matching_pattern(".env.local") == ".env.*"
    assert matching_pattern(".envrc") == ".envrc"
    assert matching_pattern(".env.example") == "!.env.example"

    baseline = (root / "docs" / "SECURITY_BASELINE.md").read_text(encoding="utf-8")
    assert "`.env`, `.env.*`, `.envrc`" in baseline
