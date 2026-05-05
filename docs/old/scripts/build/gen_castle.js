#!/usr/bin/env node
/*
 * gen_castle.js — generates skeleton TMX files and Tiled .world files for
 * the Westgate Castle expansion. Run with `node gen_castle.js`.
 */
const fs = require('fs');
const path = require('path');

const OUT_TMX_DIR = path.join(__dirname, '..', 'res', 'xml');
const OUT_WORLD_DIR = path.join(__dirname, '..', 'world');
fs.mkdirSync(OUT_TMX_DIR, { recursive: true });
fs.mkdirSync(OUT_WORLD_DIR, { recursive: true });

const TILE = 32;
const ROOM_W = 16, ROOM_H = 12;          // tiles per main-floor room
const ROOM_PX_W = ROOM_W * TILE;          // 512
const ROOM_PX_H = ROOM_H * TILE;          // 384

// ---- Grid of main-floor rooms (col, row) -> { mapId, file, signKey, tilesetSet } ----
// File names are exactly what the engine will load. jasia's bedroom must be home.tmx.
const MAIN = [
  // row 0
  { col: 0, row: 0, mapId: 'castle_grove',         file: 'castle_grove.tmx',         displayKey: 'wg_castle_room_grove' },
  { col: 1, row: 0, mapId: 'castle_garden',        file: 'castle_garden.tmx',        displayKey: 'wg_castle_room_garden' },
  { col: 2, row: 0, mapId: 'castle_antichamber',   file: 'castle_antichamber.tmx',   displayKey: 'wg_castle_room_antichamber' },
  { col: 3, row: 0, mapId: 'castle_throne',        file: 'castle_throne.tmx',        displayKey: 'wg_castle_room_throne' },
  { col: 4, row: 0, mapId: 'castle_workroom',      file: 'castle_workroom.tmx',      displayKey: 'wg_castle_room_workroom' },
  // row 1
  { col: 0, row: 1, mapId: 'castle_kitchen',       file: 'castle_kitchen.tmx',       displayKey: 'wg_castle_room_kitchen' },
  { col: 1, row: 1, mapId: 'castle_dining',        file: 'castle_dining.tmx',        displayKey: 'wg_castle_room_dining' },
  { col: 2, row: 1, mapId: 'castle_hall',          file: 'castle_hall.tmx',          displayKey: 'wg_castle_room_hall' },
  { col: 3, row: 1, mapId: 'castle_trophy',        file: 'castle_trophy.tmx',        displayKey: 'wg_castle_room_trophy' },
  { col: 4, row: 1, mapId: 'castle_library',       file: 'castle_library.tmx',       displayKey: 'wg_castle_room_library' },
  // row 2
  { col: 0, row: 2, mapId: 'castle_guest_west',    file: 'castle_guest_west.tmx',    displayKey: 'wg_castle_room_guest_west' },
  { col: 1, row: 2, mapId: 'castle_sunny_bedroom', file: 'castle_sunny_bedroom.tmx', displayKey: 'wg_castle_room_sunny' },
  { col: 2, row: 2, mapId: 'castle_entry',         file: 'castle_entry.tmx',         displayKey: 'wg_castle_room_entry' },
  // jasia's bedroom MUST be home.tmx so the game will load it as the player home map.
  { col: 3, row: 2, mapId: 'home',                 file: 'home.tmx',                 displayKey: 'wg_castle_room_home' },
  { col: 4, row: 2, mapId: 'castle_guest_east',    file: 'castle_guest_east.tmx',    displayKey: 'wg_castle_room_guest_east' },
];
// quick lookup
const byPos = new Map(MAIN.map(r => [`${r.col},${r.row}`, r]));

// Door positions inside a 16x12 room (in tile units)
const DOORS = {
  N: { tx: 7,  ty: 0  },
  S: { tx: 7,  ty: 11 },
  E: { tx: 15, ty: 5  },
  W: { tx: 0,  ty: 5  },
};
const opp = { N: 'S', S: 'N', E: 'W', W: 'E' };
const dx = { N: 0, S: 0, E: 1, W: -1 };
const dy = { N: -1, S: 1, E: 0, W: 0 };

