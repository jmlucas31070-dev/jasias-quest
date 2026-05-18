"""Andor's Trail / ATCS JSON format helpers and normalizers."""

from __future__ import annotations

import copy
from typing import Any

VALID_REQUIRE_TYPES = {
    "questProgress",
    "questLatestProgress",
    "inventoryRemove",
    "inventoryKeep",
    "wear",
    "skillLevel",
    "killedMonster",
    "timerElapsed",
    "usedItem",
    "spentGold",
    "consumedBonemeals",
    "hasActorCondition",
    "random",
    "factionScore",
}

VALID_REWARD_TYPES = {
    "questProgress",
    "removeQuestProgress",
    "dropList",
    "skillIncrease",
    "actorCondition",
    "alignmentChange",
    "alignmentSet",
    "giveItem",
    "createTimer",
    "spawnAll",
    "removeSpawnArea",
    "deactivateSpawnArea",
    "activateMapObjectGroup",
    "deactivateMapObjectGroup",
    "changeMapFilter",
    "mapchange",
}

ACTOR_CONDITION_CATEGORIES = {"spiritual", "mental", "physical", "blood"}


def make_conv(cid: str, message: str, replies: list | None = None, rewards: list | None = None) -> dict:
    entry: dict[str, Any] = {"id": cid, "message": message}
    if replies:
        entry["replies"] = replies
    if rewards:
        entry["rewards"] = rewards
    return entry


def req_inv_keep(item_id: str, qty: int = 1) -> dict:
    return {"requireType": "inventoryKeep", "requireID": item_id, "value": qty}


def req_inv_remove(item_id: str, qty: int = 1) -> dict:
    return {"requireType": "inventoryRemove", "requireID": item_id, "value": qty}


def req_random(chance_pct: int) -> dict:
    return {"requireType": "random", "requireID": str(chance_pct)}


def req_quest_progress(quest_id: str, progress: int | str) -> dict:
    return {"requireType": "questProgress", "requireID": quest_id, "value": progress}


def req_actor_condition(condition_id: str) -> dict:
    return {"requireType": "hasActorCondition", "requireID": condition_id}


def r_give_item(item_id: str, qty: int = 1) -> dict:
    return {"rewardType": "giveItem", "rewardID": item_id, "value": qty}


def r_quest_progress(quest_id: str, progress: int | str) -> dict:
    return {"rewardType": "questProgress", "rewardID": quest_id, "value": progress}


def r_drop_list(droplist_id: str) -> dict:
    return {"rewardType": "dropList", "rewardID": droplist_id}


def r_actor_condition(condition_id: str, duration: int = 999) -> dict:
    return {"rewardType": "actorCondition", "rewardID": condition_id, "value": duration}


def r_mapchange(place: str, map_name: str) -> dict:
    return {"rewardType": "mapchange", "rewardID": place, "mapName": map_name}


def drop_item(item_id: str, chance: str | int = "100", qty_min: int = 1, qty_max: int = 1) -> dict:
    return {
        "itemID": item_id,
        "chance": str(chance),
        "quantity": {"min": qty_min, "max": qty_max},
    }


def quest_stage(progress: int, log_text: str, reward_xp: int = 0, finishes: int = 0) -> dict:
    stage = {"progress": progress, "logText": log_text}
    if reward_xp:
        stage["rewardExperience"] = reward_xp
    if finishes:
        stage["finishesQuest"] = finishes
    return stage


def make_quest(qid: str, name: str, stages: list, show_in_log: int = 1) -> dict:
    return {"id": qid, "name": name, "showInLog": show_in_log, "stages": stages}


def _legacy_item_requirements(items: list) -> list[dict]:
    requires = []
    for entry in items:
        if isinstance(entry, dict):
            item_id = entry.get("itemID") or entry.get("item")
            qty = entry.get("quantity", 1)
        else:
            item_id = entry
            qty = 1
        if item_id:
            requires.append(req_inv_keep(item_id, qty))
    return requires


def _legacy_item_removals(items: list) -> list[dict]:
    requires = []
    for entry in items:
        if isinstance(entry, dict):
            item_id = entry.get("itemID") or entry.get("item")
            qty = entry.get("quantity", 1)
        else:
            item_id = entry
            qty = 1
        if item_id:
            requires.append(req_inv_remove(item_id, qty))
    return requires


