# Bank Pack — Developer Guide

A self-contained content overlay for the
[jasias-quest](https://github.com/jmlucas31070-dev/jasias-quest) fork of
Andor's Trail. Adds a universal banking system: deposit/withdraw, loans,
lockbox storage, and droplist-backed mystery caches. Every branch shares
a single ledger because all state lives on the player (inventory items +
quest progress).

---

## File layout

```
res/
  values/
    loadresources.xml          # additive — merge into existing
    strings.xml                # additive — merge into existing
  xml/
    worldmap.xml               # additive — merge into existing
    westgate_market.tmx        # MODIFIED (replaces existing)
    jq_bank_template.tmx       # NEW — reusable interior, copy per city
    jq_bank_westgate.tmx       # NEW — Westgate branch (wired)
    jq_bank_ados.tmx           # NEW — placeholder host map, ready to wire
    jq_bank_crossglen.tmx      # NEW — placeholder host map, ready to wire
    jq_bank_fallhaven.tmx      # NEW — placeholder host map, ready to wire
    jq_bank_vilegard.tmx       # NEW — placeholder host map, ready to wire
  raw/
    jq_bank_items.json
    jq_bank_droplists.json
    jq_bank_actorconditions.json   (empty for now; reserved)
    jq_bank_monsters.json
    jq_bank_quests.json
    jq_bank_itemcategories.json
    jq_bank_conversationlists.json
    jq_bank_maps.json
README_DEV.md
README_PLAYER.md
```

All new resource IDs use the `jq_` prefix (`jq_bank_*`, `jq_voucher_*`,
`jq_note_*`, `jq_good_*`, `jq_npc_bank_*`, `jq_quest_bank*`). No vanilla
or Westgate IDs are touched.

---

## Maps changed

| File | Change | Why |
|---|---|---|
| `res/xml/westgate_market.tmx` | **Modified.** Three new objects appended to the `eventLayer`: a `MapChange` door (`jq_bank_westgate_door` at `x=864 y=288`), a Sign above it (`jq_bank_westgate_sign`), and a return MapChange spawn (`from_jq_bank_westgate`). All vanilla objects untouched. | The bank entry on the south-east stall row, with a sign above the door and a landing tile right outside it that the bank's south exit drops you onto. |
| `res/xml/jq_bank_template.tmx` | **New.** 16×12 indoor map, 32px tiles, `indoor1.tsx` + `objects1.tsx`. South wall has a 2-tile door gap. eventLayer has: south `MapChange exit` (placeholder host), three `Spawn` NPCs (banker, clerk, guard), one `Sign`. | The reusable interior. To drop a branch into a new city: copy this file to `jq_bank_<city>.tmx`, set the exit's `map`/`place` to point at your host map, set the signpost string to `@string/jq_bank_signpost_<city>`, and add a matching MapChange door on the host map. |
| `res/xml/jq_bank_<city>.tmx` (5 files) | **New.** Same as template, but with the city's host map name baked into the south exit and the sign string keyed to that branch. Westgate is wired; the others have `PLACEHOLDER_HOST_MAP` so they're a drop-in away. | Per-city instances all use the same banker monsterType (`jq_npc_banker`) and therefore the same conversation tree, so all banks share state. |
| `res/xml/worldmap.xml` | **Additive.** One `<map>` per new bank interior. | Required by the engine to resolve worldmap coordinates. |

---

## Mechanics

### Account / membership card

- Quest `jq_quest_bank_member` tracks "have you joined" (`progress=0` no, `1` yes).
- The first reply in `jq_banker_main` requires `progress=0`. Picking it sets
  progress to 1 and gives the player one **Bank Membership Card** (item
  `jq_bank_card`, `iconID=items_misc:01`).
- Every other top-level reply requires `inventoryKeep` of the card. So if
  the player drops the card they can re-open an account by the same flow.

### Currency: bank notes

- Seven denominations: `jq_note_10`, `jq_note_50`, `jq_note_100`,
  `jq_note_500`, `jq_note_1000`, `jq_note_5000`, `jq_note_10000`.
- Deposit: reply requires `inventory_remove` of N gold and rewards 1
  matching note. Withdraw: requires `inventory_remove` of 1 note and
  rewards N gold. **Par for par** — no fee. Notes have a `baseMarketCost`
  equal to their face value, so a player who tries to sell one to a
  shopkeep gets the same value (intentional).
- Because notes are inventory items, they automatically work at every
  branch.

### Loans

- One quest, `jq_quest_bank`, tracks the active loan via its progress stage.
  - `0` — no loan
  - `10` — small (borrowed 100, owe 110)
  - `20` — medium (borrowed 500, owe 550)
  - `30` — large (borrowed 1000, owe 1100)
  - `40` — huge (borrowed 5000, owe 5500)
  - `99` — repaid (transient — the "back" reply on `jq_bank_loan_paid`
    immediately resets to 0 so the player can borrow again)
- "Take" replies require `progress=0`; they set progress to the tier and
  reward the principal.
- "Repay" replies require the matching tier *and* `inventory_remove` of
  the owed amount; they set progress to 99.
- "Status" branches by the same `progress` requires to display the
  appropriate string.
- Single active loan only. Trying to borrow with one outstanding fails
  the `progress=0` requirement and the reply is hidden by the engine.

### Lockbox

Three sub-flows under the lockbox menu:

1. **Deposit a valuable.** For each of the 16 storable items
   (`jq_good_<id>`), a reply consumes the item and gives a matching
   voucher (`jq_voucher_<id>`). Vouchers are inventory items, so the
   player can carry them between branches.
2. **Redeem a voucher.** For each storable, a reply consumes the matching
   voucher and rewards via the per-item droplist (`jq_bank_drop_<id>`).
   Each droplist guarantees the original item back at 100% chance — the
   indirection is intentional. **This is the "have the bank save the
   droplist information and produce the items when removed" requirement
   in this pack: every redeem is a droplist roll, and the droplist is
   what the bank "remembered" for that slot.** It also lets you change
   payouts later (e.g., add bonus items, randomise) by editing only
   `jq_bank_droplists.json`, without touching any conversation.
3. **Mystery Cache.** Buy a `jq_voucher_cache` for 50 gold, then redeem
   it for a roll on `jq_bank_drop_cache`. That droplist contains a base
   25–200 gold drop plus weighted chances at gems, scrolls, and even
   small bank notes — a real-time droplist payout from a deposited slip.

### NPCs

Three monsters defined in `jq_bank_monsters.json`:

- `jq_npc_banker` — `phraseID=jq_banker_main`. The full menu lives here.
- `jq_npc_bank_clerk` — `phraseID=jq_clerk_main`. Small talk + rates.
- `jq_npc_bank_guard` — `phraseID=jq_guard_main`. Atmosphere only.

All three have `combatTraits.maxHP=1` and `attacksPerTurn=0` so the
engine treats them as harmless civilians (same pattern existing
Westgate stall NPCs use).

---

## How to wire a bank into a new city

1. Copy `jq_bank_template.tmx` to `jq_bank_<city>.tmx`.
2. Edit the south exit's `MapChange` properties:
   ```xml
   <property name="map"   value="<your_host_map>"/>
   <property name="place" value="from_jq_bank_<city>"/>
   ```
3. Edit the signpost message to `@string/jq_bank_signpost_<city>` and add
   the matching string in `strings.xml`.
4. On `<your_host_map>.tmx`, add **one** `MapChange` door pointing at
   `jq_bank_<city>` with `place=entry` (the template uses `entry` as the
   landing place inside the bank), and one `MapChange` named
   `from_jq_bank_<city>` for the player to land on after leaving.
5. Add `<map name="jq_bank_<city>" .../>` in `worldmap.xml`.
6. Add `<item>@raw/jq_bank_maps</item>` in `loadresources.xml` if not
   already present (it is in this pack).

That's it. Because the new bank uses the same `jq_npc_banker` monsterType,
its banker shares conversation, ledger, lockbox vouchers, and loan state
with every other branch.

---

## Installation

1. Copy this `res/` tree on top of `AndorsTrail/res/` in your fork.
2. Merge each `<array>` from `values/loadresources.xml` into the matching
   array in your existing `loadresources.xml` (additive — append the
   new `<item>` lines).
3. Merge the new `<string>` entries from `values/strings.xml` into your
   existing `strings.xml`.
4. Merge each `<map>` entry from `xml/worldmap.xml` into your existing
   `worldmap.xml`.
5. Replace `res/xml/westgate_market.tmx` with the version in this pack
   (only object-layer additions; the ground/object/above layers and
   nextobjectid are unchanged).
6. Rebuild the APK from Android Studio.

---

## Stats

- 41 items (1 membership card, 7 notes, 16 storable valuables, 16
  matching vouchers, 1 mystery cache voucher)
- 17 droplists (1 mystery cache + 16 per-storable redemption droplists)
- 3 NPCs
- 22 conversation phrases
- 2 quests (loan ledger + membership marker)
- 6 maps (1 template + 5 city branches)
- 116 strings