function csvLayer(w, h, tileId = 1) {
  const row = Array(w).fill(tileId).join(',');
  return Array(h).fill(row).join(',\n');
}

function header(w, h, nextId, extraTilesets = '') {
  return `<?xml version="1.0" encoding="UTF-8"?>
<map version="1.0" tiledversion="1.4.3" orientation="orthogonal"
     renderorder="right-down" width="${w}" height="${h}"
     tilewidth="${TILE}" tileheight="${TILE}" infinite="0"
     nextlayerid="5" nextobjectid="${nextId}">
  <tileset firstgid="1"   source="indoor1.tsx"/>
  <tileset firstgid="257" source="objects1.tsx"/>
${extraTilesets}`;
}

function groundLayer(w, h) {
  return `  <layer id="1" name="Ground" width="${w}" height="${h}">
    <data encoding="csv">
${csvLayer(w, h)}
    </data>
  </layer>
  <layer id="2" name="Object" width="${w}" height="${h}"/>
  <layer id="3" name="Above" width="${w}" height="${h}"/>`;
}

function mapChange(id, name, x, y, targetMap, place) {
  return `    <object id="${id}" name="${name}" type="MapChange" x="${x}" y="${y}" width="32" height="32">
      <properties><property name="map" value="${targetMap}"/><property name="place" value="${place}"/></properties>
    </object>`;
}
function spawn(id, name, x, y, monsterType, qty = 1) {
  return `    <object id="${id}" name="${name}" type="Spawn" x="${x}" y="${y}" width="32" height="32">
      <properties><property name="monsterType" value="${monsterType}"/><property name="quantity" value="${qty}"/></properties>
    </object>`;
}
function sign(id, name, x, y, msg) {
  return `    <object id="${id}" name="${name}" type="Sign" x="${x}" y="${y}" width="32" height="32">
      <properties><property name="message" value="${msg}"/></properties>
    </object>`;
}

// Build neighbor MapChange objects for a main-floor room
function neighborMapChanges(room, startId) {
  const out = [];
  let id = startId;
  for (const dir of ['N', 'S', 'E', 'W']) {
    const nc = room.col + dx[dir], nr = room.row + dy[dir];
    const nb = byPos.get(`${nc},${nr}`);
    if (!nb) continue;
    const d = DOORS[dir];
    const x = d.tx * TILE, y = d.ty * TILE;
    out.push(mapChange(id++, `door_${dir.toLowerCase()}`, x, y, nb.mapId, `from_${room.mapId}`));
  }
  return { xml: out.join('\n'), nextId: id };
}

