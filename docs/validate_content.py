#!/usr/bin/env python3
"""Validate generated JSON under docs/raw for Andor's Trail / ATCS compatibility."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from at_format import (
    ACTOR_CONDITION_CATEGORIES,
    VALID_REQUIRE_TYPES,
    VALID_REWARD_TYPES,
)

RAW = Path(__file__).resolve().parent / "raw"


def check_conversations(path: Path, data: list) -> list[str]:
    errors = []
    ids: set[str] = set()
    for phrase in data:
        if not isinstance(phrase, dict):
            errors.append(f"{path.name}: conversation entry is not an object")
            continue
        pid = phrase.get("id")
        if not pid:
            errors.append(f"{path.name}: conversation missing id")
            continue
        if pid in ids:
            errors.append(f"{path.name}: duplicate conversation id {pid}")
        ids.add(pid)
        if "ID" in phrase:
            errors.append(f"{path.name}:{pid}: legacy field ID (use id)")
        if "text" in phrase and "message" not in phrase:
            errors.append(f"{path.name}:{pid}: legacy field text (use message)")
        for key in ("requirements", "actions", "chance", "successActions", "failureActions", "startCombat"):
            if key in phrase:
                errors.append(f"{path.name}:{pid}: legacy phrase field {key}")
        for reply in phrase.get("replies", []) or []:
            if "text" not in reply:
                errors.append(f"{path.name}:{pid}: reply missing text")
            if "nextPhraseID" not in reply:
                errors.append(f"{path.name}:{pid}: reply missing nextPhraseID")
            for req in reply.get("requires", []) or []:
                rt = req.get("requireType")
                if rt not in VALID_REQUIRE_TYPES:
                    errors.append(f"{path.name}:{pid}: invalid requireType {rt!r}")
            for rew in reply.get("rewards", []) or []:
                rt = rew.get("rewardType")
                if rt not in VALID_REWARD_TYPES:
                    errors.append(f"{path.name}:{pid}: invalid rewardType {rt!r}")
        for rew in phrase.get("rewards", []) or []:
            rt = rew.get("rewardType")
            if rt not in VALID_REWARD_TYPES:
                errors.append(f"{path.name}:{pid}: invalid phrase rewardType {rt!r}")
    return errors


def check_droplists(path: Path, data: list) -> list[str]:
    errors = []
    for dl in data:
        did = dl.get("id")
        if not did:
            errors.append(f"{path.name}: droplist missing id")
        for item in dl.get("items", []):
            if "itemID" not in item:
                errors.append(f"{path.name}:{did}: droplist item missing itemID")
            if "item" in item:
                errors.append(f"{path.name}:{did}: droplist item uses legacy key item")
            if "quantity" not in item:
                errors.append(f"{path.name}:{did}: droplist item missing quantity")
            if "chance" not in item:
                errors.append(f"{path.name}:{did}: droplist item missing chance")
    return errors


def check_quests(path: Path, data: list) -> list[str]:
    errors = []
    for quest in data:
        if "stages" not in quest:
            errors.append(f"{path.name}:{quest.get('id')}: quest missing stages")
        if "objectives" in quest:
            errors.append(f"{path.name}:{quest.get('id')}: quest uses legacy objectives")
        for stage in quest.get("stages", []):
            if "progress" not in stage or "logText" not in stage:
                errors.append(f"{path.name}:{quest.get('id')}: invalid quest stage")
    return errors


def check_actor_conditions(path: Path, data: list) -> list[str]:
    errors = []
    for cond in data:
        cid = cond.get("id")
        if not cond.get("category"):
            errors.append(f"{path.name}:{cid}: actor condition missing category")
        elif cond["category"] not in ACTOR_CONDITION_CATEGORIES:
            errors.append(f"{path.name}:{cid}: invalid category {cond['category']!r}")
        if "isNegative" in cond:
            errors.append(f"{path.name}:{cid}: legacy field isNegative")
    return errors


def check_items(path: Path, data: list) -> list[str]:
    errors = []
    for item in data:
        for field in ("id", "name", "category", "iconID"):
            if field not in item:
                errors.append(f"{path.name}:{item.get('id')}: item missing {field}")
    return errors


def check_monsters(path: Path, data: list) -> list[str]:
    errors = []
    for monster in data:
        mid = monster.get("id")
        for field in ("id", "name", "iconID"):
            if field not in monster:
                errors.append(f"{path.name}:{mid}: monster missing {field}")
        conv = monster.get("conversation", "")
        if conv and not conv.startswith("conversationlist_"):
            errors.append(f"{path.name}:{mid}: conversation must reference conversationlist_*")
    return errors


def validate_raw_dir(raw_dir: Path = RAW) -> list[str]:
    errors: list[str] = []
    for path in sorted(raw_dir.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"{path.name}: invalid JSON ({exc})")
            continue
        if not isinstance(data, list):
            errors.append(f"{path.name}: root must be a JSON array")
            continue
        name = path.name
        if name.startswith("conversationlist"):
            errors.extend(check_conversations(path, data))
        elif name.startswith("droplists"):
            errors.extend(check_droplists(path, data))
        elif name.startswith("questlist"):
            errors.extend(check_quests(path, data))
        elif name.startswith("actorconditions"):
            errors.extend(check_actor_conditions(path, data))
        elif name.startswith("itemlist"):
            errors.extend(check_items(path, data))
        elif name.startswith("monsterlist"):
            errors.extend(check_monsters(path, data))
    return errors


def main() -> int:
    errors = validate_raw_dir()
    if errors:
        print(f"Validation failed with {len(errors)} issue(s):", file=sys.stderr)
        for err in errors[:50]:
            print(f"  - {err}", file=sys.stderr)
        if len(errors) > 50:
            print(f"  ... and {len(errors) - 50} more", file=sys.stderr)
        return 1
    count = len(list(RAW.glob("*.json")))
    print(f"Validated {count} JSON files — all compatible with Andor's Trail / ATCS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
