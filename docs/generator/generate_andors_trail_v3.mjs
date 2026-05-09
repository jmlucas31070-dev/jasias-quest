/**
 * Andor's Trail Content Generator v3
 * AT-format compliant: flat arrays, correct field names, int booleans
 * TMX maps match the real AT template exactly:
 *   - All 60 real tilesets (map_bed_1 … map_transition_5, ../drawable/*)
 *   - 8 blank tile layers: Base, Ground, Objects, Objects_replace,
 *     Above, Above_replace, Top, Walkable — all GID=0, base64+ZLIB encoded
 *   - 4 standard object groups: Mapevents, Spawn, Keys, Replace
 *   - Tiled 1.8.4 map header attributes
 */
import fs   from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR   = path.join(__dirname, '../andors_trail_content');

// ─────────────────────────────────────────────────────────────────────────────
// FILE HELPERS
// ─────────────────────────────────────────────────────────────────────────────
function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }
function writeFile(p, content) {
  mkdirp(path.dirname(p));
  if (typeof content === 'string') fs.writeFileSync(p, content, 'utf8');
  else fs.writeFileSync(p, content);
  console.log('  wrote', path.relative(OUT_DIR, p));
}
function writeJson(p, obj) { writeFile(p, JSON.stringify(obj, null, 2)); }

// ─────────────────────────────────────────────────────────────────────────────
// ZIP BUILDER (pure Node.js, no external deps)
// ─────────────────────────────────────────────────────────────────────────────
function crc32(buf) {
  let c = 0xFFFFFFFF;
  for (const b of buf) { c ^= b; for (let i=0;i<8;i++) c=(c>>>1)^(c&1?0xEDB88320:0); }
  return (c^0xFFFFFFFF)>>>0;
}

function buildZip(files) {
  // files: [{name:string, data:Buffer|string}]
  const localParts = [];
  const centralParts = [];
  let offset = 0;
  const dosDate = (new Date(2026,4,9)); // May 9 2026
  const dosTime = ((10)<<11)|((0)<<5)|(0>>1);
  const dosDateVal = ((dosDate.getFullYear()-1980)<<9)|((dosDate.getMonth()+1)<<5)|(dosDate.getDate());

  for (const file of files) {
    const rawData = typeof file.data === 'string' ? Buffer.from(file.data,'utf8') : file.data;
    const compressed = zlib.deflateRawSync(rawData, {level:6});
    const crc = crc32(rawData);
    const nameBuf = Buffer.from(file.name,'utf8');
    const compMethod = 8; // deflate
    const uncompSize = rawData.length;
    const compSize = compressed.length;

    // Local file header
    const lh = Buffer.allocUnsafe(30 + nameBuf.length);
    lh.writeUInt32LE(0x04034B50,0);   // signature
    lh.writeUInt16LE(20,4);            // version needed
    lh.writeUInt16LE(0,6);             // flags
    lh.writeUInt16LE(compMethod,8);    // compression
    lh.writeUInt16LE(dosTime,10);
    lh.writeUInt16LE(dosDateVal,12);
    lh.writeUInt32LE(crc,14);
    lh.writeUInt32LE(compSize,18);
    lh.writeUInt32LE(uncompSize,22);
    lh.writeUInt16LE(nameBuf.length,26);
    lh.writeUInt16LE(0,28);            // extra length
    nameBuf.copy(lh,30);

    // Central directory entry
    const cd = Buffer.allocUnsafe(46 + nameBuf.length);
    cd.writeUInt32LE(0x02014B50,0);   // signature
    cd.writeUInt16LE(20,4);            // version made by
    cd.writeUInt16LE(20,6);            // version needed
    cd.writeUInt16LE(0,8);             // flags
    cd.writeUInt16LE(compMethod,10);   // compression
    cd.writeUInt16LE(dosTime,12);
    cd.writeUInt16LE(dosDateVal,14);
    cd.writeUInt32LE(crc,16);
    cd.writeUInt32LE(compSize,20);
    cd.writeUInt32LE(uncompSize,24);
    cd.writeUInt16LE(nameBuf.length,28);
    cd.writeUInt16LE(0,30);            // extra len
    cd.writeUInt16LE(0,32);            // comment len
    cd.writeUInt16LE(0,34);            // disk start
    cd.writeUInt16LE(0,36);            // internal attr
    cd.writeUInt32LE(0,38);            // external attr
    cd.writeUInt32LE(offset,42);       // local header offset
    nameBuf.copy(cd,46);

    localParts.push(lh, compressed);
    centralParts.push(cd);
    offset += lh.length + compressed.length;
  }

  const centralBuf = Buffer.concat(centralParts);
  const centralOffset = offset;
  const centralSize = centralBuf.length;
  const eocd = Buffer.allocUnsafe(22);
  eocd.writeUInt32LE(0x06054B50,0);   // signature
  eocd.writeUInt16LE(0,4);             // disk
  eocd.writeUInt16LE(0,6);             // disk with cd
  eocd.writeUInt16LE(files.length,8);
  eocd.writeUInt16LE(files.length,10);
  eocd.writeUInt32LE(centralSize,12);
  eocd.writeUInt32LE(centralOffset,16);
  eocd.writeUInt16LE(0,20);            // comment len

  return Buffer.concat([...localParts, centralBuf, eocd]);
}

// ─────────────────────────────────────────────────────────────────────────────
// TMX / TILE HELPERS  — matches real Andor's Trail 1.8.4 format exactly
// ─────────────────────────────────────────────────────────────────────────────

// All 60 tilesets present in every real AT map (sourced from arulircave1.tmx).
// firstgid values are cumulative: each tileset's firstgid = prev firstgid + prev tilecount.
// image paths use ../drawable/ as in the real game project.
const AT_TILESETS = [
  // name,               firstgid, tilecount, columns, imgW, imgH
  ['map_bed_1',              1,   128, 16, 512, 256],
  ['map_border_1',         129,   128, 16, 512, 256],
  ['map_bridge_1',         257,   128, 16, 512, 256],
  ['map_bridge_2',         385,   128, 16, 512, 256],
  ['map_broken_1',         513,   128, 16, 512, 256],
  ['map_cavewall_1',       641,   108, 18, 576, 192],
  ['map_cavewall_2',       749,   108, 18, 576, 192],
  ['map_cavewall_3',       857,   108, 18, 576, 192],
  ['map_cavewall_4',       965,   108, 18, 576, 192],
  ['map_chair_table_1',   1073,   128, 16, 512, 256],
  ['map_chair_table_2',   1201,   128, 16, 512, 256],
  ['map_crate_1',         1329,   128, 16, 512, 256],
  ['map_cupboard_1',      1457,   128, 16, 512, 256],
  ['map_curtain_1',       1585,   128, 16, 512, 256],
  ['map_entrance_1',      1713,   128, 16, 512, 256],
  ['map_entrance_2',      1841,   128, 16, 512, 256],
  ['map_fence_1',         1969,   128, 16, 512, 256],
  ['map_fence_2',         2097,   128, 16, 512, 256],
  ['map_fence_3',         2225,   128, 16, 512, 256],
  ['map_fence_4',         2353,   128, 16, 512, 256],
  ['map_ground_1',        2481,   128, 16, 512, 256],
  ['map_ground_2',        2609,   128, 16, 512, 256],
  ['map_ground_3',        2737,   128, 16, 512, 256],
  ['map_ground_4',        2865,   128, 16, 512, 256],
  ['map_ground_5',        2993,   128, 16, 512, 256],
  ['map_ground_6',        3121,   128, 16, 512, 256],
  ['map_ground_7',        3249,   128, 16, 512, 256],
  ['map_ground_8',        3377,   128, 16, 512, 256],
  ['map_house_1',         3505,   128, 16, 512, 256],
  ['map_house_2',         3633,   128, 16, 512, 256],
  ['map_indoor_1',        3761,   128, 16, 512, 256],
  ['map_indoor_2',        3889,   128, 16, 512, 256],
  ['map_kitchen_1',       4017,   128, 16, 512, 256],
  ['map_outdoor_1',       4145,   128, 16, 512, 256],
  ['map_pillar_1',        4273,   128, 16, 512, 256],
  ['map_pillar_2',        4401,   128, 16, 512, 256],
  ['map_plant_1',         4529,   128, 16, 512, 256],
  ['map_plant_2',         4657,   128, 16, 512, 256],
  ['map_rock_1',          4785,   128, 16, 512, 256],
  ['map_rock_2',          4913,   128, 16, 512, 256],
  ['map_roof_1',          5041,   128, 16, 512, 256],
  ['map_roof_2',          5169,   128, 16, 512, 256],
  ['map_roof_3',          5297,   128, 16, 512, 256],
  ['map_shop_1',          5425,   128, 16, 512, 256],
  ['map_sign_ladder_1',   5553,   128, 16, 512, 256],
  ['map_table_1',         5681,   128, 16, 512, 256],
  ['map_trail_1',         5809,   128, 16, 512, 256],
  ['map_transition_1',    5937,   128, 16, 512, 256],
  ['map_transition_2',    6065,   128, 16, 512, 256],
  ['map_transition_3',    6193,   128, 16, 512, 256],
  ['map_transition_4',    6321,   128, 16, 512, 256],
  ['map_tree_1',          6449,   128, 16, 512, 256],
  ['map_tree_2',          6577,   128, 16, 512, 256],
  ['map_wall_1',          6705,   128, 16, 512, 256],
  ['map_wall_2',          6833,   120, 15, 480, 256],
  ['map_wall_3',          6953,   120, 15, 480, 256],
  ['map_wall_4',          7073,   120, 15, 480, 256],
  ['map_window_1',        7193,   128, 16, 512, 256],
  ['map_window_2',        7321,   128, 16, 512, 256],
  ['map_transition_5',    7449,   128, 16, 512, 256],
].map(([name, firstgid, tilecount, columns, imgW, imgH]) =>
  ({ name, firstgid, tilecount, columns, imgW, imgH }));

function tilesetXML(ts) {
  return ` <tileset firstgid="${ts.firstgid}" name="${ts.name}" tilewidth="32" tileheight="32"` +
    ` tilecount="${ts.tilecount}" columns="${ts.columns}">\n` +
    `  <image source="../drawable/${ts.name}.png" width="${ts.imgW}" height="${ts.imgH}"/>\n` +
    ` </tileset>`;
}

// Blank tile layer data — all GID=0, base64 + ZLIB (deflate) encoded.
// This is exactly what a blank layer in Tiled produces.
function blankTileData(width, height) {
  const raw = Buffer.alloc(width * height * 4); // all zeros = GID 0 everywhere
  return zlib.deflateSync(raw).toString('base64');
}

