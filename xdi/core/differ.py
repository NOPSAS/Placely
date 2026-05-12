"""
XDi Differ
Sammenligner to SlimBIM-dokumenter og returnerer strukturerte endringer.
Nyttig for å finne forskjellen mellom "sist godkjent" og "as_built".
"""
from typing import Any


def diff_slimbim(base: dict, updated: dict) -> dict:
    """
    Sammenlign to SlimBIM-dokumenter.
    Returnerer:
      {
        "added":   [...],   # nye objekter i 'updated'
        "removed": [...],   # fjernede objekter fra 'base'
        "changed": [...],   # objekter som er endret
        "summary": {...}    # oppsummering
      }
    """
    added   = []
    removed = []
    changed = []

    base_walls    = _index_by_id(_collect(base,    "walls"))
    updated_walls = _index_by_id(_collect(updated, "walls"))

    base_rooms    = _index_by_id(_collect(base,    "rooms"))
    updated_rooms = _index_by_id(_collect(updated, "rooms"))

    # Vegger
    for wid, wall in updated_walls.items():
        if wid not in base_walls:
            added.append({"type": "wall", "id": wid, "data": wall})
        else:
            diffs = _field_diff(base_walls[wid], wall)
            if diffs:
                changed.append({"type": "wall", "id": wid, "changes": diffs})

    for wid in base_walls:
        if wid not in updated_walls:
            removed.append({"type": "wall", "id": wid})

    # Rom
    for rid, room in updated_rooms.items():
        if rid not in base_rooms:
            added.append({"type": "room", "id": rid, "data": room})
        else:
            diffs = _field_diff(base_rooms[rid], room)
            if diffs:
                changed.append({"type": "room", "id": rid, "changes": diffs})

    for rid in base_rooms:
        if rid not in updated_rooms:
            removed.append({"type": "room", "id": rid})

    return {
        "added":   added,
        "removed": removed,
        "changed": changed,
        "summary": {
            "total_added":   len(added),
            "total_removed": len(removed),
            "total_changed": len(changed),
            "has_changes":   bool(added or removed or changed),
        },
    }


def _collect(doc: dict, entity_type: str) -> list[dict]:
    results = []
    for building in doc.get("property", {}).get("buildings", []):
        for floor in building.get("floors", []):
            results.extend(floor.get(entity_type, []))
    return results


def _index_by_id(items: list[dict]) -> dict[str, dict]:
    return {item["id"]: item for item in items if "id" in item}


def _field_diff(old: dict, new: dict) -> list[dict]:
    diffs = []
    all_keys = set(old.keys()) | set(new.keys())
    for key in all_keys:
        ov = old.get(key)
        nv = new.get(key)
        if ov != nv:
            diffs.append({"field": key, "from": ov, "to": nv})
    return diffs