def _legacy_actions_to_rewards(actions: list) -> list[dict]:
    rewards = []
    for action in actions:
        if not isinstance(action, dict):
            continue
        if "giveItem" in action:
            rewards.append(r_give_item(action["giveItem"], action.get("quantity", 1)))
        if "removeItem" in action:
            # handled as requires on reply, not reward
            pass
        if "completeQuestObjectives" in action:
            for obj in action["completeQuestObjectives"]:
                if isinstance(obj, str):
                    if obj.startswith("quest_"):
                        rewards.append(r_quest_progress(obj, 100))
                    elif "_league_progress" in obj:
                        region = obj.split("_")[0]
                        rewards.append(r_quest_progress(f"quest_{region}_league", 100))
    return rewards


def normalize_reply(reply: dict) -> dict:
    out = copy.deepcopy(reply)
    if "requires" not in out:
        out["requires"] = []

    if "requiresItems" in out:
        out["requires"].extend(_legacy_item_requirements(out.pop("requiresItems")))
    if "consumeItems" in out:
        out["requires"].extend(_legacy_item_removals(out.pop("consumeItems")))

    if "requiresQuestProgress" in out:
        for obj in out.pop("requiresQuestProgress"):
            if isinstance(obj, str):
                if obj.startswith("beast_"):
                    out["requires"].append(req_inv_keep(f"item_{obj}"))
                elif obj.startswith("item_"):
                    out["requires"].append(req_inv_keep(obj))
                else:
                    out["requires"].append(req_inv_keep(obj))

    if "rewardItems" in out:
        out.setdefault("rewards", [])
        for entry in out.pop("rewardItems"):
            item_id = entry.get("itemID") or entry.get("item")
            if item_id:
                out["rewards"].append(r_give_item(item_id, entry.get("quantity", 1)))

    if "startQuest" in out:
        out.setdefault("rewards", [])
        out["rewards"].append(r_quest_progress(out.pop("startQuest"), 10))

    if "completeQuestObjectives" in out:
        out.setdefault("rewards", [])
        out["rewards"].extend(_legacy_actions_to_rewards([{"completeQuestObjectives": out.pop("completeQuestObjectives")}]))

    if "rewardConditions" in out:
        out.setdefault("rewards", [])
        for cond in out.pop("rewardConditions"):
            out["rewards"].append(
                r_actor_condition(cond.get("conditionID", ""), cond.get("duration", 999))
            )

    if not out["requires"]:
        out.pop("requires", None)
    if "rewards" in out and not out["rewards"]:
        out.pop("rewards", None)
    return out


def make_capture_conversation_set(beast_id: str, beast_name: str, item_id: str, capture_rate: int) -> list[dict]:
    """Build capture / fight / flee dialogue set for one wild beast."""
    conv_id = f"conv_{beast_id}"
    catch_roll = f"catch_{beast_id}_roll"
    catch_ok = f"catch_{beast_id}_ok"
    catch_fail = f"catch_{beast_id}_fail"
    return [
        make_conv(
            conv_id,
            f"A wild {beast_name} stands before you.",
            [
                {"text": "Use Spirit Orb.", "nextPhraseID": catch_roll},
                {"text": "Fight.", "nextPhraseID": "F"},
                {"text": "Leave.", "nextPhraseID": "X"},
            ],
        ),
        make_conv(
            catch_roll,
            "",
            [
                {
                    "text": "N",
                    "nextPhraseID": catch_ok,
                    "requires": [req_random(capture_rate), req_inv_remove("spirit_orb_basic")],
                },
                {
                    "text": "N",
                    "nextPhraseID": catch_fail,
                    "requires": [req_inv_remove("spirit_orb_basic")],
                },
            ],
        ),
        make_conv(
            catch_ok,
            f"You captured {beast_name}!",
            [{"text": "Excellent.", "nextPhraseID": "R"}],
            rewards=[r_give_item(item_id), r_quest_progress("quest_catch_them_all", 10)],
        ),
        make_conv(
            catch_fail,
            f"{beast_name} broke free!",
            [{"text": "Drat.", "nextPhraseID": "X"}],
        ),
    ]


