// Generate region TMX files + Tiled world (.world) files for Astral Beasts.
//
// Produces:
//   res/xml/ab_<region>_<sub>.tmx        — 5 maps per region × 8 regions = 40 TMX files
//                                          (region 0 / Emberlands fully authored,
//                                           regions 1–7 are functional skeletons)
//   res/xml/level_<n>.world              — 8 Tiled world files, level_0 .. level_7
//
// Each TMX is 16×12 tiles at 32px = 512×384 px. World files arrange the five
// sub-maps of one region per .world file in a fixed layout:
//
//                                    [gym 2,-1]
//   [center 0,0] -- [route 1,0] -- [        2,0] -- [champion 3,0]
//                                    [hideout 2,1]
//
// The (2,0) cell is intentionally empty so that gym (north) and hideout (south)
// flank the route's terminus. Adjust freely in Tiled.

import { writeFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const XML = join(__dirname, "..", "res", "xml");
mkdirSync(XML, { recursive: true });

// Mirrored from generate.mjs — kept in sync by hand.
const REGIONS = [
  { id: "ember",   name: "Emberlands",   clade: "Cinderkin", element: "fire",      tier: 1, town: "Ashbridge",    gymLeader: "Pyralis",   champion: "Ignara",   teamAdmin: "Solrin"   },
  { id: "tide",    name: "Tideholm",     clade: "Tidefolk",  element: "water",     tier: 2, town: "Saltspire",    gymLeader: "Marenna",   champion: "Coralax",  teamAdmin: "Brackwell"},
  { id: "verdant", name: "Verdant Reach",clade: "Verdant",   element: "grass",     tier: 3, town: "Mossglen",     gymLeader: "Ferna",     champion: "Sylvane",  teamAdmin: "Thornell" },
  { id: "storm",   name: "Stormcrest",   clade: "Stormborn", element: "lightning", tier: 4, town: "Boltreach",    gymLeader: "Volta",     champion: "Tempyx",   teamAdmin: "Kestrel"  },
  { id: "frost",   name: "Frostvale",    clade: "Rimekin",   element: "ice",       tier: 5, town: "Hoarwatch",    gymLeader: "Crysell",   champion: "Glacira",  teamAdmin: "Borissa"  },
  { id: "stone",   name: "Stoneheart",   clade: "Geokin",    element: "earth",     tier: 6, town: "Granitemarch", gymLeader: "Korran",    champion: "Tellurik", teamAdmin: "Quarrick" },
  { id: "dusk",    name: "Duskwood",     clade: "Shadeborn", element: "shadow",    tier: 7, town: "Hollowfen",    gymLeader: "Nyxara",    champion: "Umbros",   teamAdmin: "Vellis"   },
  { id: "aether",  name: "Aetherspire",  clade: "Aetherborn",element: "light",     tier: 8, town: "Highmere",     gymLeader: "Solarya",   champion: "Lumiel",   teamAdmin: "Halen"    },
];
// Voidmarsh (region 9) is the endgame zone; it has its own TMX skeletons (so
// ab_maps.json resolves) but is not bundled into a .world file.
const ENDGAME = { id: "void", name: "Voidmarsh", clade: "Wyrmkin", element: "void", tier: 9, town: "Greylight", gymLeader: "Morrigane", champion: "Voidrak", teamAdmin: "Sablehex" };

const W = 16, H = 12, TILE = 32;
const PX_W = W * TILE, PX_H = H * TILE;

// ---------------------------------------------------------------------------
// TMX building blocks
// ---------------------------------------------------------------------------

function csvGround(fillTile) {
  const row = Array(W).fill(fillTile).join(",");
  const rows = [];
  for (let y = 0; y < H; y++) rows.push(row);
  return rows.join(",\n") + ",";
}

// "Rich" ground pattern: small palette of tile IDs from indoor1.tsx (firstgid 1)
// laid in a stable, readable pattern instead of one uniform tile. Border row
// uses tile 17 ("wall/edge") and the body alternates tiles 1 and 2 in a stripe
// so that opening one of the rich maps in Tiled shows real tile structure
// rather than a single solid color.
function csvGroundRich() {
  const rows = [];
  for (let y = 0; y < H; y++) {
    const cells = [];
    for (let x = 0; x < W; x++) {
      if (y === 0 || y === H - 1 || x === 0 || x === W - 1) {
        cells.push(17);                       // border
      } else if ((x + y) % 2 === 0) {
        cells.push(1);                        // body A
      } else {
        cells.push(2);                        // body B
      }
    }
    rows.push(cells.join(","));
  }
  return rows.join(",\n") + ",";
}

// "Above"-layer decoration tiles drawn from objects1.tsx (firstgid 257). Used
// only in rich maps. Each entry is { tx, ty, tile } where tile is the global
// tile id (firstgid + local index).
function aboveLayerCSV(decorations) {
  const grid = Array.from({ length: H }, () => Array(W).fill(0));
  for (const d of decorations) {
    if (d.tx >= 0 && d.tx < W && d.ty >= 0 && d.ty < H) grid[d.ty][d.tx] = d.tile;
  }
  return grid.map(row => row.join(",")).join(",\n") + ",";
}

function tmxOpen(nextObjectId) {
  return `<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0" tiledversion="1.4.3" orientation="orthogonal"
     renderorder="right-down" width="${W}" height="${H}"
     tilewidth="${TILE}" tileheight="${TILE}" infinite="0"
     nextlayerid="5" nextobjectid="${nextObjectId}">
  <tileset firstgid="1"   source="indoor1.tsx"/>
  <tileset firstgid="257" source="objects1.tsx"/>
`;
}

function layers(ground = 1, opts = {}) {
  const groundData = opts.rich ? csvGroundRich() : csvGround(ground);
  const aboveData  = opts.decorations
    ? aboveLayerCSV(opts.decorations)
    : Array.from({ length: H }, () => Array(W).fill(0).join(",")).join(",\n") + ",";
  return `
  <layer id="1" name="Ground" width="${W}" height="${H}">
    <data encoding="csv">
${groundData}
    </data>
  </layer>
  <layer id="2" name="Object" width="${W}" height="${H}"/>
  <layer id="3" name="Above" width="${W}" height="${H}">
    <data encoding="csv">
${aboveData}
    </data>
  </layer>
`;
}

// Simple object builders
function spawn(id, name, monsterType, tx, ty, qty = 1) {
  return `    <object id="${id}" name="${name}" type="Spawn" x="${tx*TILE}" y="${ty*TILE}" width="${TILE}" height="${TILE}">
      <properties><property name="monsterType" value="${monsterType}"/><property name="quantity" value="${qty}"/></properties>
    </object>
`;
}
function area(id, name, monsterType, tx, ty, w, h, qty = 1) {
  return `    <object id="${id}" name="${name}" type="Spawn" x="${tx*TILE}" y="${ty*TILE}" width="${w*TILE}" height="${h*TILE}">
      <properties><property name="monsterType" value="${monsterType}"/><property name="quantity" value="${qty}"/></properties>
    </object>
`;
}
function mapChange(id, name, tx, ty, target, place) {
  return `    <object id="${id}" name="${name}" type="MapChange" x="${tx*TILE}" y="${ty*TILE}" width="${TILE}" height="${TILE}">
      <properties><property name="map" value="${target}"/><property name="place" value="${place}"/></properties>
    </object>
`;
}
function sign(id, name, tx, ty, message) {
  return `    <object id="${id}" name="${name}" type="Sign" x="${tx*TILE}" y="${ty*TILE}" width="${TILE}" height="${TILE}">
      <properties><property name="message" value="${message}"/></properties>
    </object>
`;
}
function namedArea(id, name, tx, ty, key) {
  return `    <object id="${id}" name="${name}" type="namedArea" x="${tx*TILE}" y="${ty*TILE}" width="${TILE}" height="${TILE}">
      <properties><property name="key" value="${key}"/></properties>
    </object>
`;
}

// ---------------------------------------------------------------------------
// Per-sub-map authoring
// ---------------------------------------------------------------------------

// Tile palette pulled from objects1.tsx (firstgid 257). Picked as four
// generic "decor" indices so a rich map shows real Above-layer geometry in
// Tiled. Re-pick to taste.
const DECOR = { crate: 257, barrel: 258, lantern: 259, banner: 273 };

function richOpts(rich, decorations) {
  return rich ? { rich: true, decorations } : {};
}

function buildCenter(r, rich) {
  let nextId = 100;
  let objs = "";
  objs += mapChange(nextId++, "exit_console", 7, 11, "home",                  `from_${r.id}_center`);
  objs += mapChange(nextId++, "to_route",     15, 5, `ab_${r.id}_route`,      "from_center");
  objs += mapChange(nextId++, "to_hideout",   8, 0, `ab_${r.id}_hideout`,     "from_center");
  objs += spawn(nextId++, "clerk",      `ab_npc_${r.id}_clerk`,      8, 4);
  objs += spawn(nextId++, "professor",  `ab_npc_${r.id}_professor`, 4, 6);
  objs += spawn(nextId++, "breeder",    `ab_npc_${r.id}_breeder`,   12, 6);
  objs += spawn(nextId++, "shopkeeper", `ab_npc_${r.id}_shopkeeper`, 8, 8);
  objs += namedArea(nextId++, "town_label", 7, 5, `${r.id}_center`);
  // Tideholm side-quest NPC: lighthouse keeper, near the entrance
  if (r.id === "tide") {
    objs += spawn(nextId++, "lighthouse_keeper", "ab_npc_tide_lighthouse_keeper", 6, 9);
  }
  if (rich) {
    objs += sign(nextId++, "welcome", 8, 9,
      `Welcome to the ${r.town} Beast Center. Healers, breeders, and orbs upstairs.`);
  }
  if (r.id === "tide") {
    objs += sign(nextId++, "harbour_notice", 11, 9,
      "HARBOUR NOTICE: Saltspire Light is dark. The keeper is asking for help.");
    objs += sign(nextId++, "shop_hours",     2, 9,
      "Tideholm Beast Center — open at every tide.");
  }
  const decor = [
    { tx: 1,  ty: 1,  tile: DECOR.crate },
    { tx: 14, ty: 1,  tile: DECOR.crate },
    { tx: 1,  ty: 10, tile: DECOR.barrel },
    { tx: 14, ty: 10, tile: DECOR.barrel },
    { tx: 7,  ty: 1,  tile: DECOR.banner },
  ];
  return tmxOpen(nextId) + layers(1, richOpts(rich, decor)) + `
  <objectgroup id="4" name="eventLayer">
${objs}  </objectgroup>
</map>
`;
}

function buildRoute(r, rich) {
  let nextId = 100;
  let objs = "";
  objs += mapChange(nextId++, "to_center",  0, 5,  `ab_${r.id}_center`,  "from_route");
  objs += mapChange(nextId++, "to_gym",     15, 5, `ab_${r.id}_gym`,     "from_route");
  objs += mapChange(nextId++, "to_hideout", 8, 11, `ab_${r.id}_hideout`, "from_route");
  const starters = [
    { mid: `ab_wild_${r.id}_${{ember:"cindlet",tide:"drilet",verdant:"sproutle",storm:"sparlet",frost:"frostlet",stone:"pebblet",dusk:"wisplet",aether:"glowlet",void:"voidlet"}[r.id]}`, tx: 4,  ty: 4 },
    { mid: `ab_wild_${r.id}_${{ember:"smokrat",tide:"brinepup",verdant:"sapnik",storm:"statikit",frost:"slushpup",stone:"quarrik",dusk:"hexpup",aether:"wingwhelp",void:"glimpup"}[r.id]}`,  tx: 10, ty: 3 },
    { mid: `ab_wild_${r.id}_${{ember:"smoulkin",tide:"brineback",verdant:"saproot",storm:"statilope",frost:"slushound",stone:"quarrigon",dusk:"hexnaught",aether:"wingseraph",void:"glimhound"}[r.id]}`, tx: 6, ty: 8 },
  ];
  for (const s of starters) objs += area(nextId++, "wild_patch", s.mid, s.tx, s.ty, 2, 2, 1);
  objs += namedArea(nextId++, "route_label", 7, 5, `${r.id}_route`);
  // Tideholm side-quest NPC: pearl diver, near the south door (the shoreline)
  if (r.id === "tide") {
    objs += spawn(nextId++, "pearl_diver", "ab_npc_tide_pearl_diver", 8, 10);
  }
  if (rich) {
    objs += sign(nextId++, "trail_marker", 8, 9,
      `${r.town} Trail. Beasts roam here. Travelers carry orbs.`);
  }
  if (r.id === "tide") {
    objs += sign(nextId++, "shoreline_notice", 7, 1,
      "SHORELINE NOTICE: Wild Brinepups travel in packs at low tide.");
    objs += sign(nextId++, "diver_pier", 9, 9,
      "Pier 3 — pearl diver on duty.");
  }
  const decor = [
    { tx: 2,  ty: 2,  tile: DECOR.barrel },
    { tx: 13, ty: 2,  tile: DECOR.barrel },
    { tx: 1,  ty: 10, tile: DECOR.lantern },
    { tx: 14, ty: 10, tile: DECOR.lantern },
  ];
  return tmxOpen(nextId) + layers(1, richOpts(rich, decor)) + `
  <objectgroup id="4" name="eventLayer">
${objs}  </objectgroup>
</map>
`;
}

function buildGym(r, rich) {
  let nextId = 100;
  let objs = "";
  objs += mapChange(nextId++, "exit_to_route", 8, 11, `ab_${r.id}_route`, "from_gym");
  objs += mapChange(nextId++, "to_champion", 15, 5, `ab_${r.id}_champion`, "from_gym");
  objs += spawn(nextId++, "gymleader", `ab_npc_${r.id}_gymleader`, 8, 2);
  objs += spawn(nextId++, "trial_keeper_a", `ab_npc_${r.id}_team_grunt`, 4, 6);
  objs += spawn(nextId++, "trial_keeper_b", `ab_npc_${r.id}_team_grunt`, 12, 6);
  objs += namedArea(nextId++, "gym_label", 7, 5, `${r.id}_gym`);
  if (rich) {
    objs += sign(nextId++, "gym_plaque", 8, 9,
      `${r.town} Gym — Leader ${r.gymLeader}. Defeat the keepers, then face the leader.`);
  }
  if (r.id === "tide") {
    objs += sign(nextId++, "rules", 8, 10,
      "Tideholm Gym Rules: one match, no orbs, no rematches the same day.");
  }
  const decor = [
    { tx: 2,  ty: 1,  tile: DECOR.banner },
    { tx: 13, ty: 1,  tile: DECOR.banner },
    { tx: 2,  ty: 10, tile: DECOR.lantern },
    { tx: 13, ty: 10, tile: DECOR.lantern },
  ];
  return tmxOpen(nextId) + layers(1, richOpts(rich, decor)) + `
  <objectgroup id="4" name="eventLayer">
${objs}  </objectgroup>
</map>
`;
}

function buildHideout(r, rich) {
  let nextId = 100;
  let objs = "";
  objs += mapChange(nextId++, "exit_to_center", 8, 11, `ab_${r.id}_center`, "from_hideout");
  objs += spawn(nextId++, "grunt_a", `ab_npc_${r.id}_team_grunt`, 3, 7);
  objs += spawn(nextId++, "grunt_b", `ab_npc_${r.id}_team_grunt`, 6, 6);
  objs += spawn(nextId++, "grunt_c", `ab_npc_${r.id}_team_grunt`, 9, 6);
  objs += spawn(nextId++, "grunt_d", `ab_npc_${r.id}_team_grunt`, 12, 7);
  objs += spawn(nextId++, "admin",   `ab_npc_${r.id}_team_admin`, 8, 2);
  objs += namedArea(nextId++, "hideout_label", 7, 5, `${r.id}_hideout`);
  if (rich) {
    objs += sign(nextId++, "warning", 8, 10,
      `Eclipse hideout. Trespass at your own risk.`);
  }
  const decor = [
    { tx: 1,  ty: 1,  tile: DECOR.crate },
    { tx: 14, ty: 1,  tile: DECOR.crate },
    { tx: 7,  ty: 1,  tile: DECOR.banner },
    { tx: 8,  ty: 1,  tile: DECOR.banner },
  ];
  return tmxOpen(nextId) + layers(1, richOpts(rich, decor)) + `
  <objectgroup id="4" name="eventLayer">
${objs}  </objectgroup>
</map>
`;
}

function buildChampion(r, rich) {
  let nextId = 100;
  let objs = "";
  objs += mapChange(nextId++, "exit_to_gym", 0, 5, `ab_${r.id}_gym`, "from_champion");
  objs += spawn(nextId++, "champion", `ab_npc_${r.id}_champion`, 8, 2);
  objs += namedArea(nextId++, "arena_label", 7, 5, `${r.id}_arena`);
  if (rich) {
    objs += sign(nextId++, "arena_plaque", 8, 9,
      `Champion's Arena — ${r.champion}. Bring the ${r.name} Crest.`);
  }
  const decor = [
    { tx: 2,  ty: 1,  tile: DECOR.banner },
    { tx: 13, ty: 1,  tile: DECOR.banner },
    { tx: 2,  ty: 10, tile: DECOR.lantern },
    { tx: 13, ty: 10, tile: DECOR.lantern },
    { tx: 7,  ty: 5,  tile: DECOR.crate },
    { tx: 8,  ty: 5,  tile: DECOR.crate },
  ];
  return tmxOpen(nextId) + layers(1, richOpts(rich, decor)) + `
  <objectgroup id="4" name="eventLayer">
${objs}  </objectgroup>
</map>
`;
}

// ---------------------------------------------------------------------------
// Emit TMX files
// ---------------------------------------------------------------------------

const ALL_REGIONS = [...REGIONS, ENDGAME]; // 9 regions get TMX skeletons
let tmxCount = 0;
for (const r of ALL_REGIONS) {
  // Two worked examples: Emberlands (level_0) and Tideholm (level_1) get
  // a varied tile palette, decorative Above-layer tiles, multiple lore signs,
  // and (for tide only) two side-quest NPC spawns.
  const rich = r.id === "ember" || r.id === "tide";
  const subs = {
    center:   buildCenter(r, rich),
    route:    buildRoute(r, rich),
    gym:      buildGym(r, rich),
    hideout:  buildHideout(r, rich),
    champion: buildChampion(r, rich),
  };
  for (const [sub, content] of Object.entries(subs)) {
    const filename = `ab_${r.id}_${sub}.tmx`;
    writeFileSync(join(XML, filename), content);
    tmxCount++;
  }
}
console.log(`wrote ${tmxCount} TMX files (9 regions × 5 sub-maps)`);

// ---------------------------------------------------------------------------
// Tiled .world files (level_0.world .. level_7.world) — one per region 0..7
// World file format reference: https://doc.mapeditor.org/en/stable/manual/worlds/
// ---------------------------------------------------------------------------

// Layout (in tile-grid units; multiply by 512 / 384 for pixel coords):
//                                          gym (2,-1)
//   center (0,0) -- route (1,0) -- (gap) -- (2,0)  --  champion (3,0)
//                                          hideout (2,1)
//
// .world coordinates are pixels.
const layout = {
  center:   { gx: 0, gy: 0 },
  route:    { gx: 1, gy: 0 },
  gym:      { gx: 2, gy: -1 },
  hideout:  { gx: 2, gy: 1 },
  champion: { gx: 3, gy: 0 },
};

let worldCount = 0;
for (let i = 0; i < 8; i++) {
  const r = REGIONS[i];
  const maps = Object.entries(layout).map(([sub, pos]) => ({
    fileName: `ab_${r.id}_${sub}.tmx`,
    x: pos.gx * PX_W,
    y: pos.gy * PX_H,
    width:  PX_W,
    height: PX_H,
  }));
  const world = {
    onlyShowAdjacentMaps: false,
    type: "world",
    maps,
    patterns: [],
  };
  const filename = `level_${i}.world`;
  writeFileSync(join(XML, filename), JSON.stringify(world, null, 4) + "\n");
  worldCount++;
  console.log(`  level_${i}.world  → ${r.name} (${r.id})`);
}
console.log(`wrote ${worldCount} .world files (level_0 .. level_7)`);
