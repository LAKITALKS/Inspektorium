"""Setup step for the v0.1.1 evidence package (the only step that downloads).

Run with the interpreter that should own the virtual environments (Python 3.11
was used for the recorded runs). All output goes below ``--work``; nothing is
written into the source tree. Downloads come only from PyPI (pip) and from
the official Playwright browser download (``playwright install chromium``).
After the packages are installed, ``evidence_netguard`` (``netguard.py``) is
installed into each environment so that later measurement runs are guarded.
The three venv commands require an unused target: existing directories, files
and symlinks are rejected without removing them.

Subcommands
-----------
``build-wheel``  build a product wheel from ``git archive <commit>`` or from a
                 snapshot of a working tree (``--tree``), outside the source.
``product-venv`` create a venv, install one product wheel, install the guard.
``tools-venv``   create the harness venv from ``requirements.txt``.
``browser``      download the pinned Playwright Chromium build.
``guard``        (re)install the guard into an existing venv.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = TOOLS_DIR.parent
GUARD_SOURCE = TOOLS_DIR / "netguard.py"
GUARD_MODULE = "evidence_netguard"
GUARD_PTH = "zz_evidence_netguard.pth"
SECRET_ENV = ("ANTHROPIC_API_KEY", "OPENAI_API_KEY")
SNAPSHOT_ITEMS = ("pyproject.toml", "README.md", "LICENSE", "src")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def clean_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if k not in SECRET_ENV}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env.pop("EVIDENCE_NETGUARD_LOG", None)
    if extra:
        env.update(extra)
    return env


def now() -> str:
    return dt.datetime.now(dt.UTC).isoformat(timespec="seconds")


def run_logged(
    command: list[str],
    log: Path,
    step: str,
    *,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    started = now()
    result = subprocess.run(
        command,
        cwd=cwd,
        env=env or clean_env(),
        capture_output=True,
        text=True,
        check=False,
    )
    log.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "step": step,
        "command": command,
        "cwd": str(cwd) if cwd else None,
        "started": started,
        "finished": now(),
        "returncode": result.returncode,
        "stdout_tail": result.stdout[-4000:],
        "stderr_tail": result.stderr[-4000:],
    }
    with log.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    if result.returncode != 0:
        sys.stderr.write(result.stdout + result.stderr)
        raise SystemExit(f"setup step failed: {step} (exit {result.returncode})")
    return result


def venv_python(venv: Path) -> Path:
    return venv / "bin" / "python"


def site_packages(venv: Path) -> Path:
    python = venv_python(venv)
    result = subprocess.run(
        [
            str(python),
            "-c",
            "import sysconfig; print(sysconfig.get_paths()['purelib'])",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=clean_env(),
    )
    return Path(result.stdout.strip())


def install_guard(venv: Path) -> dict[str, str]:
    target_dir = site_packages(venv)
    target = target_dir / f"{GUARD_MODULE}.py"
    shutil.copyfile(GUARD_SOURCE, target)
    (target_dir / GUARD_PTH).write_text(f"import {GUARD_MODULE}\n", encoding="utf-8")
    return {
        "venv": str(venv),
        "guard_module": str(target),
        "guard_sha256": sha256_file(target),
        "source_sha256": sha256_file(GUARD_SOURCE),
    }


def freeze(venv: Path) -> list[str]:
    result = subprocess.run(
        [str(venv_python(venv)), "-m", "pip", "freeze", "--all"],
        capture_output=True,
        text=True,
        check=True,
        env=clean_env(),
    )
    return sorted(line for line in result.stdout.splitlines() if line.strip())


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )


def cmd_build_wheel(args: argparse.Namespace) -> None:
    out = Path(args.out).resolve()
    log = Path(args.setup_log).resolve()
    src = out / "src"
    wheels = out / "wheels"
    if src.exists():
        shutil.rmtree(src)
    if wheels.exists():
        shutil.rmtree(wheels)
    src.mkdir(parents=True)
    wheels.mkdir(parents=True)
    provenance: dict[str, object] = {"created": now()}
    if args.commit:
        repo = Path(args.repo).resolve()
        full = subprocess.run(
            ["git", "-C", str(repo), "rev-parse", f"{args.commit}^{{commit}}"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        archive = out / f"source-{full[:12]}.tar"
        run_logged(
            [
                "git",
                "-C",
                str(repo),
                "archive",
                "--format=tar",
                "-o",
                str(archive),
                full,
            ],
            log,
            "git-archive",
        )
        with tarfile.open(archive) as handle:
            handle.extractall(src, filter="data")
        provenance.update(
            {
                "source_kind": "git-archive",
                "commit": full,
                "archive_sha256": sha256_file(archive),
            }
        )
    else:
        tree = Path(args.tree).resolve()
        for item in SNAPSHOT_ITEMS:
            source = tree / item
            if source.is_dir():
                shutil.copytree(
                    source,
                    src / item,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                )
            else:
                shutil.copyfile(source, src / item)
        head = subprocess.run(
            ["git", "-C", str(tree), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        diff = subprocess.run(
            ["git", "-C", str(tree), "diff", "HEAD", "--binary"],
            capture_output=True,
            check=True,
        ).stdout
        stat = subprocess.run(
            ["git", "-C", str(tree), "diff", "HEAD", "--stat"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        untracked = subprocess.run(
            ["git", "-C", str(tree), "ls-files", "--others", "--exclude-standard"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        tree_digest = hashlib.sha256()
        for path in sorted(p for p in src.rglob("*") if p.is_file()):
            relative = path.relative_to(src).as_posix()
            tree_digest.update(f"{relative}\0{sha256_file(path)}\n".encode())
        provenance.update(
            {
                "source_kind": "working-tree-snapshot",
                "snapshot_tree_sha256": tree_digest.hexdigest(),
                "head": head,
                "diff_sha256": hashlib.sha256(diff).hexdigest(),
                "diff_stat": stat,
                "untracked_files": untracked,
                "snapshot_items": list(SNAPSHOT_ITEMS),
            }
        )
    build_python = Path(args.build_python)
    run_logged(
        [
            str(build_python),
            "-m",
            "build",
            "--wheel",
            "--no-isolation",
            "--outdir",
            str(wheels),
            str(src),
        ],
        log,
        "build-wheel",
    )
    built = sorted(wheels.glob("*.whl"))
    if len(built) != 1:
        raise SystemExit(f"expected exactly one wheel, found {built}")
    provenance["wheel"] = built[0].name
    provenance["wheel_sha256"] = sha256_file(built[0])
    write_json(out / "build_provenance.json", provenance)
    print(json.dumps(provenance, indent=2))


def new_venv_target(value: str) -> Path:
    """Reject existing targets, including dangling symlinks, before setup."""
    target = Path(value)
    resolved = target.resolve()
    if target.is_symlink() or resolved.exists():
        raise SystemExit("refusing existing --venv target; choose an unused path")
    return resolved


def cmd_product_venv(args: argparse.Namespace) -> None:
    venv = new_venv_target(args.venv)
    log = Path(args.setup_log).resolve()
    wheel = Path(args.wheel).resolve()
    run_logged([sys.executable, "-m", "venv", str(venv)], log, "product-venv-create")
    run_logged(
        [
            str(venv_python(venv)),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "-c",
            str(Path(args.constraints).resolve()),
            str(wheel),
        ],
        log,
        "product-venv-install (download from PyPI)",
    )
    guard = install_guard(venv)
    info = {
        "venv": str(venv),
        "python": sys.version,
        "wheel": wheel.name,
        "wheel_sha256": sha256_file(wheel),
        "freeze": freeze(venv),
        "guard": guard,
        "created": now(),
    }
    write_json(venv / "evidence_venv.json", info)
    print(json.dumps(info, indent=2))


def cmd_tools_venv(args: argparse.Namespace) -> None:
    venv = new_venv_target(args.venv)
    log = Path(args.setup_log).resolve()
    run_logged([sys.executable, "-m", "venv", str(venv)], log, "tools-venv-create")
    run_logged(
        [
            str(venv_python(venv)),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "-r",
            str(Path(args.requirements).resolve()),
        ],
        log,
        "tools-venv-install (download from PyPI)",
    )
    guard = install_guard(venv)
    info = {
        "venv": str(venv),
        "python": sys.version,
        "freeze": freeze(venv),
        "guard": guard,
        "created": now(),
    }
    write_json(venv / "evidence_venv.json", info)
    print(json.dumps(info, indent=2))


def cmd_build_venv(args: argparse.Namespace) -> None:
    venv = new_venv_target(args.venv)
    log = Path(args.setup_log).resolve()
    run_logged([sys.executable, "-m", "venv", str(venv)], log, "build-venv-create")
    run_logged(
        [
            str(venv_python(venv)),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            "--no-cache-dir",
            "-r",
            str(Path(args.requirements).resolve()),
        ],
        log,
        "build-venv-install (download from PyPI)",
    )
    info = {"venv": str(venv), "freeze": freeze(venv), "created": now()}
    write_json(venv / "evidence_venv.json", info)
    print(json.dumps(info, indent=2))


def cmd_browser(args: argparse.Namespace) -> None:
    venv = Path(args.venv).resolve()
    log = Path(args.setup_log).resolve()
    browsers = Path(args.browsers_path).resolve()
    env = clean_env({"PLAYWRIGHT_BROWSERS_PATH": str(browsers)})
    run_logged(
        [str(venv / "bin" / "playwright"), "install", "chromium"],
        log,
        "browser-download (official Playwright download)",
        env=env,
    )
    print(json.dumps({"browsers_path": str(browsers)}, indent=2))


def cmd_guard(args: argparse.Namespace) -> None:
    print(json.dumps(install_guard(Path(args.venv).resolve()), indent=2))


def cmd_publish_log(args: argparse.Namespace) -> None:
    """Copy selected setup-log entries with local paths replaced.

    Run it with the interpreter that ran the setup steps, so that the path of
    that interpreter is replaced as well.
    """

    from common import Sanitizer

    work = str(Path(args.work).resolve())
    sanitizer = Sanitizer(
        {
            work: "<WORK>",
            str(EVIDENCE_DIR.parent.parent): "<REPO>",
            sys.executable: "<SETUP_PYTHON>",
            sys.base_prefix: "<SETUP_PYTHON_PREFIX>",
        }
    )
    lines = Path(args.setup_log).read_text(encoding="utf-8").splitlines()
    keep = set(range(len(lines)))
    if args.entries:
        keep = set()
        for part in args.entries.split(","):
            first, _, last = part.strip().partition("-")
            keep |= set(range(int(first), int(last or first) + 1))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as handle:
        for index, line in enumerate(lines):
            if index in keep:
                record = sanitizer.obj(json.loads(line))
                record["log_index"] = index
                handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-wheel")
    source = build.add_mutually_exclusive_group(required=True)
    source.add_argument("--commit", help="full or short commit id (git archive)")
    source.add_argument("--tree", help="working tree to snapshot (dev runs only)")
    build.add_argument("--repo", default=".", help="repository for --commit")
    build.add_argument("--out", required=True)
    build.add_argument("--build-python", required=True)
    build.add_argument("--setup-log", required=True)
    build.set_defaults(func=cmd_build_wheel)

    product = sub.add_parser("product-venv")
    product.add_argument("--venv", required=True)
    product.add_argument("--wheel", required=True)
    product.add_argument(
        "--constraints",
        default=str(EVIDENCE_DIR / "requirements-product.txt"),
    )
    product.add_argument("--setup-log", required=True)
    product.set_defaults(func=cmd_product_venv)

    tools = sub.add_parser("tools-venv")
    tools.add_argument("--venv", required=True)
    tools.add_argument("--requirements", default=str(EVIDENCE_DIR / "requirements.txt"))
    tools.add_argument("--setup-log", required=True)
    tools.set_defaults(func=cmd_tools_venv)

    buildenv = sub.add_parser("build-venv")
    buildenv.add_argument("--venv", required=True)
    buildenv.add_argument(
        "--requirements",
        default=str(EVIDENCE_DIR / "requirements-build.txt"),
    )
    buildenv.add_argument("--setup-log", required=True)
    buildenv.set_defaults(func=cmd_build_venv)

    browser = sub.add_parser("browser")
    browser.add_argument("--venv", required=True)
    browser.add_argument("--browsers-path", required=True)
    browser.add_argument("--setup-log", required=True)
    browser.set_defaults(func=cmd_browser)

    guard = sub.add_parser("guard")
    guard.add_argument("--venv", required=True)
    guard.set_defaults(func=cmd_guard)

    publish = sub.add_parser("publish-log")
    publish.add_argument("--setup-log", required=True)
    publish.add_argument("--work", required=True)
    publish.add_argument(
        "--entries", help="inclusive index ranges, e.g. 0-9 or 0-9,16-19"
    )
    publish.add_argument("--out", required=True)
    publish.set_defaults(func=cmd_publish_log)

    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