def _normalize_capture_phrase(phrase: dict) -> list[dict]:
    """Convert legacy capture phrase (chance/successActions/failureActions) to AT selectors."""
    pid = phrase.get("id") or phrase.get("ID")
    beast_name = (phrase.get("text") or phrase.get("message", "")).replace("You throw a Spirit Orb at ", "").strip(".")
    capture_rate = phrase.get("chance", 50)
    success_actions = phrase.get("successActions", [])
    failure_actions = phrase.get("failureActions", [])

    item_id = None
    beast_id = None
    for action in success_actions:
        if action.get("giveItem"):
            item_id = action["giveItem"]
        if action.get("destroyMonster"):
            beast_id = action["destroyMonster"]

    roll_id = f"{pid}_roll" if not pid.endswith("_roll") else pid
    ok_id = f"{pid}_ok"
    fail_id = f"{pid}_fail"

    ok_rewards = [r_give_item(item_id)] if item_id else []
    if beast_id:
        ok_rewards.append({"rewardType": "questProgress", "rewardID": "quest_catch_them_all", "value": 10})

    phrases = [
        make_conv(
            roll_id,
            "",
            [
                {
                    "text": "N",
                    "nextPhraseID": ok_id,
                    "requires": [req_random(capture_rate), req_inv_remove("spirit_orb_basic")],
                },
                {
                    "text": "N",
                    "nextPhraseID": fail_id,
                    "requires": [req_inv_remove("spirit_orb_basic")],
                },
            ],
        ),
        make_conv(
            ok_id,
            f"You captured {beast_name}!" if beast_name else "Capture successful!",
            [{"text": "Excellent.", "nextPhraseID": "R"}],
            rewards=ok_rewards,
        ),
        make_conv(
            fail_id,
            f"{beast_name} broke free!" if beast_name else "The beast broke free!",
            [{"text": "Drat.", "nextPhraseID": "X"}],
        ),
    ]
    return phrases


def normalize_crafting_phrase(phrase: dict) -> dict:
    pid = phrase.get("id") or phrase.get("ID")
    message = phrase.get("message") or phrase.get("text", "")
    requires = []
    for item in phrase.get("inventoryItems", []):
        requires.append(req_inv_remove(item["itemID"], item.get("quantity", 1)))
    for cond in phrase.get("actorConditions", []):
        requires.append(req_actor_condition(cond.get("condition", "")))
    rewards = []
    rew = phrase.get("rewards")
    if isinstance(rew, dict) and "items" in rew:
        for item in rew["items"]:
            rewards.append(r_give_item(item["itemID"], item.get("quantity", 1)))
    elif isinstance(rew, list):
        rewards = rew
    reply = {"text": "Craft", "nextPhraseID": "X"}
    if requires:
        reply["requires"] = requires
    if rewards:
        reply["rewards"] = rewards
    return make_conv(pid, message, [reply])


def normalize_phrase(phrase: dict) -> dict | list[dict]:
    if isinstance(phrase.get("rewards"), dict) or "inventoryItems" in phrase:
        return normalize_crafting_phrase(phrase)
    if phrase.get("chance") is not None and phrase.get("successActions") is not None:
        return _normalize_capture_phrase(phrase)

    pid = phrase.get("id") or phrase.get("ID")
    message = phrase.get("message")
    if message is None:
        message = phrase.get("text", "")

    legacy_reqs = phrase.get("requirements") or []
    legacy_actions = phrase.get("actions") or []

    normalized_reqs = []
    for req in legacy_reqs:
        if isinstance(req, dict) and "requireType" in req:
            normalized_reqs.append(req)
        elif isinstance(req, dict) and "item" in req:
            normalized_reqs.append(req_inv_keep(req["item"], req.get("quantity", 1)))

    normalized_rewards = _legacy_actions_to_rewards(legacy_actions)
    for action in legacy_actions:
        if isinstance(action, dict) and action.get("removeItem"):
            normalized_reqs.append(req_inv_remove(action["removeItem"], action.get("quantity", 1)))

    replies = [normalize_reply(r) for r in phrase.get("replies", []) or []]
    if normalized_reqs or normalized_rewards:
        for reply in replies:
            if reply.get("text") in ("Evolve my beast.", "Breed them.", "Attempt capture"):
                reply.setdefault("requires", [])
                reply["requires"].extend(copy.deepcopy(normalized_reqs))
                reply.setdefault("rewards", [])
                reply["rewards"].extend(copy.deepcopy(normalized_rewards))

    if phrase.get("startCombat"):
        replies = [{"text": "Fight!", "nextPhraseID": "F"}]

    out = make_conv(pid, message, replies or None, phrase.get("rewards"))
    if "rewards" in phrase and phrase["rewards"]:
        out["rewards"] = phrase["rewards"]
    return out


def normalize_phrase_list(phrases: list) -> list[dict]:
    out: list[dict] = []
    for phrase in phrases:
        normalized = normalize_phrase(phrase)
        if isinstance(normalized, list):
            out.extend(normalized)
        else:
            out.append(normalized)
    return out


def normalize_droplist_entry(entry: dict) -> dict:
    out = copy.deepcopy(entry)
    items = []
    for item in out.get("items", []):
        item = copy.deepcopy(item)
        if "itemID" not in item and "item" in item:
            item["itemID"] = item.pop("item")
        items.append(item)
    out["items"] = items
    return out


