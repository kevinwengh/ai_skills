#!/usr/bin/env python3
"""Discover and validate source-linked OKF repository knowledge."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote


DEFAULT_CONFIG_NAME = ".okf-index.json"
LOCAL_SCRIPT = Path("tools/okf_index.py")
REPO_SKILL = Path(".agents/skills/okf-builder")
RESERVED = {"index.md", "log.md"}
MARKDOWN_LINK = re.compile(r"\[[^\]]*]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\s*\)")
GUIDANCE_START = "<!-- okf-builder:start -->"
GUIDANCE_END = "<!-- okf-builder:end -->"


def default_config() -> dict[str, Any]:
    return {
        "version": 1,
        "source_include": ["**/*"],
        "exclude": [
            "AGENTS.md", ".okf-index.json", ".git/**", ".okf/**", ".agents/**", "tools/okf_index.py",
            "**/node_modules/**", "**/.venv/**", "**/vendor/**", "**/target/**", "**/build/**", "**/dist/**", "**/coverage/**",
            "**/.idea/**", "**/.vscode/**", "**/.obsidian/**", "**/.ipynb_checkpoints/**", "**/*.log",
            "**/.env", "**/.env.*", "**/.netrc", "**/.npmrc", "**/.aws/**", "**/.gnupg/**", "**/.kube/**", "**/.ssh/**", "**/sshkey/**", "**/id_*",
            "**/*.key", "**/*.pem", "**/*.p12", "**/*.pfx", "**/*.crt", "**/*.cer", "**/*.token", "**/*.secret", "**/secrets/**", "**/credentials/**",
        ],
        "output_directory": ".okf",
    }


def template_config() -> dict[str, Any]:
    template = Path(__file__).resolve().parents[1] / "assets" / "okf-index.config.json"
    if template.is_file():
        return json.loads(template.read_text(encoding="utf-8"))
    return default_config()


def skill_directory(root: Path) -> Path:
    bundled = Path(__file__).resolve().parents[1]
    if (bundled / "SKILL.md").is_file():
        return bundled
    installed = root / REPO_SKILL
    if (installed / "SKILL.md").is_file():
        return installed
    raise ValueError("unable to locate the okf-builder skill bundle")


def install_repo_skill(root: Path) -> bool:
    target = root / REPO_SKILL
    if target.exists():
        if not target.is_dir() or not (target / "SKILL.md").is_file():
            raise ValueError(f"refusing to overwrite non-skill directory: {target}")
        return False
    shutil.copytree(skill_directory(root), target, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    return True


@dataclass(frozen=True)
class DiscoveryResult:
    sources: int
    inventory_updated: bool
    index_created: bool


def write_if_changed(path: Path, content: str) -> bool:
    if path.is_file() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def glob_matches(path: str, pattern: str) -> bool:
    pieces: list[str] = ["^"]
    index = 0
    while index < len(pattern):
        if pattern[index:index + 3] == "**/":
            pieces.append("(?:.*/)?")
            index += 3
        elif pattern[index:index + 2] == "**":
            pieces.append(".*")
            index += 2
        elif pattern[index] == "*":
            pieces.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            pieces.append("[^/]")
            index += 1
        else:
            pieces.append(re.escape(pattern[index]))
            index += 1
    return re.fullmatch("".join([*pieces, "$"]), path) is not None


def config_path(root: Path, requested: Path) -> Path:
    path = (requested if requested.is_absolute() else root / requested).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError("configuration must be inside the repository")
    return path


def load_config(root: Path, requested: Path) -> dict[str, Any]:
    path = config_path(root, requested)
    try:
        config = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"Missing index configuration: {path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in {path}: {error}") from error
    if not isinstance(config, dict) or not isinstance(config.get("source_include"), list) or not isinstance(config.get("exclude"), list):
        raise ValueError("configuration requires source_include and exclude lists")
    output = config.get("output_directory")
    output_path = Path(output) if isinstance(output, str) else Path()
    if not isinstance(output, str) or not output or output_path.is_absolute() or output_path == Path(".") or ".." in output_path.parts:
        raise ValueError("output_directory must be a non-empty path inside the repository")
    return config


def string_list(value: Any) -> list[str]:
    return [str(item) for item in value if isinstance(item, str) and item] if isinstance(value, list) else []


def text_sha256(path: Path) -> str | None:
    try:
        with path.open("rb") as source:
            initial = source.read(8192)
            if b"\0" in initial:
                return None
            digest = hashlib.sha256(initial)
            while chunk := source.read(65536):
                digest.update(chunk)
            return digest.hexdigest()
    except OSError:
        return None


def excluded_directory(relative: str, exclusions: list[str]) -> bool:
    return any(glob_matches(f"{relative}/.okf-builder-probe", pattern) for pattern in exclusions)


def source_paths(root: Path, config: dict[str, Any]) -> list[Path]:
    patterns = string_list(config["source_include"])
    exclusions = string_list(config["exclude"])
    output = Path(config["output_directory"])
    generated_directories = (output, REPO_SKILL)
    paths: list[Path] = []
    for directory, child_directories, files in os.walk(root):
        directory_path = Path(directory)
        relative_directory = directory_path.relative_to(root)
        child_directories[:] = [
            name for name in child_directories
            if not any(
                generated == relative_directory / name or generated in (relative_directory / name).parents
                for generated in generated_directories
            )
            and not excluded_directory((relative_directory / name).as_posix(), exclusions)
        ]
        for name in files:
            path = directory_path / name
            relative = path.relative_to(root).as_posix()
            if any(glob_matches(relative, pattern) for pattern in patterns) and not any(glob_matches(relative, pattern) for pattern in exclusions):
                paths.append(path)
    return sorted(paths)


def discovery_records(root: Path, config: dict[str, Any]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    for path in source_paths(root, config):
        source_hash = text_sha256(path)
        if source_hash is None:
            continue
        relative = path.relative_to(root).as_posix()
        records.append({
            "path": relative,
            "sha256": source_hash,
            "kind": "markdown" if path.suffix.casefold() == ".md" else "text",
        })
    return records


def discovery_data(records: list[dict[str, str]]) -> str:
    return json.dumps({"version": 1, "sources": records}, ensure_ascii=False, indent=2) + "\n"


def discovery_index() -> str:
    return "---\nokf_version: \"0.1\"\n---\n\n# Repository Knowledge\n\n> Semantic concepts are produced and maintained by the OKF Builder skill.\n"


def discover(root: Path, requested: Path) -> DiscoveryResult:
    config = load_config(root, requested)
    output = root / config["output_directory"]
    records = discovery_records(root, config)
    index = output / "index.md"
    return DiscoveryResult(
        sources=len(records),
        inventory_updated=write_if_changed(output / "discovery.json", discovery_data(records)),
        index_created=not index.exists() and write_if_changed(index, discovery_index()),
    )


def parse_scalar(raw: str) -> Any:
    if raw.startswith('"'):
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw.strip('"')
    return raw.strip("'")


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}, text
    values: dict[str, Any] = {}
    for line in text[4:end].splitlines():
        match = re.fullmatch(r"([A-Za-z0-9_-]+):(?:\s*(.*))?", line)
        if match:
            key, raw = match.groups()
            values[key] = parse_scalar((raw or "").strip())
    return values, text[end + 5:]


def local_reference_error(root: Path, output: Path, origin: Path, reference: str) -> str | None:
    destination = unquote(reference.split("#", 1)[0].strip())
    if not destination or destination.startswith("//") or re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", destination):
        return None
    base = output if destination.startswith("/") else origin.parent
    target = (base / destination.lstrip("/")).resolve()
    if not target.is_relative_to(root.resolve()):
        return f"reference escapes repository: {reference}"
    if not target.exists():
        return f"missing local reference: {reference}"
    return None


def markdown_references(body: str) -> list[str]:
    return [match.group(1) or match.group(2) for match in MARKDOWN_LINK.finditer(body)]


def validate(root: Path, requested: Path) -> list[str]:
    config = load_config(root, requested)
    output = root / config["output_directory"]
    if not output.is_dir():
        return [f"Missing output directory: {output}"]
    errors: list[str] = []
    for path in sorted(output.rglob("*.md")):
        metadata, body = split_frontmatter(path.read_text(encoding="utf-8", errors="replace"))
        references = markdown_references(body)
        if isinstance(metadata.get("resource"), str):
            references.append(metadata["resource"])
        for reference in references:
            if error := local_reference_error(root, output, path, reference):
                errors.append(f"{path.relative_to(root)}: {error}")
        if path.name not in RESERVED and (not isinstance(metadata.get("type"), str) or not metadata["type"].strip()):
            errors.append(f"{path.relative_to(root)}: missing non-empty type")
    return errors


def guidance(config_name: str, output_directory: str) -> str:
    return "\n".join([
        GUIDANCE_START,
        "## Repository Knowledge",
        "",
        "Use the repo-local `okf-builder` skill in `.agents/skills/okf-builder/` to produce and maintain semantic knowledge.",
        "",
        f"Treat `{output_directory}/` as repository context. Before answering a question that may rely on repository knowledge, automatically read `{output_directory}/index.md` and follow only relevant semantic concepts and their source links.",
        "",
        f"Before producing or maintaining knowledge, run `python3 tools/okf_index.py --config {config_name} discover`, inspect `{output_directory}/discovery.json`, and analyze only the relevant source files. Do not require the user to name the bundle, an index file, or a command.",
        GUIDANCE_END,
        "",
    ])


def install(root: Path, requested: Path, output: str | None, no_guidance: bool) -> DiscoveryResult:
    install_repo_skill(root)
    config_file = config_path(root, requested)
    if not config_file.exists():
        config = template_config()
        if output:
            output_path = Path(output)
            if output_path.is_absolute() or output_path == Path(".") or ".." in output_path.parts:
                raise ValueError("output_directory must be a non-empty path inside the repository")
            config["output_directory"] = output
            config["exclude"] = [f"{output}/**" if pattern == ".okf/**" else pattern for pattern in config["exclude"]]
        write_if_changed(config_file, json.dumps(config, indent=2) + "\n")
    local_script = root / LOCAL_SCRIPT
    if Path(__file__).resolve() != local_script.resolve():
        write_if_changed(local_script, Path(__file__).read_text(encoding="utf-8"))
    config = load_config(root, requested)
    if not no_guidance:
        agents = root / "AGENTS.md"
        existing = agents.read_text(encoding="utf-8") if agents.exists() else ""
        pattern = re.compile(rf"\n?{re.escape(GUIDANCE_START)}.*?{re.escape(GUIDANCE_END)}\n?", re.DOTALL)
        write_if_changed(agents, (pattern.sub("", existing).rstrip() + "\n\n" + guidance(requested.as_posix(), config["output_directory"])).lstrip())
    return discover(root, requested)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--config", type=Path, default=Path(DEFAULT_CONFIG_NAME))
    commands = parser.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="install the repository skill, builder, config, and agent guidance")
    init.add_argument("--output", help="override the generated bundle directory")
    init.add_argument("--no-guidance", action="store_true", help="do not add the managed AGENTS.md block")
    commands.add_parser("discover", help="refresh the source inventory for semantic knowledge production")
    commands.add_parser("validate", help="check concept types and local references")
    commands.add_parser("status", help="show included source count and output location")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.root.resolve()
    try:
        if args.command == "init":
            result = install(root, args.config, args.output, args.no_guidance)
            print(f"Installed repository skill and builder; discovered {result.sources} source(s); inventory {'updated' if result.inventory_updated else 'unchanged'}.")
            return 0
        if args.command == "discover":
            result = discover(root, args.config)
            print(f"Discovered {result.sources} source(s); inventory {'updated' if result.inventory_updated else 'unchanged'}.")
            return 0
        config = load_config(root, args.config)
        if args.command == "validate":
            errors = validate(root, args.config)
            if errors:
                print("\n".join(f"- {error}" for error in errors), file=sys.stderr)
                return 1
            print("Knowledge bundle is OKF-conformant.")
            return 0
        print(f"Configured sources: {len(discovery_records(root, config))}\nOutput directory: {config['output_directory']}")
        return 0
    except ValueError as error:
        print(f"okf-builder: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