// Per-room extra event objects (NPCs, signs, special portals)
function roomExtras(room, startId) {
  let id = startId;
  const extras = [];
  const sx = 4 * TILE, sy = 5 * TILE; // spot 1
  const sx2 = 11 * TILE, sy2 = 5 * TILE; // spot 2
  switch (room.mapId) {
    case 'castle_grove':
      extras.push(spawn(id++, 'gardener', sx, sy, 'wg_npc_castle_gardener'));
      extras.push(sign(id++, 'plaque', 4*TILE, 9*TILE, '@string/wg_castle_sign_grove'));
      break;
    case 'castle_garden':
      extras.push(spawn(id++, 'flower_keeper', sx, sy, 'wg_npc_castle_flowerkeeper'));
      break;
    case 'castle_antichamber':
      extras.push(spawn(id++, 'usher', sx, sy, 'wg_npc_castle_usher'));
      extras.push(sign(id++, 'plaque', 7*TILE, 9*TILE, '@string/wg_castle_sign_antichamber'));
      break;
    case 'castle_throne':
      extras.push(spawn(id++, 'sunny', 7*TILE, 3*TILE, 'wg_npc_sunny'));
      extras.push(spawn(id++, 'royal_guard_a', 5*TILE, 5*TILE, 'wg_npc_castle_guard'));
      extras.push(spawn(id++, 'royal_guard_b', 9*TILE, 5*TILE, 'wg_npc_castle_guard'));
      extras.push(sign(id++, 'plaque', 7*TILE, 10*TILE, '@string/wg_castle_sign_throne'));
      break;
    case 'castle_workroom':
      extras.push(spawn(id++, 'scribe', sx, sy, 'wg_npc_castle_scribe'));
      break;
    case 'castle_kitchen':
      extras.push(spawn(id++, 'cook', sx, sy, 'wg_npc_castle_cook'));
      extras.push(spawn(id++, 'scullion', sx2, sy2, 'wg_npc_castle_servant'));
      break;
    case 'castle_dining':
      extras.push(spawn(id++, 'butler_dining', sx, sy, 'wg_npc_castle_majordomo'));
      extras.push(spawn(id++, 'serving_maid', sx2, sy2, 'wg_npc_castle_servant'));
      break;
    case 'castle_hall':
      // stairs down to basement 1
      extras.push(mapChange(id++, 'stairs_down_b1', 7*TILE, 6*TILE, 'castle_b1', 'from_castle_hall'));
      extras.push(spawn(id++, 'hall_guard', 4*TILE, 8*TILE, 'wg_npc_castle_guard'));
      extras.push(sign(id++, 'plaque', 7*TILE, 8*TILE, '@string/wg_castle_sign_hall'));
      break;
    case 'castle_trophy':
      extras.push(spawn(id++, 'curator', sx, sy, 'wg_npc_castle_curator'));
      extras.push(sign(id++, 'plaque', 7*TILE, 9*TILE, '@string/wg_castle_sign_trophy'));
      break;
    case 'castle_library':
      extras.push(spawn(id++, 'librarian', sx, sy, 'wg_npc_castle_librarian'));
      extras.push(sign(id++, 'plaque', 4*TILE, 9*TILE, '@string/wg_castle_sign_library'));
      break;
    case 'castle_guest_west':
      extras.push(spawn(id++, 'guest_a', sx, sy, 'wg_npc_castle_guest'));
      extras.push(spawn(id++, 'maid_a', sx2, sy2, 'wg_npc_castle_servant'));
      break;
    case 'castle_sunny_bedroom':
      extras.push(spawn(id++, 'attendant', sx, sy, 'wg_npc_castle_servant'));
      extras.push(sign(id++, 'plaque', 7*TILE, 9*TILE, '@string/wg_castle_sign_sunny'));
      break;
    case 'castle_entry':
      // South exit to westgate_market; stairs up to roof; stairs down covered by hall room.
      extras.push(mapChange(id++, 'south_exit', 7*TILE, 11*TILE, 'westgate_market', 'from_castle_entry'));
      extras.push(mapChange(id++, 'stairs_up_roof', 11*TILE, 5*TILE, 'castle_roof', 'from_castle_entry'));
      extras.push(spawn(id++, 'doorman', 4*TILE, 8*TILE, 'wg_npc_castle_doorman'));
      extras.push(sign(id++, 'plaque', 7*TILE, 9*TILE, '@string/wg_castle_sign_entry'));
      break;
    case 'home':
      // Jasia's bedroom (player's home)
      extras.push(spawn(id++, 'bed', 11*TILE, 3*TILE, 'wg_obj_bed_home'));
      extras.push(spawn(id++, 'wardrobe', 11*TILE, 8*TILE, 'wg_obj_wardrobe'));
      extras.push(sign(id++, 'plaque', 7*TILE, 9*TILE, '@string/wg_castle_sign_home'));
      break;
    case 'castle_guest_east':
      extras.push(spawn(id++, 'guest_b', sx, sy, 'wg_npc_castle_guest'));
      extras.push(spawn(id++, 'maid_b', sx2, sy2, 'wg_npc_castle_servant'));
      break;
  }
  return { xml: extras.join('\n'), nextId: id };
}

function buildMainRoom(room) {
  let nextId = 1;
  const ne = neighborMapChanges(room, nextId);
  nextId = ne.nextId;
  const ex = roomExtras(room, nextId);
  nextId = ex.nextId;
  const xml = `${header(ROOM_W, ROOM_H, nextId)}
${groundLayer(ROOM_W, ROOM_H)}

  <objectgroup id="4" name="eventLayer">
${ne.xml}
${ex.xml}
  </objectgroup>
</map>
`;
  fs.writeFileSync(path.join(OUT_TMX_DIR, room.file), xml);
}