def normalize_quest(entry: dict) -> dict:
    if "stages" in entry:
        return entry
    objectives = entry.get("objectives", [])
    out = {
        "id": entry["id"],
        "name": entry["name"],
        "showInLog": entry.get("showInLog", 1),
        "stages": [],
    }
    desc = entry.get("description")
    if desc:
        out["stages"].append(quest_stage(10, desc))
    if len(objectives) > 20:
        out["stages"].append(
            quest_stage(
                50,
                f"Progress on {entry['name']}: catch creatures across the world.",
            )
        )
        out["stages"].append(
            quest_stage(
                1000,
                f"Completed {entry['name']}.",
                reward_xp=5000,
                finishes=1,
            )
        )
    else:
        for i, obj in enumerate(objectives):
            obj_id = obj.get("id", "")
            out["stages"].append(
                quest_stage(20 + i, obj.get("name", obj_id))
            )
        if entry.get("rewards"):
            out["stages"].append(
                quest_stage(1000, f"Completed {entry['name']}.", reward_xp=500, finishes=1)
            )
    if not out["stages"]:
        out["stages"].append(quest_stage(10, entry["name"]))
    return out


def normalize_actor_condition(entry: dict) -> dict:
    out = copy.deepcopy(entry)
    if "category" not in out:
        out["category"] = "mental"
    if "isNegative" in out and "isPositive" not in out:
        out["isPositive"] = 0 if out.pop("isNegative") else 1
    effect = out.get("abilityEffect")
    if isinstance(effect, dict):
        if "increaseArmor" in effect:
            effect["increaseDamageResistance"] = effect.pop("increaseArmor")
        if "increaseDefense" in effect:
            effect["increaseBlockChance"] = effect.pop("increaseDefense")
    return out


def _conversationlist_for_legacy(conv: str) -> str:
    if conv.startswith("conversationlist_"):
        return conv
    if conv.startswith("conversation_professor"):
        return "conversationlist_professor"
    if conv.startswith("conversation_breed_") or "_breeder" in conv:
        for region in (
            "lumia", "kranix", "ignora", "hesperia", "lucidiah",
            "illystrius", "sejor", "bellom", "dorado",
        ):
            if region in conv:
                return f"conversationlist_breeding_{region}"
    for region in (
        "lumia", "kranix", "ignora", "hesperia", "lucidiah",
        "illystrius", "sejor", "bellom", "dorado",
    ):
        if f"conversation_{region}" in conv or conv.startswith(f"{region}_"):
            if "league" in conv or conv.endswith("_league_intro") or conv.endswith("_league_complete"):
                return "conversationlist_region"
            if "evolution" in conv or "evolve" in conv or "scholar" in conv:
                return f"conversationlist_{region}"
            if "shopkeeper" in conv:
                return "conversationlist_shop"
    if conv.startswith("conversation_"):
        return "conversationlist_beast"
    return f"conversationlist_{conv}"


def normalize_monster(entry: dict) -> dict:
    out = copy.deepcopy(entry)
    out_id = out.get("id", "")
    conv = out.get("conversation", "")
    if conv and not conv.startswith("conversationlist_"):
        out["conversation"] = _conversationlist_for_legacy(conv)
    if not out.get("phraseID"):
        if out_id.startswith("beast_"):
            out["phraseID"] = f"conv_{out_id}"
        elif conv.startswith("conversation_"):
            out["phraseID"] = conv.replace("conversation_", "conv_", 1)
        elif conv.startswith("conversationlist_"):
            list_name = conv.replace("conversationlist_", "")
            out["phraseID"] = f"conv_{out_id}" if out_id else None
            if out.get("phraseID") is None and list_name:
                out["phraseID"] = f"conv_{out_id}"
    if out.get("phraseID") is None:
        out.pop("phraseID", None)
    out.pop("rarity", None)
    return out


def normalize_content(filename: str, data: list) -> list:
    if not isinstance(data, list):
        return data

    if filename.startswith("droplists"):
        return [normalize_droplist_entry(x) for x in data]
    if filename.startswith("conversationlist"):
        return normalize_phrase_list(data)
    if filename.startswith("questlist"):
        return [normalize_quest(x) for x in data]
    if filename.startswith("actorconditions"):
        return [normalize_actor_condition(x) for x in data]
    if filename.startswith("monsterlist"):
        return [normalize_monster(x) for x in data]
    return data


def write_json(path, data) -> None:
    import json
    from pathlib import Path

    p = Path(path)
    normalized = normalize_content(p.name, data)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=4)
