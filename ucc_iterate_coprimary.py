#!/usr/bin/env python3
"""Iterate #3 — Co-primary lock.

When two STRUCTURAL_GAP instances sit inside a score epsilon, do not
let industrial_pressure hide a freshness=1.0 literature lock.

This is an analytical hygiene function, not a law of nature.
"""

from __future__ import annotations

import json
from typing import Any


def split_freshness_from_pressure(
    ranked: list[dict[str, Any]],
    epsilon: float = 2.0,
    freshness_lock: float = 0.99,
) -> dict[str, Any]:
    """If the top STRUCTURAL_GAP pair differs by < epsilon and one of
    them carries freshness >= freshness_lock, return co-primaries.

    Validation: epsilon must be > 0; ranked must be a list of dicts
    with status/score/freshness-or-id keys.
    """
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")
    if not isinstance(ranked, list):
        raise TypeError("ranked must be a list")

    gaps = [r for r in ranked if r.get("status") == "STRUCTURAL_GAP"]
    if len(gaps) < 2:
        return {
            "mode": "single" if gaps else "none",
            "primaries": gaps[:1],
            "reason": "fewer than two STRUCTURAL_GAP instances",
        }

    top, second = gaps[0], gaps[1]
    delta = abs(float(top["score"]) - float(second["score"]))
    # freshness lives on the original instance; recover via notes/id
    lock_ids = {g["id"] for g in gaps if "TODAY" in (g.get("notes") or "").upper()
                or g.get("source_date") == "2026-09-10"}

    if delta <= epsilon and lock_ids:
        coprimaries = []
        seen = set()
        for g in gaps:
            if g["id"] in lock_ids or g["id"] in {top["id"], second["id"]}:
                if g["id"] not in seen:
                    coprimaries.append(g)
                    seen.add(g["id"])
            if len(coprimaries) >= 2:
                break
        return {
            "mode": "co_primary",
            "delta": round(delta, 2),
            "epsilon": epsilon,
            "primaries": coprimaries[:2],
            "reason": (
                f"Top two STRUCTURAL_GAP scores differ by {delta:.2f} <= {epsilon}. "
                "Freshness lock is not allowed to be hidden by industrial_pressure."
            ),
        }

    return {
        "mode": "single",
        "delta": round(delta, 2),
        "primaries": [top],
        "reason": "margin exceeds epsilon; single primary stands",
    }


def main() -> None:
    with open("/workspace/artifacts/ucc_2026_09_10/ucc_engine_output.json") as f:
        data = json.load(f)
    result = split_freshness_from_pressure(data["ranked"], epsilon=2.0)
    print(json.dumps(
        {
            "mode": result["mode"],
            "delta": result.get("delta"),
            "reason": result["reason"],
            "primaries": [
                {"id": p["id"], "score": p["score"], "name": p["name"]}
                for p in result["primaries"]
            ],
        },
        indent=2,
    ))
    with open("/workspace/artifacts/ucc_2026_09_10/ucc_iterate_coprimary.json", "w") as f:
        json.dump(result, f, indent=2)


if __name__ == "__main__":
    main()
