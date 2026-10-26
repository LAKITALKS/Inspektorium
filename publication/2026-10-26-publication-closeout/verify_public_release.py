"""Verify the actual public release using anonymous HTTPS and four fresh installs.

No publication mutation, credentials, full test suite, or model call. Run only
AFTER publication with the reviewed expected IDs/hashes. The public/ subdirectory
contains scrubbed measured results; work/ contains local environments and data.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import tomllib
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

REPO = "LAKITALKS/Inspektorium"
HTTPS_HOSTS = {
    "github.com",
    "api.github.com",
    "codeload.github.com",
    "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
}
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
GIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})\Z")
CHECKSUM_FILE = "SHA256SUMS.txt"


class VerificationError(RuntimeError):
    pass


def require(condition, message):
    if not condition:
        raise VerificationError(message)


def hash_stream(handle):
    digest = hashlib.sha256()
    for chunk in iter(lambda: handle.read(1024 * 1024), b""):
        digest.update(chunk)
    return digest.hexdigest()


def file_hash(path):
    with path.open("rb") as handle:
        return hash_stream(handle)


def https_url(url):
    parsed = urllib.parse.urlsplit(url)
    require(
        parsed.scheme == "https"
        and parsed.hostname in HTTPS_HOSTS
        and not parsed.username
        and not parsed.password
        and parsed.port in (None, 443),
        "Download URL is outside the anonymous HTTPS allowlist",
    )
    return url


class PublicRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, message, headers, newurl):
        https_url(newurl)
        return super().redirect_request(request, fp, code, message, headers, newurl)


def checksum_entries(text):
    result = {}
    for line in text.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r"([0-9a-fA-F]{64})[ \t]+\*?([^\r\n]+)", line)
        require(match is not None, "Malformed SHA256SUMS.txt line")
        digest, name = match.groups()
        require(
            name == Path(name).name and name not in {".", ".."} and name not in result,
            "Unsafe or duplicate SHA256SUMS.txt filename",
        )
        result[name] = digest.lower()
    require(bool(result), "Empty SHA256SUMS.txt")
    return result


def expected_release_files(config):
    attachments = config.get("attachments", [])
    require(isinstance(attachments, list), "Release attachments must be a list")
    files = [
        {"filename": config[kind], "sha256": config[kind + "_sha256"]}
        for kind in ("wheel", "sdist")
    ] + attachments
    result = {}
    for item in files:
        require(
            isinstance(item, dict), "Release artifact expectation must be an object"
        )
        name, digest = item.get("filename"), item.get("sha256")
        require(
            isinstance(name, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name)
            and name != CHECKSUM_FILE
            and name not in result,
            "Unsafe, reserved or duplicate release artifact name",
        )
        require(
            isinstance(digest, str) and SHA256.fullmatch(digest),
            "Reviewed release artifact SHA-256 required",
        )
        result[name] = digest
    return result


def archive_path(name, strip_root):
    path = PurePosixPath(name)
    require(
        not path.is_absolute() and ".." not in path.parts and "\\" not in name,
        "Unsafe source archive member",
    )
    parts = path.parts[1:] if strip_root else path.parts
    require(".git" not in parts, "Source archive contains Git internals")
    return "/".join(parts)


def tar_manifest(archive, strip_root=False):
    result, roots, seen = {}, set(), set()
    for member in archive:
        path = archive_path(member.name, strip_root)
        require(member.name not in seen, "Duplicate source archive member")
        seen.add(member.name)
        if member.name:
            roots.add(PurePosixPath(member.name).parts[0])
        if member.isdir():
            continue
        require(member.isfile() and bool(path), "Nonregular source archive member")
        require(path not in result, "Duplicate normalized source archive path")
        handle = archive.extractfile(member)
        require(handle is not None, "Unreadable source archive member")
        with handle:
            result[path] = hash_stream(handle)
    if strip_root:
        require(len(roots) == 1, "Source archive must have exactly one root directory")
    return result


def archive_manifest(path):
    if path.suffix == ".zip":
        result, roots, seen = {}, set(), set()
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                name = archive_path(member.filename, True)
                require(member.filename not in seen, "Duplicate source archive member")
                seen.add(member.filename)
                roots.add(PurePosixPath(member.filename).parts[0])
                if member.is_dir():
                    continue
                mode = member.external_attr >> 16
                require(
                    mode & 0o170000 in (0, 0o100000) and bool(name),
                    "Nonregular source archive member",
                )
                require(name not in result, "Duplicate normalized source archive path")
                with archive.open(member) as handle:
                    result[name] = hash_stream(handle)
        require(len(roots) == 1, "Source archive must have exactly one root directory")
        return result
    with tarfile.open(path, "r:gz") as archive:
        return tar_manifest(archive, True)


def validate_expected(expected):
    require(expected.get("repository") == REPO, "Unexpected repository")
    require(
        GIT_ID.fullmatch(expected.get("main_commit", "")),
        "Expected exact main commit required",
    )
    require(
        set(expected.get("components", {})) == {"core", "arena"},
        "Both components required",
    )
    names = {"v0.1.0"}
    for name, item in expected["components"].items():
        require(
            item.get("tag") and re.fullmatch(r"[A-Za-z0-9._-]+", item["tag"]),
            "Unsafe tag",
        )
        names.add(item["tag"])
        expected_release_files(item)
        require(
            item["wheel"].endswith(".whl") and item["sdist"].endswith(".tar.gz"),
            "Expected wheel and sdist filenames required",
        )
        require(
            item.get("module_count") == (19 if name == "core" else 74),
            "Expected current module inventory is 19 core / 74 Arena",
        )
        require(
            isinstance(item.get("version"), str) and bool(item["version"]),
            "Package version required",
        )
    require(
        len(names) == 3 and set(expected.get("tags", {})) == names,
        "Expected old and two distinct component tags required",
    )
    for value in expected["tags"].values():
        require(
            GIT_ID.fullmatch(value.get("object", ""))
            and GIT_ID.fullmatch(value.get("commit", "")),
            "Exact tag object and peeled commit IDs required",
        )


class Verifier:
    def __init__(self, expected, output, python):
        validate_expected(expected)
        self.expected, self.output, self.python = (
            expected,
            output.resolve(),
            str(python.resolve()),
        )
        self.output.mkdir(parents=True, exist_ok=False)
        self.work, self.public = self.output / "work", self.output / "public"
        self.work.mkdir()
        self.public.mkdir()
        for name in ("logs/setup", "logs/offline", "logs/downloads"):
            (self.public / name).mkdir(parents=True)
        self.clone = self.work / "public-clone"
        self.run_dir = self.work / "outside-source"
        self.run_dir.mkdir()
        for name in ("tmp", "downloads", "venvs"):
            (self.work / name).mkdir()
        # A clean allowlist excludes tokens, provider keys, proxies, Python overrides,
        # askpass, Git command config and user/global credential configuration.
        self.env = {
            "PATH": os.environ.get("PATH", os.defpath),
            "LANG": "C.UTF-8",
            "TMPDIR": str(self.work / "tmp"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_SYSTEM": os.devnull,
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "PIP_CONFIG_FILE": os.devnull,
            "PIP_INDEX_URL": "https://pypi.org/simple",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_INPUT": "1",
            "PIP_KEYRING_PROVIDER": "disabled",
            "NETRC": os.devnull,
            "PYTHONDONTWRITEBYTECODE": "1",
        }
        self.opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({}), PublicRedirect()
        )
        self.report = {
            "schema": "inspektorium-public-verification/1.0",
            "status": "running",
            "repository": f"https://github.com/{REPO}",
            "expected": expected,
            "started_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "checks": [],
            "commands": [],
            "environments": [
                {
                    "component": component,
                    "kind": kind,
                    "status": "not_executed",
                    "outcomes": [],
                }
                for component in ("core", "arena")
                for kind in ("wheel", "sdist")
            ],
            "scope": (
                "Fresh public clone, actual public release assets and source "
                "archives; bounded offline examples"
            ),
            "guard_scope": (
                "Published Python socket guard in each post-install "
                "environment; not an OS-wide monitor"
            ),
        }
        self.save()

    def scrub(self, value):
        if isinstance(value, dict):
            return {key: self.scrub(item) for key, item in value.items()}
        if isinstance(value, list):
            return [self.scrub(item) for item in value]
        if not isinstance(value, str):
            return value
        value = value.replace(str(self.output), "<WORK>").replace(
            str(Path.home()), "<HOME>"
        )
        value = re.sub(r"/(?:Users|home)/[^/\s\"']+", "<HOME>", value)
        return re.sub(
            r"(?i)(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-ant-[A-Za-z0-9_-]{16,})",
            "<REDACTED_TOKEN>",
            value,
        )

    def save(self):
        data = self.scrub(self.report)
        (self.public / "results.json").write_text(json.dumps(data, indent=2) + "\n")

    def checked(self, name, **facts):
        self.report["checks"].append({"name": name, "status": "passed", **facts})
        self.save()
        print(json.dumps({"step": name, "status": "passed"}), flush=True)

    def run(
        self, command, name, phase="setup", cwd=None, env=None, expected=0, timeout=1200
    ):
        cmd = [str(item) for item in command]
        result = subprocess.run(
            cmd,
            cwd=cwd or self.run_dir,
            env=env or self.env,
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        log = self.public / "logs" / phase / (name + ".log")
        log.write_text(self.scrub(result.stdout + result.stderr))
        self.report["commands"].append(
            {
                "name": name,
                "phase": phase,
                "command": cmd,
                "exit_code": result.returncode,
                "expected_exit": expected,
                "log": str(log.relative_to(self.public)),
            }
        )
        self.save()
        require(
            result.returncode == expected,
            f"{name}: exit {result.returncode}, expected {expected}; see log",
        )
        return result.stdout

    def git(self, *args):
        return self.run(
            ["git", "-c", "credential.helper=", "-c", "http.extraHeader=", *args],
            f"git-{len(self.report['commands'])}",
            cwd=self.clone if self.clone.exists() else self.work,
        )

    def download(self, url, destination):
        https_url(url)
        request = urllib.request.Request(
            url, headers={"User-Agent": "Inspektorium-public-verification/1.0"}
        )
        with (
            self.opener.open(request, timeout=180) as response,
            destination.open("xb") as handle,
        ):
            final_url = https_url(response.geturl())
            shutil.copyfileobj(response, handle, length=1024 * 1024)
        facts = {
            "url": url,
            "sha256": file_hash(destination),
            "bytes": destination.stat().st_size,
            "redirect_host": urllib.parse.urlsplit(final_url).hostname,
        }
        # Signed transient redirect queries are deliberately absent from public logs.
        relative = destination.relative_to(self.work / "downloads")
        log = (
            self.public / "logs/downloads" / relative.parent / (relative.name + ".json")
        )
        log.parent.mkdir(parents=True, exist_ok=True)
        log.write_text(json.dumps(facts, indent=2) + "\n")
        return facts

    def clone_and_refs(self):
        self.git(
            "clone",
            "--no-tags",
            "--branch",
            "main",
            f"https://github.com/{REPO}.git",
            self.clone,
        )
        commit = self.git("rev-parse", "HEAD").strip()
        require(
            commit == self.expected["main_commit"],
            "Public main differs from reviewed expected commit",
        )
        require(
            self.git("status", "--porcelain").strip() == "", "Fresh clone is not clean"
        )
        for tag, expected in self.expected["tags"].items():
            self.git("fetch", "--no-tags", "origin", f"refs/tags/{tag}:refs/tags/{tag}")
            actual = {
                "object": self.git("rev-parse", f"refs/tags/{tag}").strip(),
                "commit": self.git("rev-parse", f"refs/tags/{tag}^{{commit}}").strip(),
            }
            require(
                actual == expected,
                f"Public {tag} object/commit differs from reviewed IDs",
            )
            if tag != "v0.1.0":
                require(
                    self.git("cat-file", "-t", f"refs/tags/{tag}").strip() == "tag",
                    f"{tag} is not an annotated tag",
                )
            self.checked("ref:" + tag, **actual)
        self.checked("public-main", commit=commit, anonymous_https=True)

    def expected_archive(self, tag):
        process = subprocess.Popen(
            ["git", "archive", "--format=tar", f"refs/tags/{tag}"],
            cwd=self.clone,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            with tarfile.open(fileobj=process.stdout, mode="r|") as archive:
                manifest = tar_manifest(archive)
            stderr = process.stderr.read().decode("utf-8", errors="replace")
            require(
                process.wait() == 0,
                "Local expected archive failed: " + self.scrub(stderr),
            )
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()
        return manifest

    def assets_and_archives(self):
        artifacts = {}
        for component, config in self.expected["components"].items():
            tag = config["tag"]
            quoted = urllib.parse.quote(tag, safe="")
            metadata_file = self.work / "downloads" / (component + "-release.json")
            self.download(
                f"https://api.github.com/repos/{REPO}/releases/tags/{quoted}",
                metadata_file,
            )
            metadata = json.loads(metadata_file.read_text())
            require(
                metadata.get("tag_name") == tag
                and metadata.get("draft") is False
                and bool(metadata.get("published_at")),
                f"{component} release is not published",
            )
            require(
                metadata.get("prerelease") is (component == "arena"),
                "Unexpected research prerelease status",
            )
            entries = {entry["name"]: entry for entry in metadata.get("assets", [])}
            reviewed = expected_release_files(config)
            names = [*reviewed, CHECKSUM_FILE]
            require(
                set(entries) == set(names)
                and len(entries) == len(metadata.get("assets", [])),
                (
                    f"Public {component} release assets do not exactly match "
                    "reviewed inventory"
                ),
            )
            directory = self.work / "downloads" / component
            directory.mkdir()
            for name in names:
                url = (
                    f"https://github.com/{REPO}/releases/download/{quoted}/"
                    f"{urllib.parse.quote(name, safe='')}"
                )
                require(
                    entries[name].get("browser_download_url") == url,
                    "Unexpected public release asset URL",
                )
                self.download(url, directory / name)
            sums = checksum_entries((directory / CHECKSUM_FILE).read_text())
            require(
                set(sums) == set(reviewed),
                "Published checksum inventory differs from assets",
            )
            for name, digest in reviewed.items():
                actual = file_hash(directory / name)
                require(
                    sums[name] == actual == digest,
                    (
                        f"{component} {name}: downloaded, published and reviewed "
                        "hashes disagree"
                    ),
                )
                kind = next(
                    (kind for kind in ("wheel", "sdist") if config[kind] == name),
                    "attachment:" + name,
                )
                if kind in ("wheel", "sdist"):
                    artifacts[component, kind] = directory / name
                self.checked(f"asset:{component}:{kind}", filename=name, sha256=actual)
            self.checked(
                "release:" + component,
                tag=tag,
                prerelease=metadata["prerelease"],
                published_at=metadata["published_at"],
                asset_inventory=names,
                checksum_filename=CHECKSUM_FILE,
                checksum_file_sha256=file_hash(directory / CHECKSUM_FILE),
            )
            expected = self.expected_archive(tag)
            for suffix in ("zip", "tar.gz"):
                archive = self.work / "downloads" / f"{tag}-source.{suffix}"
                self.download(
                    f"https://github.com/{REPO}/archive/refs/tags/{quoted}.{suffix}",
                    archive,
                )
                actual = archive_manifest(archive)
                require(
                    actual == expected,
                    f"Automatic {tag} {suffix} source archive differs from tag tree",
                )
                self.checked(
                    f"source-archive:{tag}:{suffix}",
                    sha256=file_hash(archive),
                    files=len(actual),
                )
        return artifacts

    def arm_guard(self, venv, label):
        python = venv / "bin/python"
        purelib = Path(
            self.run(
                [
                    python,
                    "-I",
                    "-c",
                    "import sysconfig; print(sysconfig.get_paths()['purelib'])",
                ],
                label + "-site-location",
            ).strip()
        )
        require(
            purelib.resolve().is_relative_to(venv.resolve()),
            "site-packages is outside the new environment",
        )
        guard = self.clone / "evidence/v0.1.1/tools/netguard.py"
        shutil.copyfile(guard, purelib / "evidence_netguard.py")
        (purelib / "evidence_netguard.pth").write_text("import evidence_netguard\n")
        tree = ast.parse((self.clone / "evidence/v0.1.1/tools/canary.py").read_text())
        children = [
            ast.literal_eval(node.value)
            for node in tree.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "CHILD"
                for target in node.targets
            )
        ]
        require(
            len(children) == 1 and isinstance(children[0], str),
            "Published canary CHILD missing",
        )
        canary_log = self.work / (label + "-canary.jsonl")
        env = {**self.env, "EVIDENCE_NETGUARD_LOG": str(canary_log)}
        outcome = json.loads(
            self.run(
                [python, "-I", "-c", children[0]], label + "-canary", "offline", env=env
            )
        )
        records = [json.loads(line) for line in canary_log.read_text().splitlines()]
        attempts = {
            key: value
            for key, value in outcome.items()
            if key not in {"armed", "loopback_positive_control"}
        }
        require(
            outcome.get("armed") is True
            and outcome.get("loopback_positive_control") == "connected"
            and len(attempts) == 5
            and all(value == "refused_by_guard" for value in attempts.values())
            and sum(row.get("event") == "refused" for row in records) == 5,
            "Network guard countercheck failed",
        )
        self.checked(
            label + ":guard-countercheck",
            attempted=5,
            refused=5,
            loopback_connected=True,
            guard_sha256=file_hash(guard),
        )
        runtime_log = self.work / (label + "-offline.jsonl")
        return {**self.env, "EVIDENCE_NETGUARD_LOG": str(runtime_log)}, runtime_log

    def guarded(self, command, label, env, logfile, expected=0):
        start = logfile.stat().st_size if logfile.exists() else 0
        output = self.run(command, label, "offline", env=env, expected=expected)
        require(logfile.exists(), "No runtime guard log was produced")
        with logfile.open("rb") as handle:
            handle.seek(start)
            records = [json.loads(line) for line in handle.read().decode().splitlines()]
        require(
            any(row.get("event") == "armed" for row in records),
            "Runtime guard was not armed",
        )
        require(
            not any(row.get("event") == "refused" for row in records),
            "Unexpected runtime network operation",
        )
        return output

    def installed_examples(self, component, kind, artifact):
        config = self.expected["components"][component]
        label = f"{component}-{kind}"
        row = next(
            item
            for item in self.report["environments"]
            if item["component"] == component and item["kind"] == kind
        )
        row["status"] = "running"
        self.save()
        venv = self.work / "venvs" / label
        self.run([self.python, "-m", "venv", venv], label + "-venv")
        python = venv / "bin/python"
        self.run(
            [python, "-m", "pip", "install", "--no-cache-dir", artifact],
            label + "-install",
        )
        env, logfile = self.arm_guard(venv, label)
        package = "inspektorium" if component == "core" else "agent_arena"
        distribution = "inspektorium" if component == "core" else "agent-arena"
        source = self.clone / (
            "src/inspektorium" if component == "core" else "agent-arena/src/agent_arena"
        )
        project = source.parents[1]
        declared = tomllib.loads((project / "pyproject.toml").read_text())["project"][
            "version"
        ]
        probe = f"""import {package} as package, sys, pathlib, json, hashlib, importlib.metadata as metadata