MAIN.forEach(buildMainRoom);

// ---------------- Basement 1 ----------------
// One TMX, central hall surrounded by 4 rooms.
// 32x24 tiles. Central hall ~ 10x8 in middle. Rooms 8x8 around it.
function buildBasement1() {
  const W = 32, H = 24;
  let id = 1;
  const portals = [
    mapChange(id++, 'stairs_up_main', 15*TILE, 11*TILE, 'castle_hall',  'from_castle_b1'),
    mapChange(id++, 'stairs_down_b2', 16*TILE, 12*TILE, 'castle_b2',    'from_castle_b1'),
  ];
  const npcs = [
    spawn(id++, 'armory_keeper',     5*TILE,  4*TILE,  'wg_npc_castle_armorer'),
    spawn(id++, 'servant_steward',   25*TILE, 4*TILE,  'wg_npc_castle_servant'),
    spawn(id++, 'storage_clerk',     5*TILE,  19*TILE, 'wg_npc_castle_quartermaster'),
    spawn(id++, 'guard_captain_b1',  25*TILE, 19*TILE, 'wg_npc_castle_guard_captain'),
    spawn(id++, 'patrol_b1_a',       12*TILE, 12*TILE, 'wg_npc_castle_guard'),
    spawn(id++, 'patrol_b1_b',       19*TILE, 12*TILE, 'wg_npc_castle_guard'),
  ];
  const signs = [
    sign(id++, 'sign_armory',           5*TILE, 7*TILE,  '@string/wg_castle_sign_b1_armory'),
    sign(id++, 'sign_servant_quarters', 25*TILE, 7*TILE, '@string/wg_castle_sign_b1_servant'),
    sign(id++, 'sign_storage',          5*TILE, 16*TILE, '@string/wg_castle_sign_b1_storage'),
    sign(id++, 'sign_guards_quarters',  25*TILE, 16*TILE,'@string/wg_castle_sign_b1_guards'),
  ];
  const xml = `${header(W, H, id)}
${groundLayer(W, H)}

  <objectgroup id="4" name="eventLayer">
${[...portals, ...npcs, ...signs].join('\n')}
  </objectgroup>
</map>
`;
  fs.writeFileSync(path.join(OUT_TMX_DIR, 'castle_b1.tmx'), xml);
}
buildBasement1();

// ---------------- Basement 2 ----------------
// One TMX. Warden office, armory, guard office, and a hall leading to 4 prison cells.
function buildBasement2() {
  const W = 36, H = 24;
  let id = 1;
  const portals = [
    mapChange(id++, 'stairs_up_b1', 17*TILE, 11*TILE, 'castle_b1', 'from_castle_b2'),
  ];
  const npcs = [
    spawn(id++, 'warden',         4*TILE,  4*TILE,  'wg_npc_castle_warden'),
    spawn(id++, 'b2_armorer',     17*TILE, 4*TILE,  'wg_npc_castle_armorer'),
    spawn(id++, 'guard_office',   30*TILE, 4*TILE,  'wg_npc_castle_guard_officer'),
    spawn(id++, 'jailer',         18*TILE, 14*TILE, 'wg_npc_castle_jailer'),
    spawn(id++, 'prisoner_1',     6*TILE,  20*TILE, 'wg_npc_castle_prisoner'),
    spawn(id++, 'prisoner_2',     14*TILE, 20*TILE, 'wg_npc_castle_prisoner'),
    spawn(id++, 'prisoner_3',     22*TILE, 20*TILE, 'wg_npc_castle_prisoner'),
    spawn(id++, 'prisoner_4',     30*TILE, 20*TILE, 'wg_npc_castle_prisoner'),
  ];
  const signs = [
    sign(id++, 'sign_warden',     4*TILE,  7*TILE,  '@string/wg_castle_sign_b2_warden'),
    sign(id++, 'sign_b2_armory', 17*TILE,  7*TILE,  '@string/wg_castle_sign_b2_armory'),
    sign(id++, 'sign_guard_off', 30*TILE,  7*TILE,  '@string/wg_castle_sign_b2_guard_office'),
    sign(id++, 'sign_cell_1',     6*TILE,  17*TILE, '@string/wg_castle_sign_b2_cell1'),
    sign(id++, 'sign_cell_2',    14*TILE,  17*TILE, '@string/wg_castle_sign_b2_cell2'),
    sign(id++, 'sign_cell_3',    22*TILE,  17*TILE, '@string/wg_castle_sign_b2_cell3'),
    sign(id++, 'sign_cell_4',    30*TILE,  17*TILE, '@string/wg_castle_sign_b2_cell4'),
  ];
  const xml = `${header(W, H, id)}
${groundLayer(W, H)}

  <objectgroup id="4" name="eventLayer">
${[...portals, ...npcs, ...signs].join('\n')}
  </objectgroup>
</map>
`;
  fs.writeFileSync(path.join(OUT_TMX_DIR, 'castle_b2.tmx'), xml);
}
buildBasement2();

