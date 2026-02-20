from __future__ import annotations

import os
import sys
from urllib.parse import urlparse

from aip import parse_aip, validate, AIPParseError


def load_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def resolve_target(current_file: str, target: str) -> str:
    # Local demo resolution rules:
    # - if target starts with "aip://", map to examples folder by path
    # - if target is an absolute path, treat it as relative to examples root
    # - if target is "self", return current
    if target == "self":
        return current_file

    if target.startswith("aip://"):
        u = urlparse(target)
        # u.path like "/catalog"
        rel = (u.path.lstrip("/") or "root") + ".aip.txt"
        # assume current_file is inside examples/<site>/
        site_dir = os.path.dirname(current_file)
        # climb to examples/<site> by searching for a marker file
        # simplest: site_dir is already the site folder
        return os.path.join(site_dir, rel)

    if target.startswith("/"):
        # map absolute to same directory by stripping leading slash
        site_dir = os.path.dirname(current_file)
        return os.path.join(site_dir, target.lstrip("/") + ".aip.txt")

    # relative file path
    return os.path.join(os.path.dirname(current_file), target)


def print_node(n):
    print()
    print(f"{n.title}")
    print(f"{n.description}")
    print("-" * 60)
    for line in n.content[:60]:
        print(line)
    if len(n.content) > 60:
        print("... (content truncated by browser)")
    print("-" * 60)
    print("Edges:")
    for e in n.edges:
        print(f"  {e.edge_id:10} {e.kind:3} {e.method:4} {e.target:30}  {e.summary}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python aip_browser.py <path-to-node.aip.txt>")
        sys.exit(2)

    current = sys.argv[1]
    while True:
        try:
            n = parse_aip(load_text(current))
        except (OSError, AIPParseError) as ex:
            print(f"Failed to load/parse: {current}\n{ex}")
            sys.exit(1)

        issues = validate(n)
        if issues:
            print("Warnings:")
            for w in issues:
                print(f"  - {w}")

        print_node(n)

        choice = input("\nChoose edge id (or 'q' to quit): ").strip()
        if choice.lower() in {"q", "quit", "exit"}:
            break

        edge = next((e for e in n.edges if e.edge_id == choice), None)
        if not edge:
            print("Unknown edge id.")
            continue

        # In a real client, you'd collect required inputs and make HTTP calls.
        # This demo just navigates to the target node file when possible.
        nxt = resolve_target(current, edge.target)
        if not os.path.exists(nxt):
            print(f"Target not found locally: {nxt}")
            continue
        current = nxt


if __name__ == "__main__":
    main()
