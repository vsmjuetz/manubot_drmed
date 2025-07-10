#!/usr/bin/env python3
"""Clone all public repositories of the GitHub organization 'manubot'.

This script fetches repository information using the official GitHub API
and clones each repository into a specified local directory. The cloning
status is written to a JSON logfile so repeated runs skip already existing
repositories. Designed for macOS (Python 3.x) but should work on all
platforms with Git installed.
"""

import json
import os
import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Dict

import requests

# Basis-Konfiguration
ORG_NAME = "manubot"
DEST_ENV_VAR = "MANUBOT_CLONE_DIR"
DEFAULT_DIR = Path.home() / "manubot_repos"

def get_target_dir(arg_path: str | None) -> Path:
    """Determine the directory for cloning repositories."""
    if arg_path:
        return Path(arg_path).expanduser()
    env_path = os.environ.get(DEST_ENV_VAR)
    if env_path:
        return Path(env_path).expanduser()
    return DEFAULT_DIR

TARGET_DIR: Path  # will be set in main()
LOG_FILE: Path
API_URL_TEMPLATE = "https://api.github.com/orgs/{org}/repos?per_page=100&page={page}"
def ensure_git_available() -> None:
    """Prüfen, ob das Git-Binary verfügbar ist."""
    try:
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print("Git ist nicht verfügbar: ", exc)
        sys.exit(1)


def fetch_repositories(org: str) -> List[Dict[str, str]]:
    """Alle öffentlichen Repositories der Organisation abrufen."""
    repos: List[Dict[str, str]] = []
    page = 1
    while True:
        url = API_URL_TEMPLATE.format(org=org, page=page)
        try:
            response = requests.get(url, timeout=10)
        except requests.RequestException as exc:
            print(f"Fehler beim Abrufen von {url}: {exc}")
            break
        if response.status_code != 200:
            print(f"Unerwarteter Status {response.status_code} für {url}")
            break
        data = response.json()
        if not data:
            break
        for repo in data:
            if not repo.get("private"):
                repos.append({"name": repo["name"], "clone_url": repo["clone_url"]})
        page += 1
    return repos


def load_log() -> List[Dict[str, str]]:
    """Vorhandene Logdatei laden."""
    if LOG_FILE.exists():
        try:
            with LOG_FILE.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except json.JSONDecodeError:
            pass
    return []


def save_log(entries: List[Dict[str, str]]) -> None:
    """Aktuellen Log in Datei schreiben."""
    with LOG_FILE.open("w", encoding="utf-8") as fh:
        json.dump(entries, fh, indent=2, ensure_ascii=False)


def clone_repo(clone_url: str, destination: Path) -> str:
    """Ein Repository klonen."""
    result = subprocess.run(
        ["git", "clone", clone_url, str(destination)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Clone GitHub repos of an organization"
    )
    parser.add_argument(
        "-d",
        "--dest",
        help=(
            f"directory to clone repositories to (default: ${DEST_ENV_VAR} or {DEFAULT_DIR})"
        ),
    )
    args = parser.parse_args()

    global TARGET_DIR, LOG_FILE
    TARGET_DIR = get_target_dir(args.dest)
    LOG_FILE = TARGET_DIR / "clone_report.json"

    ensure_git_available()
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    log_entries = load_log()

    existing = {entry.get("name") for entry in log_entries if entry.get("status") == "cloned"}

    repos = fetch_repositories(ORG_NAME)
    for repo in repos:
        name = repo["name"]
        clone_url = repo["clone_url"]
        dest = TARGET_DIR / name
        entry = {"name": name, "clone_url": clone_url}
        if dest.exists():
            entry.update({"status": "skipped", "message": "bereits vorhanden"})
            print(f"Überspringe {name}, bereits vorhanden")
        elif name in existing:
            entry.update({"status": "skipped", "message": "laut Log bereits geklont"})
            print(f"Überspringe {name}, laut Log bereits geklont")
        else:
            print(f"Klonen {name}...")
            output = clone_repo(clone_url, dest)
            entry.update({"status": "cloned", "message": output.strip()})
            time.sleep(1)  # Rate-Limit-Schutz
        log_entries.append(entry)
        save_log(log_entries)

    print("Fertig. Ergebnisse im Logfile:", LOG_FILE)


if __name__ == "__main__":
    main()