// ---------------- Roof ----------------
// One TMX with 4 corner towers (each a portal up to its lookout level).
function buildRoof() {
  const W = 24, H = 18;
  let id = 1;
  const portals = [
    mapChange(id++, 'stairs_down_entry', 11*TILE, 9*TILE, 'castle_entry', 'from_castle_roof'),
    mapChange(id++, 'tower_nw_up',        2*TILE, 2*TILE, 'castle_tower_nw', 'from_castle_roof'),
    mapChange(id++, 'tower_ne_up',       21*TILE, 2*TILE, 'castle_tower_ne', 'from_castle_roof'),
    mapChange(id++, 'tower_sw_up',        2*TILE, 15*TILE, 'castle_tower_sw', 'from_castle_roof'),
    mapChange(id++, 'tower_se_up',       21*TILE, 15*TILE, 'castle_tower_se', 'from_castle_roof'),
  ];
  const npcs = [
    spawn(id++, 'roof_guard',     11*TILE, 2*TILE, 'wg_npc_castle_guard'),
    spawn(id++, 'roof_marshal',   11*TILE, 15*TILE, 'wg_npc_castle_guard_captain'),
  ];
  const signs = [
    sign(id++, 'sign_roof', 11*TILE, 11*TILE, '@string/wg_castle_sign_roof'),
  ];
  const xml = `${header(W, H, id)}
${groundLayer(W, H)}

  <objectgroup id="4" name="eventLayer">
${[...portals, ...npcs, ...signs].join('\n')}
  </objectgroup>
</map>
`;
  fs.writeFileSync(path.join(OUT_TMX_DIR, 'castle_roof.tmx'), xml);
}
buildRoof();

// ---------------- 4 Tower lookouts ----------------
const TOWERS = ['nw', 'ne', 'sw', 'se'];
TOWERS.forEach(corner => {
  const W = 8, H = 8;
  let id = 1;
  const portals = [
    mapChange(id++, 'stairs_down_roof', 3*TILE, 6*TILE, 'castle_roof', `from_castle_tower_${corner}`),
  ];
  const npcs = [
    spawn(id++, 'lookout', 3*TILE, 3*TILE, 'wg_npc_castle_lookout'),
  ];
  const signs = [
    sign(id++, 'sign_tower', 4*TILE, 6*TILE, `@string/wg_castle_sign_tower_${corner}`),
  ];
  const xml = `${header(W, H, id)}
${groundLayer(W, H)}

  <objectgroup id="4" name="eventLayer">
${[...portals, ...npcs, ...signs].join('\n')}
  </objectgroup>
</map>
`;
  fs.writeFileSync(path.join(OUT_TMX_DIR, `castle_tower_${corner}.tmx`), xml);
});

// ---------------- .world files ----------------
// Tiled .world format reference:
//   https://doc.mapeditor.org/en/stable/manual/worlds/
//
// Each .world file is a JSON document of the form:
// {
//   "maps": [ { "fileName": "foo.tmx", "x": 0, "y": 0, "width": 512, "height": 384 }, ... ],
//   "type": "world"
// }
//
// We produce 15 individual per-room .world files (one per main-floor "level"),
// each containing the room itself and all its grid-immediate neighbors so the
// designer can edit a room with its surroundings visible. We also write a
// comprehensive `castle_main.world` that lays out the entire 5x3 grid plus
// the basement, roof, and tower maps at suitable offsets.

