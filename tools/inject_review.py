#!/usr/bin/env python3
"""Render kicad-happy analyzer JSON into a README summary block and a full report.

Used by .github/workflows/design-review.yml, but runnable locally:

    python3 tools/inject_review.py --sch-json sch.json --pcb-json pcb.json

Findings are grouped by rule_id so a detector that fires 24 times (one per LED)
occupies one row instead of 24. Rules listed in SUPPRESS are known false
positives for this board and are reported separately rather than silently
dropped -- see docs/design-review.md for the rationale.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

START = "<!-- kicad-happy:start -->"
END = "<!-- kicad-happy:end -->"

# rule_id -> why it does not apply to NeuralCard
SUPPRESS: dict[str, str] = {
    "LR-001": (
        "Charlieplexed matrix: R1-R6 limit current on the six shared GPIO drive "
        "lines, so no per-LED series resistor exists by design."
    ),
    "TE-001": "Business-card form factor; no test points by design.",
}

SEV_ORDER = ["critical", "error", "warning", "info"]
SEV_LABEL = {"critical": "Critical", "error": "Error", "warning": "Warning", "info": "Info"}


def load_findings(path: Path | None, source: str) -> list[dict]:
    if not path or not path.exists():
        return []
    data = json.loads(path.read_text())
    out = []
    for f in data.get("findings", []):
        f = dict(f)
        f["_src"] = source
        out.append(f)
    return out


def group(findings: list[dict]) -> list[dict]:
    """Collapse findings by rule_id, keeping the highest severity and a count."""
    buckets: dict[str, list[dict]] = defaultdict(list)
    for f in findings:
        buckets[f.get("rule_id", "?")].append(f)
    rows = []
    for rule, items in buckets.items():
        sev = min(items, key=lambda i: SEV_ORDER.index(i.get("severity", "info")))
        rows.append({
            "rule": rule,
            "severity": sev.get("severity", "info"),
            "count": len(items),
            "category": sev.get("category", ""),
            "summary": sev.get("summary") or sev.get("reason") or "",
            "src": sev["_src"],
        })
    rows.sort(key=lambda r: (SEV_ORDER.index(r["severity"]), -r["count"]))
    return rows


def sev_table(counts: Counter) -> list[str]:
    lines = ["| Severity | Count |", "|---|---|"]
    for s in SEV_ORDER:
        if counts.get(s):
            lines.append(f"| {SEV_LABEL[s]} | {counts[s]} |")
    lines.append(f"| **Total** | **{sum(counts.values())}** |")
    return lines


def findings_table(rows: list[dict], suppressed: bool) -> list[str]:
    lines = ["| Rule | Sev | N | Where | Finding |", "|---|---|---|---|---|"]
    for r in rows:
        if (r["rule"] in SUPPRESS) != suppressed:
            continue
        summary = r["summary"].replace("|", "\\|")[:110]
        lines.append(
            f"| `{r['rule']}` | {SEV_LABEL[r['severity']]} | {r['count']} "
            f"| {r['src']} | {summary} |"
        )
    return lines if len(lines) > 2 else []


def build_block(rows: list[dict], counts: Counter, adjusted: Counter) -> str:
    parts = [START, "", "### Automated design review", ""]
    parts.append(
        f"`kicad-happy` analysis of the schematic and PCB — **{sum(counts.values())} findings** "
        f"raw, **{sum(adjusted.values())}** after removing rules that do not apply to this "
        "board. Regenerated on every push."
    )
    parts += ["", "<table><tr><td>", ""]
    parts += sev_table(counts)
    parts += ["", "</td><td>", "", "**After suppression**", ""]
    parts += sev_table(adjusted)
    parts += ["", "</td></tr></table>", ""]

    active = findings_table(rows, suppressed=False)
    if active:
        parts += ["**Open findings**", ""] + active + [""]

    known = findings_table(rows, suppressed=True)
    if known:
        parts += [
            "<details><summary><b>Not applicable to this design</b> "
            f"({sum(r['count'] for r in rows if r['rule'] in SUPPRESS)} findings)</summary>",
            "",
        ] + known + [""]
        for rule, why in SUPPRESS.items():
            parts.append(f"- `{rule}` — {why}")
        parts += ["", "</details>", ""]

    parts += ["Full report: [`docs/design-review.md`](docs/design-review.md)", "", END]
    return "\n".join(parts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--sch-json", type=Path)
    ap.add_argument("--pcb-json", type=Path)
    ap.add_argument("--readme", type=Path, default=Path("README.md"))
    ap.add_argument("--report", type=Path, default=Path("docs/design-review.md"))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    findings = load_findings(args.sch_json, "sch") + load_findings(args.pcb_json, "pcb")
    if not findings:
        print("no findings parsed — check analyzer JSON paths")
        return 1

    rows = group(findings)
    counts = Counter(f.get("severity", "info") for f in findings)
    adjusted = Counter(
        f.get("severity", "info") for f in findings if f.get("rule_id") not in SUPPRESS
    )
    block = build_block(rows, counts, adjusted)

    readme = args.readme.read_text()
    if START in readme and END in readme:
        head, rest = readme.split(START, 1)
        _, tail = rest.split(END, 1)
        updated = head + block + tail
    else:
        updated = readme.rstrip() + "\n\n" + block + "\n"

    report = ["# NeuralCard — automated design review", "", "Generated by `kicad-happy`.", ""]
    report += sev_table(counts) + [""]
    report += ["## All findings by rule", ""]
    report += ["| Rule | Sev | N | Category | Where | Finding |", "|---|---|---|---|---|---|"]
    for r in rows:
        report.append(
            f"| `{r['rule']}` | {SEV_LABEL[r['severity']]} | {r['count']} | {r['category']} "
            f"| {r['src']} | {r['summary'].replace('|', chr(92) + '|')[:150]} |"
        )

    if args.dry_run:
        print(block)
        return 0

    args.readme.write_text(updated)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text("\n".join(report) + "\n")
    print(f"README block updated ({len(block)} chars); report -> {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