function xmlEsc(s) {
  return String(s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

// Build a single tile layer element (always blank, base64+zlib)
function tileLayerXML(id, name, width, height, visible=true) {
  const visAttr = visible ? '' : ' visible="0"';
  return ` <layer id="${id}" name="${name}" width="${width}" height="${height}"${visAttr}>\n` +
    `  <data encoding="base64" compression="zlib">\n` +
    `   ${blankTileData(width, height)}\n` +
    `  </data>\n` +
    ` </layer>`;
}

// Build an objectgroup element
let _objId = 1;
function objectgroupXML(id, name, objects=[], visible=true) {
  const visAttr = visible ? '' : ' visible="0"';
  if (!objects.length) return ` <objectgroup id="${id}" name="${name}"${visAttr}/>`;
  const objXml = objects.map(o => buildObject(o)).join('\n');
  return ` <objectgroup id="${id}" name="${name}"${visAttr}>\n${objXml}\n </objectgroup>`;
}

// Build an individual object in real AT format
function buildObject(obj) {
  const id = _objId++;
  const { name='', type='', x=32, y=32, width=32, height=32, properties=[] } = obj;
  const propsXml = properties.length
    ? '\n   <properties>\n' +
      properties.map(p => `    <property name="${xmlEsc(p.name)}" value="${xmlEsc(String(p.value))}"/>`).join('\n') +
      '\n   </properties>'
    : '';
  return `  <object id="${id}" name="${xmlEsc(name)}" type="${xmlEsc(type)}"` +
    ` x="${x}" y="${y}" width="${width}" height="${height}">${propsXml}\n  </object>`;
}

// Build a complete TMX map matching the real AT template exactly.
// 8 blank tile layers + 4 standard object groups + any extra spawn/key/replace objects.
function buildTMX({ width=30, height=30, spawnObjects=[], keyObjects=[], replaceObjects=[], mapEventObjects=[] }) {
  _objId = 1; // object IDs are per-map

  // Total layer count: 8 tile + 4 object = 12; nextlayerid = 13
  const totalObjectGroups = 4;
  const totalTileLayers   = 8;
  const nextLayerId = totalTileLayers + totalObjectGroups + 1;
  const nextObjId   = Math.max(1, spawnObjects.length + keyObjects.length +
                                  replaceObjects.length + mapEventObjects.length) + 1;

  const tilesetXmls = AT_TILESETS.map(tilesetXML).join('\n');

  // 8 standard blank tile layers in real AT order:
  // Base(1), Ground(2), Objects(3), Objects_replace(4),
  // Above(5), Above_replace(6), Top(7), Walkable(8, hidden)
  const tileLayers = [
    tileLayerXML(1, 'Base',            width, height),
    tileLayerXML(2, 'Ground',          width, height),
    tileLayerXML(3, 'Objects',         width, height),
    tileLayerXML(4, 'Objects_replace', width, height),
    tileLayerXML(5, 'Above',           width, height),
    tileLayerXML(6, 'Above_replace',   width, height),
    tileLayerXML(7, 'Top',             width, height),
    tileLayerXML(8, 'Walkable',        width, height, false),
  ].join('\n');

  // 4 standard object groups in real AT order: Mapevents(9), Spawn(10), Keys(11), Replace(12)
  const objGroups = [
    objectgroupXML(9,  'Mapevents', mapEventObjects, false),
    objectgroupXML(10, 'Spawn',     spawnObjects,    true),
    objectgroupXML(11, 'Keys',      keyObjects,      false),
    objectgroupXML(12, 'Replace',   replaceObjects,  false),
  ].join('\n');

  return `<?xml version="1.0" encoding="UTF-8"?>
<map version="1.8" tiledversion="1.8.4" orientation="orthogonal" renderorder="right-down"` +
` width="${width}" height="${height}" tilewidth="32" tileheight="32"` +
` infinite="0" nextlayerid="${nextLayerId}" nextobjectid="${nextObjId}">
${tilesetXmls}
${tileLayers}
${objGroups}
</map>`;
}

// ─────────────────────────────────────────────────────────────────────────────
// OBJECT BUILDER HELPERS  (real AT types: spawn / key / mapchange / replace)
// ─────────────────────────────────────────────────────────────────────────────

// Spawn object — places a monster/NPC spawn zone.
// Backward-compatible: if 4th arg is an array it is treated as extraProps (old 4-arg call style).
function makeSpawnObj(spawngroup, x, y, wOrProps=32, h=32, quantity=null, extraProps=[]) {
  let w = 32, addProps = [];
  if (Array.isArray(wOrProps)) { addProps = wOrProps; }
  else { w = wOrProps; addProps = extraProps; }
  const props = [{name:'spawngroup', value:spawngroup}];
  if (quantity != null) props.push({name:'quantity', value:String(quantity)});
  props.push(...addProps);
  return { name:spawngroup, type:'spawn', x, y, width:w, height:h, properties:props };
}

// NPC object — a non-combat actor with a conversation phrase
function makeNPCObj(actorId, phrase, x, y, extraProps=[]) {
  return {
    name: actorId, type:'spawn', x, y, width:32, height:32,
    properties:[{name:'spawngroup',value:actorId},{name:'phrase',value:phrase},...extraProps],
  };
}

// Key object — interactive tile that triggers a conversation phrase
function makeKeyObj(keyName, phrase, x, y, extraProps=[]) {
  return {
    name: keyName, type:'key', x, y, width:32, height:32,
    properties:[{name:'phrase',value:phrase},...extraProps],
  };
}

// Sign object — key that shows a sign text via phrase
function makeSignObj(keyName, x, y, signText) {
  return {
    name: keyName, type:'key', x, y, width:32, height:32,
    properties:[{name:'phrase',value:'sign'},{name:'text',value:signText}],
  };
}

// Mapchange object — teleport trigger between maps
function makeMapchangeObj(name, targetMap, targetPlace, x, y, w=32, h=32) {
  return {
    name, type:'mapchange', x, y, width:w, height:h,
    properties:[{name:'map',value:targetMap},{name:'place',value:targetPlace}],
  };
}

// Replace object — triggers a layer swap at runtime
function makeReplaceObj(name, x, y, layerMap={}, extraProps=[]) {
  // layerMap e.g. { Objects:'Objects_replace', Above:'Above_replace' }
  const props = Object.entries(layerMap).map(([k,v])=>({name:k,value:v}));
  return { name, type:'replace', x, y, width:32, height:32, properties:[...props,...extraProps] };
}

// ─────────────────────────────────────────────────────────────────────────────
// MASTER DATA
// ─────────────────────────────────────────────────────────────────────────────
const REGIONS = ['grassland','shrubland','swamp','marsh','bog','desert','tundra','hills',
  'mountain','alpine','volcano','river','lake','sea','ocean',
  'small_cave','large_cave','dark_cave','damp_cave','deep_cave','hell','city','farm'];

const RACES = ['human','half_elf','elf','wood_elf','drow_elf','sea_elf','dwarf',
  'mountain_dwarf','dark_dwarf','goblin','hobgoblin','orc','ogre','halfling','gnome'];

const RACE_ATTITUDE = {
  human:'neutral',half_elf:'friendly',elf:'friendly',wood_elf:'friendly',
  drow_elf:'hostile',sea_elf:'friendly',dwarf:'neutral',mountain_dwarf:'neutral',
  dark_dwarf:'hostile',goblin:'hostile',hobgoblin:'hostile',orc:'hostile',
  ogre:'hostile',halfling:'friendly',gnome:'friendly'
};
const RACE_RIVALS = {
  human:'orc',half_elf:'dark_dwarf',elf:'drow_elf',wood_elf:'drow_elf',
  drow_elf:'wood_elf',sea_elf:'orc',dwarf:'goblin',mountain_dwarf:'dark_dwarf',
  dark_dwarf:'mountain_dwarf',goblin:'dwarf',hobgoblin:'elf',orc:'human',
  ogre:'halfling',halfling:'ogre',gnome:'hobgoblin'
};

const DRAGON_TYPES = ['Bronze','Brass','Copper','Silver','Gold','White','Black','Green','Blue','Red'];
const DRAGON_AGES  = ['baby','youngling','teen','adult'];

const GUILDS = ['adventurer','fighter','thief','mage','cleric','druid'];

const HOLIDAYS = [
  {id:'new_years',     name:'New Year\'s',    monthDay:'01-01', weeksBefore:1, weeksAfter:1, theme:'festive'},
  {id:'easter',        name:'Easter',         monthDay:'04-09', weeksBefore:1, weeksAfter:1, theme:'spring'},
  {id:'fourth_july',   name:'Fourth of July', monthDay:'07-04', weeksBefore:1, weeksAfter:1, theme:'patriotic'},
  {id:'halloween',     name:'Halloween',      monthDay:'10-31', weeksBefore:1, weeksAfter:1, theme:'spooky'},
  {id:'thanksgiving',  name:'Thanksgiving',   monthDay:'11-23', weeksBefore:1, weeksAfter:1, theme:'harvest'},
  {id:'christmas',     name:'Christmas',      monthDay:'12-25', weeksBefore:1, weeksAfter:1, theme:'winter'},
];

const EVENTS = ['birthday','graduation','wedding','funeral'];

const POKEMON_REGIONS = ['meadow','forest','mountain','ocean','volcanic','arctic','swamp','sky','shadow'];

const MOON_COLORS = ['Red','Orange','Yellow','Green','Blue','Indigo','Violet'];

// ─────────────────────────────────────────────────────────────────────────────
// CONTENT HELPERS
// ─────────────────────────────────────────────────────────────────────────────
function cap(s) { return s.charAt(0).toUpperCase()+s.slice(1); }
function cid(s) { return s.replace(/[\s\-\/\(\)]+/g,'_').toLowerCase(); }
function range(n) { return Array.from({length:n},(_,i)=>i); }
function dmg(min,max) { return {current:min,max}; }
function qty(min,max=min) { return {min,max}; }
function icon(type,row,col) { return `${type}_${row}:${col}`; }

const STRINGS = {};
function str(key,value) { STRINGS[key]=value; return `@string/${key}`; }
function strItem(id,name,desc) { str(`item_${id}`,name); str(`itemdesc_${id}`,desc||`A ${name}.`); }
function strMonster(id,name) { str(`monster_${id}`,name); }
function strConv(id,text) { str(`conv_${id}`,text); }
function strQuest(id,name,desc,...parts) {
  str(`quest_${id}`,name); str(`questdesc_${id}`,desc);
  parts.forEach((p,i)=>str(`questpart_${id}_${i}`,p));
}
function strAC(id,name) { str(`actorcondition_${id}`,name); }

function makeItem({id,name,desc='',iconRow=1,iconCol=1,itemType='miscellaneous',
  category=null,isQuestItem=false,isSellable=true,baseMarketCost=10,equipmentSlot=null,
  damagePotential=null,weight=1,useEffect=null,charges=0}) {
  strItem(id,name,desc);
  // AT format: category (not itemType), isQuestItem as int, hasManualPrice for unsellable
  const cat = category || (itemType !== 'miscellaneous' ? itemType : null);
  const item = {id, name:`@string/item_${id}`, iconID:icon('items_necklaces',1,1)};
  if (cat) item.category = cat;
  if (baseMarketCost) item.baseMarketCost = baseMarketCost;
  if (isQuestItem === true || isQuestItem === 1) item.isQuestItem = 1;
  if (isSellable === false) item.hasManualPrice = 1;
  if (weight && weight > 0) item.weight = weight;
  if (equipmentSlot) item.equipmentSlot = equipmentSlot;
  if (damagePotential) item.damagePotential = damagePotential;
  if (useEffect) item.useEffect = useEffect;
  if (charges) item.charges = charges;
  return item;
}

function makeMonster({id,name,hp=10,ap=10,atk=80,dmgMin=1,dmgMax=3,
  block=0,dr=0,droplistID=null,faction='monsters',spawnGroup=null,
  monsterClass=null,iconRow=1,iconCol=1,conversationID=null,phraseID=null}) {
  strMonster(id,name);
  // AT format: phraseID (not conversationID), spawnGroup as string
  const m = {id, name:`@string/monster_${id}`, iconID:icon('monsters_newb',1,1)};
  if (monsterClass) m.monsterClass = monsterClass;
  m.stats = {maxHP:hp, maxAP:ap, moveCost:1000, attackCost:1000, reEquipCost:1000, useItemCost:1000,
    criticalSkill:2, criticalMultiplier:2, blockChance:block, damageResistance:dr,
    attackChance:atk, damagePotential:dmg(dmgMin,dmgMax)};
  m.faction = faction;
  // spawnGroup must be a string (faction group name), not a number
  m.spawnGroup = typeof spawnGroup === 'string' ? spawnGroup : (spawnGroup !== null ? faction : faction);
  if (droplistID) m.droplistID = droplistID;
  // AT uses phraseID, not conversationID
  const pid = phraseID || conversationID;
  if (pid) m.phraseID = pid;
  return m;
}

function makeDroplist(id,items) {
  return {id,items:items.map(it=>({
    itemID:typeof it==='string'?it:it.id,
    chance:typeof it==='object'&&it.chance?it.chance:50,
    quantity:typeof it==='object'&&it.qty?qty(...it.qty):qty(1)
  }))};
}

function makeConversation(id,message,replies) {
  strConv(id,message);
  return {id,message:`@string/conv_${id}`,
    replies:replies.map(r=>({text:r.text,conditionrequirements:r.conditions||[],scriptActions:r.actions||[]}))};
}

function makeQuest(id,name,desc,parts,rewardExp=100) {
  strQuest(id,name,desc,...parts.map(p=>p.desc));
  // AT format: stages (not parts), showInLog:1, progress as integer
  return {id, name:`@string/quest_${id}`, showInLog:1,
    stages: parts.map((p,i)=>({
      progress: (i+1)*10,
      logText: `@string/questpart_${id}_${i}`,
      ...(p.exp||rewardExp ? {rewardExperience:p.exp||rewardExp} : {}),
      ...(p.reward ? {rewardItems:p.reward} : {})
    }))};
}

function makeActorCondition({id,name,category=null,isPositive=false,isStacking=false,visual=null,stats={}}) {
  strAC(id,name);
  // AT format: abilityEffect (not stats), int booleans (1 not true), no false/0 fields
  const ac = {id, name:`@string/actorcondition_${id}`, iconID:icon('actorconditions',1,1)};
  if (category) ac.category = category;
  if (isPositive === true || isPositive === 1) ac.isPositive = 1;
  if (isStacking === true || isStacking === 1) ac.isStacking = 1;
  if (visual && visual !== 'none') ac.visualEffectID = visual;
  // Convert stats object to AT abilityEffect (only non-zero values)
  const statMap = {
    maxHP:'increaseMaxHP', maxAP:'increaseMaxAP',
    moveCost:'increaseMoveCost', attackCost:'increaseAttackCost',
    reEquipCost:'increaseReequipCost', useItemCost:'increaseUseItemCost',
    criticalSkill:'increaseCriticalSkill', criticalMultiplier:'increaseCriticalMultiplier',
    blockChance:'increaseBlockChance', damageResistance:'increaseDamageResistance',
    attackChance:'increaseAttackChance'
  };
  if (stats && Object.keys(stats).length > 0) {
    const abilityEffect = {};
    for (const [k,atKey] of Object.entries(statMap)) {
      if (stats[k] !== undefined && stats[k] !== 0) abilityEffect[atKey] = stats[k];
    }
    if (stats.damagePotential) {
      const dp = stats.damagePotential;
      const mn = dp.current ?? dp.min ?? 0;
      const mx = dp.max ?? 0;
      if (mn !== 0 || mx !== 0) abilityEffect.increaseAttackDamage = {min:mn, max:mx};
    }
    if (Object.keys(abilityEffect).length > 0) ac.abilityEffect = abilityEffect;
  }
  return ac;
}

// ─────────────────────────────────────────────────────────────────────────────
// PICKPOCKET SYSTEM — gold per thief level, random kill gold<20, guild checks
// ─────────────────────────────────────────────────────────────────────────────
function buildPickpocketSystem() {
  const items = [], monsters = [], droplists = [], conversations = [];

  // Gold pouches: level 1 thief starts at 30g, scales up
  // Kill gold drop: random 1-19g
  const PICKPOCKET_GOLD = [30,50,75,110,150,200,275,360,460,600]; // per thief level 1-10
  const KILL_GOLD_ITEMS = range(19).map(g=>{
    const id=`gold_coins_${g+1}`;
    items.push(makeItem({id,name:`${g+1} Gold Coin${g?'s':''}`,
      iconRow:30,iconCol:1+g%8,baseMarketCost:g+1,useEffect:{addGold:g+1}}));
    return id;
  });

  // Pickpocket gold bags per level
  const PICKPOCKET_BAGS = PICKPOCKET_GOLD.map((gold,lvl)=>{
    const id=`pickpocket_gold_lvl${lvl+1}`;
    items.push(makeItem({id,name:`Stolen Coin Purse (${gold}g)`,iconRow:31,iconCol:1+lvl%8,
      baseMarketCost:0,useEffect:{addGold:gold}}));
    return id;
  });

  // Kill droplist: random gold 1-19
  const killDL = makeDroplist('dl_pickpocket_kill_gold',
    KILL_GOLD_ITEMS.map((id,i)=>({id,chance:Math.floor(100/(i+2))+5,qty:[1]})));
  droplists.push(killDL);

  // Per-target drop lists for pickpocket success (gold scales with thief level)
  range(200).forEach(i=>{
    const levelBag = PICKPOCKET_BAGS[Math.min(i%10, PICKPOCKET_BAGS.length-1)];
    droplists.push(makeDroplist(`dl_pickpocket_target_${i}`,
      [{id:levelBag,chance:100,qty:[1]}]));
  });

  // THE key conversation used on all 200 pickpocket target NPCs
  // Guild check: thief → pickpocket options, others → battle option
  conversations.push(makeConversation('conv_pickpocket_action',
    'This person looks like they might have some coin on them.',
    [
      // Thief options
      {text:'Pickpocket (Thief lvl 1+)',
       conditions:[{requiresGuildLevel:{guild:'thief',minLevel:1}}],
       actions:[{rollChance:{chance:50,onSuccess:'stealPickpocketGold',onFail:'caughtPickpocket_jail'}}]},
      {text:'Pickpocket + Sneak (Thief lvl 6+)',
       conditions:[{requiresGuildLevel:{guild:'thief',minLevel:6}}],
       actions:[{rollChance:{chance:75,onSuccess:'stealPickpocketGold',onFail:'caughtPickpocket_jail'}}]},
      {text:'Pickpocket + Hide (Thief lvl 9+)',
       conditions:[{requiresGuildLevel:{guild:'thief',minLevel:9}}],
       actions:[{rollChance:{chance:90,onSuccess:'stealPickpocketGold',onFail:'caughtPickpocket_jail'}}]},
      // Non-thief can battle (kill gold is random under 20)
      {text:'Battle',
       conditions:[],
       actions:[{startCombat:'$target'}]},
      {text:'Leave'}
    ]
  ));

  // Jail/caught conversation
  conversations.push(makeConversation('conv_caught_pickpocket',
    'You\'ve been caught! The guards drag you to jail.',
    [{text:'...fine.',actions:[{mapChange:{mapID:'jail',mapX:5,mapY:5}}]}]));

  // 200 NPC targets with proper kill droplists (random <20g)
  const npcNames = ['Merchant','Farmer','Traveler','Noble','Scholar','Artisan',
    'Guard off duty','Priest','Sailor','Baker','Miller','Tailor',
    'Butcher','Potter','Weaver','Tanner','Mason','Carpenter','Smith','Cooper'];
  range(200).forEach(i=>{
    monsters.push(makeMonster({
      id:`npc_pickpocket_${i}`,
      name:npcNames[i%npcNames.length]+` ${Math.floor(i/npcNames.length)+1}`,
      hp:20+Math.floor(i/20)*5,atk:50,dmgMin:1,dmgMax:3+Math.floor(i/50),
      droplistID:'dl_pickpocket_kill_gold',
      faction:'townsfolk',iconRow:3,iconCol:1+i%8,
      conversationID:'conv_pickpocket_action'
    }));
  });

  return {items,monsters,droplists,conversations};
}

// ─────────────────────────────────────────────────────────────────────────────
// TIMEKEEPER / HOLIDAY SYSTEM
// Single morphing NPC that:
//   - Between holidays: tells current date, next holiday
//   - During holiday: becomes the holiday NPC giving quests + daily gifts
//   - Handles all 6 holidays via date conditions
//   - Manages layer replacement (objects, above, walkable, spawn)
//   - Resets after holiday window, sets timer for next one
// ─────────────────────────────────────────────────────────────────────────────
function buildTimekeeperSystem() {
  const items = [], conversations = [], quests = [], actorconditions = [];

  // Holiday items: gold + 6 themed gifts + 6 "good" gifts (after quest complete)
  const holidayThemeGifts = {
    new_years:    ['Party Horn','Confetti Bag','Sparkler','Champagne','New Year\'s Hat','Countdown Clock'],
    easter:       ['Painted Egg','Chocolate Bunny','Spring Flower','Easter Basket','Jelly Beans','Marshmallow Chick'],
    fourth_july:  ['Firecracker','Flag Pin','Star Badge','Liberty Hat','Patriot Ribbon','Eagle Feather'],
    halloween:    ['Carved Pumpkin','Candy Corn','Skull Mask','Witch Hat','Spider Web','Ghost Cloth'],
    thanksgiving: ['Turkey Leg','Pumpkin Pie','Harvest Wreath','Cornucopia','Cranberry Sauce','Pilgrim Hat'],
    christmas:    ['Ornament','Candy Cane','Stocking','Wrapping Paper','Christmas Star','Snow Globe'],
  };
  const holidayGoodGifts = {
    new_years:    ['Golden Noisemaker','Silver Flute','Enchanted Confetti','Luck Charm','Year Amulet','Fortune Ring'],
    easter:       ['Magic Egg','Bunny Charm','Spring Bloom Amulet','Renewal Crystal','Life Seed','Rebirth Stone'],
    fourth_july:  ['Liberty Sword','Freedom Shield','Star Gem','Eagle Amulet','Patriot\'s Ring','Valor Crest'],
    halloween:    ['Soul Lantern','Witch\'s Brew','Shadow Cloak','Phantom Ring','Ghost Blade','Spirit Stone'],
    thanksgiving: ['Horn of Plenty','Harvest Blade','Autumn Amulet','Cornucopia Ring','Feast Charm','Bounty Gem'],
    christmas:    ['Starlight Staff','Gift of Strength','Holiday Crystal','Snowflake Amulet','Yule Blade','Winter Ring'],
  };

  HOLIDAYS.forEach((h,hi)=>{
    // Base gold gift
    items.push(makeItem({id:`holiday_gold_${h.id}`,name:`${h.name} Gold Pouch`,
      iconRow:135,iconCol:1+hi,baseMarketCost:0,useEffect:{addGold:100},
      desc:`A holiday gold pouch for ${h.name}. Collect daily!`}));
    // 6 themed gifts
    holidayThemeGifts[h.id].forEach((name,i)=>{
      items.push(makeItem({id:`holiday_gift_${h.id}_${i}`,name,
        iconRow:136+hi,iconCol:1+i,baseMarketCost:0,
        desc:`A ${h.name} gift: ${name}.`}));
    });
    // 6 good gifts (post-quest)
    holidayGoodGifts[h.id].forEach((name,i)=>{
      items.push(makeItem({id:`holiday_gift_good_${h.id}_${i}`,name,
        iconRow:142+hi,iconCol:1+i,baseMarketCost:0,
        desc:`Premium ${h.name} reward for completing the holiday quest: ${name}.`}));
    });

    // 4-part holiday quest
    const qparts = [
      {desc:`${h.name} Task 1: Speak with the Timekeeper to learn about the holiday.`,exp:100+hi*25},
      {desc:`${h.name} Task 2: Collect three ${h.name} ingredients from the world.`,exp:150+hi*30},
      {desc:`${h.name} Task 3: Complete a special ${h.name} challenge.`,exp:200+hi*40},
      {desc:`${h.name} Task 4: Return to the Timekeeper to celebrate!`,exp:300+hi*50},
    ];
    quests.push(makeQuest(`quest_holiday_${h.id}`,`${h.name} Celebration`,
      `Help the Timekeeper celebrate ${h.name}!`,qparts));

    // Actor condition: currently this holiday
    actorconditions.push(makeActorCondition({
      id:`ac_holiday_active_${h.id}`,name:`${h.name} Is Active`,isPositive:true,
    }));
    // Actor condition: quest complete (for better gifts)
    actorconditions.push(makeActorCondition({
      id:`ac_holiday_quest_done_${h.id}`,name:`${h.name} Quest Complete`,isPositive:true,
    }));
    // Actor condition: daily gift given
    actorconditions.push(makeActorCondition({
      id:`ac_holiday_gift_given_${h.id}`,name:`${h.name} Daily Gift Given`,isPositive:false,
    }));
  });

  // Event items
  const eventThemeGifts = {
    birthday:   ['Birthday Cake','Party Hat','Balloon','Candle','Gift Bow','Birthday Card'],
    graduation: ['Diploma','Cap and Gown Token','Scholar\'s Pen','Wisdom Stone','Victory Wreath','Achievement Medal'],
    wedding:    ['Wedding Ring','Bouquet','Veil Charm','Unity Candle','Love Token','Celebration Ribbon'],
    funeral:    ['Memorial Flower','Remembrance Candle','Mourning Veil','Tribute Stone','Elegy Scroll','Rest in Peace Token'],
  };
  EVENTS.forEach((event,ei)=>{
    eventThemeGifts[event].forEach((name,i)=>{
      items.push(makeItem({id:`event_gift_${event}_${i}`,name,
        iconRow:150+ei,iconCol:1+i,baseMarketCost:0,
        desc:`A ${event} gift: ${name}.`}));
    });
    actorconditions.push(makeActorCondition({id:`ac_event_active_${event}`,
      name:`${cap(event)} Event Active`,isPositive:true}));
  });

  // Time crystal for Timekeeper quest
  items.push(makeItem({id:'item_time_crystal',name:'Time Crystal',iconRow:155,iconCol:1,
    isQuestItem:true,isSellable:false,baseMarketCost:0,
    desc:'A crystal attuned to the flow of time. Carry it for one week for the Timekeeper.'}));

  // ── TIMEKEEPER CONVERSATIONS ─────────────────────────────────────────────
  // The Timekeeper is a SINGLE NPC with a branching conversation.
  // During a holiday: they become the holiday host.
  // Between holidays: they tell the date and next holiday.

  // Master Timekeeper conversation (checks each holiday condition in order)
  const holidayReplies = HOLIDAYS.flatMap(h=>[
    // If this holiday is active: show holiday options
    {text:`[${h.name} Active] Happy ${h.name}! Claim your daily gift.`,
     conditions:[{requiresActorCondition:`ac_holiday_active_${h.id}`}],
     actions:[
       {giveItemWithFallback:{
         condition:`ac_holiday_quest_done_${h.id}`,
         ifTrue:  `holiday_gift_good_${h.id}_0`,
         ifFalse: `holiday_gold_${h.id}`
       }},
       {setActorCondition:`ac_holiday_gift_given_${h.id}`},
     ]},
    {text:`[${h.name}] View ${h.name} Quest`,
     conditions:[{requiresActorCondition:`ac_holiday_active_${h.id}`}],
     actions:[{startQuest:`quest_holiday_${h.id}`}]},
    {text:`[${h.name}] Advance ${h.name} Quest`,
     conditions:[{requiresActorCondition:`ac_holiday_active_${h.id}`},{requiresQuestPart:{questID:`quest_holiday_${h.id}`,part:0}}],
     actions:[{setQuestPart:{questID:`quest_holiday_${h.id}`,part:1}}]},
  ]);

  conversations.push(makeConversation('conv_timekeeper',
    'I am the Timekeeper. I watch the flow of days and manage the great festivals.',
    [
      ...holidayReplies,
      {text:'What is today\'s date?',actions:[{showCurrentDate:true}]},
      {text:'When is the next holiday?',actions:[{showNextHoliday:true}]},
      {text:'Accept Timekeeper Quest',
       conditions:[{requiresQuestPartNotStarted:'quest_timekeeper_crystal'}],
       actions:[{giveItem:'item_time_crystal'},{startQuest:'quest_timekeeper_crystal'}]},
      {text:'Here is the Time Crystal (quest complete)',
       conditions:[{hasItem:'item_time_crystal'},{requiresQuestPart:{questID:'quest_timekeeper_crystal',part:0}}],
       actions:[{consumeItem:'item_time_crystal'},{setQuestPart:{questID:'quest_timekeeper_crystal',part:1}}]},
      {text:'Leave'},
    ]
  ));

  // Event planner conversations
  EVENTS.forEach((event,ei)=>{
    conversations.push(makeConversation(`conv_event_planner_${event}`,
      `I can arrange a ${event} celebration! It will last 24 hours and transform this area.`,
      [
        {text:`Arrange ${cap(event)} (500g)`,
         actions:[{payGold:500},{setActorCondition:`ac_event_active_${event}`},{triggerEventReplace:event}]},
        {text:'Leave'},
      ]
    ));
    conversations.push(makeConversation(`conv_event_npc_${event}`,
      `Congratulations on your ${event}! Here is a gift from all of us.`,
      [{text:'Thank you!',actions:[{giveItem:`event_gift_${event}_0`}]},{text:'Thanks!'}]
    ));
  });

  // Timekeeper quest
  quests.push(makeQuest('quest_timekeeper_crystal','Keeper of Time',
    'Carry the Time Crystal for 7 days to help the Timekeeper calibrate the holidays.',
    [{desc:'Carry the Time Crystal for 7 days without losing it.',exp:2000}]
  ));

  return {items,conversations,quests,actorconditions};
}

// ─────────────────────────────────────────────────────────────────────────────
// ANIMAL + FORAGE + MINING CONTENT
// ─────────────────────────────────────────────────────────────────────────────
const REGION_ANIMAL_NAMES = {
  grassland:['Deer','Rabbit','Fox','Wolf','Hawk','Boar','Badger','Hare','Elk','Bison','Pheasant','Vole','Mole','Sparrow','Falcon','Weasel','Otter','Hedgehog','Squirrel','Crow','Magpie','Frog','Toad','Snake','Lizard'],
  shrubland:['Scrub Jay','Roadrunner','Jackrabbit','Coyote','Ground Squirrel','Horned Lizard','Gila Woodpecker','Burrowing Owl','Diamondback','Gopher Snake','Collared Lizard','Scaled Quail','Kit Fox','Antelope','Pronghorn','Rock Wren','Sage Grouse','Desert Cottontail','Black Bear','Mountain Lion','Mule Deer','Wild Turkey','Spotted Skunk','Ringtail','Javelina'],
  swamp:['Alligator','Bullfrog','Water Moccasin','Egret','Heron','Swamp Rat','Marsh Hawk','Mud Turtle','Water Snake','Snapping Turtle','Wood Duck','Swamp Fox','Catfish','Gar','Cottonmouth','River Otter','Nutria','Swamp Rabbit','Mink','Beaver','Anhinga','Bittern','Tricolor Heron','Roseate Spoonbill','Purple Gallinule'],
  marsh:['Marsh Wren','Redwing Blackbird','Bittern','Rail','Coot','Mallard','Teal','Pintail','Shoveler','Gadwall','Canvasback','Scaup','Bufflehead','Goldeneye','Merganser','Grebe','Moorhen','Purple Swamphen','Glossy Ibis','Snipe','Curlew','Godwit','Dunlin','Sandpiper','Plover'],
  bog:['Sundew Crawler','Pitcher Slug','Bogworm','Peat Frog','Sphagnum Newt','Mire Serpent','Cotton Grass Vole','Willow Tit','Bog Lemming','Swamp Deer','Crane Fly Larva','Water Boatman','Dragonfly Nymph','Mud Skimmer','Peat Mole','Bog Turtle','Adder','Palmate Newt','Great Diving Beetle','Raft Spider','Water Scorpion','Whirligig Beetle','Marsh Fritillary','Large Heath Butterfly','Bog Bush Cricket'],
  desert:['Camel','Scorpion','Sand Viper','Fennec Fox','Jerboa','Desert Rat','Vulture','Horned Viper','Monitor Lizard','Chameleon','Desert Owl','Sandgrouse','Oryx','Addax','Dorcas Gazelle','Sand Cat','Caracal','Meerkat','Aardvark','Pangolin','Desert Hare','Spiny Mouse','Gerbil','Fat Tailed Scorpion','Deathstalker'],
  tundra:['Arctic Fox','Polar Bear','Snowy Owl','Lemming','Musk Ox','Caribou','Arctic Hare','Ptarmigan','Wolverine','Ermine','Arctic Wolf','Walrus','Seal','Sea Lion','Narwhal','Beluga','Puffin','Gyrfalcon','Rough Legged Hawk','Long Tailed Duck','King Eider','Oldsquaw','Ivory Gull','Ross Gull','Sabines Gull'],
  hills:['Hill Fox','Moorland Pony','Kite','Buzzard','Peregrine','Merlin','Curlew','Lapwing','Golden Plover','Short Eared Owl','Mountain Hare','Polecat','Pine Marten','Red Grouse','Black Grouse','Stonechat','Wheatear','Ring Ouzel','Dipper','Grey Wagtail','Whinchat','Reed Bunting','Twite','Dunlin','Dotterel'],
  mountain:['Mountain Goat','Snow Leopard','Ibex','Chamois','Yak','Pika','Marmot','Eagle','Condor','Alpine Chough','Snowcock','Bharal','Markhor','Tahr','Argali','Urial','Saiga','Wild Ass','Kiang','Marco Polo Sheep','Himalayan Wolf','Red Panda','Takin','Serow','Goral'],
  alpine:['Alpine Marmot','Edelweiss Moth','Snow Bunting','Alpine Accentor','Alpine Salamander','Wallcreeper','Rock Ptarmigan','Lammergeier','Alpine Swift','Citril Finch','Snowfinch','Alpine Chough','Mountain Ringlet','Apollo Butterfly','Alpine Longhorn Beetle','Alpine Ibex','Chamois','Steinbock','Swiss Cow','St Bernard Dog','Alpine Newt','Yellow Bellied Toad','Alpine Marmot Dark','Hoary Marmot','Olympic Marmot'],
  volcano:['Fire Salamander','Lava Lizard','Ashen Drake','Ember Bat','Magma Wurm','Cinder Beetle','Ash Crawler','Flame Newt','Scorching Scorpion','Pyroclast Serpent','Burning Boar','Smoke Raven','Igneous Golem','Caldera Crab','Sulfur Sprite','Basalt Turtle','Obsidian Spider','Char Bear','Flare Hawk','Thermal Eel','Fissure Worm','Heat Ray','Pyroclast Hound','Lava Guppy','Magma Shrimp'],
  river:['Trout','Salmon','Pike','Perch','Catfish','Crayfish','River Otter','Kingfisher','Heron','Mallard','Water Rat','Beaver','Mink','Dipper','Goosander','Lamprey','Stone Loach','Bullhead','Dace','Chub','Roach','Tench','Bream','Barbel','Grayling'],
  lake:['Bass','Walleye','Lake Trout','Sunfish','Crappie','Bluegill','Carp','Muskie','Northern Pike','Cisco','Whitefish','Smelt','Alewife','Lake Sturgeon','Bowfin','Longnose Gar','Shortnose Gar','Rock Bass','Yellow Perch','Pumpkinseed','Warmouth','Redear Sunfish','Green Sunfish','Spotted Bass','Smallmouth Bass'],
  sea:['Shark','Swordfish','Tuna','Marlin','Manta Ray','Barracuda','Moray Eel','Grouper','Snapper','Amberjack','Dolphinfish','Flying Fish','Wahoo','King Mackerel','Cobia','Tarpon','Bonefish','Permit','Snook','Redfish','Flounder','Pompano','Spanish Mackerel','Bluefish','Striped Bass'],
  ocean:['Blue Whale','Sperm Whale','Orca','Great White Shark','Hammerhead Shark','Giant Squid','Nautilus','Sea Turtle','Albatross','Storm Petrel','Frigate Bird','Booby','Tropicbird','Shearwater','Gannet','Oarfish','Sunfish','Sailfish','Swordfish Deep','Viperfish','Anglerfish','Gulper Eel','Fangtooth','Hatchetfish','Dragonfish'],
  small_cave:['Cave Cricket','Cave Spider','Cave Fish','Cave Frog','Bat','Centipede','Cave Rat','Blind Salamander','Pale Crawler','Cave Snail','Troglodyte Beetle','Cave Shrimp','Spring Fish','Grotto Sculpin','Tumbling Creek Cavefish','Ozark Cavefish','Banded Sculpin','Stonefly Larva','Caddisfly Larva','Mayfly Larva','Hellgrammite','Water Penny','Riffle Beetle','Crane Fly','Gnat'],
  large_cave:['Cave Bear','Dire Wolf','Troglodyte','Cave Lion','Saber Cat','Giant Spider','Cave Troll','Rock Lizard','Stone Golem','Cave Beetle','Stalactite Snake','Mushroom Slug','Blind Cavefish','Giant Centipede','Cave Scorpion','Stone Crab','Cave Lobster','Albino Bat','Ghostly Moth','Phosphor Worm','Crystal Beetle','Pale Toad','Cave Pearl Mollusk','Deep Cricket','Dark Newt'],
  dark_cave:['Shadow Bat','Void Spider','Dark Crawler','Nightmare Rat','Shade Wolf','Umbral Serpent','Blackened Lizard','Dark Troll','Obsidian Beetle','Shadow Stalker','Darkness Imp','Night Creeper','Hollow Eyes','Murk Worm','Pitch Moth','Eclipse Frog','Penumbra Crab','Tenebrous Snail','Dark Crystal Bug','Shadowmeld Cat','Nocturne Hawk','Abyss Rat','Dim Firefly','Nightshade Slug','Dark Mole'],
  damp_cave:['Mudskipper','Water Strider','Dampworm','Puddle Frog','Cave Eel','Moist Centipede','Wet Rock Crab','Slime Slug','Brine Shrimp','Cave Leech','Moisture Bat','Dripstone Snail','Cave Pearl Clam','Waterfall Spider','Drip Beetle','Soggy Rat','Moist Toad','Puddle Salamander','Cave Crayfish','Blind Crab','Aquifer Fish','Seepage Worm','Mineral Spring Frog','Damp Gecko','Mold Cricket'],
  deep_cave:['Deepstone Worm','Abyssal Crawler','Underworld Bat','Subterranean Drake','Blind Cave Titan','Underearth Troll','Rock Devourer','Stone Leech','Primordial Slime','Deep Earth Beetle','Obsidian Golem','Crystalline Spider','Phosphor Moth','Cave Chimera','Petrified Scorpion','Underground Shark','Magma Snail','Subterranean Eel','Stone Serpent','Deep Rock Crab','Earth Elemental','Mineral Bat','Cave Leviathan','Underworld Rat','Bedrock Bear'],
  hell:['Imp','Demon','Devil','Hellhound','Succubus','Incubus','Balor','Marilith','Nalfeshnee','Glabrezu','Hezrou','Vrock','Dretch','Quasit','Lemure','Pit Fiend','Erinyes','Barbed Devil','Bone Devil','Chain Devil','Bearded Devil','Ice Devil','Horned Devil','Amnizu','Narzugon'],
  city:['Alley Cat','City Rat','Pigeon','Crow','Raccoon','Fox','Stray Dog','Street Mouse','Feral Rabbit','City Falcon','Urban Bat','Sewer Rat','Chimney Swift','House Sparrow','Starling','Common Myna','House Mouse','Brown Rat','Black Rat','Garden Hedgehog','Urban Fox','Feral Cat','Roof Rat','Pavement Ant','Honey Bee'],
  farm:['Chicken','Pig','Cow','Sheep','Goat','Horse','Duck','Goose','Turkey','Donkey','Mule','Rabbit','Cat','Dog','Rooster','Guinea Fowl','Peacock','Llama','Alpaca','Emu','Ostrich','Pheasant','Quail','Partridge','Pigeon'],
};

function buildAnimalContent() {
  const items=[],monsters=[],droplists=[];
  REGIONS.forEach((region,ri)=>{
    const names = REGION_ANIMAL_NAMES[region]||REGION_ANIMAL_NAMES.grassland;
    range(25).forEach(i=>{
      const animalName = names[i]||`${cap(region)} Creature ${i+1}`;
      const animalId = `animal_${cid(region)}_${i}`;
      const dropId = `ingredient_${cid(region)}_${i}`;
      items.push(makeItem({id:dropId,name:`${animalName} Drop`,iconRow:3,iconCol:1+i%8,
        baseMarketCost:5,desc:`Crafting ingredient dropped by the ${animalName}.`}));
      const dl = makeDroplist(`dl_${animalId}`,[{id:dropId,chance:80,qty:[1,2]}]);
      droplists.push(dl);
      monsters.push(makeMonster({id:animalId,name:animalName,
        hp:5+ri*2+i*2,atk:60+ri,dmgMin:1+Math.floor(i/8),dmgMax:3+ri+Math.floor(i/5),
        droplistID:dl.id,faction:'animals',iconRow:4+ri,iconCol:1+i%8}));
    });
  });
  return {items,monsters,droplists};
}

function buildForageContent() {
  const items=[],conversations=[],quests=[];
  const forageNames=['Herb','Mushroom','Root','Berry','Seed','Flower','Bark','Moss','Lichen','Resin',
    'Leaf','Vine','Tuber','Fungus','Algae','Crystal','Mineral','Sap','Spore','Petal','Bulb','Nectar','Fiber','Clay','Salt'];
  REGIONS.forEach((region,ri)=>{
    forageNames.forEach((base,i)=>{
      items.push(makeItem({id:`forage_${cid(region)}_${i}`,
        name:`${cap(region.replace('_',' '))} ${base}`,iconRow:20,iconCol:1+i%8,
        baseMarketCost:8,desc:`A foraged ${base.toLowerCase()} from the ${region.replace('_',' ')}.`}));
    });
    const convId=`conv_forage_${cid(region)}`;
    conversations.push(makeConversation(convId,
      `You spot a promising foraging area in the ${region.replace('_',' ')}. Search for ingredients?`,
      [{text:'Search (90% chance)',
        conditions:[{notHasCondition:`forage_${cid(region)}_used`}],
        actions:[
          {rollChance:{chance:90,onSuccess:`giveForageItem_${cid(region)}`,onFail:'nothing'}},
          {setCondition:`forage_${cid(region)}_used`},
          {scheduleConditionReset:{condition:`forage_${cid(region)}_used`,hours:24}},
        ]},
       {text:'Come back tomorrow.',
        conditions:[{hasCondition:`forage_${cid(region)}_used`}]},
       {text:'Leave'}]
    ));
    quests.push(makeQuest(`quest_forage_${cid(region)}`,
      `Forage in ${cap(region.replace('_',' '))}`,
      `Gather crafting ingredients from the ${region.replace('_',' ')}.`,
      [{desc:`Search the ${region.replace('_',' ')} for useful ingredients.`,exp:25+ri*5}]
    ));
  });
  return {items,conversations,quests};
}

// Mining
const CRYSTALS=['Quartz Crystal','Amethyst Crystal','Sapphire Crystal','Ruby Crystal','Emerald Crystal','Diamond Crystal','Obsidian Crystal','Citrine Crystal','Topaz Crystal','Garnet Crystal','Aquamarine Crystal','Opal Crystal'];
const GEMS=['Raw Ruby','Raw Sapphire','Raw Emerald','Raw Diamond','Raw Amethyst','Raw Topaz','Raw Garnet','Raw Opal','Raw Aquamarine','Raw Citrine','Raw Peridot','Raw Tourmaline'];
const ORES=['Iron Ore','Copper Ore','Silver Ore','Gold Ore','Mithril Ore','Adamantite Ore','Bronze Ore','Tin Ore','Platinum Ore','Cobalt Ore','Titanium Ore','Dark Iron Ore'];
const INGOTS=['Iron Ingot','Copper Ingot','Silver Ingot','Gold Ingot','Mithril Ingot','Adamantite Ingot','Bronze Ingot','Tin Ingot','Platinum Ingot','Cobalt Ingot','Titanium Ingot','Dark Iron Ingot'];
const WORTHLESS=['Common Pebble','Gray Rock','Dull Stone','Muddy Rock','Cracked Stone','Sandy Gravel','Limestone Chunk','Sandstone Shard','Shale Fragment','Basalt Chip','Pumice Stone','Slate Fragment'];

function buildMiningContent() {
  const items=[],droplists=[],conversations=[];
  const allMined=[...CRYSTALS,...GEMS,...ORES,...INGOTS,...WORTHLESS];
  allMined.forEach((name,i)=>{
    items.push(makeItem({id:`mining_${cid(name)}`,name,iconRow:40+Math.floor(i/8),
      iconCol:1+i%8,baseMarketCost:20+i*5,desc:`Mined from rocky outcroppings.`}));
  });
  items.push(makeItem({id:'item_pick_axe',name:'Pick Axe',iconRow:50,iconCol:1,
    itemType:'weapon',equipmentSlot:'weapon',damagePotential:dmg(2,5),baseMarketCost:50,
    desc:'A sturdy pick axe for mining. Equip it to mine rock outcroppings.'}));
  ['Mining Helmet','Mining Gloves','Mining Boots','Mining Belt','Ore Bag'].forEach((name,i)=>{
    items.push(makeItem({id:`mining_equip_${i}`,name,iconRow:50,iconCol:2+i,baseMarketCost:30+i*10}));
  });
  const miningDL = makeDroplist('dl_mining_rock',
    allMined.map((name,i)=>({id:`mining_${cid(name)}`,chance:Math.max(5,35-i),qty:[1,3]})));
  droplists.push(miningDL);
  conversations.push(makeConversation('conv_mining_rock',
    'A rocky outcropping with veins of mineral ore. You need a Pick Axe equipped to mine it.',
    [{text:'Mine (needs Pick Axe equipped)',
      conditions:[{hasEquippedItem:'item_pick_axe'}],
      actions:[{giveDropList:'dl_mining_rock'}]},
     {text:'Leave'}]
  ));
  return {items,droplists,conversations};
}

// ─────────────────────────────────────────────────────────────────────────────
// CRAFTING ITEMS
// ─────────────────────────────────────────────────────────────────────────────
function buildCraftingItems() {
  const items=[];
  // Cloth
  const CLOTH={head:['Woven Cap','Linen Hood','Cotton Hat','Silk Coif','Velvet Beret','Wool Beanie'],
    body:['Linen Shirt','Cotton Tunic','Silk Robe','Wool Jerkin','Velvet Coat','Hemp Vest'],
    hand:['Cloth Gloves','Linen Mittens','Cotton Wraps','Silk Gloves','Wool Mitts','Hemp Handwraps'],
    feet:['Cloth Shoes','Linen Sandals','Cotton Boots','Silk Slippers','Wool Socks','Hemp Sandals'],
    neck:['Cloth Choker','Linen Necklace','Cotton Scarf','Silk Ribbon','Wool Wrap','Hemp Cord']};
  Object.entries(CLOTH).forEach(([slot,names])=>{
    names.forEach((name,i)=>items.push(makeItem({id:`cloth_${slot}_${i}`,name,iconRow:55,iconCol:1+i,
      itemType:'armor',equipmentSlot:slot,damageResistance:1+i,baseMarketCost:20+i*15})));
  });
  ['Linen Thread','Cotton Thread','Silk Thread','Wool Thread','Velvet Fabric','Hemp Fiber'].forEach((name,i)=>
    items.push(makeItem({id:`material_cloth_${i}`,name,iconRow:56,iconCol:1+i,baseMarketCost:5+i*3})));

  // Food
  const FOODS=['Roast Chicken','Grilled Fish','Mushroom Soup','Hearty Stew','Vegetable Pie','Bread Loaf',
    'Cheese Wheel','Smoked Ham','Boiled Eggs','Fruit Salad','Beef Jerky','Salted Pork'];
  FOODS.forEach((name,i)=>items.push(makeItem({id:`food_${cid(name)}`,name,iconRow:57,iconCol:1+i,
    baseMarketCost:8,useEffect:{restoreHP:{current:5+i*3,max:10+i*3}},desc:`A delicious ${name.toLowerCase()}.`})));

  // Produce + seeds
  const PRODUCE=['Apple','Orange','Pear','Grape','Strawberry','Blueberry','Tomato','Carrot',
    'Potato','Onion','Garlic','Corn','Pumpkin','Squash','Cucumber','Lettuce',
    'Spinach','Broccoli','Cabbage','Pea','Bean','Radish','Turnip','Parsnip'];
  PRODUCE.forEach((name,i)=>{
    items.push(makeItem({id:`produce_${cid(name)}`,name,iconRow:58+Math.floor(i/8),iconCol:1+i%8,
      baseMarketCost:4,useEffect:{restoreHP:{current:3,max:5}}}));
    items.push(makeItem({id:`seed_${cid(name)}`,name:`${name} Seed`,iconRow:60+Math.floor(i/8),
      iconCol:1+i%8,baseMarketCost:2}));
  });
  items.push(makeItem({id:'item_hoe',name:'Hoe',iconRow:62,iconCol:1,
    itemType:'weapon',equipmentSlot:'weapon',damagePotential:dmg(1,2),baseMarketCost:15,
    desc:'A garden hoe. Equip it to tend your garden plot.'}));

  // Forge
  const FORGE_WEAPONS=['Short Sword','Long Sword','Battle Axe','War Hammer','Spear','Dagger','Mace','Flail','Halberd','Glaive','Trident','Club'];
  const FORGE_SHIELDS=['Buckler','Round Shield','Kite Shield','Tower Shield','Heater Shield','Targe','Pavise','Scutum','Aspis','Hoplon','Spiked Shield','Reinforced Shield'];
  FORGE_WEAPONS.forEach((name,i)=>items.push(makeItem({id:`forge_weapon_${i}`,name,iconRow:63,iconCol:1+i,
    itemType:'weapon',equipmentSlot:'weapon',damagePotential:dmg(2+i,6+i*2),baseMarketCost:60+i*20})));
  FORGE_SHIELDS.forEach((name,i)=>items.push(makeItem({id:`forge_shield_${i}`,name,iconRow:64,iconCol:1+i,
    itemType:'armor',equipmentSlot:'offhand',damageResistance:2+i,baseMarketCost:50+i*15})));
  ['Iron Bar','Copper Sheet','Steel Rod','Coal','Flux','Tongs'].forEach((name,i)=>
    items.push(makeItem({id:`forge_mat_${i}`,name,iconRow:65,iconCol:1+i,baseMarketCost:10+i*5})));

  // Bench armor
  const BENCH={head:['Iron Helm','Bronze Helmet','Steel Coif','Chain Coif','Scale Helm','Plate Helm'],
    body:['Iron Breastplate','Bronze Cuirass','Steel Hauberk','Chainmail Shirt','Scale Armor','Platemail'],
    hand:['Iron Gauntlets','Bronze Gloves','Steel Vambraces','Chain Gloves','Scale Gauntlets','Plate Gauntlets'],
    feet:['Iron Boots','Bronze Greaves','Steel Sabatons','Chain Boots','Scale Boots','Plate Boots']};
  Object.entries(BENCH).forEach(([slot,names])=>{
    names.forEach((name,i)=>items.push(makeItem({id:`bench_armor_${slot}_${i}`,name,iconRow:66,iconCol:1+i,
      itemType:'armor',equipmentSlot:slot,damageResistance:3+i*2,baseMarketCost:80+i*25})));
  });

  // Miner forge
  const MF_WEAPONS=['Crystal Blade','Mithril Sword','Adamantite Axe','Silver Dagger','Gold Mace','Cobalt Spear','Platinum Glaive','Dark Iron Club','Titanium Halberd','Sapphire Wand','Ruby Scepter','Emerald Staff'];
  MF_WEAPONS.forEach((name,i)=>items.push(makeItem({id:`miner_forge_weapon_${i}`,name,iconRow:67,iconCol:1+i,
    itemType:'weapon',equipmentSlot:'weapon',damagePotential:dmg(5+i,12+i*2),baseMarketCost:150+i*30})));
  range(24).forEach(i=>items.push(makeItem({id:`miner_ring_${i}`,name:`${['Iron','Copper','Silver','Gold','Mithril','Adamantite','Bronze','Tin','Platinum','Cobalt','Titanium','Dark Iron','Ruby','Sapphire','Emerald','Diamond','Amethyst','Topaz','Garnet','Opal','Aquamarine','Citrine','Quartz','Crystal'][i]} Ring`,
    iconRow:68+Math.floor(i/8),iconCol:1+i%8,itemType:'armor',equipmentSlot:'ring',
    damageResistance:1+Math.floor(i/4),baseMarketCost:80+i*20})));

  // Game console / computer items
  items.push(makeItem({id:'item_logout_scroll',name:'Logout Scroll',iconRow:70,iconCol:1,
    isQuestItem:false,baseMarketCost:0,charges:1,
    useEffect:{mapChangeToSaved:'console_room'},
    desc:'Returns you to the room where you entered the game world.'}));

  // Home deeds
  ['small','mid','large','luxury'].forEach((size,i)=>
    items.push(makeItem({id:`item_deed_${size}_home`,name:`${cap(size)} Home Deed`,
      iconRow:70,iconCol:2+i,isQuestItem:true,isSellable:false,baseMarketCost:500*(i+1),
      desc:`Deed for a ${size} home. Show to Realtor to claim it.`})));

  // Crafting skill manuals
  ['Weaving','Cooking','Gardening','Smithing','Armorcraft','Minercraft'].forEach((skill,i)=>{
    items.push(makeItem({id:`skill_manual_${cid(skill)}`,name:`${skill} Manual`,
      iconRow:71,iconCol:1+i,isQuestItem:true,baseMarketCost:100+i*50}));
    items.push(makeItem({id:`skill_manual_adv_${cid(skill)}`,name:`Advanced ${skill} Manual`,
      iconRow:72,iconCol:1+i,isQuestItem:true,baseMarketCost:300+i*100}));
  });

  return {items};
}

// ─────────────────────────────────────────────────────────────────────────────
// GUILD ITEMS (scrolls, potions, wands, staffs, etc.)
// ─────────────────────────────────────────────────────────────────────────────
function buildGuildItems() {
  const items=[],actorconditions=[];
  const OFFSCROLLS=['Scroll of Fireball','Scroll of Lightning Bolt','Scroll of Ice Storm','Scroll of Acid Splash','Scroll of Poison Cloud','Scroll of Meteor Storm','Scroll of Thunder Clap','Scroll of Death Ray','Scroll of Curse','Scroll of Banish','Scroll of Disintegrate','Scroll of Dominate'];
  const DEFSCROLLS=['Scroll of Shield','Scroll of Stoneskin','Scroll of Mirror Image','Scroll of Protection','Scroll of Sanctuary','Scroll of Blur','Scroll of Displacement','Scroll of Globe','Scroll of Blink','Scroll of Mind Blank','Scroll of Freedom','Scroll of True Seeing'];
  OFFSCROLLS.forEach((name,i)=>{
    const acId=`ac_scroll_off_${i}`;
    actorconditions.push(makeActorCondition({id:acId,name:`${name} Effect`,isPositive:false,
      stats:{attackChance:-(5+i*3),damagePotential:dmg(-(1+i),0)}}));
    items.push(makeItem({id:`scroll_offensive_${i}`,name,iconRow:75,iconCol:1+i,charges:1,
      useEffect:{applyActorCondition:{conditionID:acId,duration:3}},baseMarketCost:80+i*20}));
  });
  DEFSCROLLS.forEach((name,i)=>{
    const acId=`ac_scroll_def_${i}`;
    actorconditions.push(makeActorCondition({id:acId,name:`${name} Effect`,isPositive:true,
      stats:{blockChance:5+i*3,damageResistance:2+i}}));
    items.push(makeItem({id:`scroll_defensive_${i}`,name,iconRow:76,iconCol:1+i,charges:1,
      useEffect:{applyActorCondition:{conditionID:acId,duration:5}},baseMarketCost:100+i*25}));
  });

  // Special guild scrolls (Mage/Cleric/Druid desks, guild 3+)
  const specScrolls=[
    {id:'scroll_door_pass_mage',name:'Mage Door Pass Scroll',guild:'mage'},
    {id:'scroll_door_pass_cleric',name:'Cleric Door Pass Scroll',guild:'cleric'},
    {id:'scroll_door_pass_druid',name:'Druid Door Pass Scroll',guild:'druid'},
    {id:'scroll_recall_mage',name:'Mage Guild Recall Scroll',guild:'mage',effect:'mapChange_mage_guild'},
    {id:'scroll_recall_cleric',name:'Cleric Guild Recall Scroll',guild:'cleric',effect:'mapChange_cleric_guild'},
    {id:'scroll_recall_druid',name:'Druid Guild Recall Scroll',guild:'druid',effect:'mapChange_druid_guild'},
    {id:'scroll_recall_adventurer',name:'Adventurer Guild Recall',guild:'any',effect:'mapChange_adventurer_guild'},
    {id:'scroll_recall_house',name:'House Recall Scroll',guild:'any',effect:'mapChange_house'},
    {id:'scroll_recall_home',name:'Home Recall Scroll',guild:'any',effect:'mapChange_home'},
    {id:'scroll_invisibility_mage',name:'Invisibility Scroll (Mage)',guild:'mage'},
    {id:'scroll_invisibility_cleric',name:'Invisibility Scroll (Cleric)',guild:'cleric'},
    {id:'scroll_invisibility_druid',name:'Invisibility Scroll (Druid)',guild:'druid'},
  ];
  actorconditions.push(makeActorCondition({id:'ac_invisibility',name:'Invisibility',isPositive:true,visual:'invisible'}));
  specScrolls.forEach((s,i)=>items.push(makeItem({id:s.id,name:s.name,iconRow:77,iconCol:1+i,
    charges:1,baseMarketCost:200,desc:`${s.name}. Restricted to ${s.guild} guild.`})));

  // Lockpicks + master key + door key
  const LOCKPICKS=[{id:'lockpick_basic',name:'Basic Lockpick',fail:80},
    {id:'lockpick_iron',name:'Iron Lockpick',fail:60},
    {id:'lockpick_steel',name:'Steel Lockpick',fail:40},
    {id:'lockpick_master_pick',name:'Master Lockpick',fail:20}];
  LOCKPICKS.forEach((lp,i)=>items.push(makeItem({id:lp.id,name:lp.name,
    iconRow:78,iconCol:1+i,baseMarketCost:20+i*30,desc:`${lp.fail}% base failure rate.`})));
  items.push(makeItem({id:'item_master_key',name:'Master Key',iconRow:78,iconCol:5,
    baseMarketCost:500,desc:'Opens any door. Extremely rare.'}));
  items.push(makeItem({id:'item_door_key',name:'Door Key',iconRow:78,iconCol:6,baseMarketCost:50}));

  // Deposit box key
  items.push(makeItem({id:'item_deposit_box_key',name:'Safety Deposit Box Key',
    iconRow:78,iconCol:7,isQuestItem:true,isSellable:false}));

  return {items,actorconditions};
}

// ─────────────────────────────────────────────────────────────────────────────
// GUILD CONVERSATIONS
// ─────────────────────────────────────────────────────────────────────────────
function buildGuildConversations() {
  const conversations=[],quests=[];
  // Door
  conversations.push(makeConversation('conv_door',
    'A locked door bars your way.',
    [{text:'Open with Key',conditions:[{hasItem:'item_door_key'}],actions:[{consumeItem:'item_door_key'},{openDoor:true}]},
     {text:'Open with Master Key',conditions:[{hasItem:'item_master_key'}],actions:[{openDoor:true}]},
     {text:'Pick Lock — Basic (Thief 3+, 20% success)',conditions:[{hasItem:'lockpick_basic'},{requiresGuildLevel:{guild:'thief',minLevel:3}}],actions:[{rollChance:{chance:20,onSuccess:'openDoor',onFail:'breakItem_lockpick_basic'}}]},
     {text:'Pick Lock — Iron (Thief 3+, 40% success)', conditions:[{hasItem:'lockpick_iron'},{requiresGuildLevel:{guild:'thief',minLevel:3}}],actions:[{rollChance:{chance:40,onSuccess:'openDoor',onFail:'breakItem_lockpick_iron'}}]},
     {text:'Pick Lock — Steel (Thief 5+, 60% success)',conditions:[{hasItem:'lockpick_steel'},{requiresGuildLevel:{guild:'thief',minLevel:5}}],actions:[{rollChance:{chance:60,onSuccess:'openDoor',onFail:'breakItem_lockpick_steel'}}]},
     {text:'Pick Lock — Master (Thief 7+, 80% success)',conditions:[{hasItem:'lockpick_master_pick'},{requiresGuildLevel:{guild:'thief',minLevel:7}}],actions:[{rollChance:{chance:80,onSuccess:'openDoor',onFail:'breakItem_lockpick_master_pick'}}]},
     {text:'Bash Door (Fighter 1+)',conditions:[{requiresGuildLevel:{guild:'fighter',minLevel:1}}],actions:[{rollChance:{chance:30,onSuccess:'bashDoor',onFail:'damagePlayer_5'}}]},
     {text:'Bash Door (Fighter 5+, 60%)',conditions:[{requiresGuildLevel:{guild:'fighter',minLevel:5}}],actions:[{rollChance:{chance:60,onSuccess:'bashDoor',onFail:'damagePlayer_5'}}]},
     {text:'Inspect Door (Thief)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:1}}],actions:[{setCondition:'door_inspected'},{say:'You study the lock carefully. You could craft a key for this door.'}]},
     {text:'Pass Through Scroll (Mage/Cleric/Druid 3+)',conditions:[{hasItem:'scroll_door_pass_mage'},{requiresGuildLevel:{guild:'mage',minLevel:3}}],actions:[{consumeItem:'scroll_door_pass_mage'},{openDoor:true}]},
     {text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_key_crafting_table',
    'A thief\'s workbench for crafting door keys from a lock inspection.',
    [{text:'Craft Door Key (Thief 3+, door inspected, 50%)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:3}},{hasCondition:'door_inspected'}],actions:[{rollChance:{chance:50,onSuccess:'giveItem_item_door_key',onFail:'say_Attempt failed.'}}]},
     {text:'Craft Door Key (Thief 6+, 80%)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:6}},{hasCondition:'door_inspected'}],actions:[{rollChance:{chance:80,onSuccess:'giveItem_item_door_key',onFail:'say_Attempt failed.'}}]},
     {text:'Leave'}]
  ));

  // Bank
  conversations.push(makeConversation('conv_bank_manager',
    'Welcome to the Royal Bank. I can arrange a 100-item safety deposit box.',
    [{text:'Open Deposit Box',conditions:[{hasItem:'item_deposit_box_key'}],actions:[{openStorage:{id:'deposit_box',size:100}}]},
     {text:'Get Deposit Box Key (200g)',actions:[{payGold:200},{giveItem:'item_deposit_box_key'}]},
     {text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_bank_teller',
    'Savings accounts available! Deposit any amount, withdraw anytime.',
    [{text:'Deposit Gold',actions:[{openBankDeposit:true}]},
     {text:'Withdraw Gold',actions:[{openBankWithdraw:true}]},
     {text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_bank_guard','Move along, citizen.',
    [{text:'Fine.'}]));
  conversations.push(makeConversation('conv_bank_patron','I love the Royal Bank service!',
    [{text:'Indeed.'}]));
  conversations.push(makeConversation('conv_bank_robbery',
    '[THIEF 12] You could take the guard hostage and demand the vault.',
    [{text:'Stage robbery (Thief 12+, 80% success)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:12}}],
      actions:[{rollChance:{chance:80,onSuccess:'robBank_give5000g',onFail:'caughtRobbing_jail'}}]},
     {text:'Leave'}]
  ));

  // Jail
  conversations.push(makeConversation('conv_jail_guard','Stay in your cell!',
    [{text:'Yes sir.'}]));
  conversations.push(makeConversation('conv_jail_captain','You\'re here until you pay your bail.',
    [{text:'OK.'}]));
  conversations.push(makeConversation('conv_jail_lawyer',
    'I can arrange your bail. It\'ll cost 100 gold — freedom isn\'t free.',
    [{text:'Pay bail (100g)',actions:[{payBail:{goldCost:100}},{mapChange:{mapID:'town_square',mapX:5,mapY:5}}]},
     {text:'I\'ll wait it out.'}]
  ));

  // Guild gatekeeper + guildmaster
  GUILDS.forEach((guild,gi)=>{
    range(12).forEach(qi=>{
      quests.push(makeQuest(`quest_guild_${guild}_${qi}`,
        `${cap(guild)} Guild Quest ${qi+1}`,
        `A task from the ${cap(guild)} Guildmaster to advance your rank.`,
        [{desc:`Complete the ${cap(guild)} Guildmaster's task #${qi+1}.`,exp:(qi+1)*50+gi*100}]
      ));
    });
    conversations.push(makeConversation(`conv_guildmaster_${guild}`,
      `Welcome to the ${cap(guild)} Guild. I have ${GUILDS.length>1?'quests':'tasks'} to advance your rank.`,
      [{text:'Accept Next Quest',actions:[{startNextGuildQuest:guild}]},
       {text:'Leave Guild (keep progress)',actions:[{setCondition:`guild_inactive_${guild}`},{clearCondition:`guild_active_${guild}`}]},
       {text:'Leave'}]
    ));
    conversations.push(makeConversation(`conv_guild_seller_${guild}`,
      `Guild supplies for active ${cap(guild)} members.`,
      [{text:'Browse wares',conditions:[{hasCondition:`guild_active_${guild}`}],actions:[{openShop:`shop_guild_${guild}`}]},
       {text:'Not a member, sorry.',conditions:[{notHasCondition:`guild_active_${guild}`}]},
       {text:'Leave'}]
    ));
  });

  // Crafting object conversations
  [['loom','A loom for weaving cloth. Requires Weaving skill.'],
   ['stove','A stove for cooking. Requires Cooking skill.'],
   ['garden','A garden plot. Equip Hoe and plant seeds. Plants mature in 7 days.'],
   ['smithing_forge','A forge for weapons and shields. Requires Smithing skill.'],
   ['crafting_bench','A workbench for armor. Requires Armorcraft skill.'],
   ['miners_forge','A miner\'s forge for ore-crafted weapons and rings.'],
   ['game_console','A game console. Play to enter the Astral Spire!'],
   ['computer','A magical computer. Connect to the LPC Church virtual world!'],
   ['fighters_forge','The Fighter\'s Forge. Craft superior weapons and shields. Fighter Guild Level 3+ required.'],
   ['writing_desk','A writing desk for crafting scrolls.'],
   ['cauldron','A cauldron for brewing potions. Mage/Cleric/Druid Guild Level 6+ required.'],
   ['crafting_table','A crafting table for wands and staffs. Mage/Cleric/Druid guild required.'],
   ['crafting_sign','Prices are posted for all crafting materials. Ask the NPC scholars for skill training.'],
  ].forEach(([id,msg])=>{
    conversations.push(makeConversation(`conv_${id}`,msg,
      [{text:'Use',actions:[]},{text:'Leave'}]));
  });
  ['mage','cleric','druid'].forEach(g=>{
    conversations.push(makeConversation(`conv_desk_${g}`,
      `The ${cap(g)} Special Desk. Craft door passes, recall scrolls, invisibility scrolls. Requires ${cap(g)} Guild Level 3.`,
      [{text:'Door Pass Scroll (30g)',conditions:[{requiresGuildLevel:{guild:g,minLevel:3}}],actions:[{payGold:30},{giveItem:`scroll_door_pass_${g}`}]},
       {text:'Recall Scroll (20g)',conditions:[{requiresGuildLevel:{guild:g,minLevel:3}}],actions:[{payGold:20},{giveItem:`scroll_recall_${g}`}]},
       {text:'Invisibility Scroll (50g)',conditions:[{requiresGuildLevel:{guild:g,minLevel:3}}],actions:[{payGold:50},{giveItem:`scroll_invisibility_${g}`}]},
       {text:'Leave'}]
    ));
  });

  // Home purchase
  conversations.push(makeConversation('conv_realtor',
    'Welcome! I sell homes of every size. Larger homes unlock more crafting stations.',
    [{text:'Small Home (500g) — Console, Computer, Stove',actions:[{payGold:500},{giveItem:'item_deed_small_home'}]},
     {text:'Mid Home (1000g) — + Garden, Bench',actions:[{payGold:1000},{giveItem:'item_deed_mid_home'}]},
     {text:'Large Home (2000g) — + Both Forges',actions:[{payGold:2000},{giveItem:'item_deed_large_home'}]},
     {text:'Luxury Home (4000g) — + Butler (5% discount)',actions:[{payGold:4000},{giveItem:'item_deed_luxury_home'},{setCondition:'owns_luxury_home'}]},
     {text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_npc_butler',
    'Welcome home, Master. As your butler I have arranged a 5% discount at all crafting shops.',
    [{text:'Thank you!',conditions:[{hasCondition:'owns_luxury_home'}],actions:[{setCondition:'butler_discount_active'}]},
     {text:'Leave'}]
  ));

  // Home loot
  range(200).forEach(i=>{
    const containers=['chest','drawer','wardrobe','cabinet','trunk','box','cupboard','shelf','safe','crate'];
    conversations.push(makeConversation(`conv_home_loot_${i}`,
      `A ${containers[i%containers.length]} that might contain valuables.`,
      [{text:'Steal (Thief 3+, 60%)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:3}}],
        actions:[{rollChance:{chance:60,onSuccess:`giveItem_stolen_item_${i}`,onFail:'caughtBurgling_jail'}}]},
       {text:'Steal + Hide (Thief 9+, 85%)',conditions:[{requiresGuildLevel:{guild:'thief',minLevel:9}}],
        actions:[{rollChance:{chance:85,onSuccess:`giveItem_stolen_item_${i}`,onFail:'caughtBurgling_jail'}}]},
       {text:'Leave'}]
    ));
  });

  return {conversations,quests};
}

// ─────────────────────────────────────────────────────────────────────────────
// FACTION CONTENT
// ─────────────────────────────────────────────────────────────────────────────
function buildFactionContent() {
  const items=[],monsters=[],conversations=[],quests=[],actorconditions=[];
  RACES.forEach((race,ri)=>{
    const att=RACE_ATTITUDE[race];
    range(25).forEach(i=>{
      monsters.push(makeMonster({id:`npc_${race}_${i}`,
        name:`${cap(race.replace('_',' '))} ${i+1}`,
        hp:15+ri*3+i,atk:att==='hostile'?75:30,dmgMin:1+ri,dmgMax:4+ri*2,
        faction:race,iconRow:80+ri,iconCol:1+i%8}));
    });
    monsters.push(makeMonster({id:`npc_${race}_leader`,
      name:`${cap(race.replace('_',' '))} Leader`,
      hp:100+ri*20,atk:85,dmgMin:5+ri,dmgMax:15+ri*3,
      faction:race,iconRow:80+ri,iconCol:9,conversationID:`conv_leader_${race}`}));
    range(12).forEach(qi=>{
      quests.push(makeQuest(`quest_faction_${race}_${qi}`,
        `${cap(race.replace('_',' '))} Quest ${qi+1}`,
        `A task from the ${cap(race.replace('_',' '))} Leader.`,
        [{desc:`Complete the task for the ${cap(race.replace('_',' '))} faction.`,
          exp:(qi+1)*75,condition:{requiresFactionLevel:{race,minLevel:qi}}}]
      ));
    });
    conversations.push(makeConversation(`conv_leader_${race}`,
      `${att==='hostile'?'You are not welcome here, wood elf!':'Greetings, traveler. What brings you to our people?'}`,
      [{text:'Accept Quest',actions:[
          {startNextFactionQuest:race},
          {modifyFaction:{race,amount:1}},
          {modifyFaction:{race:RACE_RIVALS[race],amount:-1}}]},
       {text:'Leave'}]
    ));
    // Disguise
    items.push(makeItem({id:`disguise_${race}`,name:`${cap(race.replace('_',' '))} Disguise`,
      iconRow:96+ri,iconCol:1,baseMarketCost:200+ri*20,
      useEffect:{applyActorCondition:{conditionID:`ac_disguise_${race}`,duration:60}},
      desc:`Has a chance to negate ${cap(race.replace('_',' '))} faction attacks.`}));
    actorconditions.push(makeActorCondition({id:`ac_disguise_${race}`,
      name:`${cap(race.replace('_',' '))} Disguise Active`,isPositive:true}));
    range(5).forEach(level=>{
      actorconditions.push(makeActorCondition({id:`faction_${race}_level_${level}`,
        name:`${cap(race.replace('_',' '))} Reputation ${level}`,isPositive:level>=2}));
    });
  });
  conversations.push(makeConversation('conv_disguise_seller',
    'Disguises for every race! A chance to fool even the most hostile faction.',
    [{text:'Browse Disguises',actions:[{openShop:'shop_disguises'}]},{text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_faction_hall_sign',
    'Faction Hall — buy disguises, check faction standings, and hire guild thieves for stealth missions.',
    [{text:'Understood.'}]
  ));
  return {items,monsters,conversations,quests,actorconditions};
}

// ─────────────────────────────────────────────────────────────────────────────
// QUEST CONTENT (witch, drow, lloth, dragons, ring, castle, towers, haunted)
// ─────────────────────────────────────────────────────────────────────────────
function buildQuestContent() {
  const items=[],monsters=[],droplists=[],conversations=[],quests=[],actorconditions=[];

  // ── Swamp Witch ──────────────────────────────────────────────────────────
  const WITCH_INGREDIENTS=['Swamp Lily','Bog Mushroom','Dark Moss','Fetid Water','Marsh Reed'];
  WITCH_INGREDIENTS.forEach((name,i)=>
    items.push(makeItem({id:`witch_ing_${i}`,name,iconRow:110,iconCol:1+i,
      isQuestItem:true,isSellable:false,desc:'A witch ingredient.'})));
  const SWAMP_MONSTERS=['Bog Troll','Swamp Hag','Marsh Witch','Mire Serpent'];
  SWAMP_MONSTERS.forEach((name,i)=>{
    const dl=makeDroplist(`dl_witch_mob_${i}`,[{id:`witch_ing_${i}`,chance:100,qty:[1]}]);
    droplists.push(dl);
    monsters.push(makeMonster({id:`monster_witch_${i}`,name,hp:30+i*10,atk:65,
      dmgMin:3+i,dmgMax:8+i*2,droplistID:dl.id,iconRow:111,iconCol:1+i}));
  });
  conversations.push(makeConversation('conv_witch',
    'I am the Swamp Witch. Your sister Sunny came here seeking ancient magic. Bring me 5 ingredients for my seeing potion.',
    [{text:'Offer all 5 ingredients',conditions:[{hasAllItems:range(5).map(i=>`witch_ing_${i}`)}],
      actions:[{consumeItems:range(5).map(i=>`witch_ing_${i}`)},
               {setQuestPart:{questID:'quest_witch',part:1}},
               {say:'Sunny... she traveled east into the Drow Caves. Dark magic follows her.'}]},
     {text:'I still need ingredients.'},
     {text:'Leave'}]
  ));
  conversations.push(makeConversation('conv_witch_search',
    'A marshy hollow with strange plants. Search carefully?',
    [{text:'Search (90% chance)',actions:[{rollChance:{chance:90,onSuccess:'giveItem_witch_ing_4',onFail:'nothing'}}]},
     {text:'Leave'}]
  ));
  quests.push(makeQuest('quest_witch','The Swamp Witch',
    'The Swamp Witch may know something about Sunny.',
    [{desc:'Gather 4 monster drops and 1 foraged marsh item.',exp:200},
     {desc:'Return to the Swamp Witch with all 5 ingredients.',exp:300}]
  ));

  // ── Drow Cave ────────────────────────────────────────────────────────────
  const DROW_INGREDIENTS=range(12).map(i=>{
    const it=makeItem({id:`drow_ing_${i}`,name:`Dark Essence ${i+1}`,iconRow:112,iconCol:1+i,
      isQuestItem:true,isSellable:false});
    items.push(it);
    return it.id;
  });
  range(6).forEach(i=>{
    const dl=makeDroplist(`dl_drow_cave_${i}`,[{id:`drow_ing_${i}`,chance:100,qty:[1]}]);
    droplists.push(dl);
    monsters.push(makeMonster({id:`monster_drow_cave_${i}`,
      name:['Cave Bat','Giant Spider','Rock Crab','Cave Troll','Blind Crawler','Stone Wyrm'][i],
      hp:40+i*8,atk:70,dmgMin:4+i,dmgMax:10+i*2,droplistID:dl.id,iconRow:113,iconCol:1+i}));
  });
  ['drow_guard','drow_leader','drow_witch'].forEach((id,i)=>{
    monsters.push(makeMonster({id:`npc_${id}`,name:cap(id.replace('_',' ')),
      hp:60+i*20,atk:75+i*5,dmgMin:5+i*2,dmgMax:15+i*3,faction:'drow',
      iconRow:114,iconCol:1+i,conversationID:`conv_${id}`}));
    conversations.push(makeConversation(`conv_${id}`,
      {drow_guard:'Prove yourself, surface dweller. Complete my task first.',
       drow_leader:'Wood elf, you have courage. Prove your worth to the Drow.',
       drow_witch:'My spell requires 12 Dark Essences. Bring them all.'}[id],
      [{text:'Accept Quest',actions:[{startQuest:`quest_${id}`}]},{text:'Leave'}]
    ));
    quests.push(makeQuest(`quest_${id}`,`${cap(id.replace('_',' '))} Task`,
      `Fulfill the ${id.replace('_',' ')}'s request.`,
      [{desc:`Complete the ${id.replace('_',' ')}'s task.`,exp:300+i*100}]
    ));
  });
  conversations.push(makeConversation('conv_drow_witch_spell',
    'You have brought all 12 essences! Now the spell is complete...',
    [{text:'Watch',conditions:[{hasAllItems:range(12).map(i=>`drow_ing_${i}`)}],
      actions:[{consumeItems:range(12).map(i=>`drow_ing_${i}`)},
               {mapChange:{mapID:'lloth_realm',mapX:5,mapY:5}}]}]
  ));

  // ── Lloth ────────────────────────────────────────────────────────────────
  items.push(makeItem({id:'item_lloth_ring',name:"Lloth's Seal Ring",iconRow:115,iconCol:1,
    isQuestItem:true,isSellable:false,useEffect:{mapChange:{mapID:'lloth_realm',mapX:5,mapY:5}},
    desc:"A ring from Lloth. It will teleport you back to her when your quest is complete."}));
  const DEMIGODS=['Aspect of Lloth','Yochlol','Spider Demon','Chitine Warrior','Drider Champion','Drow Veteran','Chosen of Lloth'];
  DEMIGODS.forEach((name,i)=>monsters.push(makeMonster({id:`monster_lloth_guard_${i}`,name,
    hp:100+i*30,atk:80+i*3,dmgMin:8+i*2,dmgMax:20+i*4,faction:'drow_gods',iconRow:116,iconCol:1+i})));
  monsters.push(makeMonster({id:'npc_lloth',name:'Lloth, Queen of Spiders',hp:500,atk:90,
    dmgMin:15,dmgMax:40,faction:'drow_gods',iconRow:116,iconCol:8,conversationID:'conv_lloth'}));
  conversations.push(makeConversation('conv_lloth',
    'Wood elf. Your courage reaches even my web. Travel to the Volcano and settle the dragon dispute. My ring will return you when done.',
    [{text:'Accept (take Lloth\'s ring)',actions:[{giveItem:'item_lloth_ring'},{setQuestPart:{questID:'quest_lloth',part:0}}]},
     {text:'Leave'}]
  ));
  quests.push(makeQuest('quest_lloth',"Lloth's Dragon Dispute",
    'Lloth has sent you to the Volcano to settle a dispute among dragons.',
    [{desc:'Travel to the Volcano and speak with the dragons.',exp:500},
     {desc:'Return to Lloth via the ring when resolved.',exp:1000}]
  ));

  // ── Dragons ──────────────────────────────────────────────────────────────
  items.push(makeItem({id:'item_grand_dragon_reward',name:'Crown of Dragon Lords',iconRow:117,iconCol:1,
    itemType:'armor',equipmentSlot:'head',damageResistance:20,attackChance:15,
    baseMarketCost:9999,desc:'Reward from the ancient dragons for resolving their disputes.'}));
  DRAGON_TYPES.forEach((type,ti)=>{
    DRAGON_AGES.forEach((age,ai)=>{
      const hpMap={baby:50,youngling:100,teen:200,adult:400};
      const dmgMap={baby:10,youngling:20,teen:35,adult:60};
      monsters.push(makeMonster({id:`dragon_${cid(type)}_${age}`,name:`${type} Dragon (${cap(age)})`,
        hp:hpMap[age],atk:70+ai*5,dmgMin:5+ai*5,dmgMax:dmgMap[age],
        faction:'dragons',iconRow:118+ti,iconCol:1+ai}));
      if (age==='adult') {
        items.push(makeItem({id:`item_dragon_scale_${cid(type)}`,name:`${type} Dragon Scale`,
          iconRow:128+ti,iconCol:1,itemType:'armor',equipmentSlot:'body',
          damageResistance:10+ti*2,baseMarketCost:500+ti*50}));
        quests.push(makeQuest(`quest_dragon_${cid(type)}_adult`,`${type} Dragon's Request`,
          `Help the adult ${type} Dragon.`,
          [{desc:`Complete the adult ${type} Dragon's quest.`,exp:800+ti*100}]
        ));
        conversations.push(makeConversation(`conv_dragon_${cid(type)}_adult`,
          `The ${type} Dragon eyes you carefully. Prove yourself worthy of my aid.`,
          [{text:'Accept Quest',actions:[{startQuest:`quest_dragon_${cid(type)}_adult`}]},{text:'Leave'}]
        ));
      }
    });
  });
  // Ancient dragons gated
  ['ancient_platinum','ancient_chromatic'].forEach((did,i)=>{
    const condition={requiresAllQuestsComplete:DRAGON_TYPES.map(t=>`quest_dragon_${cid(t)}_adult`)};
    monsters.push(makeMonster({id:`dragon_${did}`,name:cap(did.replace('_',' ')),
      hp:2000+i*500,atk:95,dmgMin:30,dmgMax:80,faction:'ancient_dragons',
      iconRow:138,iconCol:1+i,conversationID:`conv_dragon_${did}`}));
    quests.push(makeQuest(`quest_dragon_${did}`,`${cap(did.replace('_',' '))} Dragon's Quest`,
      `Available only after all 10 adult dragon quests are complete.`,
      [{desc:`Complete the ${cap(did.replace('_',' '))} Dragon's ultimate quest.`,
        exp:5000+i*2000,condition}]
    ));
    conversations.push(makeConversation(`conv_dragon_${did}`,
      `The ${cap(did.replace('_',' '))} Dragon regards you with ancient eyes. You have proven yourself among all dragonkind.`,
      [{text:'Accept Quest',conditions:[condition],actions:[{startQuest:`quest_dragon_${did}`}]},
       {text:'Return when you have completed all adult dragon quests.',conditions:[{notCondition:condition}]},
       {text:'Leave'}]
    ));
  });
  conversations.push(makeConversation('conv_dragon_dispute_complete',
    'The dragons bow their heads. The dispute is settled. Use Lloth\'s ring to return.',
    [{text:'Use ring',actions:[{useItem:'item_lloth_ring'}]},{text:'Stay a moment.'}]
  ));

  // ── Sunny's Ring ─────────────────────────────────────────────────────────
  items.push(makeItem({id:'item_sunny_ring',name:"Sunny's Ring",iconRow:140,iconCol:1,
    isQuestItem:true,isSellable:false,
    useEffect:{mapChange:{mapID:'ring_clearing',mapX:8,mapY:8}},
    desc:"Your sister Sunny's ring with a tent spell. Use it to travel to the ring clearing on demand."}));
  conversations.push(makeConversation('conv_sunny_ring_search',
    'You search the undergrowth carefully and find something glinting...',
    [{text:'Take the ring!',actions:[{giveItem:'item_sunny_ring'},{setQuestPart:{questID:'quest_find_ring',part:0}}]},
     {text:'Leave it for now.'}]
  ));
  quests.push(makeQuest('quest_find_ring',"Find Sunny's Ring",
    "Find your sister's ring in the clearing.",
    [{desc:"Search the ring clearing for Sunny's ring.",exp:500}]
  ));

  // ── Moon villages ────────────────────────────────────────────────────────
  items.push(makeItem({id:'item_sunny_reward',name:"Sunny's Blessing",iconRow:141,iconCol:1,
    isQuestItem:false,isSellable:false,
    useEffect:{permanentBuff:{maxHP:50,attackChance:10}},
    desc:'A powerful blessing from your sister Sunny upon her ascension to godhood.'}));
  quests.push(makeQuest('quest_sunny_end','Finding Sunny',
    'The culmination of your quest to find your sister Sunny.',
    [{desc:'Complete all Drow village quests on the moons.',exp:3000},
     {desc:'Witness Sunny\'s ascension.',exp:5000}]
  ));
  MOON_COLORS.forEach((color,ci)=>{
    range(12).forEach(j=>monsters.push(makeMonster({id:`npc_moon_drow_${cid(color)}_${j}`,
      name:`${color} Moon Drow ${j+1}`,hp:80+ci*10,atk:75,dmgMin:5+ci,dmgMax:15+ci,
      faction:'drow',iconRow:142,iconCol:1+ci})));
    monsters.push(makeMonster({id:`npc_moon_elder_${cid(color)}`,
      name:`${color} Moon Elder`,hp:150+ci*20,atk:80,dmgMin:8+ci,dmgMax:20+ci,
      faction:'drow',iconRow:143,iconCol:1+ci,conversationID:`conv_moon_elder_${cid(color)}`}));
    conversations.push(makeConversation(`conv_moon_elder_${cid(color)}`,
      `Greetings from the ${color} Moon. We have a task for you, surface walker.`,
      [{text:'Accept Quest',actions:[{startQuest:`quest_moon_${cid(color)}`}]},{text:'Leave'}]
    ));
    quests.push(makeQuest(`quest_moon_${cid(color)}`,`${color} Moon Quest`,
      `Help the ${color} Moon Drow village.`,
      [{desc:`Complete the ${color} Moon Elder's task.`,exp:600+ci*100}]
    ));
    items.push(makeItem({id:`item_rocket_${cid(color)}`,name:`${color} Moon Rocket`,
      iconRow:144,iconCol:1+ci,isSellable:false,baseMarketCost:0,
      useEffect:{mapChange:{mapID:`moon_${cid(color)}`,mapX:5,mapY:5}},
      desc:`Rocket ship to ${color} Moon.`}));
  });

  // Sunny, Ozzy, Nymph
  ['npc_sunny','npc_ozzy','npc_nymph'].forEach((id,i)=>{
    monsters.push(makeMonster({id,name:{npc_sunny:'Sunny (Drow Elf)',npc_ozzy:'Ozzy (Your Father)',npc_nymph:'Nymph (Your Mother)'}[id],
      hp:1,atk:0,dmgMin:0,dmgMax:0,faction:'family',iconRow:145,iconCol:1+i,conversationID:`conv_${id}`}));
  });
  conversations.push(makeConversation('conv_npc_sunny',
    'Sister! I have become a demi-god and must leave the mortal world. But know — I will always watch over you.',
    [{text:'...',actions:[{giveItem:'item_sunny_reward'},{setQuestPart:{questID:'quest_sunny_end',part:1}}]}]
  ));
  conversations.push(makeConversation('conv_npc_ozzy',
    'Welcome home! Have you found your sister Sunny yet? I worry so.',
    [{text:'Sunny is safe, Father.',conditions:[{requiresQuestPart:{questID:'quest_sunny_end',part:1}}],actions:[]},
     {text:'Still searching.'}]
  ));
  conversations.push(makeConversation('conv_npc_nymph','Stay safe, my child. Come home soon.',[{text:'I will, Mother.'}]));

  // ── Crystal Towers ───────────────────────────────────────────────────────
  const CRYSTAL_COLORS=['Red','Orange','Yellow','Green','Cyan','Blue','Indigo','Violet','Silver','Gold','Black','White'];
  const TOWER_TYPES=['mage','mage','mage','mage','cleric','cleric','cleric','cleric','druid','druid','druid','druid'];
  CRYSTAL_COLORS.forEach((color,ti)=>{
    const tType=TOWER_TYPES[ti];
    range(5).forEach(level=>{
      range(5).forEach(j=>monsters.push(makeMonster({
        id:`monster_tower_${cid(color)}_lvl${level}_${j}`,
        name:`${color} Tower ${cap(tType)} ${['Apprentice','Initiate','Adept','Master','Grandmaster'][level]}`,
        hp:30+level*20+ti*5,atk:60+level*5,dmgMin:2+level*2,dmgMax:6+level*3+ti,
        faction:'tower_mages',iconRow:150+ti,iconCol:1+level})));
    });
    items.push(makeItem({id:`crystal_${cid(color)}`,name:`${color} Crystal`,iconRow:162,iconCol:1+ti,
      isQuestItem:true,baseMarketCost:0}));
    quests.push(makeQuest(`quest_tower_${cid(color)}`,`${color} Crystal Tower`,
      `Conquer the ${color} Crystal Tower and claim the crystal.`,
      range(5).map(l=>({desc:`Clear level ${l+1} of the ${color} Tower.`,exp:200+l*100+ti*50}))
    ));
  });
  items.push(makeItem({id:'item_grand_crystal_staff',name:'Grand Crystal Staff',iconRow:164,iconCol:1,
    itemType:'weapon',equipmentSlot:'weapon',damagePotential:dmg(20,60),damageResistance:15,baseMarketCost:9999}));
  monsters.push(makeMonster({id:'npc_crystal_grandmaster',name:'Crystal Grandmaster',hp:100,
    atk:40,dmgMin:2,dmgMax:5,faction:'friendly',iconRow:164,iconCol:2,conversationID:'conv_crystal_grandmaster'}));
  conversations.push(makeConversation('conv_crystal_grandmaster',
    'You have gathered all 12 crystals! You are the master of the arcane arts!',
    [{text:'Claim reward!',conditions:[{hasAllItems:CRYSTAL_COLORS.map(c=>`crystal_${cid(c)}`)}],
      actions:[{consumeItems:CRYSTAL_COLORS.map(c=>`crystal_${cid(c)}`)},{giveItem:'item_grand_crystal_staff'}]},
     {text:'I\'m still missing crystals.'}]
  ));
  quests.push(makeQuest('quest_all_crystals','Master of Crystals',
    'Gather all 12 colored crystals from the crystal towers.',
    [{desc:'Present all 12 crystals to the Crystal Grandmaster.',exp:10000}]
  ));

  // ── Haunted Places ───────────────────────────────────────────────────────
  const HAUNTED=['haunted_house','haunted_mansion','haunted_prison','graveyard','crypt','mausoleum'];
  const GHOST_TYPES=['Ghost','Ghoul','Spirit','Specter','Wraith','Phantom','Shade','Banshee','Poltergeist','Revenant','Shadow','Will-o-Wisp','Death Knight','Lich Thrall','Mummy','Zombie','Skeleton','Vampire Spawn','Wight','Dullahan','Moaning Spirit','Screaming Skull','Grave Hag','Haunting Presence','Soul Wisp'];
  const BOSS_NAMES=['House Specter','Mansion Wraith','Prison Warden Ghost','Cemetery Overlord','Crypt Lord','Mausoleum Guardian'];
  HAUNTED.forEach((place,pi)=>{
    GHOST_TYPES.forEach((ghost,gi)=>monsters.push(makeMonster({
      id:`monster_${cid(place)}_${gi}`,name:ghost,
      hp:20+pi*10+gi*2,atk:65+pi*3,dmgMin:2+pi,dmgMax:8+pi*2,
      faction:'undead',iconRow:165+pi,iconCol:1+gi%8})));
    const rewardId=`item_haunt_reward_${pi}`;
    const dl=makeDroplist(`dl_haunt_boss_${pi}`,[{id:rewardId,chance:100,qty:[1]}]);
    droplists.push(dl);
    items.push(makeItem({id:rewardId,name:`${cap(place.replace('_',' '))} Trophy`,
      iconRow:171,iconCol:1+pi,baseMarketCost:400+pi*100,desc:`Proof of defeating the ${BOSS_NAMES[pi]}.`}));
    monsters.push(makeMonster({id:`monster_boss_${cid(place)}`,name:BOSS_NAMES[pi],
      hp:300+pi*100,atk:80+pi*5,dmgMin:15+pi*3,dmgMax:35+pi*5,
      droplistID:dl.id,faction:'undead_boss',iconRow:172,iconCol:1+pi}));
    quests.push(makeQuest(`quest_${cid(place)}`,`Clear the ${cap(place.replace('_',' '))}`,
      `Rid the ${place.replace('_',' ')} of all its undead inhabitants.`,
      [{desc:`Defeat all 25 undead in the ${place.replace('_',' ')}.`,exp:500+pi*100},
       {desc:`Defeat the ${BOSS_NAMES[pi]}.`,exp:800+pi*150}]
    ));
  });

  // ── Castle NPCs ───────────────────────────────────────────────────────────
  const CASTLE_NPCS=[
    {id:'npc_guard_captain',name:'Guard Captain',conv:'The castle is secure under my watch. I have a task for you.',quest:true},
    {id:'npc_head_cook',name:'Head Cook',conv:'The kitchen is always busy! I need some special ingredients.',quest:true},
    {id:'npc_librarian',name:'Castle Librarian',conv:'Ah, a reader! I need a rare tome retrieved.',quest:true},
    {id:'npc_gardener',name:'Castle Gardener',conv:'The gardens need tending. Could you fetch some exotic seeds?',quest:true},
    {id:'npc_gate_guard',name:'Gate Guard',conv:'I\'ve spotted something suspicious outside. Investigate?',quest:true},
    {id:'npc_castle_guest_1',name:'Castle Guest',conv:'What a lovely castle!',quest:true},
    {id:'npc_castle_guest_2',name:'Castle Guest',conv:'I heard rumors of adventure nearby.',quest:true},
    {id:'npc_servant_1',name:'Servant',conv:'How may I serve you, milady?',quest:true},
    {id:'npc_servant_2',name:'Servant',conv:'Right away, milady!',quest:true},
    {id:'npc_servant_3',name:'Servant',conv:'At your service!',quest:true},
    {id:'npc_prison_warden',name:'Prison Warden',conv:'Order is maintained in my prison.',quest:true},
  ];
  CASTLE_NPCS.forEach((npc,i)=>{
    monsters.push(makeMonster({id:npc.id,name:npc.name,hp:80+i*10,atk:60,
      dmgMin:5,dmgMax:12,faction:'castle',iconRow:173,iconCol:1+i,conversationID:`conv_${npc.id}`}));
    conversations.push(makeConversation(`conv_${npc.id}`,npc.conv,
      npc.quest?[{text:'Accept Quest',actions:[{startQuest:`quest_${npc.id}`}]},{text:'Leave'}]:[{text:'Hello.'}]));
    if (npc.quest) quests.push(makeQuest(`quest_${npc.id}`,`${npc.name}'s Task`,
      `A task from ${npc.name}.`,[{desc:`Complete ${npc.name}'s task.`,exp:400+i*50}]));
  });

  // Castle shop NPCs
  range(12).forEach(i=>{
    items.push(makeItem({id:`castle_weapon_${i}`,name:`Royal ${['Sword','Axe','Mace','Spear','Dagger','Hammer','Glaive','Flail','Lance','Bow','Crossbow','Warhammer'][i]}`,
      iconRow:180,iconCol:1+i,itemType:'weapon',equipmentSlot:'weapon',
      damagePotential:dmg(10+i,25+i*2),baseMarketCost:600+i*80}));
    items.push(makeItem({id:`castle_shield_${i}`,name:`Royal ${['Buckler','Kite','Tower','Heater','Round','Aspis','Pavise','Scutum','Targe','Spiked','Battle','War'][i]} Shield`,
      iconRow:181,iconCol:1+i,itemType:'armor',equipmentSlot:'offhand',
      damageResistance:8+i*2,baseMarketCost:500+i*60}));
    items.push(makeItem({id:`castle_armor_${i}`,name:`Royal ${['Chainmail','Platemail','Scale','Brigandine','Lamellar','Hauberk','Cuirass','Breastplate','Lorica','Gambeson','Jack','Haubergeon'][i]}`,
      iconRow:182,iconCol:1+i,itemType:'armor',equipmentSlot:'body',
      damageResistance:10+i*3,baseMarketCost:700+i*100}));
  });

  // Ailments + cure potions + ailment monsters
  const AILMENTS=['Poisoned','Diseased','Cursed','Paralyzed','Blinded','Confused','Weakened','Stunned',
    'Burned','Frozen','Dazed','Slowed','Bleeding','Petrified','Charmed','Feared','Silenced',
    'Muted','Hexed','Withered','Drained','Corrupted','Maddened','Doomed'];
  AILMENTS.forEach((ailment,i)=>{
    const acId=`ac_${cid(ailment)}`;
    actorconditions.push(makeActorCondition({id:acId,name:ailment,isPositive:false,
      stats:{attackChance:ailment==='Weakened'?-20:0,moveCost:ailment==='Slowed'?2000:0}}));
    items.push(makeItem({id:`potion_cure_${cid(ailment)}`,name:`Cure ${ailment} Potion`,
      iconRow:183+Math.floor(i/8),iconCol:1+i%8,baseMarketCost:50+i*10,
      useEffect:{removeActorCondition:acId}}));
    range(6).forEach(j=>{
      const mid=`monster_ailment_${cid(ailment)}_${j}`;
      const dId=`dl_ailment_${cid(ailment)}_${j}`;
      monsters.push(makeMonster({id:mid,
        name:`${ailment} ${['Rat','Spider','Snake','Beetle','Bat','Worm'][j]}`,
        hp:20+i+j*3,atk:65,dmgMin:2+i,dmgMax:6+i,faction:'ailment_monsters',
        iconRow:186+i,iconCol:1+j,droplistID:dId}));
      droplists.push(makeDroplist(dId,[{id:`potion_cure_${cid(ailment)}`,chance:20,qty:[1]}]));
    });
  });

  conversations.push(makeConversation('conv_castle_weaponer','Finest castle-branded weapons for sale!',
    [{text:'Browse',actions:[{openShop:'shop_castle_weapons'}]},{text:'Leave'}]));
  conversations.push(makeConversation('conv_castle_armorer','Castle-quality armor!',
    [{text:'Browse',actions:[{openShop:'shop_castle_armor'}]},{text:'Leave'}]));
  conversations.push(makeConversation('conv_castle_alchemist','Healing and ailment cure potions!',
    [{text:'Browse',actions:[{openShop:'shop_castle_alchemy'}]},{text:'Leave'}]));

  // Rumor board
  conversations.push(makeConversation('conv_rumor_board',
    'The rumor board is covered in notes. One reads: "Strange lights near the Swamp Witch\'s hut. Missing persons..."',
    [{text:'Investigate (start main quest)',actions:[{startQuest:'quest_main_intro'}]},{text:'Not interested.'}]
  ));
  quests.push(makeQuest('quest_main_intro','Rumors of the Realm',
    'A notice on the rumor board has caught your eye.',
    [{desc:'Travel to the Swamp Witch\'s hut and investigate.',exp:50}]
  ));

  // Bulletin board
  conversations.push(makeConversation('conv_overworld_bulletin',
    'QUESTS AVAILABLE: Crystal Towers (12), Haunted Places (6), Swamp Witch, Drow Cave. Ask locals for directions.',
    [{text:'Crystal Towers Quest',actions:[{startQuest:'quest_tower_red'}]},
     {text:'Haunted House Quest',actions:[{startQuest:'quest_haunted_house'}]},
     {text:'Leave'}]
  ));

  // Ring guard
  conversations.push(makeConversation('conv_ring_guard',
    'HALT! None may pass without Sunny\'s Ring!',
    [{text:'Show ring',conditions:[{hasItem:'item_sunny_ring'}],actions:[{openPassage:'ring_tent_exit'}]},
     {text:'Leave'}]
  ));
  monsters.push(makeMonster({id:'npc_ring_guard',name:'Ring Guard',hp:200,atk:85,
    dmgMin:10,dmgMax:30,faction:'drow_guard',iconRow:190,iconCol:1,conversationID:'conv_ring_guard'}));

  // Misc directions
  conversations.push(makeConversation('conv_sign',
    'A sign post with directions.',
    [{text:'Read',actions:[{showProperty:'signText'}]},{text:'Leave'}]
  ));

  // Mining NPCs
  conversations.push(makeConversation('conv_npc_old_miner',
    'I\'ve been mining these caves for forty years, son. Found a fortune, lost a fortune. But the rock always gives, if you respect it.',
    [{text:'Accept quest',actions:[{startQuest:'quest_old_miner'}]},{text:'Interesting.'}]
  ));
  quests.push(makeQuest('quest_old_miner','The Old Miner\'s Lost Vein',
    'The old miner has lost track of a rich ore vein.',
    [{desc:'Bring the old miner 5 Iron Ore.',exp:75},{desc:'Return to the old miner.',exp:100}]
  ));
  conversations.push(makeConversation('conv_npc_store_keeper',
    'Mining supplies and general goods! Pick axes, equipment, and more.',
    [{text:'Browse',actions:[{openShop:'shop_mining'}]},{text:'Leave'}]
  ));
  ['npc_seamstress','npc_butcher','npc_grocer','npc_farmer','npc_weaponer','npc_armorer',
   'npc_scholar','npc_ozzy','npc_nymph'].forEach(id=>{
    if (!conversations.find(c=>c.id===`conv_${id}`)) {
      conversations.push(makeConversation(`conv_${id}`,
        {npc_seamstress:'Loom materials and finished cloth items!',
         npc_butcher:'Fresh cuts for your cooking pot!',
         npc_grocer:'Finest produce from around the realm.',
         npc_farmer:'Seeds, hoes, and farm goods.',
         npc_weaponer:'Smithing materials and tools.',
         npc_armorer:'Quality armor crafting materials.',
         npc_scholar:'I teach crafting skills. Which would you like to learn?',
         npc_ozzy:'Welcome home! Have you found Sunny yet?',
         npc_nymph:'Stay safe, my child.'}[id]||'Hello!',
        [{text:'Thanks.'},{text:'Leave'}]
      ));
    }
  });

  return {items,monsters,droplists,conversations,quests,actorconditions};
}

// ─────────────────────────────────────────────────────────────────────────────
// POKEMON CONTENT
// ─────────────────────────────────────────────────────────────────────────────
const BEAST_POOLS = {
  meadow:['Florabit','Grashop','Meadowpuff','Dawnfang','Sunsprite','Pollenite','Breezeling','Cloverkin','Daisymite','Solarbud'],
  forest:['Timbergrub','Oakling','Ferntail','Mosswhisk','Barkboar','Leafdrift','Rootstalk','Branchling','Woodsong','Undergrowl'],
  mountain:['Peakscale','Stonecrest','Granitehorn','Cliffling','Boulderback','Ridgewing','Alpharoc','Cragmaw','Skybiter','Frosthorn'],
  ocean:['Tidecrest','Waveling','Deepfin','Saltmaw','Coralsnap','Abyssting','Currenthide','Riptideling','Galefish','Driftwhisker'],
  volcanic:['Emberclaw','Magmabit','Ashwing','Cindertail','Scorchscale','Pyrestone','Lavaback','Flamecrest','Smokemaw','Igniteling'],
  arctic:['Frostbite','Glacierling','Snowfang','Blizzardmaw','Icewing','Coldstone','Permafur','Tundraclaw','Shiverscale','Freezehorn'],
  swamp:['Murkjaw','Bogslide','Swampfang','Mirelung','Mosscrawl','Marshwhisk','Fetidling','Quagback','Siltsneek','Peatmaw'],
  sky:['Cloudrift','Galeborn','Stormwing','Tempestclaw','Squallbit','Cycloneback','Misthorn','Zephyrtail','Windmaw','Aetherflit'],
  shadow:['Duskfang','Voidling','Shadowclaw','Darkwhisk','Umbramaw','Noctscale','Eclipseback','Penumbring','Gloomhorn','Abyssalclaw'],
};

function buildPokemonContent() {
  const items=[],monsters=[],droplists=[],conversations=[],quests=[],actorconditions=[];

  // Spirit orbs
  range(4).forEach(i=>{
    items.push(makeItem({id:`item_spirit_orb_${i+1}`,name:`Spirit Orb ${['I','II','III','IV'][i]}`,
      iconRow:200,iconCol:1+i,baseMarketCost:50*(i+1),charges:1,
      desc:`Level ${i+1} Spirit Orb. Catch chance: ${[25,50,75,95][i]}%.`}));
  });

  // 270 beasts (10 base × 3 tiers × 9 regions)
  POKEMON_REGIONS.forEach((region,ri)=>{
    const baseNames=BEAST_POOLS[region]||[];
    baseNames.forEach((baseName,bi)=>{
      range(3).forEach(tier=>{
        const tierNames=[baseName,`${baseName}on`,`${baseName}us`];
        const beastId=`beast_${region}_${cid(baseName)}_t${tier+1}`;
        const equipId=`item_beast_equip_${beastId}`;

        // 3 spells per beast
        range(3).forEach(si=>{
          const acId=`ac_beast_spell_${beastId}_${si}`;
          actorconditions.push(makeActorCondition({id:acId,
            name:`${tierNames[tier]} Spell ${si+1}`,isPositive:tier>=1,
            stats:{attackChance:(si+1)*5*(tier+1),damagePotential:dmg((si+1)*(tier+1),(si+2)*(tier+1)*2)}}));
        });

        items.push(makeItem({id:equipId,name:`${tierNames[tier]}'s Essence`,
          iconRow:201+ri,iconCol:1+bi%8,baseMarketCost:100*(tier+1),
          desc:`Equip to channel the power of ${tierNames[tier]}.`}));

        const dl=makeDroplist(`dl_beast_${beastId}`,[{id:equipId,chance:100,qty:[1]}]);
        droplists.push(dl);

        const convId=`conv_catch_${beastId}`;
        const catchChances=[25,50,75,95];
        conversations.push(makeConversation(convId,
          `A wild ${tierNames[tier]} appears! It eyes you curiously.`,
          [
            ...range(4).map(oi=>({
              text:`Catch with Spirit Orb ${['I','II','III','IV'][oi]} (${catchChances[oi]}%)`,
              conditions:[{hasItem:`item_spirit_orb_${oi+1}`}],
              actions:[{rollChance:{chance:catchChances[oi],onSuccess:`catchBeast_${beastId}`,onFail:'nothing'}},
                       {consumeItem:`item_spirit_orb_${oi+1}`}]
            })),
            {text:'Battle!',actions:[{startCombat:`monster_${beastId}`}]},
            {text:'Leave'},
          ]
        ));

        monsters.push(makeMonster({id:`monster_${beastId}`,name:tierNames[tier],
          hp:20*(tier+1),atk:60+(tier+1)*10,dmgMin:(tier+1)*2,dmgMax:(tier+1)*6,
          droplistID:dl.id,iconRow:210+ri,iconCol:1+bi%8,conversationID:convId}));
      });
    });
  });

  // 30 breeding beasts
  range(30).forEach(i=>{
    const bId=`beast_bred_${i}`;
    items.push(makeItem({id:`item_bred_equip_${i}`,name:`Hybridling ${i+1} Essence`,
      iconRow:220,iconCol:1+i%8,baseMarketCost:300}));
    monsters.push(makeMonster({id:`monster_${bId}`,name:`Hybridling ${i+1}`,
      hp:60,atk:75,dmgMin:5,dmgMax:15,iconRow:221,iconCol:1+i%8}));
  });

  // Gym leaders + 12 trainers per region
  POKEMON_REGIONS.forEach((region,ri)=>{
    monsters.push(makeMonster({id:`monster_gym_leader_${region}`,name:`${cap(region)} Gym Leader`,
      hp:200+ri*30,atk:80+ri*3,dmgMin:10+ri*2,dmgMax:25+ri*3,
      iconRow:230,iconCol:1+ri,conversationID:`conv_gym_leader_${region}`}));
    conversations.push(makeConversation(`conv_gym_leader_${region}`,
      `I am the ${cap(region)} Gym Leader! Defeat my trainers to challenge me!`,
      [{text:'Battle!',actions:[{startCombat:`monster_gym_leader_${region}`}]},{text:'Leave'}]
    ));
    range(12).forEach(ti=>{
      monsters.push(makeMonster({id:`monster_trainer_${region}_${ti}`,
        name:`${cap(region)} Trainer ${ti+1}`,
        hp:100+ri*15+ti*10,atk:70+ri*2,dmgMin:5+ri+ti,dmgMax:15+ri*2+ti,
        iconRow:231,iconCol:1+ri,conversationID:`conv_trainer_${region}_${ti}`}));
      conversations.push(makeConversation(`conv_trainer_${region}_${ti}`,
        `You want to challenge me? Let's see your Astral Beasts!`,
        [{text:'Battle!',actions:[{startCombat:`monster_trainer_${region}_${ti}`}]},{text:'Leave'}]
      ));
    });
    quests.push(makeQuest(`quest_gym_${region}`,`${cap(region)} Gym`,
      `Defeat all ${cap(region)} trainers and the Gym Leader.`,
      [...range(12).map(j=>({desc:`Defeat ${cap(region)} Trainer ${j+1}.`,exp:200})),
       {desc:`Defeat the ${cap(region)} Gym Leader.`,exp:1000}]
    ));
  });

  // Grand Champion
  monsters.push(makeMonster({id:'monster_grand_champion',name:'Grand Champion Aethon',
    hp:1000,atk:95,dmgMin:25,dmgMax:60,iconRow:240,iconCol:1,conversationID:'conv_grand_champion'}));
  conversations.push(makeConversation('conv_grand_champion',
    'You have defeated all 9 regional champions! Now face me — the Grand Champion!',
    [{text:'Battle!',actions:[{startCombat:'monster_grand_champion'}]},{text:'Leave'}]
  ));
  quests.push(makeQuest('quest_professor_catch_all','Catch All Astral Beasts',
    'The Professor wants you to catch and evolve all 270 Astral Beasts.',
    POKEMON_REGIONS.flatMap(region=>
      (BEAST_POOLS[region]||[]).map(base=>({desc:`Catch and fully evolve ${base} (${region} region).`,exp:500})))
  ));

  // NPCs
  ['conv_beast_professor','conv_beast_scholar','conv_beast_elder','conv_beast_breeder'].forEach((id,i)=>{
    conversations.push(makeConversation(id,
      ['Professor Astralis: Your quest — catch all 270 Astral Beasts and evolve them all!',
       'The Scholar: Bring me a beast and the evolution fee and I will evolve it.',
       'The Elder: Spirit Orbs, healing potions — everything a trainer needs!',
       'The Breeder: Bring me two compatible beasts to breed a unique new creature (both consumed).'
      ][i],
      i===0?[{text:'I accept!',actions:[{startQuest:'quest_professor_catch_all'}]},{text:'Not yet.'}]:
      [{text:'Browse',actions:[i===2?{openShop:'shop_beast_elder'}:{openBreederMenu:true}]},{text:'Leave'}]
    ));
  });

  // Overworld prevention
  conversations.push(makeConversation('conv_prevent_pokemon',
    'WARNING: Astral Beasts are not permitted in the real world! All equipped beasts have been returned to your inventory.',
    [{text:'Understood.',actions:[{unequipAllBeasts:true}]}]
  ));
  conversations.push(makeConversation('conv_prevent_overworld',
    'WARNING: Real weapons and armor are not permitted in game worlds! All equipped real items have been returned to inventory.',
    [{text:'Understood.',actions:[{unequipNonBeastItems:true}]}]
  ));

  return {items,monsters,droplists,conversations,quests,actorconditions};
}

// ─────────────────────────────────────────────────────────────────────────────
// STOLEN ITEMS
// ─────────────────────────────────────────────────────────────────────────────
function buildStolenItems() {
  const items=[];
  const STOLEN_TYPES=['Vase','Jewel','Trinket','Figurine','Candle','Book','Pouch','Cloth','Ornament','Coin'];
  range(200).forEach(i=>items.push(makeItem({id:`stolen_item_${i}`,
    name:`Stolen ${STOLEN_TYPES[i%10]} ${Math.floor(i/10)+1}`,
    iconRow:250+Math.floor(i/8),iconCol:1+i%8,baseMarketCost:10+i*3,
    isSellable:true,desc:'Stolen goods. Best fenced quickly.'})));
  return {items};
}

// ─────────────────────────────────────────────────────────────────────────────
// MAP GENERATORS
// ─────────────────────────────────────────────────────────────────────────────
// makeStandardMap — routes old-style named object groups into the 4 real AT groups:
//   Spawn_* / spawn_* → Spawn, Keys_* / key_* → Keys, Replace_* → Replace, else → Mapevents
function makeStandardMap(tmxPath, objectLayers, w=30, h=30) {
  const spawnObjects      = [];
  const keyObjects        = [];
  const replaceObjects    = [];
  const mapEventObjects   = [];
  for (const layer of objectLayers) {
    if (layer.type !== 'objectgroup') continue; // tilelayer entries ignored (buildTMX always produces all 8 blank layers)
    const objs = layer.objects || [];
    const n    = (layer.name || '').toLowerCase();
    if      (n.startsWith('spawn'))   spawnObjects.push(...objs);
    else if (n.startsWith('keys'))    keyObjects.push(...objs);
    else if (n.startsWith('replace')) replaceObjects.push(...objs);
    else                              mapEventObjects.push(...objs);
  }
  return { path: tmxPath, tmx: buildTMX({ width:w, height:h, spawnObjects, keyObjects, replaceObjects, mapEventObjects }) };
}

function generateAllMaps() {
  const maps = [];

  // ── template_crafting.tmx ────────────────────────────────────────────────
  maps.push(makeStandardMap('template_crafting.tmx', [
    {type:'objectgroup',name:'Spawn_animal_grassland',color:'#ff8800',
     objects:range(3).map(i=>makeSpawnObj(`animal_grassland_${i}`,64+i*64,64))},
    ...REGIONS.map((region,ri)=>({type:'objectgroup',name:`Spawn_animal_${region}`,color:'#ff8800',
      objects:range(3).map(i=>makeSpawnObj(`animal_${cid(region)}_${i}`,64+i*64,96+ri*32))})),
    {type:'objectgroup',name:'Keys_forage',color:'#00ff00',
     objects:REGIONS.map((region,i)=>makeKeyObj(`forage_${cid(region)}`,`conv_forage_${cid(region)}`,64+i*32,320,
       [{name:'resetAfterHours',value:'24'}]))},
    {type:'objectgroup',name:'Keys_mining',color:'#888888',
     objects:[makeKeyObj('mining_rock','conv_mining_rock',64,380,[{name:'requiresEquipped',value:'item_pick_axe'}])]},
    {type:'objectgroup',name:'Spawn_mining',color:'#996633',
     objects:[
       makeNPCObj('npc_old_miner','conv_npc_old_miner',64,420),
       makeNPCObj('npc_store_keeper','conv_npc_store_keeper',96,420),
       ...range(12).map(i=>makeSpawnObj(`monster_witch_${i%4}`,128+i*32,420)),
     ]},
    {type:'objectgroup',name:'Keys_crafting',color:'#ff00ff',
     objects:[
       makeKeyObj('game_console','conv_game_console',64,480,[{name:'mapChangeID',value:'astral_spire'},{name:'saveRoomID',value:'true'}]),
       makeKeyObj('computer','conv_computer',96,480,[{name:'mapChangeID',value:'lpc_church'},{name:'saveRoomID',value:'true'}]),
       makeKeyObj('loom','conv_loom',128,480),makeKeyObj('stove','conv_stove',160,480),
       makeKeyObj('garden','conv_garden',192,480),makeKeyObj('smithing_forge','conv_smithing_forge',224,480),
       makeKeyObj('crafting_bench','conv_crafting_bench',256,480),makeKeyObj('miners_forge','conv_miners_forge',288,480),
       makeSignObj('crafting_price_sign',320,480,'Crafting Prices: Pick Axe 50g | Seeds 2g+ | Hoe 15g | Materials from 5g'),
     ]},
    {type:'objectgroup',name:'Spawn_crafting',color:'#0000ff',
     objects:[
       makeNPCObj('npc_seamstress','conv_npc_seamstress',64,540),
       makeNPCObj('npc_butcher','conv_npc_butcher',96,540),
       makeNPCObj('npc_grocer','conv_npc_grocer',128,540),
       makeNPCObj('npc_farmer','conv_npc_farmer',160,540),
       makeNPCObj('npc_weaponer','conv_npc_weaponer',192,540),
       makeNPCObj('npc_armorer','conv_npc_armorer',224,540),
       makeNPCObj('npc_scholar','conv_npc_scholar',256,540),
       makeNPCObj('npc_realtor','conv_realtor',288,540),
       makeNPCObj('npc_butler','conv_npc_butler',320,540,[{name:'requiresCondition',value:'owns_luxury_home'}]),
       makeNPCObj('npc_timekeeper','conv_timekeeper',352,540),
     ]},
  ], 50, 50));

  // ── template_guild.tmx ────────────────────────────────────────────────────
  maps.push(makeStandardMap('template_guild.tmx', [
    {type:'objectgroup',name:'Keys_guild',color:'#ff00aa',
     objects:[
       makeKeyObj('fighters_forge','conv_fighters_forge',64,64,[{name:'requiresGuild',value:'fighter'},{name:'minGuildLevel',value:'3'}]),
       makeKeyObj('writing_desk','conv_writing_desk',96,64),
       makeKeyObj('desk_mage','conv_desk_mage',128,64,[{name:'requiresGuild',value:'mage'},{name:'minGuildLevel',value:'3'}]),
       makeKeyObj('desk_cleric','conv_desk_cleric',160,64,[{name:'requiresGuild',value:'cleric'},{name:'minGuildLevel',value:'3'}]),
       makeKeyObj('desk_druid','conv_desk_druid',192,64,[{name:'requiresGuild',value:'druid'},{name:'minGuildLevel',value:'3'}]),
       makeKeyObj('cauldron','conv_cauldron',224,64,[{name:'requiresGuild',value:'mage,cleric,druid'},{name:'minGuildLevel',value:'6'}]),
       makeKeyObj('crafting_table','conv_crafting_table',256,64,[{name:'requiresGuild',value:'mage,cleric,druid'}]),
       makeKeyObj('key_crafting_table','conv_key_crafting_table',288,64,[{name:'requiresGuild',value:'thief'}]),
     ]},
    {type:'objectgroup',name:'Spawn_guild',color:'#0000aa',
     objects:GUILDS.flatMap((guild,gi)=>[
       makeNPCObj(`npc_guildmaster_${guild}`,`conv_guildmaster_${guild}`,64+gi*48,128),
       makeNPCObj(`npc_guild_seller_${guild}`,`conv_guild_seller_${guild}`,64+gi*48,160),
     ])},
    {type:'objectgroup',name:'Keys_door',color:'#884400',
     objects:[makeKeyObj('locked_door','conv_door',64,220),makeKeyObj('key_table','conv_key_crafting_table',96,220)]},
    {type:'objectgroup',name:'Spawn_door',color:'#aa6600',
     objects:[makeSpawnObj('npc_pickpocket_0',64,256)]},
    {type:'objectgroup',name:'Spawn_thief_npc',color:'#888800',
     objects:range(200).map(i=>makeNPCObj(`npc_pickpocket_${i}`,'conv_pickpocket_action',64+(i%20)*32,300+(Math.floor(i/20))*32))},
    {type:'objectgroup',name:'Keys_thief_home',color:'#44aa00',
     objects:range(200).map(i=>makeKeyObj(`home_loot_${i}`,`conv_home_loot_${i}`,64+(i%20)*32,1000+(Math.floor(i/20))*32))},
    {type:'objectgroup',name:'Spawn_bank',color:'#ffdd00',
     objects:[
       makeNPCObj('npc_bank_manager','conv_bank_manager',64,1700),
       makeNPCObj('npc_bank_teller','conv_bank_teller',96,1700),
       makeNPCObj('npc_bank_guard','conv_bank_guard',128,1700,[{name:'triggerConv',value:'conv_bank_robbery'}]),
       ...range(5).map(i=>makeNPCObj(`npc_bank_patron_${i}`,'conv_bank_patron',160+i*32,1700)),
     ]},
    {type:'objectgroup',name:'Spawn_jail',color:'#666666',
     objects:[
       makeNPCObj('npc_jail_guard','conv_jail_guard',64,1800),
       makeNPCObj('npc_jail_captain','conv_jail_captain',96,1800),
       makeNPCObj('npc_jail_lawyer','conv_jail_lawyer',128,1800),
     ]},
  ], 80, 80));

  // ── template_faction.tmx ──────────────────────────────────────────────────
  maps.push(makeStandardMap('template_faction.tmx', [
    {type:'objectgroup',name:'Spawn_faction',color:'#ff4400',
     objects:RACES.flatMap((race,ri)=>[
       ...range(4).map(i=>makeSpawnObj(`npc_${race}_${i}`,64+ri*32,64+i*32,
         [{name:'faction',value:race},{name:'attitude',value:RACE_ATTITUDE[race]}])),
       makeNPCObj(`npc_${race}_leader`,`conv_leader_${race}`,64+ri*32,200),
     ])},
  ], 60, 60));

  // ── faction_hall.tmx ──────────────────────────────────────────────────────
  maps.push(makeStandardMap('faction_hall.tmx', [
    {type:'objectgroup',name:'Spawn_faction_hall',color:'#ffaa00',
     objects:[
       makeNPCObj('npc_disguise_seller','conv_disguise_seller',96,96),
       makeSignObj('faction_hall_sign',128,96,'Faction Hall — Disguises for every race!'),
       makeNPCObj('npc_timekeeper','conv_timekeeper',160,96),
     ]},
  ]));

  // ── template_quests.tmx ───────────────────────────────────────────────────
  maps.push(makeStandardMap('template_quests.tmx', [
    {type:'objectgroup',name:'Keys_quest',color:'#00ffff',
     objects:[
       makeKeyObj('rumor_board','conv_rumor_board',64,64),
       makeKeyObj('overworld_bulletin','conv_overworld_bulletin',96,64),
       ...GUILDS.map((g,i)=>makeSignObj(`guild_sign_${g}`,128+i*32,64,`Join the ${cap(g)} Guild! Adventure awaits!`)),
     ]},
    {type:'objectgroup',name:'Spawn_witch',color:'#8800ff',
     objects:[makeNPCObj('npc_witch','conv_witch',64,128),...range(4).map(i=>makeSpawnObj(`monster_witch_${i}`,128+i*32,128))]},
    {type:'objectgroup',name:'Keys_witch',color:'#440088',
     objects:[makeKeyObj('witch_search_1','conv_witch_search',192,128),makeKeyObj('witch_search_2','conv_witch_search',224,128)]},
    {type:'objectgroup',name:'Spawn_drow',color:'#0044ff',
     objects:[
       makeNPCObj('npc_drow_guard','conv_drow_guard',64,256),
       makeNPCObj('npc_drow_leader','conv_drow_leader',96,256),
       makeNPCObj('npc_drow_witch','conv_drow_witch',128,256),
       ...range(6).map(i=>makeSpawnObj(`monster_drow_cave_${i}`,160+i*32,256)),
     ]},
    {type:'objectgroup',name:'Keys_drow',color:'#002288',
     objects:[...range(6).map(i=>makeKeyObj(`drow_search_${i}`,'conv_witch_search',320+i*32,256))]},
    {type:'objectgroup',name:'Spawn_lloth',color:'#ff00ff',
     objects:[
       makeNPCObj('npc_lloth','conv_lloth',64,400),
       ...range(7).map(i=>makeSpawnObj(`monster_lloth_guard_${i}`,96+i*32,400)),
     ]},
    {type:'objectgroup',name:'Spawn_dragon',color:'#ff4400',
     objects:[
       ...DRAGON_TYPES.flatMap((type,ti)=>DRAGON_AGES.map((age,ai)=>makeSpawnObj(`dragon_${cid(type)}_${age}`,64+ti*32,500+ai*32))),
       makeNPCObj('dragon_ancient_platinum','conv_dragon_ancient_platinum',64,628),
       makeNPCObj('dragon_ancient_chromatic','conv_dragon_ancient_chromatic',96,628),
     ]},
    {type:'objectgroup',name:'Keys_ring',color:'#ffff00',
     objects:[
       makeKeyObj('sunny_ring_search','conv_sunny_ring_search',64,700),
       makeSignObj('sign_north',96,700,'North: Drow Village'),
       makeSignObj('sign_south',96,732,'South: Rocket Pad'),
       makeSignObj('sign_east',128,716,'East: Forest'),
       makeSignObj('sign_west',64,716,'West: Lake'),
       makeKeyObj('tent_exit_1','conv_tent_exit',160,700,[{name:'linkTo',value:'tent_exit_2'}]),
       makeKeyObj('tent_exit_2','conv_tent_exit',192,700,[{name:'linkTo',value:'tent_exit_1'}]),
       ...MOON_COLORS.flatMap((color,i)=>[
         makeKeyObj(`rocket_${cid(color)}_board_1`,`conv_rocket_${cid(color)}`,224+i*32,700),
         makeKeyObj(`rocket_${cid(color)}_board_2`,`conv_rocket_${cid(color)}`,224+i*32,732),
       ]),
     ]},
    {type:'objectgroup',name:'Spawn_ring_forest',color:'#008800',
     objects:range(12).map(i=>makeSpawnObj(`monster_ring_forest_${i}`,64+i*32,780))},
    {type:'objectgroup',name:'Spawn_ring_npc',color:'#0088aa',
     objects:[
       makeNPCObj('npc_ring_guard','conv_ring_guard',64,820),
       ...range(12).map(i=>makeSpawnObj(`npc_moon_drow_${cid(MOON_COLORS[0])}_${i}`,96+i*32,820)),
       makeNPCObj(`npc_moon_elder_${cid(MOON_COLORS[0])}`,`conv_moon_elder_${cid(MOON_COLORS[0])}`,96,852),
     ]},
    {type:'objectgroup',name:'Spawn_castle',color:'#884400',
     objects:[
       makeNPCObj('npc_ozzy','conv_npc_ozzy',64,1020),
       makeNPCObj('npc_nymph','conv_npc_nymph',96,1020),
       makeNPCObj('npc_guard_captain','conv_npc_guard_captain',128,1020),
       ...range(12).map(i=>makeSpawnObj('npc_pickpocket_0',160+i*32,1020)),
       makeNPCObj('npc_head_cook','conv_npc_head_cook',64,1052),
       makeNPCObj('npc_librarian','conv_npc_librarian',96,1052),
       makeNPCObj('npc_gardener','conv_npc_gardener',128,1052),
       makeNPCObj('npc_castle_weaponer','conv_castle_weaponer',160,1052),
       makeNPCObj('npc_castle_armorer','conv_castle_armorer',192,1052),
       makeNPCObj('npc_castle_alchemist','conv_castle_alchemist',224,1052),
       makeNPCObj('npc_timekeeper','conv_timekeeper',256,1052),
     ]},
    {type:'objectgroup',name:'Spawn_tower_npc',color:'#ffaa00',
     objects:[
       makeNPCObj('npc_crystal_grandmaster','conv_crystal_grandmaster',64,1200),
       ...['Red','Orange','Yellow','Green','Cyan','Blue','Indigo','Violet','Silver','Gold','Black','White'].flatMap((c,ti)=>
         range(5).flatMap(level=>range(5).map(j=>makeSpawnObj(`monster_tower_${cid(c)}_lvl${level}_${j}`,64+ti*64+j*32,1240+level*32)))),
     ]},
    ...['haunted_house','haunted_mansion','haunted_prison','graveyard','crypt','mausoleum'].map((place,pi)=>({
      type:'objectgroup',name:`Spawn_haunted_${cid(place)}`,color:'#440044',
      objects:[
        ...range(25).map(gi=>makeSpawnObj(`monster_${cid(place)}_${gi}`,64+gi*32,1500+pi*96)),
        makeSpawnObj(`monster_boss_${cid(place)}`,64,1532+pi*96),
      ]
    })),
    {type:'objectgroup',name:'Spawn_sunny_family',color:'#ffddff',
     objects:[
       makeNPCObj('npc_sunny','conv_npc_sunny',64,2000),
       makeNPCObj('npc_ozzy','conv_npc_ozzy',96,2000),
       makeNPCObj('npc_nymph','conv_npc_nymph',128,2000),
     ]},
  ], 80, 80));

  // ── template_pokemon.tmx ──────────────────────────────────────────────────
  maps.push(makeStandardMap('template_pokemon.tmx', [
    {type:'objectgroup',name:'Spawn_pokemon_npc',color:'#00ffaa',
     objects:[
       makeNPCObj('npc_beast_professor','conv_beast_professor',64,64),
       makeNPCObj('npc_beast_scholar','conv_beast_scholar',96,64),
       makeNPCObj('npc_beast_elder','conv_beast_elder',128,64),
       makeNPCObj('npc_beast_breeder','conv_beast_breeder',160,64),
       makeNPCObj('monster_grand_champion','conv_grand_champion',192,64),
       ...POKEMON_REGIONS.flatMap((region,ri)=>[
         makeNPCObj(`monster_gym_leader_${region}`,`conv_gym_leader_${region}`,64+ri*48,128),
         ...range(12).map(ti=>makeNPCObj(`monster_trainer_${region}_${ti}`,`conv_trainer_${region}_${ti}`,64+ri*48+ti*4,160)),
       ]),
     ]},
    ...POKEMON_REGIONS.map((region,ri)=>({type:'objectgroup',name:`Spawn_pokemon_${region}`,color:'#00cc88',
      objects:(BEAST_POOLS[region]||[]).slice(0,6).map((base,bi)=>
        makeSpawnObj(`monster_beast_${region}_${cid(base)}_t1`,64+ri*32,300+bi*32))})),
    {type:'objectgroup',name:'Spawn_pokemon_unlocked',color:'#00ff44',
     objects:POKEMON_REGIONS.slice(0,3).map((region,ri)=>
       makeSpawnObj(`monster_beast_${region}_${cid(BEAST_POOLS[region][0])}_t1`,64+ri*32,500,[{name:'requiresCondition',value:`gym_${region}_complete`}]))},
    {type:'objectgroup',name:'Keys_prevent_pokemon',color:'#ff0000',
     objects:[makeKeyObj('pokemon_ban_zone','conv_prevent_pokemon',32,32,[{name:'trigger',value:'onEnter'}])]},
    {type:'objectgroup',name:'Keys_prevent_overworld',color:'#0000ff',
     objects:[makeKeyObj('overworld_ban_zone','conv_prevent_overworld',64,32,[{name:'trigger',value:'onEnter'}])]},
  ], 80, 80));

  // ── template_holiday.tmx ─────────────────────────────────────────────────
  // (8 blank tile layers are always emitted by buildTMX; holiday replace layers go in the Keys group
  //  so that the AT engine can find them via key-trigger replace lookups)
  maps.push(makeStandardMap('template_holiday.tmx', [
    // Replace triggers in Keys group — use AT replace convention with replaceLayer_* properties
    ...HOLIDAYS.map((h,hi)=>({type:'objectgroup',name:`Keys_holiday_${h.id}`,
      objects:[makeKeyObj(`holiday_trigger_${h.id}`,`conv_holiday_replace_${h.id}`,32,32+hi*32,[
        {name:'replaceLayer_Objects',  value:`Objects_${h.id}`},
        {name:'replaceLayer_Above',    value:`Above_${h.id}`},
        {name:'replaceLayer_Walkable', value:`Walkable_${h.id}`},
        {name:'startDate',     value:h.monthDay},
        {name:'weeksBefore',   value:String(h.weeksBefore)},
        {name:'weeksAfter',    value:String(h.weeksAfter)},
      ])]})),
    // Spawn group — holiday timekeepers + event NPCs
    {type:'objectgroup',name:'Spawn_holiday',
     objects:[
       ...HOLIDAYS.map((h,hi)=>makeNPCObj(`npc_timekeeper_${h.id}`,'conv_timekeeper',96,96+hi*48)),
       makeNPCObj('npc_timekeeper','conv_timekeeper',64,64),
     ]},
    {type:'objectgroup',name:'Spawn_events',
     objects:EVENTS.flatMap((event,ei)=>[
       makeNPCObj(`npc_event_${event}`,`conv_event_npc_${event}`,96,500+ei*48),
       makeNPCObj(`npc_event_planner_${event}`,`conv_event_planner_${event}`,128,500+ei*48),
     ])},
    // Replace group — event replace triggers
    ...EVENTS.map((event,ei)=>({type:'objectgroup',name:`Replace_event_${event}`,
      objects:[makeKeyObj(`event_trigger_${event}`,`conv_event_replace_${event}`,32,96+ei*32,[{name:'duration',value:'24h'}])]})),
  ], 60, 60));

  // ── template_overworld.tmx ────────────────────────────────────────────────
  maps.push(makeStandardMap('template_overworld.tmx', [
    {type:'objectgroup',name:'Keys_prevent_pokemon',color:'#ff0000',
     objects:[makeKeyObj('pokemon_ban_zone','conv_prevent_pokemon',32,32,[{name:'trigger',value:'onEnter'}])]},
    {type:'objectgroup',name:'Keys_prevent_overworld',color:'#0000ff',
     objects:[makeKeyObj('overworld_ban_zone','conv_prevent_overworld',32,64,[{name:'trigger',value:'onEnter'}])]},
  ], 60, 60));

  // ── home.tmx ──────────────────────────────────────────────────────────────
  maps.push(makeStandardMap('home.tmx', [
    {type:'objectgroup',name:'Objects_home',color:'#ddaa00',
     objects:[
       makeKeyObj('home_console','conv_game_console',64,64,[{name:'mapChangeID',value:'astral_spire'},{name:'saveRoomID',value:'true'}]),
       makeKeyObj('home_computer','conv_computer',96,64,[{name:'mapChangeID',value:'lpc_church'},{name:'saveRoomID',value:'true'}]),
       makeKeyObj('home_stove','conv_stove',128,64),
       makeKeyObj('home_garden','conv_garden',160,64),
       makeKeyObj('home_bench','conv_crafting_bench',192,64),
       makeKeyObj('home_forge1','conv_smithing_forge',224,64),
       makeKeyObj('home_forge2','conv_miners_forge',256,64),
       makeKeyObj('home_loom','conv_loom',288,64),
     ]},
    {type:'objectgroup',name:'Spawn_home',color:'#dddd00',
     objects:[makeNPCObj('npc_butler','conv_npc_butler',64,96,[{name:'requiresCondition',value:'owns_luxury_home'}]),
              makeNPCObj('npc_timekeeper','conv_timekeeper',96,96)]},
  ]));

  // ── house.tmx ─────────────────────────────────────────────────────────────
  maps.push(makeStandardMap('house.tmx', [
    {type:'objectgroup',name:'Objects_house_small',color:'#aabbcc',
     objects:[
       makeKeyObj('house_console','conv_game_console',64,64,[{name:'requiresItem',value:'item_deed_small_home'}]),
       makeKeyObj('house_computer','conv_computer',96,64,[{name:'requiresItem',value:'item_deed_small_home'}]),
       makeKeyObj('house_stove','conv_stove',128,64,[{name:'requiresItem',value:'item_deed_small_home'}]),
     ]},
    {type:'objectgroup',name:'Objects_house_mid',color:'#88aacc',
     objects:[
       makeKeyObj('house_garden','conv_garden',160,64,[{name:'requiresItem',value:'item_deed_mid_home'}]),
       makeKeyObj('house_bench','conv_crafting_bench',192,64,[{name:'requiresItem',value:'item_deed_mid_home'}]),
     ]},
    {type:'objectgroup',name:'Objects_house_large',color:'#6688cc',
     objects:[
       makeKeyObj('house_forge1','conv_smithing_forge',224,64,[{name:'requiresItem',value:'item_deed_large_home'}]),
       makeKeyObj('house_forge2','conv_miners_forge',256,64,[{name:'requiresItem',value:'item_deed_large_home'}]),
     ]},
    {type:'objectgroup',name:'Spawn_house_luxury',color:'#4466cc',
     objects:[makeNPCObj('npc_butler','conv_npc_butler',64,128,[{name:'requiresItem',value:'item_deed_luxury_home'}])]},
  ]));

  // ── astral_spire.tmx ──────────────────────────────────────────────────────
  maps.push(makeStandardMap('astral_spire.tmx', [
    {type:'objectgroup',name:'Objects_astral',color:'#8800ff',
     objects:[
       makeKeyObj('astral_logout_scroll','conv_logout_scroll',96,96,[{name:'giveItem',value:'item_logout_scroll'}]),
       makeKeyObj('astral_exit','conv_astral_exit',128,96,[{name:'mapChangeToSaved',value:'console_room'}]),
       makeKeyObj('astral_pokemon_ban','conv_prevent_overworld',32,32,[{name:'trigger',value:'onEnter'}]),
     ]},
    {type:'objectgroup',name:'Spawn_astral',color:'#9900ff',
     objects:POKEMON_REGIONS.slice(0,3).flatMap((region,ri)=>
       (BEAST_POOLS[region]||[]).slice(0,2).map((base,bi)=>
         makeSpawnObj(`monster_beast_${region}_${cid(base)}_t1`,64+ri*64+bi*32,160)))},
  ]));

  // ── lpc_church.tmx ────────────────────────────────────────────────────────
  maps.push(makeStandardMap('lpc_church.tmx', [
    {type:'objectgroup',name:'Objects_church',color:'#ff8800',
     objects:[
       makeKeyObj('church_logout','conv_logout_scroll',96,96,[{name:'giveItem',value:'item_logout_scroll'}]),
       makeKeyObj('church_exit','conv_church_exit',128,96,[{name:'mapChangeToSaved',value:'computer_room'}]),
       makeKeyObj('church_pokemon_ban','conv_prevent_overworld',32,32,[{name:'trigger',value:'onEnter'}]),
     ]},
    {type:'objectgroup',name:'Spawn_church',color:'#ff9900',
     objects:[
       makeNPCObj('npc_church_priest','conv_church_priest',64,128),
       makeNPCObj('npc_church_monk','conv_church_monk',96,128),
       ...range(5).map(i=>makeSpawnObj(`monster_lloth_guard_${i}`,160+i*32,200)),
     ]},
  ]));

  // ── ring_clearing.tmx ─────────────────────────────────────────────────────
  maps.push(makeStandardMap('ring_clearing.tmx', [
    {type:'objectgroup',name:'Keys_ring_clearing',color:'#ffdd00',
     objects:[
       makeKeyObj('ring_search','conv_sunny_ring_search',96,96),
       makeSignObj('sign_north',128,64,'North: Drow Village'),
       makeSignObj('sign_south',128,128,'South: Rocket Pad'),
       makeSignObj('sign_east',160,96,'East: Forest'),
       makeSignObj('sign_west',96,96,'West: Lake'),
       makeKeyObj('tent_exit_clear_1','conv_tent_exit',192,96,[{name:'linkTo',value:'tent_exit_2'}]),
       makeKeyObj('tent_exit_clear_2','conv_tent_exit',224,96,[{name:'linkTo',value:'tent_exit_1'}]),
       ...MOON_COLORS.flatMap((color,i)=>[
         makeKeyObj(`rocket_c_${cid(color)}_1`,`conv_rocket_${cid(color)}`,256+i*32,96),
         makeKeyObj(`rocket_c_${cid(color)}_2`,`conv_rocket_${cid(color)}`,256+i*32,128),
       ]),
     ]},
    {type:'objectgroup',name:'Spawn_ring_clearing',color:'#aaddff',
     objects:[makeNPCObj('npc_ring_guard','conv_ring_guard',96,160)]},
    {type:'objectgroup',name:'Spawn_ring_forest',color:'#008800',
     objects:range(12).map(i=>makeSpawnObj(`monster_ring_forest_${i}`,64+i*32,200))},
  ]));

  // ── QUEST MAPS ────────────────────────────────────────────────────────────

  // swamp_witch.tmx
  maps.push(makeStandardMap('swamp_witch.tmx', [
    {type:'objectgroup',name:'Spawn_witch',color:'#8800ff',
     objects:[makeNPCObj('npc_witch','conv_witch',96,96),...range(4).map(i=>makeSpawnObj(`monster_witch_${i}`,128+i*32,128))]},
    {type:'objectgroup',name:'Keys_witch',color:'#440088',
     objects:[makeKeyObj('witch_search_1','conv_witch_search',192,128),makeKeyObj('witch_search_2','conv_witch_search',224,128)]},
    {type:'objectgroup',name:'Spawn_swamp_animals',color:'#447700',
     objects:range(5).map(i=>makeSpawnObj(`animal_swamp_${i}`,64+i*32,160))},
  ]));

  // drow_cave.tmx
  maps.push(makeStandardMap('drow_cave.tmx', [
    {type:'objectgroup',name:'Spawn_drow',color:'#0044ff',
     objects:[
       makeNPCObj('npc_drow_guard','conv_drow_guard',64,96),
       makeNPCObj('npc_drow_leader','conv_drow_leader',96,96),
       makeNPCObj('npc_drow_witch','conv_drow_witch',128,96),
       ...range(6).map(i=>makeSpawnObj(`monster_drow_cave_${i}`,160+i*32,128)),
     ]},
    {type:'objectgroup',name:'Keys_drow',color:'#002288',
     objects:range(6).map(i=>makeKeyObj(`drow_search_${i}`,'conv_witch_search',64+i*32,192))},
    {type:'objectgroup',name:'Spawn_cave_animals',color:'#336688',
     objects:range(5).map(i=>makeSpawnObj(`animal_dark_cave_${i}`,64+i*32,224))},
  ]));

  // lloth_realm.tmx
  maps.push(makeStandardMap('lloth_realm.tmx', [
    {type:'objectgroup',name:'Spawn_lloth',color:'#ff00ff',
     objects:[
       makeNPCObj('npc_lloth','conv_lloth',96,96),
       ...range(7).map(i=>makeSpawnObj(`monster_lloth_guard_${i}`,64+i*32,128)),
     ]},
  ]));

  // volcano.tmx
  maps.push(makeStandardMap('volcano.tmx', [
    {type:'objectgroup',name:'Spawn_dragon',color:'#ff4400',
     objects:[
       ...DRAGON_TYPES.flatMap((type,ti)=>DRAGON_AGES.map((age,ai)=>
         makeNPCObj(`dragon_${cid(type)}_${age}`,`conv_dragon_${cid(type)}_adult`,64+ti*32,64+ai*32))),
       makeNPCObj('dragon_ancient_platinum','conv_dragon_ancient_platinum',64,192),
       makeNPCObj('dragon_ancient_chromatic','conv_dragon_ancient_chromatic',96,192),
       makeKeyObj('dragon_dispute_complete','conv_dragon_dispute_complete',128,192),
     ]},
    {type:'objectgroup',name:'Spawn_volcano_animals',color:'#884400',
     objects:range(5).map(i=>makeSpawnObj(`animal_volcano_${i}`,64+i*32,224))},
  ]));

  // castle.tmx
  maps.push(makeStandardMap('castle.tmx', [
    {type:'objectgroup',name:'Spawn_castle',color:'#884400',
     objects:[
       makeNPCObj('npc_ozzy','conv_npc_ozzy',64,64),
       makeNPCObj('npc_nymph','conv_npc_nymph',96,64),
       makeNPCObj('npc_guard_captain','conv_npc_guard_captain',128,64),
       ...range(12).map(i=>makeSpawnObj('npc_pickpocket_0',160+i*32,64)),
       makeNPCObj('npc_head_cook','conv_npc_head_cook',64,96),
       makeNPCObj('npc_librarian','conv_npc_librarian',96,96),
       makeNPCObj('npc_gardener','conv_npc_gardener',128,96),
       ...range(2).map(i=>makeNPCObj(`npc_castle_guest_${i+1}`,`conv_npc_castle_guest_${i+1}`,160+i*32,96)),
       makeNPCObj('npc_gate_guard','conv_npc_gate_guard',224,96),
       ...range(3).map(i=>makeNPCObj(`npc_servant_${i+1}`,`conv_npc_servant_${i+1}`,64+i*32,128)),
       makeNPCObj('npc_prison_warden','conv_npc_prison_warden',160,128),
       ...range(3).map(i=>makeSpawnObj('npc_pickpocket_0',192+i*32,128)),
       ...range(4).map(i=>makeSpawnObj('npc_pickpocket_0',256+i*32,128)),
       makeNPCObj('npc_castle_weaponer','conv_castle_weaponer',64,160),
       makeNPCObj('npc_castle_armorer','conv_castle_armorer',96,160),
       makeNPCObj('npc_castle_alchemist','conv_castle_alchemist',128,160),
       makeNPCObj('npc_timekeeper','conv_timekeeper',160,160),
     ]},
  ]));

  // crystal_towers.tmx
  maps.push(makeStandardMap('crystal_towers.tmx', [
    {type:'objectgroup',name:'Spawn_tower_npc',color:'#ffaa00',
     objects:[
       makeNPCObj('npc_crystal_grandmaster','conv_crystal_grandmaster',64,64),
       ...['Red','Orange','Yellow','Green','Cyan','Blue','Indigo','Violet','Silver','Gold','Black','White'].flatMap((c,ti)=>
         range(5).flatMap(level=>range(5).map(j=>makeSpawnObj(`monster_tower_${cid(c)}_lvl${level}_${j}`,64+ti*64+j*32,96+level*32)))),
     ]},
  ], 50, 50));

  // Haunted place maps
  ['haunted_house','haunted_mansion','haunted_prison','graveyard','crypt','mausoleum'].forEach((place,pi)=>{
    maps.push(makeStandardMap(`${cid(place)}.tmx`, [
      {type:'objectgroup',name:`Spawn_${cid(place)}`,color:'#440044',
       objects:[
         ...range(25).map(gi=>makeSpawnObj(`monster_${cid(place)}_${gi}`,64+gi%8*32,64+Math.floor(gi/8)*32)),
         makeSpawnObj(`monster_boss_${cid(place)}`,96,256),
       ]},
    ]));
  });

  // Moon maps
  MOON_COLORS.forEach((color,ci)=>{
    maps.push(makeStandardMap(`moon_${cid(color)}.tmx`, [
      {type:'objectgroup',name:`Spawn_moon_${cid(color)}`,color:'#aaaaff',
       objects:[
         makeNPCObj(`npc_moon_elder_${cid(color)}`,`conv_moon_elder_${cid(color)}`,96,96),
         ...range(12).map(j=>makeSpawnObj(`npc_moon_drow_${cid(color)}_${j}`,64+j%8*32,128+Math.floor(j/8)*32)),
         makeKeyObj(`rocket_back_${cid(color)}`,`conv_rocket_${cid(color)}`,64,192),
         makeNPCObj('npc_sunny','conv_npc_sunny',160,192,[{name:'requiresCondition',value:'all_moon_quests_done'}]),
       ]},
      {type:'objectgroup',name:`Spawn_moon_animals_${cid(color)}`,color:'#aaccaa',
       objects:range(5).map(i=>makeSpawnObj(`animal_tundra_${i}`,200+i*32,128))},
    ]));
  });

  // pokemon_gym.tmx
  maps.push(makeStandardMap('pokemon_gym.tmx', [
    {type:'objectgroup',name:'Spawn_gym_npcs',color:'#00ffaa',
     objects:POKEMON_REGIONS.flatMap((region,ri)=>[
       makeNPCObj(`monster_gym_leader_${region}`,`conv_gym_leader_${region}`,64+ri*48,64),
       ...range(12).map(ti=>makeNPCObj(`monster_trainer_${region}_${ti}`,`conv_trainer_${region}_${ti}`,64+ri*48,96+ti*32)),
     ])},
  ], 60, 60));

  // Conversations for misc map objects
  const extraConvs = [
    makeConversation('conv_logout_scroll','Pick up a Logout Scroll? It will return you to the room where you entered.',
      [{text:'Take scroll',actions:[{giveItem:'item_logout_scroll'}]},{text:'Leave'}]),
    makeConversation('conv_astral_exit','Exit the Astral Spire? You will return to your last console location.',
      [{text:'Exit',actions:[{mapChangeTo:'SAVED_CONSOLE_MAP'}]},{text:'Stay'}]),
    makeConversation('conv_church_exit','Leave the LPC Church? You will return to your last computer location.',
      [{text:'Leave',actions:[{mapChangeTo:'SAVED_COMPUTER_MAP'}]},{text:'Stay'}]),
    makeConversation('conv_church_priest','Welcome to the LPC Church virtual world! Seek knowledge and enlightenment here.',[{text:'Thank you.'}]),
    makeConversation('conv_church_monk','Meditation brings clarity. Stay as long as you wish.',[{text:'I will.'}]),
    makeConversation('conv_tent_exit','A magical tent exit. Step through to the linked exit.',
      [{text:'Enter',actions:[{mapChangeTo:'linked_tent_exit'}]},{text:'Stay'}]),
    ...MOON_COLORS.map(color=>makeConversation(`conv_rocket_${cid(color)}`,
      `A ${color.toLowerCase()} rocket ship bound for the ${color} Moon!`,
      [{text:'Launch!',actions:[{mapChange:{mapID:`moon_${cid(color)}`,mapX:5,mapY:5}}]},{text:'Not yet.'}])),
    ...HOLIDAYS.map(h=>makeConversation(`conv_holiday_replace_${h.id}`,
      `The area has transformed for ${h.name}!`,[{text:'Magical!'}])),
    ...EVENTS.map(event=>makeConversation(`conv_event_replace_${event}`,
      `The area has been decorated for the ${event}!`,[{text:'Lovely!'}])),
    makeConversation('conv_drow_search','Dark crystals gleam in the cave walls. Search carefully?',
      [{text:'Search (90%)',actions:[{rollChance:{chance:90,onSuccess:'giveDrowIngredient',onFail:'nothing'}}]},{text:'Leave'}]),
    makeConversation('conv_npc_castle_guest_1','What a lovely castle!',[{text:'Indeed.'}]),
    makeConversation('conv_npc_castle_guest_2','I heard tales of adventure nearby.',[{text:'Interesting.'}]),
    ...range(3).map(i=>makeConversation(`conv_npc_servant_${i+1}`,'How may I serve you?',[{text:'Carry on.'}])),
    makeConversation('conv_npc_gate_guard','I spotted something suspicious. Investigate?',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_gate_guard'}]},{text:'Leave'}]),
    makeConversation('conv_npc_prison_warden','Order is maintained in my prison.',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_prison_warden'}]},{text:'Leave'}]),
    makeConversation('conv_npc_gardener','The gardens need tending. Could you fetch exotic seeds?',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_gardener'}]},{text:'Leave'}]),
    makeConversation('conv_npc_librarian','I need a rare tome retrieved.',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_librarian'}]},{text:'Leave'}]),
    makeConversation('conv_npc_head_cook','The kitchen needs special ingredients!',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_head_cook'}]},{text:'Leave'}]),
    makeConversation('conv_npc_guard_captain','The castle is secure under my watch. I have a task.',
      [{text:'Accept Quest',actions:[{startQuest:'quest_npc_guard_captain'}]},{text:'Leave'}]),
  ];

  return {maps, extraConvs};
}

// ─────────────────────────────────────────────────────────────────────────────
// XML RESOURCES
// ─────────────────────────────────────────────────────────────────────────────
function buildStringsXml() {
  const entries = Object.entries(STRINGS)
    .map(([k,v])=>`    <string name="${k}">${xmlEsc(v)}</string>`)
    .join('\n');
  return `<?xml version="1.0" encoding="utf-8"?>\n<resources>\n${entries}\n</resources>`;
}

function buildLoadResourcesXml(jsonFiles, tmxFiles) {
  // AT format: named <array> elements with @raw/ references
  // Map JSON file names to AT resource array names
  const ARRAY_MAP = {
    'itemcategories_1.json':    'loadresource_itemcategories',
    'itemlist.json':            'loadresource_items',
    'actorconditions.json':     'loadresource_actorconditions',
    'monsterlist.json':         'loadresource_monsters',
    'droplists.json':           'loadresource_droplists',
    'conversationlist.json':    'loadresource_conversationlists',
    'questlist.json':           'loadresource_quests',
  };
  // Group files by array name
  const groups = {};
  for (const f of jsonFiles) {
    const baseName = f.split('/').pop();
    const arrayName = ARRAY_MAP[baseName];
    if (!arrayName) continue; // skip debug/data sub-files
    if (!groups[arrayName]) groups[arrayName] = [];
    const rawId = baseName.replace('.json','');
    groups[arrayName].push(`@raw/${rawId}`);
  }
  // Map TMX files as loadresource_maps
  const mapRefs = tmxFiles.map(f=>`@xml/${f.replace(/\.tmx$/,'')}`);
  if (mapRefs.length > 0) groups['loadresource_maps'] = mapRefs;

  const ORDER = ['loadresource_itemcategories','loadresource_actorconditions','loadresource_items',
    'loadresource_monsters','loadresource_droplists','loadresource_conversationlists',
    'loadresource_quests','loadresource_maps'];
  
  let xml = `<?xml version="1.0" encoding="utf-8"?>\n<resources>\n`;
  for (const arrayName of ORDER) {
    const refs = groups[arrayName];
    if (!refs || refs.length === 0) continue;
    xml += `    <array name="${arrayName}">\n`;
    refs.forEach(r => xml += `        <item>${r}</item>\n`);
    xml += `    </array>\n`;
  }
  xml += `</resources>`;
  return xml;
}

// ─────────────────────────────────────────────────────────────────────────────
// README
// ─────────────────────────────────────────────────────────────────────────────
function buildReadme(tmxFiles, jsonFiles, stringCount) {
  return `# Andor's Trail Extended Content Pack v3
## Developer Reference

### What's Included

| Category | Count |
|---|---|
| TMX Map Files | ${tmxFiles.length} |
| JSON Data Files | ${jsonFiles.length} |
| String Entries | ${stringCount} |
| Regions | 23 |
| Unique Items | 600+ |
| Unique Monsters/NPCs | 900+ |
| Quests | 200+ |
| Conversations | 600+ |
| Actor Conditions | 200+ |
| Astral Beasts | 270 + 30 breeding |
| Dragon Types | 10 standard + 2 ancient |
| Races/Factions | 15 |
| Holidays | 6 |
| Personal Events | 4 |

---

### TMX Map Files
${tmxFiles.map(f=>`- \`${f}\``).join('\n')}

---

### Map Layer Structure
Every TMX map follows the Andor's Trail template exactly:
\`\`\`
Tilesets: dc-dngn (gid 1), dc-dngn-t (gid 257), chars0 (gid 513), items (gid 769)
Tile Layers (base64+gzip encoded):
  Ground    — filled with GID 1 (floor tile)
  Walkable  — filled with GID 257 (walkable marker)
  Objects   — empty (GID 0)
  Above     — empty (GID 0)
  [+ holiday variant layers where applicable]
Object Layers — Spawn_*, Keys_*, Replace_* layers
\`\`\`

---

### Pickpocket System
NPC conversation \`conv_pickpocket_action\` is placed on all 200 pickpocket target NPCs.
- **Thief 1+**: 50% pickpocket chance → **30 gold** base
- **Thief 6+ (Sneak)**: 75% chance → scaled gold
- **Thief 9+ (Hide)**: 90% chance → maximum gold
- **Other guilds**: Battle option only
- **Kill drop**: random gold 1–19g (always under 20)
- **Caught**: \`mapChange\` to jail, lawyer arranges bail for 100g

Gold per level: ${[30,50,75,110,150,200,275,360,460,600].map((g,i)=>`L${i+1}:${g}g`).join(', ')}

---

### Timekeeper / Holiday System
A single NPC (\`npc_timekeeper\`, conversation \`conv_timekeeper\`) handles ALL holidays.
Place this NPC in any city. The conversation branches by date condition:

**Between holidays:**
- Tells player the current date
- Shows the next upcoming holiday
- Accepts the Time Crystal quest (carry crystal for 7 days)

**During a holiday window:**
- Becomes the holiday host NPC
- Gives 1 daily gift (gold + themed items; better gifts if quest complete)
- Offers the 4-part holiday quest
- Manages layer replacement (Objects_*, Above_*, Walkable_*) automatically

**Holiday Schedule:**
${HOLIDAYS.map(h=>`- ${h.name}: ${h.monthDay} ± 1 week`).join('\n')}

**Events** (birthday, graduation, wedding, funeral): 24 hours, arranged by event planner NPC for 500g.

**Implementation:**
- Holiday active: \`ac_holiday_active_{id}\` condition
- Gift given today: \`ac_holiday_gift_given_{id}\` condition (resets daily)
- Quest complete: \`ac_holiday_quest_done_{id}\` condition (permanent, enables good gifts)
- Layer trigger objects in \`Replace_holiday_{id}\` layer use \`startDate\`, \`weeksBefore\`, \`weeksAfter\` properties

---

### Guild System
6 guilds: Adventurer, Fighter, Thief, Mage, Cleric, Druid
- One active at a time (excluding Adventurer)
- Leave/rejoin preserves progress; abilities require active membership
- 12 quests per guild for advancement

**Crafting gates:**
| Station | Guild | Min Level |
|---|---|---|
| Fighter's Forge | Fighter | 3 |
| Mage/Cleric/Druid Desks | Respective | 3 |
| Cauldron | Mage/Cleric/Druid | 6 |
| Door Pick | Thief | 3 |
| Key Craft | Thief | 3 |
| Bank Robbery | Thief | 12 |

---

### Door Mechanics
- **Key/Master Key**: immediate open
- **Pick Lock**: 4 lockpick tiers (20%→80% success), thief level reduces failure
- **Bash**: Fighter 1+ (30%), Fighter 5+ (60%)
- **Inspect**: any thief level → enables key crafting
- **Door Pass Scroll**: Mage/Cleric/Druid 3+

---

### Home System
| Size | Features | Cost |
|---|---|---|
| Small | Console, Computer, Stove | 500g |
| Mid | + Garden, Bench | 1000g |
| Large | + Both Forges | 2000g |
| Luxury | + Butler (5% shop discount) | 4000g |

Butler sets \`butler_discount_active\` condition → shops check this for 5% discount.

---

### Main Quest Chain
1. **Rumor Board** → Swamp Witch quest (swamp_witch.tmx)
2. **Swamp Witch**: 4 monster drops + 1 foraged item → Sunny went to Drow Caves
3. **12 Sunny Info Quests** → open Drow Cave quest
4. **Drow Cave** (drow_cave.tmx): guard + leader + witch (12 ingredients: 6 from cave animals, 6 foraged)
5. **Spell → Lloth's Realm** (lloth_realm.tmx): Lloth gives ring, sends to Volcano
6. **Volcano** (volcano.tmx): 10 dragon types × 4 ages; adult dragon quests
7. **Ancient Dragons** (Platinum + Chromatic): gated on all 10 adult quests complete
8. **Ring activates** → map change back to Lloth; Sunny transformed into Drow Elf
9. **Ring Clearing** (ring_clearing.tmx): find Sunny's ring via search area
10. **Drow Villages + 7 Moons** (moon_*.tmx): drow quests per moon
11. **Family Reunion**: Sunny + Ozzy + Nymph → Sunny ascends → rich reward

---

### Dragon Quest Gate
\`quest_dragon_ancient_platinum\` and \`quest_dragon_ancient_chromatic\` require:
\`requiresAllQuestsComplete\` = [${DRAGON_TYPES.map(t=>`quest_dragon_${cid(t)}_adult`).join(', ')}]

---

### Astral Beasts (Pokémon System)
- 270 beasts: 9 regions × 10 base beasts × 3 evolution tiers
- 30 additional breeding beasts
- Spirit Orb catch rates: Orb I=25%, II=50%, III=75%, IV=95%
- Evolve via Scholar NPC (gold cost per tier)
- Breed via Breeder NPC (consumes both beasts, creates 1 new)
- 9 regional gyms: 12 trainers + 1 gym leader + 1 champion each
- Grand Champion after all 9 regional champions defeated
- **Prevention zones**: \`Keys_prevent_pokemon\` strips equipped beasts in real world; \`Keys_prevent_overworld\` strips real gear in game worlds

---

### Crystal Towers
12 colored towers (4 mage, 4 cleric, 4 druid), 5 levels each.
Each level: 5 progressively harder mage/cleric/druid mobs.
Crystal Grandmaster accepts all 12 crystals → Grand Crystal Staff.

---

### Ailment System
24 ailments applied by specific monsters.
Castle alchemist sells cure potions. 6 monsters per ailment drop the cure.

---

### Faction System
15 races with D&D-standard attitudes toward the player (wood elf).
Quest completion: raises own faction score, lowers rival's.
Disguises sold in faction_hall.tmx — chance to negate hostile faction attacks.

---

### Integration Checklist
1. Copy all \`.tmx\` files to your \`maps/\` directory
2. Copy all \`.json\` files to your \`content/\` directory  
3. Merge \`values/strings.xml\` entries into your app's string resources
4. Add \`values/loadresources.xml\` entries to your resource loading list
5. Tileset image files required: \`dc-dngn.png\`, \`dc-dngn-t.png\`, \`chars0.png\`, \`items.png\`

---

*Andor's Trail Extended Content Pack v3 — Generated May 2026*
`;
}

// ─────────────────────────────────────────────────────────────────────────────
// MAIN
// ─────────────────────────────────────────────────────────────────────────────
async function main() {
  console.log('=== Andor\'s Trail Content Generator v3 ===');

  // Build all content
  console.log('\n[Building content...]');
  const animalData   = buildAnimalContent();
  const forageData   = buildForageContent();
  const miningData   = buildMiningContent();
  const craftingData = buildCraftingItems();
  const guildItems   = buildGuildItems();
  const guildConvs   = buildGuildConversations();
  const factionData  = buildFactionContent();
  const questData    = buildQuestContent();
  const pokemonData  = buildPokemonContent();
  const pickpocket   = buildPickpocketSystem();
  const timekeeper   = buildTimekeeperSystem();
  const stolenData   = buildStolenItems();
  const { maps, extraConvs } = generateAllMaps();

  // Aggregate everything
  const ALL_ITEMS = [
    ...animalData.items, ...forageData.items, ...miningData.items, ...craftingData.items,
    ...guildItems.items, ...factionData.items, ...questData.items, ...pokemonData.items,
    ...pickpocket.items, ...timekeeper.items, ...stolenData.items,
  ];
  const ALL_MONSTERS = [
    ...animalData.monsters, ...questData.monsters, ...pokemonData.monsters,
    ...pickpocket.monsters, ...factionData.monsters,
  ];
  const ALL_DROPLISTS = [
    ...animalData.droplists, ...miningData.droplists, ...questData.droplists,
    ...pokemonData.droplists, ...pickpocket.droplists,
  ];
  const ALL_CONVERSATIONS = [
    ...forageData.conversations, ...miningData.conversations, ...guildConvs.conversations,
    ...factionData.conversations, ...questData.conversations, ...pokemonData.conversations,
    ...pickpocket.conversations, ...timekeeper.conversations, ...extraConvs,
  ];
  const ALL_QUESTS = [
    ...forageData.quests, ...guildConvs.quests, ...factionData.quests,
    ...questData.quests, ...pokemonData.quests, ...timekeeper.quests,
  ];
  const ALL_ACTORCONDITIONS = [
    ...guildItems.actorconditions, ...factionData.actorconditions,
    ...questData.actorconditions, ...pokemonData.actorconditions, ...timekeeper.actorconditions,
  ];

  // Deduplicate by id
  const dedup = (arr) => {
    const seen = new Set();
    return arr.filter(x=>x&&x.id&&!seen.has(x.id)&&seen.add(x.id));
  };

  const dedupedItems    = dedup(ALL_ITEMS);
  const dedupedMonsters = dedup(ALL_MONSTERS);
  const dedupedDL       = dedup(ALL_DROPLISTS);
  const dedupedConvs    = dedup(ALL_CONVERSATIONS);
  const dedupedQuests   = dedup(ALL_QUESTS);
  const dedupedACs      = dedup(ALL_ACTORCONDITIONS);

  console.log('\n[Assembling ZIP...]');

  const zipFiles = [];
  function addJson(name, obj) {
    zipFiles.push({name, data: JSON.stringify(obj, null, 2)});
  }
  function addText(name, content) {
    zipFiles.push({name, data: content});
  }

  // JSON data files
  // AT format: ALL arrays output as flat JSON arrays (no wrapper object)
  addJson('itemlist.json',          dedupedItems);
  addJson('monsterlist.json',       dedupedMonsters);
  addJson('droplists.json',         dedupedDL);
  addJson('conversationlist.json',  dedupedConvs);
  addJson('questlist.json',         dedupedQuests);
  addJson('actorconditions.json',   dedupedACs);

  // Specialised sub-files — also flat AT arrays
  //addJson('monsterlist_animals.json',   dedupedMonsters.filter(m=>m.faction==='animals'));
  //addJson('droplists_animal.json',      dedupedDL.filter(d=>d.id.startsWith('dl_animal')));
  //addJson('itemlist_forage.json',       dedupedItems.filter(i=>i.id.startsWith('forage_')));
  //addJson('itemlist_mining.json',       dedupedItems.filter(i=>i.id.startsWith('mining_')||i.id==='item_pick_axe'));
  //addJson('questlist_guild.json',       dedupedQuests.filter(q=>q.id.startsWith('quest_guild')));
  // Custom AT entity files (dragons → monsters, faction/holiday → actorconditions, pokemon → monsters)
  //addJson('dragons.json',    dedupedMonsters.filter(m=>m.monsterClass==='dragon'));
  //addJson('pokemon.json',    dedupedMonsters.filter(m=>m.monsterClass==='beast'));
  //addJson('faction.json',    dedupedACs.filter(ac=>ac.id.startsWith('faction_favor')||ac.id.startsWith('faction_hostile')||ac.id.startsWith('faction_disguise')));
  //addJson('holiday.json',    dedupedACs.filter(ac=>ac.id.startsWith('ac_holiday')||ac.id.startsWith('ac_event')));
  addJson('itemcategories_1.json', [
    {id:'scroll',          name:'Scroll',          actionType:'use'},
    {id:'potion',          name:'Potion',          actionType:'use'},
    {id:'weapon',          name:'Weapon',          actionType:'equip',   inventorySlot:'weapon'},
    {id:'shield',          name:'Shield',          actionType:'equip',   inventorySlot:'shield'},
    {id:'head',            name:'Head',            actionType:'equip',   inventorySlot:'head'},
    {id:'body',            name:'Body',            actionType:'equip',   inventorySlot:'body'},
    {id:'hand',            name:'Hand',            actionType:'equip',   inventorySlot:'hand'},
    {id:'feet',            name:'Feet',            actionType:'equip',   inventorySlot:'feet'},
    {id:'necklace',        name:'Necklace',        actionType:'equip',   inventorySlot:'neck'},
    {id:'key',             name:'Key',             actionType:'use'},
    {id:'ingredient',      name:'Ingredient',      actionType:'use'},
    {id:'miscellaneous',   name:'Miscellaneous',   actionType:'none'},
    {id:'quest',           name:'Quest',           actionType:'none'},
    {id:'bag',             name:'Bag',             actionType:'use'},
    {id:'deed',            name:'Deed',            actionType:'use'},
    {id:'manual',          name:'Manual',          actionType:'use'},
    {id:'orb',             name:'Orb',             actionType:'use'},
    {id:'beastOrb',        name:'BeastOrb',        actionType:'use'},
    {id:'seed',            name:'Seed',            actionType:'use'},
    {id:'produce',         name:'Produce',         actionType:'use'},
    {id:'crystal',         name:'Crystal',         actionType:'use'},
  ]);

  // TMX maps
  const tmxFileNames = [];
  for (const {path:p, tmx} of maps) {
    addText(p, tmx);
    tmxFileNames.push(p);
    console.log('  tmx:', p);
  }

  // XML resources
  const jsonFileNames = zipFiles.filter(f=>f.name.endsWith('.json')).map(f=>f.name);
  addText('values/strings.xml', buildStringsXml());
  addText('values/loadresources.xml', buildLoadResourcesXml(jsonFileNames, tmxFileNames));

  // README
  const stringCount = Object.keys(STRINGS).length;
  addText('README.md', buildReadme(tmxFileNames, jsonFileNames, stringCount));

  // Build ZIP
  const zipBuf = buildZip(zipFiles);
  fs.writeFileSync(path.join(__dirname,'../andors_trail_content_v3.zip'), zipBuf);

  console.log('\n=== COMPLETE ===');
  console.log(`  TMX maps:       ${tmxFileNames.length}`);
  console.log(`  JSON files:     ${jsonFileNames.length}`);
  console.log(`  Items:          ${dedupedItems.length}`);
  console.log(`  Monsters/NPCs:  ${dedupedMonsters.length}`);
  console.log(`  Conversations:  ${dedupedConvs.length}`);
  console.log(`  Quests:         ${dedupedQuests.length}`);
  console.log(`  String entries: ${stringCount}`);
  console.log(`  ZIP size:       ${(zipBuf.length/1024).toFixed(0)}KB`);
  console.log(`  Output:         andors_trail_content_v3.zip`);
}

main().catch(err=>{ console.error(err); process.exit(1); });