function tmxRel(file) { return `../res/xml/${file}`; }

function writeWorld(name, maps) {
  const obj = { maps, type: 'world' };
  fs.writeFileSync(path.join(OUT_WORLD_DIR, name), JSON.stringify(obj, null, 2) + '\n');
}

// Per-room worlds — each level (main floor room) gets its own .world file
MAIN.forEach(room => {
  const maps = [];
  // Place the room at (col*ROOM_PX_W, row*ROOM_PX_H) and include neighbors at their natural offsets
  const include = (r) => maps.push({
    fileName: tmxRel(r.file),
    x: r.col * ROOM_PX_W,
    y: r.row * ROOM_PX_H,
    width: ROOM_PX_W,
    height: ROOM_PX_H,
  });
  include(room);
  for (const dir of ['N', 'S', 'E', 'W']) {
    const nb = byPos.get(`${room.col + dx[dir]},${room.row + dy[dir]}`);
    if (nb) include(nb);
  }
  // Special: hall has stairs down -> include castle_b1 below the grid
  if (room.mapId === 'castle_hall') {
    maps.push({ fileName: tmxRel('castle_b1.tmx'), x: 0, y: 3 * ROOM_PX_H + 64,
                width: 32 * TILE, height: 24 * TILE });
  }
  // Special: entry has stairs up -> include castle_roof above the grid
  if (room.mapId === 'castle_entry') {
    maps.push({ fileName: tmxRel('castle_roof.tmx'), x: 0, y: -(18 * TILE + 64),
                width: 24 * TILE, height: 18 * TILE });
  }
  writeWorld(`${room.mapId}.world`, maps);
});

// Comprehensive overview world — every map placed sensibly
{
  const maps = [];
  for (const r of MAIN) {
    maps.push({
      fileName: tmxRel(r.file),
      x: r.col * ROOM_PX_W,
      y: r.row * ROOM_PX_H,
      width: ROOM_PX_W,
      height: ROOM_PX_H,
    });
  }
  // basement 1 below main grid
  maps.push({ fileName: tmxRel('castle_b1.tmx'), x: 0, y: 3 * ROOM_PX_H + 96,
              width: 32 * TILE, height: 24 * TILE });
  // basement 2 below basement 1
  maps.push({ fileName: tmxRel('castle_b2.tmx'), x: 0, y: 3 * ROOM_PX_H + 96 + 24 * TILE + 96,
              width: 36 * TILE, height: 24 * TILE });
  // roof above main grid
  maps.push({ fileName: tmxRel('castle_roof.tmx'), x: 0, y: -(18 * TILE + 96),
              width: 24 * TILE, height: 18 * TILE });
  // towers above the roof, side by side
  ['nw', 'ne', 'sw', 'se'].forEach((c, i) => {
    maps.push({
      fileName: tmxRel(`castle_tower_${c}.tmx`),
      x: i * (8 * TILE + 32),
      y: -(18 * TILE + 96) - (8 * TILE + 96),
      width: 8 * TILE,
      height: 8 * TILE,
    });
  });
  writeWorld('castle_overview.world', maps);
}

// Per-floor worlds for the non-main areas
writeWorld('castle_basement1.world', [
  { fileName: tmxRel('castle_b1.tmx'), x: 0, y: 0, width: 32 * TILE, height: 24 * TILE },
]);
writeWorld('castle_basement2.world', [
  { fileName: tmxRel('castle_b2.tmx'), x: 0, y: 0, width: 36 * TILE, height: 24 * TILE },
]);
writeWorld('castle_roof.world', [
  { fileName: tmxRel('castle_roof.tmx'), x: 0, y: 0, width: 24 * TILE, height: 18 * TILE },
]);
TOWERS.forEach(c => {
  writeWorld(`castle_tower_${c}.world`, [
    { fileName: tmxRel(`castle_tower_${c}.tmx`), x: 0, y: 0, width: 8 * TILE, height: 8 * TILE },
  ]);
});

console.log('Generated castle TMX files and .world files.');