origin = pathlib.Path(package.__file__).resolve()
print(json.dumps({{"version": metadata.version({distribution!r}), "runtime_version": package.__version__,
 "site_packages": "site-packages" in origin.parts, "inside_venv": origin.is_relative_to(pathlib.Path(sys.prefix).resolve()),
 "modules": {{str(f.relative_to(origin.parent)): hashlib.sha256(f.read_bytes()).hexdigest()
             for f in origin.parent.rglob("*.py")}}}}))"""  # noqa: E501
        installed = json.loads(
            self.guarded([python, "-I", "-c", probe], label + "-identity", env, logfile)
        )
        expected = {
            str(path.relative_to(source)): file_hash(path)
            for path in source.rglob("*.py")
        }
        require(
            installed["inside_venv"] and installed["site_packages"],
            "Package import is outside its site-packages",
        )
        require(
            installed["version"]
            == installed["runtime_version"]
            == declared
            == config["version"],
            "Installed/declared/expected versions differ",
        )
        require(
            installed["modules"] == expected
            and len(expected) == config["module_count"],
            "Installed modules differ from the fresh public clone",
        )
        row.update(
            version=installed["version"],
            site_packages=True,
            matched_module_count=len(expected),
            module_hashes=expected,
            artifact_sha256=file_hash(artifact),
        )
        cli = venv / "bin" / distribution
        self.guarded([cli, "--help"], label + "-help", env, logfile)
        if component == "core":
            cases = sorted(
                path
                for path in (self.clone / "examples").iterdir()
                if (path / "input.json").is_file()
            )
            require(len(cases) == 5, "Expected exactly five core example cases")
            for case in cases:
                for fmt, suffix in (("json", "json"), ("markdown", "md")):
                    destination = self.run_dir / f"{label}-{case.name}.{suffix}"
                    self.guarded(
                        [
                            cli,
                            "inspect",
                            "--input",
                            case / "input.json",
                            "--proposals",
                            case / "proposals.json",
                            "--format",
                            fmt,
                            "--output",
                            destination,
                        ],
                        label + "-" + case.name + "-" + fmt,
                        env,
                        logfile,
                    )
                    require(
                        destination.read_bytes()
                        == (case / ("expected_report." + suffix)).read_bytes(),
                        "Core example output differs from published expected bytes",
                    )
                    row["outcomes"].append(
                        {
                            "case": case.name,
                            "format": fmt,
                            "status": "passed",
                            "sha256": file_hash(destination),
                        }
                    )
        else:
            examples = self.clone / "agent-arena/examples/phase10"
            bundles = self.run_dir / (label + "-bundles")
            for name in ("positive", "negative", "unknown"):
                self.guarded(
                    [
                        cli,
                        "audit",
                        "validate",
                        "--task",
                        examples / (name + "-task.json"),
                    ],
                    label + "-" + name + "-validate",
                    env,
                    logfile,
                )
                result = json.loads(
                    self.guarded(
                        [
                            cli,
                            "audit",
                            "run",
                            "--offline",
                            "--task",
                            examples / (name + "-task.json"),
                            "--recording",
                            examples / (name + "-recording.json"),
                            "--output-root",
                            bundles,
                        ],
                        label + "-" + name,
                        env,
                        logfile,
                        expected=2 if name == "unknown" else 0,
                    )
                )
                status = "REVIEW_REQUIRED" if name == "unknown" else "READY_FOR_RELEASE"
                require(
                    result.get("status") == status and bool(result.get("path")),
                    "Unexpected Arena example state",
                )
                inspected = json.loads(
                    self.guarded(
                        [cli, "audit", "inspect", "--bundle", result["path"]],
                        label + "-" + name + "-inspect",
                        env,
                        logfile,
                    )
                )
                require(
                    inspected.get("valid") is True
                    and inspected.get("status") == status,
                    "Arena inspect failed",
                )
                if name == "unknown":
                    rejected = json.loads(
                        self.guarded(
                            [
                                cli,
                                "audit",
                                "release",
                                "--bundle",
                                result["path"],
                                "--output-root",
                                bundles,
                                "--reviewer",
                                "Public offline verification",
                                "--reason",
                                "Synthetic refusal check",
                            ],
                            label + "-unknown-release",
                            env,
                            logfile,
                            expected=2,
                        )
                    )
                    require(
                        rejected.get("status") == "RELEASE_BLOCKED"
                        and rejected.get("path") is None,
                        "Unresolved example was not blocked from release",
                    )
                row["outcomes"].append(
                    {
                        "case": name,
                        "status": status,
                        "inspect_valid": True,
                        "release_blocked": True
                        if name == "unknown"
                        else "not requested",
                    }
                )
            if kind == "wheel":
                archive = (
                    self.clone / "agent-arena/analysis/c25_p9_20261011/live_retest"
                )
                derived = self.run_dir / "derived-LR01"
                extraction = json.loads(
                    self.guarded(
                        [
                            python,
                            "-I",
                            self.clone
                            / "agent-arena/scripts/extract_recorded_capture.py",
                            "--capture",
                            archive / "captures/attempt-002.json",
                            "--task",
                            archive / "tasks/LR-01.json",
                            "--output",
                            derived,
                        ],
                        "arena-wheel-extract-LR01",
                        env,
                        logfile,
                    )
                )
                require(
                    extraction["recording_sha256"]
                    == file_hash(derived / "recording.json"),
                    "Derivation recording hash mismatch",
                )
                result = json.loads(
                    self.guarded(
                        [
                            cli,
                            "audit",
                            "run",
                            "--offline",
                            "--task",
                            derived / "task.json",
                            "--recording",
                            derived / "recording.json",
                            "--output-root",
                            bundles,
                        ],
                        "arena-wheel-LR01",
                        env,
                        logfile,
                    )
                )
                require(
                    result.get("status") == "READY_FOR_RELEASE",
                    "LR01 recorded-offline reanalysis failed",
                )
                inspected = json.loads(
                    self.guarded(
                        [cli, "audit", "inspect", "--bundle", result["path"]],
                        "arena-wheel-LR01-inspect",
                        env,
                        logfile,
                    )
                )
                require(
                    inspected.get("valid") is True,
                    "Derived LR01 bundle inspection failed",
                )
                row["outcomes"].append(
                    {
                        "case": "historical-LR01-derived-recording",
                        "status": result["status"],
                        "inspect_valid": True,
                        "mode": "recorded_offline",
                        "native_historical_replay": False,
                        "derivation": extraction,
                    }
                )
        self.guarded([python, "-m", "pip", "check"], label + "-pip-check", env, logfile)
        records = [json.loads(line) for line in logfile.read_text().splitlines()]
        row.update(
            status="passed",
            armed_records=sum(record.get("event") == "armed" for record in records),
            refused_operations=sum(
                record.get("event") == "refused" for record in records
            ),
        )
        self.checked(
            "environment:" + label, version=row["version"], module_count=len(expected)
        )

    def execute(self):
        try:
            self.clone_and_refs()
            artifacts = self.assets_and_archives()
            for component in ("core", "arena"):
                for kind in ("wheel", "sdist"):
                    self.installed_examples(component, kind, artifacts[component, kind])
            require(
                not self.git("status", "--porcelain").strip(),
                "Verification modified the fresh public clone",
            )
            require(
                self.git("rev-parse", "HEAD").strip() == self.expected["main_commit"],
                "Fresh clone HEAD changed",
            )
            expected_refs = {
                "refs/heads/main": self.expected["main_commit"],
                **{
                    "refs/tags/" + tag: data["object"]
                    for tag, data in self.expected["tags"].items()
                },
            }
            remote = self.git("ls-remote", "--refs", "origin", *expected_refs)
            observed_refs = {
                line.split()[1]: line.split()[0] for line in remote.splitlines()
            }
            require(
                observed_refs == expected_refs,
                "Public refs changed during verification",
            )
            self.checked("public-refs-still-match", refs=observed_refs)
            self.report["status"] = "passed"
        except Exception as exc:
            self.report["status"] = "failed"
            self.report["failure"] = {"type": type(exc).__name__, "message": str(exc)}
            for row in self.report["environments"]:
                if row["status"] == "running":
                    row["status"] = "failed"
            raise
        finally:
            self.report["finished_at_utc"] = time.strftime(
                "%Y-%m-%dT%H:%M:%SZ", time.gmtime()
            )
            self.save()


def self_test():
    artifact_config = {
        "wheel": "example-1.0-py3-none-any.whl",
        "wheel_sha256": "a" * 64,
        "sdist": "example-1.0.tar.gz",
        "sdist_sha256": "b" * 64,
        "attachments": [{"filename": "example-e1-evidence.zip", "sha256": "c" * 64}],
    }
    require(
        expected_release_files(artifact_config)
        == {
            "example-1.0-py3-none-any.whl": "a" * 64,
            "example-1.0.tar.gz": "b" * 64,
            "example-e1-evidence.zip": "c" * 64,
        },
        "Reviewed evidence attachment positive control",
    )
    for attachment in (
        {"filename": CHECKSUM_FILE, "sha256": "c" * 64},
        {"filename": artifact_config["wheel"], "sha256": "c" * 64},
        {"filename": "../escape.zip", "sha256": "c" * 64},
        {"filename": "evidence.zip", "sha256": "REPLACE_WITH_REVIEWED_SHA256"},
    ):
        try:
            expected_release_files({**artifact_config, "attachments": [attachment]})
        except VerificationError:
            pass
        else:
            raise VerificationError(
                "Reviewed evidence attachment negative control failed"
            )
    require(
        checksum_entries("a" * 64 + "  example.whl\n") == {"example.whl": "a" * 64},
        "Checksum positive control",
    )
    for text in (
        "bad  example.whl",
        "a" * 64 + "  ../escape",
        ("a" * 64 + "  same\n") * 2,
    ):
        try:
            checksum_entries(text)
        except VerificationError:
            pass
        else:
            raise VerificationError("Checksum negative control failed")
    for name in (
        "../escape",
        "/absolute",
        "root/../escape",
        "root/.git/config",
        "root\\escape",
    ):
        try:
            archive_path(name, True)
        except VerificationError:
            pass
        else:
            raise VerificationError("Archive path negative control failed")
    payload = io.BytesIO()
    with tarfile.open(fileobj=payload, mode="w") as archive:
        item = tarfile.TarInfo("root/a.txt")
        item.size = 3
        archive.addfile(item, io.BytesIO(b"abc"))
    payload.seek(0)
    with tarfile.open(fileobj=payload) as archive:
        require(
            tar_manifest(archive, True)
            == {"a.txt": hashlib.sha256(b"abc").hexdigest()},
            "Tar positive control",
        )
    with tempfile.TemporaryDirectory(
        prefix="public-verifier-selftest-", dir=Path(__file__).resolve().parent
    ) as directory:
        path = Path(directory) / "source.zip"
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("root/a.txt", "abc")
        require(
            archive_manifest(path) == {"a.txt": hashlib.sha256(b"abc").hexdigest()},
            "ZIP positive control",
        )
    print(
        json.dumps(
            {
                "self_test": "passed",
                "network_executed": False,
                "release_verification_executed": False,
            }
        )
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--expectations", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--python", type=Path, default=Path(sys.executable))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if args.expectations is None or args.output is None:
        parser.error(
            "--expectations and a new --output directory are required after publication"
        )
    verifier = None
    try:
        verifier = Verifier(
            json.loads(args.expectations.read_text()), args.output, args.python
        )
        verifier.execute()
    except Exception as exc:
        text = verifier.scrub(str(exc)) if verifier else type(exc).__name__
        print(json.dumps({"status": "failed", "error": text}), file=sys.stderr)
        return 1
    print(json.dumps({"status": "passed", "results": "public/results.json"}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
