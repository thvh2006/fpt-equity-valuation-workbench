#!/usr/bin/env python3
"""Check official research pages for availability and material HTML changes."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "configs" / "live_sources.json"
DEFAULT_OUTPUT = PROJECT_ROOT / "reports" / "live_source_status.json"


class VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hidden_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.hidden_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in {"script", "style", "noscript", "svg"} and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self.hidden_depth:
            self.parts.append(data)


def normalised_text(payload: bytes) -> str:
    parser = VisibleTextParser()
    parser.feed(payload.decode("utf-8", errors="ignore"))
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def monitored_text(payload: bytes, source: dict) -> str:
    """Limit article checks to issuer evidence, excluding rotating news and site chrome."""
    text = normalised_text(payload)
    start_marker = source.get("content_start")
    end_marker = source.get("content_end")
    if start_marker:
        start = text.find(start_marker)
        if start < 0:
            raise ValueError(f"content_start marker not found: {start_marker}")
        text = text[start:]
    if end_marker:
        end = text.find(end_marker)
        if end < 0:
            raise ValueError(f"content_end marker not found: {end_marker}")
        text = text[:end]
    return text.strip()


def fetch(source: dict) -> tuple[int, str]:
    request = urllib.request.Request(source["url"], headers={"User-Agent": "FPT-equity-research-monitor/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = response.read()
        evidence = monitored_text(payload, source)
        return response.status, sha256(evidence.encode("utf-8")).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--fail-on-change", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    results = []
    for source in config["sources"]:
        try:
            status, fingerprint = fetch(source)
            baseline = source.get("baseline_sha256", "")
            changed = bool(baseline) and fingerprint != baseline
            results.append({**source, "http_status": status, "current_sha256": fingerprint, "changed": changed, "error": None})
        except Exception as exc:
            results.append({**source, "http_status": None, "current_sha256": None, "changed": False, "error": str(exc)})

    output = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "changed_count": sum(bool(item["changed"]) for item in results),
        "error_count": sum(bool(item["error"]) for item in results),
        "sources": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))
    if args.fail_on_change and (output["changed_count"] or output["error_count"]):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
