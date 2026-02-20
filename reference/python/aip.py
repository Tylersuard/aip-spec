from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Edge:
    edge_id: str
    kind: str          # NAV | QRY | ACT
    method: str        # GET | POST (others allowed)
    target: str        # aip://... | /path | self
    summary: str
    meta: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class AIPNode:
    version: str
    node: str
    fetch: str
    title: str
    description: str
    content: List[str]
    edges: List[Edge]


class AIPParseError(ValueError):
    pass


def parse_aip(text: str) -> AIPNode:
    lines = [ln.rstrip("\n") for ln in text.splitlines()]

    # Trim leading/trailing blank lines
    while lines and lines[0].strip() == "":
        lines.pop(0)
    while lines and lines[-1].strip() == "":
        lines.pop()

    if not lines or not lines[0].startswith("AIP/"):
        raise AIPParseError("Missing AIP/<version> header")

    version = lines[0].split("/", 1)[1].strip()
    fields: Dict[str, str] = {}
    content: List[str] = []
    edges: List[Edge] = []

    mode = "header"  # header | content | edges
    i = 1

    current_edge: Optional[Edge] = None
    current_section: Optional[str] = None

    def parse_field(line: str) -> None:
        if ":" not in line:
            raise AIPParseError(f"Invalid header line: {line}")
        k, v = line.split(":", 1)
        fields[k.strip()] = v.strip()

    while i < len(lines):
        ln = lines[i]

        if mode == "header":
            if ln.startswith("Content:"):
                mode = "content"
            elif ln.startswith("Edges:"):
                # Allow empty Content: for rare cases, but strongly discourage
                content = content or []
                mode = "edges"
            elif ln.strip() == "":
                pass
            else:
                parse_field(ln)

        elif mode == "content":
            if ln.startswith("Edges:"):
                mode = "edges"
            else:
                # Store content lines with minimal normalization
                if ln.startswith("  "):
                    content.append(ln[2:])
                elif ln.strip() == "":
                    # keep blank lines as separators
                    content.append("")
                else:
                    # Non-indented content lines are allowed but discouraged
                    content.append(ln)

        elif mode == "edges":
            if ln.strip() == "":
                pass
            elif ln.startswith("  ") and not ln.startswith("    "):
                # New edge: "id KIND METHOD TARGET - summary"
                if " - " not in ln:
                    raise AIPParseError(f"Invalid edge line: {ln}")
                left, summary = ln.strip().split(" - ", 1)
                parts = left.split()
                if len(parts) < 4:
                    raise AIPParseError(f"Invalid edge left side: {left}")
                edge_id, kind, method = parts[0], parts[1], parts[2]
                target = " ".join(parts[3:])
                current_edge = Edge(edge_id=edge_id, kind=kind, method=method, target=target, summary=summary)
                edges.append(current_edge)
                current_section = None
            elif ln.startswith("    "):
                if current_edge is None:
                    raise AIPParseError("Edge metadata without an edge")
                stripped = ln.strip()
                # Section headers like "Input:" or "Output:"
                if stripped.endswith(":") and " " not in stripped[:-1]:
                    current_section = stripped[:-1]
                    current_edge.meta.setdefault(current_section, [])
                else:
                    sec = current_section or "Meta"
                    current_edge.meta.setdefault(sec, []).append(stripped)
            else:
                raise AIPParseError(f"Unexpected indentation: {ln}")

        i += 1

    for req in ("Node", "Fetch", "Title", "Description"):
        if req not in fields:
            raise AIPParseError(f"Missing required field: {req}")
    if not content and "Content:" not in "\n".join(lines):
        raise AIPParseError("Missing Content: section")
    if not edges and "Edges:" not in "\n".join(lines):
        raise AIPParseError("Missing Edges: section")

    return AIPNode(
        version=version,
        node=fields["Node"],
        fetch=fields["Fetch"],
        title=fields["Title"],
        description=fields["Description"],
        content=content,
        edges=edges,
    )


def validate(node: AIPNode) -> List[str]:
    issues: List[str] = []
    if not node.node.startswith("aip://"):
        issues.append("Node should start with aip://")
    if not (node.fetch.startswith("http://") or node.fetch.startswith("https://") or node.fetch.startswith("file://")):
        issues.append("Fetch should be http(s):// or file:// for local demos")
    for e in node.edges:
        if e.kind not in {"NAV", "QRY", "ACT"}:
            issues.append(f"Edge {e.edge_id}: unknown kind {e.kind}")
        # method is flexible, but warn on common typos
        if not e.method.isalpha():
            issues.append(f"Edge {e.edge_id}: invalid method {e.method}")
    return issues
