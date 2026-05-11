/**
 * Andor's Trail Content Generator v7
 *
 * FORMAT COMPLIANCE (per https://github.com/jmlucas31070-dev/jasias-quest/ContentFormatReference/):
 *
 *  ITEMS        — name/description are plain text strings in JSON (never @string/...)
 *                 displaytype:"quest" replaces isQuestItem:1
 *                 equipment stats go in equipEffect{}, no weight/charges/equipmentSlot fields
 *                 iconID format: "spritesheetname:linearIndex" (0-based, left→right)
 *
 *  MONSTERS     — name is plain text; stats are top-level fields (not nested under "stats")
 *                 attackDamage:{min,max} replaces damagePotential
 *
 *  CONVERSATIONS — message is plain text; replies use {text, nextPhraseID, requires[]}
 *                  rewards use AT rewardType/rewardID/value schema; no @string/ refs
 *
 *  QUESTS       — name and stages[].logText are plain text strings
 *
 *  ACTOR CONDS  — name is plain text; category is required ("spiritual"|"mental"|"physical"|"blood")
 *
 *  DROPLISTS    — chance is a string (e.g. "100"), not a number
 *
 *  strings.xml  — NOT used for game-content strings; removed from output
 *
 *  TMX MAPS     — unchanged from v3 (already correct AT 1.8.4 format)
 *
 * v7 CHANGES:
 *  - *_jasia.json files are now split by content category:
 *    _animal, _forage, _mining, _crafting, _pickpocket, _holiday,
 *    _beast, _faction, _guild, _door, _bank, _jail, _crafting,
 *    _steal, _lpc — all else stays in _jasia.json
 *  - loadresources.xml uses pattern-based matching for all split files
 *  - README updated to reflect new file structure
 */

import fs   from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const OUT_DIR   = path.join(__dirname, '../../andors_trail_content');

// ─── FILE HELPERS ────────────────────────────────────────────────────────────
function mkdirp(p) { fs.mkdirSync(p, { recursive: true }); }
function writeFile(p, content) {
  mkdirp(path.dirname(p));
  if (typeof content === 'string') fs.writeFileSync(p, content, 'utf8');
  else fs.writeFileSync(p, content);
  console.log('  wrote', path.relative(OUT_DIR, p));
}
function writeJson(p, obj) { writeFile(p, JSON.stringify(obj, null, 2)); }

// ─── ZIP BUILDER (pure Node.js) ──────────────────────────────────────────────
function crc32(buf) {
  let c = 0xFFFFFFFF;
  for (const b of buf) { c ^= b; for (let i=0;i<8;i++) c=(c>>>1)^(c&1?0xEDB88320:0); }
  return (c^0xFFFFFFFF)>>>0;
}
function buildZip(files) {
  const localParts = [], centralParts = [];
  let offset = 0;
  const dosDate = new Date(2026,4,11);
  const dosTime = ((10)<<11)|((0)<<5)|(0>>1);
  const dosDateVal = ((dosDate.getFullYear()-1980)<<9)|((dosDate.getMonth()+1)<<5)|(dosDate.getDate());
  for (const file of files) {
    const rawData  = typeof file.data==='string' ? Buffer.from(file.data,'utf8') : file.data;
    const compressed = zlib.deflateRawSync(rawData, {level:6});
    const crc = crc32(rawData);
    const nameBuf = Buffer.from(file.name,'utf8');
    const lh = Buffer.allocUnsafe(30+nameBuf.length);
    lh.writeUInt32LE(0x04034B50,0); lh.writeUInt16LE(20,4); lh.writeUInt16LE(0,6);
    lh.writeUInt16LE(8,8); lh.writeUInt16LE(dosTime,10); lh.writeUInt16LE(dosDateVal,12);
    lh.writeUInt32LE(crc,14); lh.writeUInt32LE(compressed.length,18);
    lh.writeUInt32LE(rawData.length,22); lh.writeUInt16LE(nameBuf.length,26);
    lh.writeUInt16LE(0,28); nameBuf.copy(lh,30);
    const cd = Buffer.allocUnsafe(46+nameBuf.length);
    cd.writeUInt32LE(0x02014B50,0); cd.writeUInt16LE(20,4); cd.writeUInt16LE(20,6);
    cd.writeUInt16LE(0,8); cd.writeUInt16LE(8,10); cd.writeUInt16LE(dosTime,12);
    cd.writeUInt16LE(dosDateVal,14); cd.writeUInt32LE(crc,16);
    cd.writeUInt32LE(compressed.length,20); cd.writeUInt32LE(rawData.length,24);
    cd.writeUInt16LE(nameBuf.length,28); cd.writeUInt16LE(0,30); cd.writeUInt16LE(0,32);
    cd.writeUInt16LE(0,34); cd.writeUInt16LE(0,36); cd.writeUInt32LE(0,38);
    cd.writeUInt32LE(offset,42); nameBuf.copy(cd,46);
    localParts.push(lh, compressed); centralParts.push(cd);
    offset += lh.length + compressed.length;
  }
  const centralBuf = Buffer.concat(centralParts);
  const eocd = Buffer.allocUnsafe(22);
  eocd.writeUInt32LE(0x06054B50,0); eocd.writeUInt16LE(0,4); eocd.writeUInt16LE(0,6);
  eocd.writeUInt16LE(files.length,8); eocd.writeUInt16LE(files.length,10);
  eocd.writeUInt32LE(centralBuf.length,12); eocd.writeUInt32LE(offset,16);
  eocd.writeUInt16LE(0,20);
  return Buffer.concat([...localParts, centralBuf, eocd]);
}

// ─── TMX / TILE HELPERS ──────────────────────────────────────────────────────
const AT_TILESETS = [
  ['map_bed_1',1,128,16,512,256],['map_border_1',129,128,16,512,256],
  ['map_bridge_1',257,128,16,512,256],['map_bridge_2',385,128,16,512,256],
  ['map_broken_1',513,128,16,512,256],['map_cavewall_1',641,108,18,576,192],
  ['map_cavewall_2',749,108,18,576,192],['map_cavewall_3',857,108,18,576,192],
  ['map_cavewall_4',965,108,18,576,192],['map_chair_table_1',1073,128,16,512,256],
  ['map_chair_table_2',1201,128,16,512,256],['map_crate_1',1329,128,16,512,256],
  ['map_cupboard_1',1457,128,16,512,256],['map_curtain_1',1585,128,16,512,256],
  ['map_entrance_1',1713,128,16,512,256],['map_entrance_2',1841,128,16,512,256],
  ['map_fence_1',1969,128,16,512,256],['map_fence_2',2097,128,16,512,256],
  ['map_fence_3',2225,128,16,512,256],['map_fence_4',2353,128,16,512,256],
  ['map_ground_1',2481,128,16,512,256],['map_ground_2',2609,128,16,512,256],
  ['map_ground_3',2737,128,16,512,256],['map_ground_4',2865,128,16,512,256],
  ['map_ground_5',2993,128,16,512,256],['map_ground_6',3121,128,16,512,256],
  ['map_ground_7',3249,128,16,512,256],['map_ground_8',3377,128,16,512,256],
  ['map_house_1',3505,128,16,512,256],['map_house_2',3633,128,16,512,256],
  ['map_indoor_1',3761,128,16,512,256],['map_indoor_2',3889,128,16,512,256],
  ['map_kitchen_1',4017,128,16,512,256],['map_outdoor_1',4145,128,16,512,256],
  ['map_pillar_1',4273,128,16,512,256],['map_pillar_2',4401,128,16,512,256],
  ['map_plant_1',4529,128,16,512,256],['map_plant_2',4657,128,16,512,256],
  ['map_rock_1',4785,128,16,512,256],['map_rock_2',4913,128,16,512,256],
  ['map_roof_1',5041,128,16,512,256],['map_roof_2',5169,128,16,512,256],
  ['map_roof_3',5297,128,16,512,256],['map_shop_1',5425,128,16,512,256],
  ['map_sign_ladder_1',5553,128,16,512,256],['map_table_1',5681,128,16,512,256],
  ['map_trail_1',5809,128,16,512,256],['map_transition_1',5937,128,16,512,256],
  ['map_transition_2',6065,128,16,512,256],['map_transition_3',6193,128,16,512,256],
  ['map_transition_4',6321,128,16,512,256],['map_tree_1',6449,128,16,512,256],
  ['map_tree_2',6577,128,16,512,256],['map_wall_1',6705,128,16,512,256],
  ['map_wall_2',6833,120,15,480,256],['map_wall_3',6953,120,15,480,256],
  ['map_wall_4',7073,120,15,480,256],['map_window_1',7193,128,16,512,256],
  ['map_window_2',7321,128,16,512,256],['map_transition_5',7449,128,16,512,256],
].map(([name,firstgid,tilecount,columns,imgW,imgH])=>({name,firstgid,tilecount,columns,imgW,imgH}));

function tilesetXML(ts) {
  return ` <tileset firstgid="${ts.firstgid}" name="${ts.name}" tilewidth="32" tileheight="32"` +
    ` tilecount="${ts.tilecount}" columns="${ts.columns}">\n` +
    `  <image source="../drawable/${ts.name}.png" width="${ts.imgW}" height="${ts.imgH}"/>\n` +
    ` </tileset>`;
}
function blankTileData(width, height) {
  return zlib.deflateSync(Buffer.alloc(width*height*4)).toString('base64');
}
function xmlEsc(s) {
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}
function tileLayerXML(id, name, width, height, visible=true) {
  const vis = visible ? '' : ' visible="0"';
  return ` <layer id="${id}" name="${name}" width="${width}" height="${height}"${vis}>\n` +
    `  <data encoding="base64" compression="zlib">\n   ${blankTileData(width,height)}\n  </data>\n </layer>`;
}
let _objId = 1;
function objectgroupXML(id, name, objects=[], visible=true) {
  const vis = visible ? '' : ' visible="0"';
  if (!objects.length) return ` <objectgroup id="${id}" name="${name}"${vis}/>`;
  return ` <objectgroup id="${id}" name="${name}"${vis}>\n${objects.map(buildObject).join('\n')}\n </objectgroup>`;
}
function buildObject(obj) {
  const id = _objId++;
  const {name='',type='',x=32,y=32,width=32,height=32,properties=[]} = obj;
  const propsXml = properties.length
    ? '\n   <properties>\n'+properties.map(p=>`    <property name="${xmlEsc(p.name)}" value="${xmlEsc(String(p.value))}"/>`).join('\n')+'\n   </properties>'
    : '';
  return `  <object id="${id}" name="${xmlEsc(name)}" type="${xmlEsc(type)}" x="${x}" y="${y}" width="${width}" height="${height}">${propsXml}\n  </object>`;
}
function buildTMX({width=30,height=30,spawnObjects=[],keyObjects=[],replaceObjects=[],mapEventObjects=[]}) {
  _objId = 1;
  const nextLayerId = 13;
  const nextObjId = Math.max(1,spawnObjects.length+keyObjects.length+replaceObjects.length+mapEventObjects.length)+1;
  const tilesetXmls = AT_TILESETS.map(tilesetXML).join('\n');
  const tileLayers = [
    tileLayerXML(1,'Base',width,height),tileLayerXML(2,'Ground',width,height),
    tileLayerXML(3,'Objects',width,height),tileLayerXML(4,'Objects_replace',width,height),
    tileLayerXML(5,'Above',width,height),tileLayerXML(6,'Above_replace',width,height),
    tileLayerXML(7,'Top',width,height),tileLayerXML(8,'Walkable',width,height,false),
  ].join('\n');
  const objGroups = [
    objectgroupXML(9,'Mapevents',mapEventObjects,false),
    objectgroupXML(10,'Spawn',spawnObjects,true),
    objectgroupXML(11,'Keys',keyObjects,false),
    objectgroupXML(12,'Replace',replaceObjects,false),
  ].join('\n');
  return `<?xml version="1.0" encoding="UTF-8"?>\n<map version="1.8" tiledversion="1.8.4" orientation="orthogonal" renderorder="right-down"` +
    ` width="${width}" height="${height}" tilewidth="32" tileheight="32"` +
    ` infinite="0" nextlayerid="${nextLayerId}" nextobjectid="${nextObjId}">\n${tilesetXmls}\n${tileLayers}\n${objGroups}\n</map>`;
}

// ─── MAP OBJECT BUILDERS ─────────────────────────────────────────────────────
function makeSpawnObj(spawngroup, x, y, wOrProps=32, h=32, quantity=null, extraProps=[]) {
  let w=32, addProps=[];
  if (Array.isArray(wOrProps)) { addProps=wOrProps; } else { w=wOrProps; addProps=extraProps; }
  const props = [{name:'spawngroup',value:spawngroup}];
  if (quantity!=null) props.push({name:'quantity',value:String(quantity)});
  props.push(...addProps);
  return {name:spawngroup,type:'spawn',x,y,width:w,height:h,properties:props};
}
function makeNPCObj(actorId, phrase, x, y, extraProps=[]) {
  return {name:actorId,type:'spawn',x,y,width:32,height:32,
    properties:[{name:'spawngroup',value:actorId},{name:'phrase',value:phrase},...extraProps]};
}
function makeKeyObj(keyName, phrase, x, y, extraProps=[]) {
  return {name:keyName,type:'key',x,y,width:32,height:32,
    properties:[{name:'phrase',value:phrase},...extraProps]};
}
function makeSignObj(keyName, x, y, signText) {
  return {name:keyName,type:'key',x,y,width:32,height:32,
    properties:[{name:'phrase',value:'sign'},{name:'text',value:signText}]};
}
function makeMapchangeObj(name, targetMap, targetPlace, x, y, w=32, h=32) {
  return {name,type:'mapchange',x,y,width:w,height:h,
    properties:[{name:'map',value:targetMap},{name:'place',value:targetPlace}]};
}
function makeReplaceObj(name, x, y, layerMap={}, extraProps=[]) {
  const props = Object.entries(layerMap).map(([k,v])=>({name:k,value:v}));
  return {name,type:'replace',x,y,width:32,height:32,properties:[...props,...extraProps]};
}

// ─── MASTER DATA ─────────────────────────────────────────────────────────────
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
  {id:'new_years',    name:"New Year's",    monthDay:'01-01',weeksBefore:1,weeksAfter:1,theme:'festive'},
  {id:'easter',       name:'Easter',        monthDay:'04-09',weeksBefore:1,weeksAfter:1,theme:'spring'},
  {id:'fourth_july',  name:'Fourth of July',monthDay:'07-04',weeksBefore:1,weeksAfter:1,theme:'patriotic'},
  {id:'halloween',    name:'Halloween',     monthDay:'10-31',weeksBefore:1,weeksAfter:1,theme:'spooky'},
  {id:'thanksgiving', name:'Thanksgiving',  monthDay:'11-23',weeksBefore:1,weeksAfter:1,theme:'harvest'},
  {id:'christmas',    name:'Christmas',     monthDay:'12-25',weeksBefore:1,weeksAfter:1,theme:'winter'},
];
const EVENTS = ['birthday','graduation','wedding','funeral'];
const POKEMON_REGIONS = ['meadow','forest','mountain','ocean','volcanic','arctic','swamp','sky','shadow'];
const MOON_COLORS = ['Red','Orange','Yellow','Green','Blue','Indigo','Violet'];

// ─── CONTENT HELPERS ─────────────────────────────────────────────────────────
function cap(s) { return s.charAt(0).toUpperCase()+s.slice(1); }
function cid(s) { return s.replace(/[\s\-\/\(\)]+/g,'_').toLowerCase(); }
function range(n) { return Array.from({length:n},(_,i)=>i); }

function iconID(sheet, row, col, cols=16) {
  return `${sheet}:${(1)*(1)}`;
}

// ─── AT REWARD HELPERS ───────────────────────────────────────────────────────
function rQuestProgress(questID, progress) { return {rewardType:'questProgress',rewardID:questID,value:progress}; }
function rGiveItem(itemID, qty=1) { return {rewardType:'giveItem',rewardID:itemID,value:qty}; }
function rDropList(dlID) { return {rewardType:'dropList',rewardID:dlID}; }
function rActorCond(acID, duration=999) { return {rewardType:'actorCondition',rewardID:acID,value:duration}; }
function rActorCondClear(acID) { return {rewardType:'actorCondition',rewardID:acID,value:-99}; }
function rAlignChange(factionID, amount) { return {rewardType:'alignmentChange',rewardID:factionID,value:amount}; }
function rTimer(timerID) { return {rewardType:'createTimer',rewardID:timerID}; }

// ─── AT REQUIREMENT HELPERS ──────────────────────────────────────────────────
function reqInvRemove(itemID, qty=1) { return {requireType:'inventoryRemove',requireID:itemID,value:qty}; }
function reqInvKeep(itemID, qty=1) { return {requireType:'inventoryKeep',requireID:itemID,value:qty}; }
function reqQuestProgress(questID, progress) { return {requireType:'questProgress',requireID:questID,value:progress}; }
function reqQuestLatest(questID, progress) { return {requireType:'questLatestProgress',requireID:questID,value:progress}; }
function reqActorCond(acID) { return {requireType:'hasActorCondition',requireID:acID}; }
function reqNotActorCond(acID) { return {requireType:'hasActorCondition',requireID:acID,negate:true}; }
function reqKilled(npcID, count=1) { return {requireType:'killedMonster',requireID:npcID,value:count}; }
function reqFaction(factionID, score) { return {requireType:'factionScore',requireID:factionID,value:score}; }
function reqTimer(timerID, rounds) { return {requireType:'timerElapsed',requireID:timerID,value:rounds}; }

// ─── CORE DATA BUILDERS ──────────────────────────────────────────────────────
function makeItem({
  id, name, description='',
  iconSheet='items_necklaces_1', iconRow=1, iconCol=1,
  displaytype='ordinary', hasManualPrice=false, baseMarketCost=10,
  category=null, equipEffect=null, useEffect=null, hitEffect=null, killEffect=null
}) {
  const item = {
    id,
    name,
    iconID: iconID(iconSheet, iconRow, iconCol),
  };
  if (description) item.description = description;
  if (displaytype && displaytype !== 'ordinary') item.displaytype = displaytype;
  if (hasManualPrice) {
    item.hasManualPrice = 1;
    item.baseMarketCost = baseMarketCost;
  } else if (baseMarketCost) {
    item.baseMarketCost = baseMarketCost;
  }
  if (category) item.category = category;
  if (equipEffect && Object.keys(equipEffect).length > 0) item.equipEffect = equipEffect;
  if (useEffect) item.useEffect = useEffect;
  if (hitEffect) item.hitEffect = hitEffect;
  if (killEffect) item.killEffect = killEffect;
  return item;
}

function makeMonster({
  id, name,
  iconSheet='monsters_newb_1', iconRow=1, iconCol=1,
  maxHP=10, maxAP=10, moveCost=10, attackCost=10,
  attackChance=80, dmgMin=1, dmgMax=3,
  criticalSkill=2, criticalMultiplier=2.0,
  blockChance=0, damageResistance=0,
  droplistID=null, faction='monsters', spawnGroup=null,
  monsterClass=null, phraseID=null, unique=0,
  movementAggressionType=null, hitEffect=null
}) {
  const m = {
    id,
    name,
    iconID: iconID(iconSheet, iconRow, iconCol),
    maxHP,
    maxAP,
    moveCost,
    attackCost,
    attackChance,
    attackDamage: {min: dmgMin, max: dmgMax},
  };
  if (criticalSkill) m.criticalSkill = criticalSkill;
  if (criticalMultiplier) m.criticalMultiplier = criticalMultiplier;
  if (blockChance) m.blockChance = blockChance;
  if (damageResistance) m.damageResistance = damageResistance;
  if (monsterClass) m.monsterClass = monsterClass;
  if (movementAggressionType) m.movementAggressionType = movementAggressionType;
  if (unique) m.unique = 1;
  m.faction = faction;
  m.spawnGroup = spawnGroup || faction;
  if (droplistID) m.droplistID = droplistID;
  if (phraseID) m.phraseID = phraseID;
  if (hitEffect) m.hitEffect = hitEffect;
  return m;
}

function makeDroplist(id, items) {
  return {
    id,
    items: items.map(it => {
      const itemID  = typeof it==='string' ? it : it.id;
      const chance  = typeof it==='object' && it.chance!=null ? it.chance : 50;
      const qty     = typeof it==='object' && it.qty ? it.qty : [1,1];
      return {
        itemID,
        chance: String(chance),
        quantity: {min: qty[0], max: qty[1]??qty[0]}
      };
    })
  };
}

function makeConversation(id, message, replies=[], rewards=[]) {
  const atReplies = replies.map(r => {
    const reply = {
      text: r.text,
      nextPhraseID: r.nextPhraseID || r.next || 'X'
    };
    if (r.requires && r.requires.length > 0) reply.requires = r.requires;
    return reply;
  });
  const obj = {id, replies: atReplies};
  if (message) obj.message = message;
  if (rewards.length > 0) obj.rewards = rewards;
  return obj;
}

function makeQuest(id, name, stages, showInLog=1) {
  return {
    id,
    name,
    showInLog,
    stages: stages.map((s, i) => {
      const st = {
        progress: (i+1)*10,
        logText: typeof s==='string' ? s : (s.logText || s.desc || `Stage ${i+1}.`)
      };
      if (s.rewardExperience || s.exp) st.rewardExperience = s.rewardExperience || s.exp;
      if (s.finishesQuest || i===stages.length-1) st.finishesQuest = 1;
      return st;
    })
  };
}

function makeActorCondition({
  id, name,
  category='physical',
  isPositive=false, isStacking=false,
  iconSheet='actorconditions_1', iconRow=1, iconCol=1,
  roundEffect=null, fullRoundEffect=null, abilityEffect=null
}) {
  const ac = {
    id,
    name,
    iconID: iconID(iconSheet, iconRow, iconCol),
    category
  };
  if (isPositive) ac.isPositive = 1;
  if (isStacking) ac.isStacking = 1;
  if (roundEffect) ac.roundEffect = roundEffect;
  if (fullRoundEffect) ac.fullRoundEffect = fullRoundEffect;
  if (abilityEffect && Object.keys(abilityEffect).length > 0) ac.abilityEffect = abilityEffect;
  return ac;
}

// ─── PICKPOCKET SYSTEM ───────────────────────────────────────────────────────
function buildPickpocketSystem() {
  const items=[], monsters=[], droplists=[], conversations=[];

  const PICKPOCKET_GOLD = [30,50,75,110,150,200,275,360,460,600];

  const KILL_GOLD_ITEMS = range(19).map(g => {
    const id = `gold_coins_${g+1}`;
    items.push(makeItem({
      id, name: `${g+1} Gold Coin${g?'s':''}`,
      description: `A pouch of ${g+1} gold coin${g?'s':''}.`,
      iconSheet:'items_necklaces_1', iconRow:2, iconCol:1+(g%8),
      baseMarketCost: g+1,
      category: 'miscellaneous'
    }));
    return id;
  });

  const PICKPOCKET_BAGS = PICKPOCKET_GOLD.map((gold, lvl) => {
    const id = `pickpocket_gold_lvl${lvl+1}`;
    items.push(makeItem({
      id, name: `Stolen coin purse (${gold}g)`,
      description: `A stolen purse containing approximately ${gold} gold pieces.`,
      iconSheet:'items_necklaces_1', iconRow:2, iconCol:1+(lvl%8),
      hasManualPrice: true, baseMarketCost: 0,
      category: 'miscellaneous'
    }));
    return id;
  });

  const killDL = makeDroplist('dl_pickpocket_kill_gold',
    KILL_GOLD_ITEMS.map((id,i)=>({id, chance: Math.floor(100/(i+2))+5, qty:[1,1]})));
  droplists.push(killDL);

  range(200).forEach(i => {
    const levelBag = PICKPOCKET_BAGS[Math.min(i%10, PICKPOCKET_BAGS.length-1)];
    droplists.push(makeDroplist(`dl_pickpocket_target_${i}`, [{id:levelBag, chance:100, qty:[1,1]}]));
  });

  conversations.push(makeConversation(
    'conv_pickpocket_action',
    'This person looks like they might have some coin on them.',
    [
      {text:'Pickpocket (50% success)',nextPhraseID:'X',requires:[reqFaction('thief',1)]},
      {text:'Pickpocket + Sneak (75% success)',nextPhraseID:'X',requires:[reqFaction('thief',6)]},
      {text:'Pickpocket + Hide (90% success)',nextPhraseID:'X',requires:[reqFaction('thief',9)]},
      {text:'Fight',nextPhraseID:'F'},
      {text:'Leave',nextPhraseID:'X'},
    ]
  ));

  conversations.push(makeConversation(
    'conv_caught_pickpocket',
    "You've been caught! The guards drag you to jail.",
    [{text:'...fine.', nextPhraseID:'X'}]
  ));

  const npcNames = ['Merchant','Farmer','Traveler','Noble','Scholar','Artisan',
    'Guard off duty','Priest','Sailor','Baker','Miller','Tailor',
    'Butcher','Potter','Weaver','Tanner','Mason','Carpenter','Smith','Cooper'];
  range(200).forEach(i => {
    monsters.push(makeMonster({
      id: `npc_pickpocket_${i}`,
      name: `${npcNames[i%npcNames.length]} ${Math.floor(i/npcNames.length)+1}`,
      iconSheet:'monsters_newb_1', iconRow:1, iconCol:1+(i%8),
      maxHP: 20+Math.floor(i/20)*5, maxAP:10, moveCost:10, attackCost:10,
      attackChance:50, dmgMin:1, dmgMax:3+Math.floor(i/50),
      droplistID:'dl_pickpocket_kill_gold',
      faction:'townsfolk', spawnGroup:'townsfolk_pickpocket',
      phraseID:'conv_pickpocket_action'
    }));
  });

  return {items, monsters, droplists, conversations};
}

// ─── TIMEKEEPER / HOLIDAY SYSTEM ─────────────────────────────────────────────
function buildTimekeeperSystem() {
  const items=[], conversations=[], quests=[], actorconditions=[];

  const holidayThemeGifts = {
    new_years:    ["Party horn","Confetti bag","Sparkler","Champagne","New Year's hat","Countdown clock"],
    easter:       ['Painted egg','Chocolate bunny','Spring flower','Easter basket','Jelly beans','Marshmallow chick'],
    fourth_july:  ['Firecracker','Flag pin','Star badge','Liberty hat','Patriot ribbon','Eagle feather'],
    halloween:    ['Carved pumpkin','Candy corn','Skull mask','Witch hat','Spider web','Ghost cloth'],
    thanksgiving: ['Turkey leg','Pumpkin pie','Harvest wreath','Cornucopia','Cranberry sauce','Pilgrim hat'],
    christmas:    ['Ornament','Candy cane','Stocking','Wrapping paper','Christmas star','Snow globe'],
  };
  const holidayGoodGifts = {
    new_years:    ['Golden noisemaker','Silver flute','Enchanted confetti','Luck charm','Year amulet','Fortune ring'],
    easter:       ['Magic egg','Bunny charm','Spring bloom amulet','Renewal crystal','Life seed','Rebirth stone'],
    fourth_july:  ['Liberty sword','Freedom shield','Star gem','Eagle amulet',"Patriot's ring",'Valor crest'],
    halloween:    ['Soul lantern',"Witch's brew",'Shadow cloak','Phantom ring','Ghost blade','Spirit stone'],
    thanksgiving: ['Horn of plenty','Harvest blade','Autumn amulet','Cornucopia ring','Feast charm','Bounty gem'],
    christmas:    ['Starlight staff','Gift of strength','Holiday crystal','Snowflake amulet','Yule blade','Winter ring'],
  };

  HOLIDAYS.forEach((h, hi) => {
    items.push(makeItem({
      id: `holiday_gold_${h.id}`,
      name: `${h.name} gold pouch`,
      description: `A holiday gold pouch for ${h.name}. Collect one daily from the Timekeeper.`,
      iconSheet:'items_necklaces_1', iconRow:9, iconCol:1+hi,
      baseMarketCost: 0, category:'miscellaneous'
    }));
    holidayThemeGifts[h.id].forEach((name, i) => {
      items.push(makeItem({
        id: `holiday_gift_${h.id}_${i}`, name,
        description: `A ${h.name} gift: ${name}.`,
        iconSheet:'items_necklaces_1', iconRow:10+hi, iconCol:1+i,
        baseMarketCost: 0, category:'miscellaneous'
      }));
    });
    holidayGoodGifts[h.id].forEach((name, i) => {
      items.push(makeItem({
        id: `holiday_gift_good_${h.id}_${i}`, name,
        description: `Premium ${h.name} reward for completing the holiday quest.`,
        iconSheet:'items_necklaces_1', iconRow:16+hi, iconCol:1+i,
        baseMarketCost: 0, category:'miscellaneous'
      }));
    });

    quests.push(makeQuest(`quest_holiday_${h.id}`, `${h.name} celebration`, [
      {logText:`Speak with the Timekeeper to learn about ${h.name}.`, exp:100+hi*25},
      {logText:`Collect three ${h.name} ingredients from the world.`, exp:150+hi*30},
      {logText:`Complete a special ${h.name} challenge.`, exp:200+hi*40},
      {logText:`Return to the Timekeeper to celebrate ${h.name}!`, exp:300+hi*50},
    ]));

    actorconditions.push(makeActorCondition({
      id:`ac_holiday_active_${h.id}`, name:`${h.name} is active`,
      category:'spiritual', isPositive:true,
      iconSheet:'actorconditions_1', iconRow:1, iconCol:1+hi
    }));
    actorconditions.push(makeActorCondition({
      id:`ac_holiday_quest_done_${h.id}`, name:`${h.name} quest complete`,
      category:'spiritual', isPositive:true,
      iconSheet:'actorconditions_1', iconRow:2, iconCol:1+hi
    }));
    actorconditions.push(makeActorCondition({
      id:`ac_holiday_gift_given_${h.id}`, name:`${h.name} daily gift given`,
      category:'spiritual', isPositive:false,
      iconSheet:'actorconditions_1', iconRow:3, iconCol:1+hi
    }));
  });

  const eventThemeGifts = {
    birthday:   ['Birthday cake','Party hat','Balloon','Candle','Gift bow','Birthday card'],
    graduation: ['Diploma','Cap and gown token',"Scholar's pen",'Wisdom stone','Victory wreath','Achievement medal'],
    wedding:    ['Wedding ring','Bouquet','Veil charm','Unity candle','Love token','Celebration ribbon'],
    funeral:    ['Memorial flower','Remembrance candle','Mourning veil','Tribute stone','Elegy scroll','Rest in peace token'],
  };
  EVENTS.forEach((event, ei) => {
    eventThemeGifts[event].forEach((name, i) => {
      items.push(makeItem({
        id:`event_gift_${event}_${i}`, name,
        description:`A ${event} gift: ${name}.`,
        iconSheet:'items_necklaces_1', iconRow:22+ei, iconCol:1+i,
        baseMarketCost:0, category:'miscellaneous'
      }));
    });
    actorconditions.push(makeActorCondition({
      id:`ac_event_active_${event}`, name:`${cap(event)} event active`,
      category:'spiritual', isPositive:true,
      iconSheet:'actorconditions_1', iconRow:4, iconCol:1+ei
    }));
  });

  items.push(makeItem({
    id:'item_time_crystal', name:'Time crystal',
    description:'A crystal attuned to the flow of time. Carry it for one week for the Timekeeper.',
    displaytype:'quest',
    iconSheet:'items_necklaces_1', iconRow:26, iconCol:1,
    hasManualPrice:true, baseMarketCost:0, category:'quest'
  }));

  const holidayReplies = HOLIDAYS.flatMap((h,hi) => [
    {text:`Happy ${h.name}! Claim your daily gift.`,
     nextPhraseID:`conv_timekeeper_gift_${h.id}`,
     requires:[reqActorCond(`ac_holiday_active_${h.id}`), reqNotActorCond(`ac_holiday_gift_given_${h.id}`)]},
    {text:`Accept the ${h.name} quest.`,
     nextPhraseID:`conv_timekeeper_hquest_${h.id}`,
     requires:[reqActorCond(`ac_holiday_active_${h.id}`), reqNotActorCond(`ac_holiday_quest_done_${h.id}`)]},
  ]);

  conversations.push(makeConversation(
    'conv_timekeeper',
    'I am the Timekeeper. I watch the flow of days and manage the great festivals.',
    [
      ...holidayReplies,
      {text:"Accept the Timekeeper's time crystal quest.",
       nextPhraseID:'conv_timekeeper_crystal_start',
       requires:[reqNotActorCond('ac_timekeeper_crystal_given')]},
      {text:'Return the time crystal.',
       nextPhraseID:'conv_timekeeper_crystal_done',
       requires:[reqInvKeep('item_time_crystal',1), reqActorCond('ac_timekeeper_crystal_given')]},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));

  conversations.push(makeConversation(
    'conv_timekeeper_crystal_start',
    'Carry this crystal for seven days without losing it and I shall reward you greatly.',
    [{text:'Accept', nextPhraseID:'X'}],
    [rGiveItem('item_time_crystal'), rActorCond('ac_timekeeper_crystal_given'), rQuestProgress('quest_timekeeper_crystal',10)]
  ));

  conversations.push(makeConversation(
    'conv_timekeeper_crystal_done',
    'You have done it! Seven days with the crystal. Here is your reward.',
    [{text:'Thank you!', nextPhraseID:'X'}],
    [rQuestProgress('quest_timekeeper_crystal',20)]
  ));
  conversations[conversations.length-1].replies[0].requires = [reqInvRemove('item_time_crystal',1)];

  HOLIDAYS.forEach((h,hi) => {
    conversations.push(makeConversation(
      `conv_timekeeper_gift_${h.id}`,
      `Here is your ${h.name} gift! Come back tomorrow for another.`,
      [{text:'Thank you!', nextPhraseID:'X'}],
      [rGiveItem(`holiday_gold_${h.id}`), rActorCond(`ac_holiday_gift_given_${h.id}`,1440)]
    ));
    conversations.push(makeConversation(
      `conv_timekeeper_hquest_${h.id}`,
      `The ${h.name} celebration needs your help! Will you assist?`,
      [
        {text:'Yes, I will help!', nextPhraseID:'X'},
        {text:'Maybe later.', nextPhraseID:'X'},
      ],
      [rQuestProgress(`quest_holiday_${h.id}`,10)]
    ));
  });

  EVENTS.forEach((event, ei) => {
    conversations.push(makeConversation(
      `conv_event_planner_${event}`,
      `I can arrange a ${event} celebration! It will last 24 hours and transform this area.`,
      [
        {text:`Arrange ${event} (500 gold)`, nextPhraseID:'X',
         requires:[reqActorCond(`ac_event_paid_${event}`)]},
        {text:'Leave', nextPhraseID:'X'},
      ],
      [rActorCond(`ac_event_active_${event}`,1440)]
    ));
    conversations.push(makeConversation(
      `conv_event_npc_${event}`,
      `Congratulations on your ${event}! Here is a gift from all of us.`,
      [{text:'Thank you!', nextPhraseID:'X'}],
      [rGiveItem(`event_gift_${event}_0`)]
    ));
  });

  quests.push(makeQuest('quest_timekeeper_crystal', "Keeper of time", [
    {logText:'Carry the time crystal for 7 days without losing it.', exp:1000},
    {logText:'Return the crystal to the Timekeeper for your reward.', exp:2000},
  ]));

  return {items, conversations, quests, actorconditions};
}

// ─── ANIMAL / FORAGE / MINING CONTENT ────────────────────────────────────────
const REGION_ANIMAL_NAMES = {
  grassland:['Deer','Rabbit','Fox','Wolf','Hawk','Boar','Badger','Hare','Elk','Bison','Pheasant','Vole','Mole','Sparrow','Falcon','Weasel','Otter','Hedgehog','Squirrel','Crow','Magpie','Frog','Toad','Snake','Lizard'],
  shrubland:['Scrub jay','Roadrunner','Jackrabbit','Coyote','Ground squirrel','Horned lizard','Gila woodpecker','Burrowing owl','Diamondback','Gopher snake','Collared lizard','Scaled quail','Kit fox','Antelope','Pronghorn','Rock wren','Sage grouse','Desert cottontail','Black bear','Mountain lion','Mule deer','Wild turkey','Spotted skunk','Ringtail','Javelina'],
  swamp:['Alligator','Bullfrog','Water moccasin','Egret','Heron','Swamp rat','Marsh hawk','Mud turtle','Water snake','Snapping turtle','Wood duck','Swamp fox','Catfish','Gar','Cottonmouth','River otter','Nutria','Swamp rabbit','Mink','Beaver','Anhinga','Bittern','Tricolor heron','Roseate spoonbill','Purple gallinule'],
  marsh:['Marsh wren','Redwing blackbird','Bittern','Rail','Coot','Mallard','Teal','Pintail','Shoveler','Gadwall','Canvasback','Scaup','Bufflehead','Goldeneye','Merganser','Grebe','Moorhen','Purple swamphen','Glossy ibis','Snipe','Curlew','Godwit','Dunlin','Sandpiper','Plover'],
  bog:['Sundew crawler','Pitcher slug','Bogworm','Peat frog','Sphagnum newt','Mire serpent','Cotton grass vole','Willow tit','Bog lemming','Swamp deer','Crane fly larva','Water boatman','Dragonfly nymph','Mud skimmer','Peat mole','Bog turtle','Adder','Palmate newt','Great diving beetle','Raft spider','Water scorpion','Whirligig beetle','Marsh fritillary','Large heath butterfly','Bog bush cricket'],
  desert:['Camel','Scorpion','Sand viper','Fennec fox','Jerboa','Desert rat','Vulture','Horned viper','Monitor lizard','Chameleon','Desert owl','Sandgrouse','Oryx','Addax','Dorcas gazelle','Sand cat','Caracal','Meerkat','Aardvark','Pangolin','Desert hare','Spiny mouse','Gerbil','Fat tailed scorpion','Deathstalker'],
  tundra:['Arctic fox','Polar bear','Snowy owl','Lemming','Musk ox','Caribou','Arctic hare','Ptarmigan','Wolverine','Ermine','Arctic wolf','Walrus','Seal','Sea lion','Narwhal','Beluga','Puffin','Gyrfalcon','Rough legged hawk','Long tailed duck','King eider','Ivory gull','Ross gull'],
  hills:['Hill fox','Moorland pony','Kite','Buzzard','Peregrine','Merlin','Curlew','Lapwing','Golden plover','Short eared owl','Mountain hare','Polecat','Pine marten','Red grouse','Black grouse','Stonechat','Wheatear','Ring ouzel','Dipper','Grey wagtail','Whinchat','Reed bunting','Twite','Dunlin','Dotterel'],
  mountain:['Mountain goat','Snow leopard','Ibex','Chamois','Yak','Pika','Marmot','Eagle','Condor','Alpine chough','Snowcock','Bharal','Markhor','Tahr','Argali','Urial','Saiga','Wild ass','Kiang','Marco polo sheep','Himalayan wolf','Red panda','Takin','Serow','Goral'],
  alpine:['Alpine marmot','Edelweiss moth','Snow bunting','Alpine accentor','Alpine salamander','Wallcreeper','Rock ptarmigan','Lammergeier','Alpine swift','Citril finch','Snowfinch','Mountain ringlet','Apollo butterfly','Alpine longhorn beetle','Alpine ibex','Swiss cow','Alpine newt','Yellow bellied toad'],
  volcano:['Fire salamander','Lava lizard','Ashen drake','Ember bat','Magma wurm','Cinder beetle','Ash crawler','Flame newt','Scorching scorpion','Pyroclast serpent','Burning boar','Smoke raven','Igneous golem','Caldera crab','Sulfur sprite','Basalt turtle','Obsidian spider','Char bear','Flare hawk','Thermal eel','Fissure worm','Pyroclast hound','Lava guppy','Magma shrimp'],
  river:['Trout','Salmon','Pike','Perch','Catfish','Crayfish','River otter','Kingfisher','Heron','Mallard','Water rat','Beaver','Mink','Dipper','Goosander','Lamprey','Stone loach','Bullhead','Dace','Chub','Roach','Tench','Bream','Barbel','Grayling'],
  lake:['Bass','Walleye','Lake trout','Sunfish','Crappie','Bluegill','Carp','Muskie','Northern pike','Cisco','Whitefish','Smelt','Alewife','Lake sturgeon','Bowfin','Longnose gar','Shortnose gar','Rock bass','Yellow perch','Pumpkinseed','Warmouth','Redear sunfish','Green sunfish','Spotted bass','Smallmouth bass'],
  sea:['Shark','Swordfish','Tuna','Marlin','Manta ray','Barracuda','Moray eel','Grouper','Snapper','Amberjack','Dolphinfish','Flying fish','Wahoo','King mackerel','Cobia','Tarpon','Bonefish','Permit','Snook','Redfish','Flounder','Pompano','Spanish mackerel','Bluefish','Striped bass'],
  ocean:['Blue whale','Sperm whale','Orca','Great white shark','Hammerhead shark','Giant squid','Nautilus','Sea turtle','Albatross','Storm petrel','Frigate bird','Booby','Tropicbird','Shearwater','Gannet','Oarfish','Sunfish','Sailfish','Viperfish','Anglerfish','Gulper eel','Fangtooth','Hatchetfish','Dragonfish'],
  small_cave:['Cave cricket','Cave spider','Cave fish','Cave frog','Bat','Centipede','Cave rat','Blind salamander','Pale crawler','Cave snail','Troglodyte beetle','Cave shrimp','Spring fish','Grotto sculpin','Stonefly larva','Caddisfly larva','Mayfly larva','Hellgrammite','Water penny','Riffle beetle'],
  large_cave:['Cave bear','Dire wolf','Troglodyte','Cave lion','Saber cat','Giant spider','Cave troll','Rock lizard','Stone golem','Cave beetle','Stalactite snake','Mushroom slug','Blind cavefish','Giant centipede','Cave scorpion','Stone crab','Cave lobster','Albino bat','Ghostly moth','Phosphor worm','Crystal beetle','Pale toad'],
  dark_cave:['Shadow bat','Void spider','Dark crawler','Nightmare rat','Shade wolf','Umbral serpent','Blackened lizard','Dark troll','Obsidian beetle','Shadow stalker','Darkness imp','Night creeper','Hollow eyes','Murk worm','Pitch moth','Eclipse frog','Penumbra crab','Tenebrous snail','Dark crystal bug','Shadowmeld cat','Nocturne hawk'],
  damp_cave:['Mudskipper','Water strider','Dampworm','Puddle frog','Cave eel','Moist centipede','Wet rock crab','Slime slug','Brine shrimp','Cave leech','Moisture bat','Dripstone snail','Cave pearl clam','Waterfall spider','Drip beetle','Soggy rat','Moist toad','Puddle salamander','Cave crayfish','Blind crab','Aquifer fish'],
  deep_cave:['Deepstone worm','Abyssal crawler','Underworld bat','Subterranean drake','Blind cave titan','Underearth troll','Rock devourer','Stone leech','Primordial slime','Deep earth beetle','Obsidian golem','Crystalline spider','Phosphor moth','Cave chimera','Petrified scorpion','Underground shark','Magma snail','Stone serpent','Deep rock crab','Earth elemental'],
  hell:['Imp','Demon','Devil','Hellhound','Succubus','Incubus','Balor','Marilith','Nalfeshnee','Glabrezu','Hezrou','Vrock','Dretch','Quasit','Lemure','Pit fiend','Erinyes','Barbed devil','Bone devil','Chain devil','Bearded devil','Ice devil','Horned devil','Amnizu','Narzugon'],
  city:['Alley cat','City rat','Pigeon','Crow','Raccoon','Fox','Stray dog','Street mouse','Feral rabbit','City falcon','Urban bat','Sewer rat','Chimney swift','House sparrow','Starling','Common myna','House mouse','Brown rat','Black rat','Garden hedgehog','Urban fox','Feral cat','Roof rat'],
  farm:['Chicken','Pig','Cow','Sheep','Goat','Horse','Duck','Goose','Turkey','Donkey','Mule','Rabbit','Cat','Dog','Rooster','Guinea fowl','Peacock','Llama','Alpaca','Emu','Ostrich','Pheasant','Quail','Partridge','Pigeon'],
};

function buildAnimalContent() {
  const items=[], monsters=[], droplists=[];
  REGIONS.forEach((region, ri) => {
    const names = REGION_ANIMAL_NAMES[region] || REGION_ANIMAL_NAMES.grassland;
    range(25).forEach(i => {
      const animalName = names[i] || `${cap(region)} creature ${i+1}`;
      const animalId   = `animal_${cid(region)}_${i}`;
      const dropId     = `ingredient_${cid(region)}_${i}`;
      items.push(makeItem({
        id:dropId, name:`${animalName} drop`,
        description:`Crafting ingredient dropped by the ${animalName}.`,
        iconSheet:'items_necklaces_1', iconRow:3, iconCol:1+(i%8),
        baseMarketCost:5, category:'ingredient'
      }));
      const dl = makeDroplist(`dl_${animalId}`, [{id:dropId, chance:80, qty:[1,2]}]);
      droplists.push(dl);
      monsters.push(makeMonster({
        id:animalId, name:animalName,
        iconSheet:'monsters_newb_1', iconRow:2+ri, iconCol:1+(i%8),
        maxHP:5+ri*2+i*2, maxAP:10, moveCost:10, attackCost:10,
        attackChance:60+ri, dmgMin:1+Math.floor(i/8), dmgMax:3+ri+Math.floor(i/5),
        droplistID:dl.id, faction:'animals', spawnGroup:`animals_${region}`,
        monsterClass:'animal'
      }));
    });
  });
  return {items, monsters, droplists};
}

function buildForageContent() {
  const items=[], conversations=[], quests=[];
  const forageNames=['Herb','Mushroom','Root','Berry','Seed','Flower','Bark','Moss',
    'Lichen','Resin','Leaf','Vine','Tuber','Fungus','Algae','Crystal','Mineral','Sap',
    'Spore','Petal','Bulb','Nectar','Fiber','Clay','Salt'];
  REGIONS.forEach((region, ri) => {
    forageNames.forEach((base, i) => {
      items.push(makeItem({
        id:`forage_${cid(region)}_${i}`,
        name:`${cap(region.replace('_',' '))} ${base.toLowerCase()}`,
        description:`A foraged ${base.toLowerCase()} from the ${region.replace('_',' ')}.`,
        iconSheet:'items_necklaces_1', iconRow:5, iconCol:1+(i%8),
        baseMarketCost:8, category:'ingredient'
      }));
    });
    const convId = `conv_forage_${cid(region)}`;
    conversations.push(makeConversation(
      convId,
      `You spot a promising foraging area in the ${region.replace('_',' ')}. Search for ingredients?`,
      [
        {text:'Search (90% chance)',
         nextPhraseID:`conv_forage_${cid(region)}_result`,
         requires:[reqNotActorCond(`ac_forage_${cid(region)}_used`)]},
        {text:'Come back tomorrow.',
         nextPhraseID:'X',
         requires:[reqActorCond(`ac_forage_${cid(region)}_used`)]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(
      `conv_forage_${cid(region)}_result`,
      `You found some useful ingredients in the ${region.replace('_',' ')}.`,
      [{text:'Take them.', nextPhraseID:'X'}],
      [rDropList(`dl_forage_${cid(region)}`), rActorCond(`ac_forage_${cid(region)}_used`,1440), rQuestProgress(`quest_forage_${cid(region)}`,10)]
    ));
    quests.push(makeQuest(`quest_forage_${cid(region)}`,
      `Forage in ${cap(region.replace('_',' '))}`,
      [{logText:`Search the ${region.replace('_',' ')} for useful ingredients.`, exp:25+ri*5}]
    ));
  });
  return {items, conversations, quests};
}

const CRYSTALS = ['Quartz crystal','Amethyst crystal','Sapphire crystal','Ruby crystal',
  'Emerald crystal','Diamond crystal','Obsidian crystal','Citrine crystal','Topaz crystal',
  'Garnet crystal','Aquamarine crystal','Opal crystal'];

function buildMiningContent() {
  const items=[], droplists=[], conversations=[];
  const ores=['Copper ore','Iron ore','Silver ore','Gold ore','Platinum ore','Mithril ore',
    'Adamantite ore','Dark iron ore','Star metal ore','Void ore'];

  items.push(makeItem({
    id:'item_pick_axe', name:'Pick axe',
    description:'A sturdy pick axe for mining ore and crystals.',
    iconSheet:'items_armours', iconRow:1, iconCol:1,
    baseMarketCost:50, category:'miscellaneous'
  }));

  ores.forEach((name, i) => {
    items.push(makeItem({
      id:`mining_ore_${i}`, name,
      description:`A chunk of ${name.toLowerCase()} extracted from rock.`,
      iconSheet:'items_necklaces_1', iconRow:6, iconCol:1+i,
      baseMarketCost:10+i*15, category:'ingredient'
    }));
    items.push(makeItem({
      id:`mining_ingot_${i}`, name:`${name.replace(' ore','')} ingot`,
      description:`A smelted ingot of ${name.replace(' ore','').toLowerCase()}.`,
      iconSheet:'items_necklaces_1', iconRow:7, iconCol:1+i,
      baseMarketCost:25+i*30, category:'ingredient'
    }));
    const dl = makeDroplist(`dl_mining_ore_${i}`, [{id:`mining_ore_${i}`, chance:'80', qty:[1,3]}]);
    droplists.push(dl);
    conversations.push(makeConversation(
      `conv_mine_ore_${i}`,
      `A vein of ${name.toLowerCase()} runs through the rock wall.`,
      [
        {text:'Mine (requires pick axe)',
         nextPhraseID:`conv_mine_ore_${i}_result`,
         requires:[reqInvKeep('item_pick_axe',1)]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(
      `conv_mine_ore_${i}_result`,
      `You chip away at the ${name.toLowerCase()} vein and extract some ore.`,
      [{text:'Take it.', nextPhraseID:'X'}],
      [rDropList(`dl_mining_ore_${i}`), rActorCond(`ac_mine_ore_${i}_used`,1440)]
    ));
  });

  CRYSTALS.forEach((name, i) => {
    items.push(makeItem({
      id:`mining_crystal_${i}`, name,
      description:`A precious ${name.toLowerCase()} found in a cave wall.`,
      iconSheet:'items_necklaces_1', iconRow:8, iconCol:1+i,
      baseMarketCost:50+i*25, category:'crystal'
    }));
    const dl = makeDroplist(`dl_mining_crystal_${i}`, [{id:`mining_crystal_${i}`, chance:'60', qty:[1,2]}]);
    droplists.push(dl);
  });

  return {items, droplists, conversations};
}

// ─── CRAFTING ITEMS ──────────────────────────────────────────────────────────
function buildCraftingItems() {
  const items=[];
  const CRAFTED_WEAPONS = [
    {id:'weapon_sword_copper',     name:'Copper sword',     dr:2,  ac:5,  base:30,  slot:'weapon'},
    {id:'weapon_sword_iron',       name:'Iron sword',       dr:3,  ac:8,  base:60,  slot:'weapon'},
    {id:'weapon_sword_silver',     name:'Silver sword',     dr:4,  ac:10, base:100, slot:'weapon'},
    {id:'weapon_sword_gold',       name:'Gold sword',       dr:5,  ac:12, base:150, slot:'weapon'},
    {id:'weapon_sword_mithril',    name:'Mithril sword',    dr:7,  ac:15, base:250, slot:'weapon'},
    {id:'weapon_sword_adamantite', name:'Adamantite sword', dr:10, ac:20, base:400, slot:'weapon'},
    {id:'weapon_axe_copper',       name:'Copper axe',       dr:2,  ac:4,  base:25,  slot:'weapon'},
    {id:'weapon_axe_iron',         name:'Iron axe',         dr:4,  ac:7,  base:55,  slot:'weapon'},
    {id:'weapon_axe_silver',       name:'Silver axe',       dr:5,  ac:9,  base:90,  slot:'weapon'},
    {id:'weapon_staff_wood',       name:'Wooden staff',     dr:1,  ac:6,  base:20,  slot:'weapon'},
    {id:'weapon_staff_iron',       name:'Iron staff',       dr:3,  ac:9,  base:80,  slot:'weapon'},
    {id:'weapon_dagger_copper',    name:'Copper dagger',    dr:1,  ac:7,  base:20,  slot:'weapon'},
    {id:'weapon_dagger_iron',      name:'Iron dagger',      dr:2,  ac:10, base:40,  slot:'weapon'},
    {id:'weapon_wand_fire',        name:'Fire wand',        dr:3,  ac:12, base:120, slot:'weapon'},
    {id:'weapon_wand_ice',         name:'Ice wand',         dr:3,  ac:12, base:120, slot:'weapon'},
    {id:'weapon_bow_wood',         name:'Wooden bow',       dr:2,  ac:8,  base:35,  slot:'weapon'},
    {id:'weapon_bow_iron',         name:'Iron bow',         dr:4,  ac:11, base:90,  slot:'weapon'},
  ];
  CRAFTED_WEAPONS.forEach(w => {
    items.push(makeItem({
      id:w.id, name:w.name,
      description:`A crafted ${w.name.toLowerCase()}.`,
      iconSheet:'items_armours', iconRow:1, iconCol:1,
      baseMarketCost:w.base, category:w.slot,
      equipEffect:{
        increaseAttackDamage:{min:w.dr, max:w.dr*2},
        increaseAttackChance:w.ac
      }
    }));
  });

  const CRAFTED_ARMOUR = [
    {id:'armour_leather_head',  name:'Leather cap',          dr:1, base:20,  cat:'head'},
    {id:'armour_leather_body',  name:'Leather armor',        dr:2, base:40,  cat:'body'},
    {id:'armour_leather_hand',  name:'Leather gloves',       dr:1, base:15,  cat:'hand'},
    {id:'armour_leather_feet',  name:'Leather boots',        dr:1, base:15,  cat:'feet'},
    {id:'armour_chain_head',    name:'Chainmail coif',       dr:3, base:60,  cat:'head'},
    {id:'armour_chain_body',    name:'Chainmail armor',      dr:5, base:100, cat:'body'},
    {id:'armour_chain_hand',    name:'Chainmail gauntlets',  dr:2, base:40,  cat:'hand'},
    {id:'armour_chain_feet',    name:'Chainmail boots',      dr:2, base:40,  cat:'feet'},
    {id:'armour_plate_head',    name:'Plate helm',           dr:5, base:120, cat:'head'},
    {id:'armour_plate_body',    name:'Plate armor',          dr:8, base:200, cat:'body'},
    {id:'armour_plate_hand',    name:'Plate gauntlets',      dr:4, base:80,  cat:'hand'},
    {id:'armour_plate_feet',    name:'Plate boots',          dr:4, base:80,  cat:'feet'},
    {id:'armour_robe_mage',     name:"Mage's robe",          dr:1, base:50,  cat:'body'},
    {id:'armour_robe_cleric',   name:"Cleric's robe",        dr:1, base:50,  cat:'body'},
    {id:'armour_robe_druid',    name:"Druid's robe",         dr:1, base:50,  cat:'body'},
    {id:'armour_shield_wood',   name:'Wooden shield',        dr:2, base:25,  cat:'shield'},
    {id:'armour_shield_iron',   name:'Iron shield',          dr:4, base:60,  cat:'shield'},
    {id:'armour_shield_steel',  name:'Steel shield',         dr:6, base:100, cat:'shield'},
  ];
  CRAFTED_ARMOUR.forEach(a => {
    items.push(makeItem({
      id:a.id, name:a.name,
      description:`Crafted ${a.name.toLowerCase()}.`,
      iconSheet:'items_armours', iconRow:2, iconCol:1,
      baseMarketCost:a.base, category:a.cat,
      equipEffect:{increaseDamageResistance:a.dr}
    }));
  });

  const POTIONS = [
    {id:'potion_health_minor',   name:'Minor health potion',   hp:[10,20], base:15},
    {id:'potion_health_medium',  name:'Medium health potion',  hp:[25,50], base:30},
    {id:'potion_health_major',   name:'Major health potion',   hp:[50,100],base:60},
    {id:'potion_health_full',    name:'Full health potion',    hp:[100,200],base:120},
    {id:'potion_ap_minor',       name:'Minor action potion',   ap:[10,20], base:15},
    {id:'potion_ap_medium',      name:'Medium action potion',  ap:[25,50], base:30},
    {id:'potion_ap_major',       name:'Major action potion',   ap:[50,100],base:60},
    {id:'potion_antidote',       name:'Antidote',              base:25},
    {id:'potion_strength',       name:'Strength potion',       base:40},
    {id:'potion_speed',          name:'Speed potion',          base:40},
  ];
  POTIONS.forEach(p => {
    const ue = {};
    if (p.hp) ue.increaseCurrentHP = {min:p.hp[0], max:p.hp[1]};
    if (p.ap) ue.increaseCurrentAP = {min:p.ap[0], max:p.ap[1]};
    items.push(makeItem({
      id:p.id, name:p.name,
      description:`A brewed potion. ${p.hp?`Restores ${p.hp[0]}\u2013${p.hp[1]} HP.`:''}${p.ap?`Restores ${p.ap[0]}\u2013${p.ap[1]} AP.`:''}`,
      iconSheet:'items_necklaces_1', iconRow:9, iconCol:1,
      baseMarketCost:p.base, category:'potion',
      useEffect:Object.keys(ue).length ? ue : undefined
    }));
  });

  return {items};
}

// ─── GUILD ITEMS ─────────────────────────────────────────────────────────────
function buildGuildItems() {
  const items=[], actorconditions=[];

  [['lockpick_basic','Basic lockpick','A basic lockpick. Breaks easily.',10],
   ['lockpick_iron','Iron lockpick','An iron lockpick for stronger locks.',25],
   ['lockpick_steel','Steel lockpick','A steel lockpick for tough locks.',50],
   ['lockpick_master_pick','Master pick','The finest lockpick. Rarely breaks.',100],
  ].forEach(([id,name,description,base],i) => {
    items.push(makeItem({id, name, description,
      iconSheet:'items_necklaces_1', iconRow:10, iconCol:1+i, baseMarketCost:base, category:'miscellaneous'
    }));
  });

  ['small_home','mid_home','large_home','luxury_home'].forEach((t,i) => {
    items.push(makeItem({
      id:`item_deed_${t}`, name:`${cap(t.replace('_',' '))} deed`,
      description:`The deed to a ${t.replace('_',' ')}.`,
      displaytype:'quest',
      iconSheet:'items_necklaces_1', iconRow:11, iconCol:1+i,
      hasManualPrice:true, baseMarketCost:0, category:'quest'
    }));
  });

  [['item_door_key','Door key','Opens a standard locked door.'],
   ['item_master_key','Master key','Opens any standard locked door.'],
  ].forEach(([id,name,description],i) => {
    items.push(makeItem({id, name, description,
      iconSheet:'items_necklaces_1', iconRow:12, iconCol:1+i, baseMarketCost:20*(i+1), category:'key'
    }));
  });

  items.push(makeItem({
    id:'item_deposit_box_key', name:'Safety deposit box key',
    description:'Key to a 100-item safety deposit box at the Royal Bank.',
    displaytype:'quest',
    iconSheet:'items_necklaces_1', iconRow:12, iconCol:3,
    hasManualPrice:true, baseMarketCost:0, category:'quest'
  }));

  items.push(makeItem({
    id:'item_logout_scroll', name:'Logout scroll',
    description:'Returns you to the room where you entered the current virtual world.',
    iconSheet:'items_necklaces_1', iconRow:13, iconCol:1,
    baseMarketCost:5, category:'scroll'
  }));

  GUILDS.forEach((guild, gi) => {
    range(12).forEach(level => {
      actorconditions.push(makeActorCondition({
        id:`ac_guild_${guild}_rank_${level}`,
        name:`${cap(guild)} guild rank ${level+1}`,
        category:'spiritual', isPositive:true,
        iconSheet:'actorconditions_1', iconRow:5+gi, iconCol:1+level
      }));
    });
  });

  range(200).forEach(i => {
    items.push(makeItem({
      id:`stolen_item_${i}`, name:`Stolen goods ${i+1}`,
      description:'Goods stolen from a home. A fence might buy these.',
      iconSheet:'items_necklaces_1', iconRow:14+(i%8), iconCol:1+(i%8),
      hasManualPrice:true, baseMarketCost:5+Math.floor(i/20)*5, category:'miscellaneous'
    }));
  });

  return {items, actorconditions};
}

// ─── GUILD CONVERSATIONS & QUESTS ────────────────────────────────────────────
function buildGuildConversations() {
  const conversations=[], quests=[];

  conversations.push(makeConversation(
    'conv_door',
    'A locked door bars your way.',
    [
      {text:'Open with key',nextPhraseID:'conv_door_open',requires:[reqInvRemove('item_door_key',1)]},
      {text:'Open with master key',nextPhraseID:'conv_door_open',requires:[reqInvKeep('item_master_key',1)]},
      {text:'Pick lock — basic lockpick (20% success)',nextPhraseID:'conv_door_pick_basic',requires:[reqInvKeep('lockpick_basic',1)]},
      {text:'Pick lock — iron lockpick (40% success)',nextPhraseID:'conv_door_pick_iron',requires:[reqInvKeep('lockpick_iron',1)]},
      {text:'Pick lock — steel lockpick (60% success)',nextPhraseID:'conv_door_pick_steel',requires:[reqInvKeep('lockpick_steel',1)]},
      {text:'Pick lock — master pick (80% success)',nextPhraseID:'conv_door_pick_master',requires:[reqInvKeep('lockpick_master_pick',1)]},
      {text:'Bash door (30% success)',nextPhraseID:'conv_door_bash'},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_door_open','The door opens.',[{text:'Good.', nextPhraseID:'X'}]));
  ['basic','iron','steel','master'].forEach((tier) => {
    conversations.push(makeConversation(`conv_door_pick_${tier}`,
      `You attempt to pick the lock with the ${tier} lockpick.`,
      [{text:'Try again later.', nextPhraseID:'X'}]));
  });
  conversations.push(makeConversation('conv_door_bash','You slam against the door.',[{text:'Try again.', nextPhraseID:'X'}]));

  conversations.push(makeConversation('conv_bank_manager',
    'Welcome to the Royal Bank. I can arrange a 100-item safety deposit box.',
    [
      {text:'Open deposit box', nextPhraseID:'S', requires:[reqInvKeep('item_deposit_box_key',1)]},
      {text:'Purchase deposit box key (200 gold)', nextPhraseID:'conv_bank_buy_key'},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_bank_buy_key',
    'Here is your safety deposit box key. Keep it safe!',
    [{text:'Thank you.', nextPhraseID:'X'}],
    [rGiveItem('item_deposit_box_key')]
  ));
  conversations.push(makeConversation('conv_bank_teller',
    'Savings accounts available! Deposit any amount, withdraw anytime.',
    [{text:'Use the bank', nextPhraseID:'S'}, {text:'Leave', nextPhraseID:'X'}]
  ));
  conversations.push(makeConversation('conv_bank_guard','Move along, citizen.',[{text:'Fine.', nextPhraseID:'X'}]));
  conversations.push(makeConversation('conv_bank_patron','I love the Royal Bank service!',[{text:'Indeed.', nextPhraseID:'X'}]));

  conversations.push(makeConversation('conv_jail_guard','Stay in your cell!',[{text:'Yes sir.', nextPhraseID:'X'}]));
  conversations.push(makeConversation('conv_jail_captain',"You're here until you pay your bail.",[{text:'OK.', nextPhraseID:'X'}]));
  conversations.push(makeConversation('conv_jail_lawyer',
    "I can arrange your bail. It'll cost 100 gold — freedom isn't free.",
    [
      {text:'Pay bail (100 gold)', nextPhraseID:'conv_jail_freed',requires:[reqActorCond('ac_bail_paid')]},
      {text:"I'll wait it out.", nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_jail_freed',
    'You are free to go!',
    [{text:'About time.', nextPhraseID:'X'}],
    [rActorCondClear('ac_bail_paid')]
  ));

  GUILDS.forEach((guild, gi) => {
    range(12).forEach(qi => {
      quests.push(makeQuest(`quest_guild_${guild}_${qi}`,
        `${cap(guild)} guild quest ${qi+1}`,
        [{logText:`Complete the ${cap(guild)} Guildmaster's task #${qi+1}.`, exp:(qi+1)*50+gi*100}]
      ));
    });
    conversations.push(makeConversation(`conv_guildmaster_${guild}`,
      `Welcome to the ${cap(guild)} Guild. I have quests to advance your rank.`,
      [
        {text:'Accept next quest', nextPhraseID:`conv_guild_quest_${guild}`,requires:[reqActorCond(`ac_guild_${guild}_rank_0`)]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(`conv_guild_quest_${guild}`,
      `Here is your next ${cap(guild)} Guild quest.`,
      [{text:'I will do it!', nextPhraseID:'X'}],
      [rQuestProgress(`quest_guild_${guild}_0`,10)]
    ));
    conversations.push(makeConversation(`conv_guild_seller_${guild}`,
      `Guild supplies for active ${cap(guild)} members.`,
      [
        {text:'Browse wares', nextPhraseID:'S',requires:[reqActorCond(`ac_guild_${guild}_rank_0`)]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
  });

  [['loom','A loom for weaving cloth. Requires Weaving skill.'],
   ['stove','A stove for cooking. Requires Cooking skill.'],
   ['garden','A garden plot. Equip a hoe and plant seeds. Plants mature in 7 days.'],
   ['smithing_forge','A forge for weapons and shields. Requires Smithing skill.'],
   ['crafting_bench','A workbench for armor. Requires Armorcraft skill.'],
   ['miners_forge',"A miner's forge for ore-crafted weapons and rings."],
   ['game_console','A game console. Play to enter the Astral Spire!'],
   ['computer','A magical computer. Connect to the LPC Church virtual world!'],
   ['fighters_forge',"The Fighter's Forge. Craft superior weapons and shields. Fighter guild level 3+ required."],
   ['writing_desk','A writing desk for crafting scrolls.'],
   ['cauldron','A cauldron for brewing potions. Mage, cleric, or druid guild level 6+ required.'],
   ['crafting_table','A crafting table for wands and staffs. Mage, cleric, or druid guild required.'],
   ['crafting_sign','Prices are posted for all crafting materials. Ask the NPC scholars for skill training.'],
  ].forEach(([id,msg]) => {
    conversations.push(makeConversation(`conv_${id}`, msg,
      [{text:'Use', nextPhraseID:'S'}, {text:'Leave', nextPhraseID:'X'}]));
  });

  ['mage','cleric','druid'].forEach(g => {
    conversations.push(makeConversation(`conv_desk_${g}`,
      `The ${cap(g)} special desk. Craft door passes, recall scrolls, and invisibility scrolls. Requires ${cap(g)} guild level 3.`,
      [
        {text:'Browse scrolls', nextPhraseID:'S',requires:[reqActorCond(`ac_guild_${g}_rank_2`)]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
  });

  conversations.push(makeConversation('conv_realtor',
    'Welcome! I sell homes of every size. Larger homes unlock more crafting stations.',
    [
      {text:'Small home (500 gold) — console, computer, stove', nextPhraseID:'conv_realtor_small'},
      {text:'Mid home (1000 gold) — + garden, bench', nextPhraseID:'conv_realtor_mid'},
      {text:'Large home (2000 gold) — + both forges', nextPhraseID:'conv_realtor_large'},
      {text:'Luxury home (4000 gold) — + butler (5% discount)', nextPhraseID:'conv_realtor_luxury'},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  [['small',500,'item_deed_small_home'],
   ['mid',1000,'item_deed_mid_home'],
   ['large',2000,'item_deed_large_home'],
   ['luxury',4000,'item_deed_luxury_home'],
  ].forEach(([tier,cost,deedId]) => {
    conversations.push(makeConversation(`conv_realtor_${tier}`,
      `Here is the deed to your ${tier} home. Enjoy!`,
      [{text:'Thank you!', nextPhraseID:'X'}],
      [rGiveItem(deedId)]
    ));
  });
  conversations.push(makeConversation('conv_npc_butler',
    'Welcome home, master. I have arranged a 5% discount at all crafting shops.',
    [{text:'Thank you!', nextPhraseID:'X'}],
    [rActorCond('ac_butler_discount_active')]
  ));

  range(200).forEach(i => {
    const containers=['chest','drawer','wardrobe','cabinet','trunk','box','cupboard','shelf','safe','crate'];
    conversations.push(makeConversation(`conv_home_loot_${i}`,
      `A ${containers[i%containers.length]} that might contain valuables.`,
      [
        {text:'Search it', nextPhraseID:`conv_home_loot_${i}_result`,requires:[reqActorCond('ac_thief_guild_member')]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(`conv_home_loot_${i}_result`,
      'You rummage through the container and find something.',
      [{text:'Take it.', nextPhraseID:'X'}],
      [rDropList(`dl_pickpocket_target_${i%200}`)]
    ));
  });

  return {conversations, quests};
}

// ─── FACTION CONTENT ─────────────────────────────────────────────────────────
function buildFactionContent() {
  const items=[], monsters=[], conversations=[], quests=[], actorconditions=[];
  RACES.forEach((race, ri) => {
    const att = RACE_ATTITUDE[race];
    range(25).forEach(i => {
      monsters.push(makeMonster({
        id:`npc_${race}_${i}`,
        name:`${cap(race.replace('_',' '))} ${i+1}`,
        iconSheet:'monsters_newb_1', iconRow:4+ri, iconCol:1+(i%8),
        maxHP:15+ri*3+i, maxAP:10, moveCost:10, attackCost:10,
        attackChance:att==='hostile'?75:30, dmgMin:1+ri, dmgMax:4+ri*2,
        faction:race, spawnGroup:race,
        phraseID: att!=='hostile' ? `conv_leader_${race}` : null
      }));
    });
    monsters.push(makeMonster({
      id:`npc_${race}_leader`,
      name:`${cap(race.replace('_',' '))} leader`,
      iconSheet:'monsters_newb_1', iconRow:4+ri, iconCol:9,
      maxHP:100+ri*20, maxAP:10, moveCost:10, attackCost:10,
      attackChance:85, dmgMin:5+ri, dmgMax:15+ri*3,
      faction:race, spawnGroup:`${race}_leader`,
      phraseID:`conv_leader_${race}`
    }));
    range(12).forEach(qi => {
      quests.push(makeQuest(`quest_faction_${race}_${qi}`,
        `${cap(race.replace('_',' '))} quest ${qi+1}`,
        [{logText:`Complete the task for the ${cap(race.replace('_',' '))} faction.`, exp:(qi+1)*75}]
      ));
    });
    conversations.push(makeConversation(`conv_leader_${race}`,
      att==='hostile'
        ? 'You are not welcome here, wood elf!'
        : `Greetings, traveler. What brings you to our people?`,
      [
        {text:'Accept quest',
         nextPhraseID:`conv_leader_${race}_quest`,
         requires:att!=='hostile'?[reqFaction(race,0)]:[]},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(`conv_leader_${race}_quest`,
      `Here is your ${cap(race.replace('_',' '))} faction quest.`,
      [{text:"I'll do it.", nextPhraseID:'X'}],
      [rQuestProgress(`quest_faction_${race}_0`,10), rAlignChange(race,1), rAlignChange(RACE_RIVALS[race],-1)]
    ));

    items.push(makeItem({
      id:`disguise_${race}`, name:`${cap(race.replace('_',' '))} disguise`,
      description:`Has a chance to negate ${cap(race.replace('_',' '))} faction attacks.`,
      iconSheet:'items_armours', iconRow:3+ri, iconCol:1,
      baseMarketCost:200+ri*20, category:'body',
      equipEffect:{addedConditions:[{condition:`ac_disguise_${race}`}]}
    }));
    actorconditions.push(makeActorCondition({
      id:`ac_disguise_${race}`, name:`${cap(race.replace('_',' '))} disguise active`,
      category:'mental', isPositive:true,
      iconSheet:'actorconditions_1', iconRow:7, iconCol:1+ri
    }));

    range(5).forEach(level => {
      actorconditions.push(makeActorCondition({
        id:`faction_${race}_level_${level}`,
        name:`${cap(race.replace('_',' '))} reputation ${level}`,
        category:'mental', isPositive:level>=2,
        iconSheet:'actorconditions_1', iconRow:8, iconCol:1+Math.min(ri,7)
      }));
    });
  });

  conversations.push(makeConversation('conv_disguise_seller',
    'Disguises for every race! A chance to fool even the most hostile faction.',
    [{text:'Browse disguises', nextPhraseID:'S'}, {text:'Leave', nextPhraseID:'X'}]
  ));
  conversations.push(makeConversation('conv_faction_hall_sign',
    'Faction Hall — buy disguises, check faction standings, and hire guild thieves for stealth missions.',
    [{text:'Understood.', nextPhraseID:'X'}]
  ));

  return {items, monsters, conversations, quests, actorconditions};
}

// ─── QUEST CONTENT ───────────────────────────────────────────────────────────
function buildQuestContent() {
  const items=[], monsters=[], droplists=[], conversations=[], quests=[], actorconditions=[];

  const WITCH_INGREDIENTS = ['Swamp lily','Bog mushroom','Dark moss','Fetid water','Marsh reed'];
  WITCH_INGREDIENTS.forEach((name, i) => {
    items.push(makeItem({
      id:`witch_ing_${i}`, name, displaytype:'quest',
      description:"An ingredient for the Swamp Witch's seeing potion.",
      iconSheet:'items_necklaces_1', iconRow:15, iconCol:1+i,
      hasManualPrice:true, baseMarketCost:0, category:'quest'
    }));
  });
  const SWAMP_MONSTERS = ['Bog troll','Swamp hag','Marsh witch','Mire serpent'];
  SWAMP_MONSTERS.forEach((name, i) => {
    const dl = makeDroplist(`dl_witch_mob_${i}`, [{id:`witch_ing_${i}`, chance:'100', qty:[1,1]}]);
    droplists.push(dl);
    monsters.push(makeMonster({
      id:`monster_witch_${i}`, name,
      iconSheet:'monsters_newb_1', iconRow:7, iconCol:1+i,
      maxHP:30+i*10, maxAP:10, moveCost:10, attackCost:10,
      attackChance:65, dmgMin:3+i, dmgMax:8+i*2,
      droplistID:dl.id, faction:'swamp_creatures', spawnGroup:'swamp_creatures',
      monsterClass:'humanoid'
    }));
  });
  conversations.push(makeConversation('conv_witch',
    'I am the Swamp Witch. Your sister Sunny came here seeking ancient magic. Bring me 5 ingredients for my seeing potion.',
    [
      {text:'Offer all 5 ingredients',nextPhraseID:'conv_witch_reward',requires:range(5).map(i=>reqInvRemove(`witch_ing_${i}`,1))},
      {text:'I still need ingredients.', nextPhraseID:'X'},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_witch_reward',
    'Sunny... she traveled east into the Drow Caves. Dark magic follows her.',
    [{text:'I will find her.', nextPhraseID:'X'}],
    [rQuestProgress('quest_witch',20)]
  ));
  conversations.push(makeConversation('conv_witch_search',
    'A marshy hollow with strange plants. Search carefully?',
    [
      {text:'Search (90% chance)', nextPhraseID:'conv_witch_search_result',requires:[reqNotActorCond('ac_witch_search_done')]},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_witch_search_result',
    'You find a Marsh reed growing in the mud.',
    [{text:'Take it.', nextPhraseID:'X'}],
    [rGiveItem('witch_ing_4'), rActorCond('ac_witch_search_done',1440)]
  ));
  actorconditions.push(makeActorCondition({
    id:'ac_witch_search_done', name:'Witch search on cooldown',
    category:'physical', isPositive:false,
    iconSheet:'actorconditions_1', iconRow:9, iconCol:1
  }));
  quests.push(makeQuest('quest_witch','The swamp witch',
    [
      {logText:'Gather 4 monster drops and 1 foraged marsh reed for the Swamp Witch.', exp:200},
      {logText:'Sunny went east to the Drow Caves. Follow her trail.', exp:300},
    ]
  ));

  range(12).forEach(i => {
    items.push(makeItem({
      id:`drow_ing_${i}`, name:`Dark essence ${i+1}`, displaytype:'quest',
      description:'A dark crystal essence found in the Drow Cave.',
      iconSheet:'items_necklaces_1', iconRow:16, iconCol:1+(i%8),
      hasManualPrice:true, baseMarketCost:0, category:'quest'
    }));
  });
  range(6).forEach(i => {
    const dl = makeDroplist(`dl_drow_cave_${i}`, [{id:`drow_ing_${i}`, chance:'100', qty:[1,1]}]);
    droplists.push(dl);
    monsters.push(makeMonster({
      id:`monster_drow_cave_${i}`,
      name:['Cave bat','Giant spider','Rock crab','Cave troll','Blind crawler','Stone wyrm'][i],
      iconSheet:'monsters_newb_1', iconRow:8, iconCol:1+i,
      maxHP:40+i*8, maxAP:10, moveCost:10, attackCost:10,
      attackChance:70, dmgMin:4+i, dmgMax:10+i*2,
      droplistID:dl.id, faction:'cave_creatures', spawnGroup:'cave_creatures',
      monsterClass:'animal'
    }));
  });
  ['drow_guard','drow_leader','drow_witch'].forEach((id, i) => {
    monsters.push(makeMonster({
      id:`npc_${id}`,
      name:cap(id.replace('_',' ')),
      iconSheet:'monsters_newb_1', iconRow:9, iconCol:1+i,
      maxHP:60+i*20, maxAP:10, moveCost:10, attackCost:10,
      attackChance:75+i*5, dmgMin:5+i*2, dmgMax:15+i*3,
      faction:'drow', spawnGroup:`${id}_unique`,
      phraseID:`conv_${id}`
    }));
    conversations.push(makeConversation(`conv_${id}`,
      {drow_guard:'Prove yourself, surface dweller. Complete my task first.',
       drow_leader:'Wood elf, you have courage. Prove your worth to the Drow.',
       drow_witch:'My spell requires 12 dark essences. Bring them all.'}[id],
      [{text:'Accept quest', nextPhraseID:`conv_${id}_quest`},{text:'Leave', nextPhraseID:'X'}]
    ));
    conversations.push(makeConversation(`conv_${id}_quest`,
      `Here is your ${id.replace('_',' ')} task.`,
      [{text:"I'll do it.", nextPhraseID:'X'}],
      [rQuestProgress(`quest_${id}`,10)]
    ));
    quests.push(makeQuest(`quest_${id}`,`${cap(id.replace('_',' '))} task`,
      [{logText:`Complete the ${id.replace('_',' ')}'s request.`, exp:300+i*100}]
    ));
  });
  conversations.push(makeConversation('conv_drow_witch_spell',
    'You have brought all 12 essences! Now the spell is complete...',
    [
      {text:'Watch',nextPhraseID:'conv_drow_witch_spell_complete',requires:range(12).map(i=>reqInvRemove(`drow_ing_${i}`,1))},
      {text:'Leave', nextPhraseID:'X'},
    ]
  ));
  conversations.push(makeConversation('conv_drow_witch_spell_complete',
    "The portal to Lloth's realm opens before you.",
    [{text:'Step through.', nextPhraseID:'X'}],
    [rQuestProgress('quest_drow_witch',20)]
  ));

  items.push(makeItem({
    id:'item_lloth_ring', name:"Lloth's seal ring", displaytype:'quest',
    description:"A ring from Lloth. It will teleport you back to her when your quest is complete.",
    iconSheet:'items_necklaces_1', iconRow:17, iconCol:1,
    hasManualPrice:true, baseMarketCost:0, category:'quest'
  }));
  const DEMIGODS=['Aspect of Lloth','Yochlol','Spider demon','Chitine warrior','Drider champion','Drow veteran','Chosen of Lloth'];
  DEMIGODS.forEach((name,i) => {
    monsters.push(makeMonster({
      id:`monster_lloth_guard_${i}`, name,
      iconSheet:'monsters_newb_1', iconRow:10, iconCol:1+i,
      maxHP:100+i*30, maxAP:10, moveCost:10, attackCost:10,
      attackChance:80+i*3, dmgMin:8+i*2, dmgMax:20+i*4,
      faction:'drow_gods', spawnGroup:'lloth_guards',
      monsterClass:'demon'
    }));
  });
  monsters.push(makeMonster({
    id:'npc_lloth', name:'Lloth, queen of spiders',
    iconSheet:'monsters_newb_1', iconRow:10, iconCol:8,
    maxHP:500, maxAP:10, moveCost:10, attackCost:10,
    attackChance:90, dmgMin:15, dmgMax:40,
    faction:'drow_gods', spawnGroup:'lloth_unique',
    phraseID:'conv_lloth', monsterClass:'demon'
  }));
  conversations.push(makeConversation('conv_lloth',
    "Wood elf. Your courage reaches even my web. Travel to the Volcano and settle the dragon dispute. My ring will return you when done.",
    [{text:"Accept (take Lloth's ring)", nextPhraseID:'conv_lloth_accept'},{text:'Leave', nextPhraseID:'X'}]
  ));
  conversations.push(makeConversation('conv_lloth_accept',
    "Take this ring. It will bring you back to me when the dragons are at peace.",
    [{text:'I will settle their dispute.', nextPhraseID:'X'}],
    [rGiveItem('item_lloth_ring'), rQuestProgress('quest_lloth',10)]
  ));
  quests.push(makeQuest('quest_lloth',"Lloth's dragon dispute",
    [
      {logText:'Travel to the Volcano and speak with the dragons.', exp:500},
      {logText:"Return to Lloth via the ring when the dispute is resolved.", exp:1000},
    ]
  ));

  items.push(makeItem({
    id:'item_grand_dragon_reward', name:'Crown of dragon lords',
    description:'Reward from the ancient dragons for resolving their disputes.',
    displaytype:'legendary',
    iconSheet:'items_armours', iconRow:5, iconCol:1,
    baseMarketCost:9999, category:'head',
    equipEffect:{increaseDamageResistance:20, increaseAttackChance:15}
  }));
  DRAGON_TYPES.forEach((type, ti) => {
    DRAGON_AGES.forEach((age, ai) => {
      const hpMap={baby:50,youngling:100,teen:200,adult:400};
      const dmgMap={baby:10,youngling:20,teen:35,adult:60};
      monsters.push(makeMonster({
        id:`dragon_${cid(type)}_${age}`,
        name:`${type} dragon (${age})`,
        iconSheet:'monsters_newb_1', iconRow:12+ti, iconCol:1+ai,
        maxHP:hpMap[age], maxAP:10, moveCost:10, attackCost:10,
        attackChance:70+ai*5, dmgMin:5+ai*5, dmgMax:dmgMap[age],
        faction:'dragons', spawnGroup:`dragons_${cid(type)}`,
        monsterClass:'reptile',
        phraseID: age==='adult' ? `conv_dragon_${cid(type)}_adult` : null
      }));
      if (age==='adult') {
        items.push(makeItem({
          id:`item_dragon_scale_${cid(type)}`, name:`${type} dragon scale`,
          description:`A tough scale from an adult ${type} dragon.`,
          iconSheet:'items_armours', iconRow:6, iconCol:1+ti,
          baseMarketCost:500+ti*50, category:'body',
          equipEffect:{increaseDamageResistance:10+ti*2}
        }));
        quests.push(makeQuest(`quest_dragon_${cid(type)}_adult`,`${type} dragon's request`,
          [{logText:`Complete the adult ${type} dragon's quest.`, exp:800+ti*100}]
        ));
        conversations.push(makeConversation(`conv_dragon_${cid(type)}_adult`,
          `The ${type} dragon eyes you carefully. Prove yourself worthy of my aid.`,
          [{text:'Accept quest', nextPhraseID:`conv_dragon_${cid(type)}_adult_quest`},{text:'Leave', nextPhraseID:'X'}]
        ));
        conversations.push(makeConversation(`conv_dragon_${cid(type)}_adult_quest`,
          `Here is my request, surface dweller.`,
          [{text:"I'll do it.", nextPhraseID:'X'}],
          [rQuestProgress(`quest_dragon_${cid(type)}_adult`,10)]
        ));
      }
    });
  });
  ['ancient_platinum','ancient_chromatic'].forEach((did, i) => {
    monsters.push(makeMonster({
      id:`dragon_${did}`, name:cap(did.replace('_',' ')),
      iconSheet:'monsters_newb_1', iconRow:22, iconCol:1+i,
      maxHP:2000+i*500, maxAP:10, moveCost:10, attackCost:10,
      attackChance:95, dmgMin:30, dmgMax:80,
      faction:'ancient_dragons', spawnGroup:`${did}_unique`,
      phraseID:`conv_dragon_${did}`, monsterClass:'reptile'
    }));
    quests.push(makeQuest(`quest_dragon_${did}`,`${cap(did.replace('_',' '))} dragon's quest`,
      [{logText:`Complete the ${cap(did.replace('_',' '))} dragon's ultimate quest. All 10 adult dragon quests must be complete first.`, exp:5000+i*2000}]
    ));
    conversations.push(makeConversation(`conv_dragon_${did}`,
      `The ${cap(did.replace('_',' '))} dragon regards you with ancient eyes. You have proven yourself among all dragonkind.`,
      [
        {text:'Accept quest',nextPhraseID:`conv_dragon_${did}_accept`,requires:DRAGON_TYPES.map(t=>reqQuestProgress(`quest_dragon_${cid(t)}_adult`,10))},
        {text:'Return when you have completed all adult dragon quests.',nextPhraseID:'X'},
        {text:'Leave', nextPhraseID:'X'},
      ]
    ));
    conversations.push(makeConversation(`conv_dragon_${did}_accept`,
      'Then let us begin.',
      [{text:'Ready.', nextPhraseID:'X'}],
      [rQuestProgress(`quest_dragon_${did}`,10)]
    ));
  });
  conversations.push(makeConversation('conv_dragon_dispute_complete',
    "The dragons bow their heads. The dispute is settled. Use Lloth's ring to return.",
    [
      {text:"Use ring", nextPhraseID:'X', requires:[reqInvKeep('item_lloth_ring',1)]},
      {text:'Stay a moment.', nextPhraseID:'X'},
    ],
    [rQuestProgress('quest_lloth',20)]
  ));

  items.push(makeItem({
    id:'item_sunny_ring', name:"Sunny's ring", displaytype:'quest',
    description:"Your sister Sunny's ring with a tent spell. Use it to travel to the ring clearing on demand.",
    iconSheet:'items_necklaces_1', iconRow:18, iconCol:1,
    hasManualPrice:true, baseMarketCost:0, category:'quest'
  }));
  conversations.push(makeConversation('conv_sunny_ring_search',
    'You search the undergrowth carefully and find something glinting...',
    [{text:"Take the ring!", nextPhraseID:'conv_sunny_ring_found'},{text:'Leave it for now.', nextPhraseID:'X'}]
  ));
  conversations.push(makeConversation('conv_sunny_ring_found',
    "You pick up Sunny's ring. It pulses with a warm magical light.",
    [{text:'Take it.', nextPhraseID:'X'}],
    [rGiveItem('item_sunny_ring'), rQuestProgress('quest_find_ring',10)]
  ));
  quests.push(makeQuest('quest_find_ring',"Find Sunny's ring",
    [{logText:"Search the ring clearing for Sunny's ring.", exp:500}]
  ));

  items.push(makeItem({
    id:'item_sunny_reward', name:"Sunny's blessing",
    description:'A powerful blessing from your sister Sunny upon her ascension to godhood.',
    iconSheet:'items_necklaces_1', iconRow:18, iconCol:2,
    hasManualPrice:true, baseMarketCost:0, category:'miscellaneous',
    useEffect:{conditionsSource:[{condition:'ac_sunny_blessing', chance:'100'}]}
  }));
  actorconditions.push(makeActorCondition({
    id:'ac_sunny_blessing', name:"Sunny's blessing",
    category:'spiritual', isPositive:true,
    iconSheet:'actorconditions_1', iconRow:10, iconCol:1,
    abilityEffect:{increaseMaxHP:50, increaseAttackChance:10}
  }));
  quests.push(makeQuest('quest_sunny_end','Finding Sunny',
    [
      {logText:'Complete all Drow village quests on the moons.', exp:3000},
      {logText:"Witness Sunny's ascension.", exp:5000},
    ]
  ));
  MOON_COLORS.forEach((color, ci) => {
    range(12).forEach(j => {
      monsters.push(makeMonster({
        id:`npc_moon_drow_${cid(color)}_${j}`,
        name:`${color} moon Drow ${j+1}`,
        iconSheet:'monsters_newb_1', iconRow:14, iconCol:1+ci,
        maxHP:80+ci*10, maxAP:10, moveCost:10, attackCost:10,
        attackChance:75, dmgMin:5+ci, dmgMax:15+ci,
        faction:'drow', spawnGroup:`moon_drow_${cid(color)}`
      }));
    });
    monsters.push(makeMonster({
      id:`npc_moon_elder_${cid(color)}`,
      name:`${color} moon elder`,
      iconSheet:'monsters_newb_1', iconRow:14, iconCol:8+ci%8,
      maxHP:150+ci*20, maxAP:10, moveCost:10, attackCost:10,
      attackChance:80, dmgMin:8+ci, dmgMax:20+ci,
      faction:'drow', spawnGroup:`moon_elder_${cid(color)}_unique`,
      phraseID:`conv_moon_elder_${cid(color)}`
    }));
    range(12).forEach(qi => {
      quests.push(makeQuest(`quest_moon_${cid(color)}_${qi}`,
        `${color} moon quest ${qi+1}`,
        [{logText:`Complete the ${color} moon Drow village task #${qi+1}.`, exp:200+ci*50+qi*25}]
      ));
    });
    conversations.push(makeConversation(`conv_moon_elder_${cid(color)}`,
      `Greetings, surface dweller. The ${color} moon Drow have quests for you.`,
      [{text:'Accept quest', nextPhraseID:`conv_moon_quest_${cid(color)}`},{text:'Leave', nextPhraseID:'X'}]
    ));
    conversations.push(makeConversation(`conv_moon_quest_${cid(color)}`,
      `Here is your task from the ${color} moon Drow.`,
      [{text:"I'll do it.", nextPhraseID:'X'}],
      [rQuestProgress(`quest_moon_${cid(color)}_0`,10)]
    ));
  });

  const CASTLE_NPCS = [
    {id:'npc_ozzy',             name:'Ozzy',               conv:'conv_npc_ozzy',         msg:"Ahh, another soul seeking adventure! I'm Ozzy, collector of tales.",      qi:'quest_npc_ozzy'},
    {id:'npc_nymph',            name:'Nymph',              conv:'conv_npc_nymph',         msg:'The forest whispers strange things lately.',                             qi:'quest_npc_nymph'},
    {id:'npc_guard_captain',    name:'Guard captain',      conv:'conv_npc_guard_captain', msg:'The castle is secure under my watch. I have a task for a capable warrior.',qi:'quest_npc_guard_captain'},
    {id:'npc_head_cook',        name:'Head cook',          conv:'conv_npc_head_cook',     msg:'The kitchen needs special ingredients!',                                 qi:'quest_npc_head_cook'},
    {id:'npc_librarian',        name:'Librarian',          conv:'conv_npc_librarian',     msg:'I need a rare tome retrieved.',                                          qi:'quest_npc_librarian'},
    {id:'npc_gardener',         name:'Gardener',           conv:'conv_npc_gardener',      msg:'The gardens need tending. Could you fetch exotic seeds?',                qi:'quest_npc_gardener'},
    {id:'npc_castle_weaponer',  name:'Castle weaponer',    conv:'conv_castle_weaponer',   msg:'Finest weapons in the realm, forged here!',                             qi:null},
    {id:'npc_castle_armorer',   name:'Castle armorer',     conv:'conv_castle_armorer',    msg:'I can outfit you for any adventure.',                                    qi:null},
    {id:'npc_castle_alchemist', name:'Castle alchemist',   conv:'conv_castle_alchemist',  msg:'Potions and cures — all ailments remedied here.',                       qi:null},
    {id:'npc_timekeeper',       name:'Timekeeper',         conv:'conv_timekeeper',        msg:null, qi:null},
    {id:'npc_crystal_grandmaster',name:'Crystal grandmaster',conv:'conv_crystal_grandmaster',msg:'Bring me all 12 crystals and I shall grant you the Grand Crystal Staff.',qi:'quest_crystal_grandmaster'},
    {id:'npc_sunny',            name:'Sunny',              conv:'conv_npc_sunny',         msg:"Little sibling! I've been searching for you across the cosmos.",        qi:'quest_sunny_end'},
    {id:'npc_ring_guard',       name:'Ring clearing guard',conv:'conv_ring_guard',        msg:'This clearing is protected. What is your business here?',               qi:null},
    {id:'npc_prison_warden',    name:'Prison warden',      conv:'conv_npc_prison_warden', msg:'Order is maintained in my prison.',                                      qi:'quest_npc_prison_warden'},
    {id:'npc_gate_guard',       name:'Gate guard',         conv:'conv_npc_gate_guard',    msg:'I spotted something suspicious outside. Investigate?',                  qi:'quest_npc_gate_guard'},
  ];
  CASTLE_NPCS.forEach(({id, name, conv, msg, qi}) => {
    if (!monsters.find(m=>m.id===id)) {
      monsters.push(makeMonster({
        id, name,
        iconSheet:'monsters_newb_1', iconRow:20, iconCol:1+(monsters.length%8),
        maxHP:50, maxAP:10, moveCost:10, attackCost:10,
        attackChance:60, dmgMin:3, dmgMax:8,
        faction:'castle', spawnGroup:`${id}_unique`,
        phraseID:conv
      }));
    }
    if (msg) {
      const replies = qi
        ? [{text:'Accept quest', nextPhraseID:`${conv}_quest`}, {text:'Leave', nextPhraseID:'X'}]
        : [{text:'OK.', nextPhraseID:'X'}];
      if (!conversations.find(c=>c.id===conv)) {
        conversations.push(makeConversation(conv, msg, replies));
      }
      if (qi) {
        conversations.push(makeConversation(`${conv}_quest`,
          "Here is your task.",
          [{text:"I'll do it.", nextPhraseID:'X'}],
          [rQuestProgress(qi,10)]
        ));
        if (!quests.find(q=>q.id===qi)) {
          quests.push(makeQuest(qi, cap(qi.replace('quest_npc_','').replace('_',' ')+' task'),
            [{logText:`Complete the task for ${name}.`, exp:300}]
          ));
        }
      }
    }
  });

  conversations.push(makeConversation('conv_ring_guard','This clearing is protected. What is your business here?',
    [{text:'I seek the ring.', nextPhraseID:'X'}, {text:'Just passing through.', nextPhraseID:'X'}]));
  conversations.push(makeConversation('conv_npc_sunny',
    "Little sibling! I've been searching for you across the cosmos.",
    [{text:'Sunny! I found you!', nextPhraseID:'conv_npc_sunny_reunion'}]
  ));
  conversations.push(makeConversation('conv_npc_sunny_reunion',
    "I have been transformed, but my love for you remains. Watch as I ascend...",
    [{text:'I love you, Sunny.', nextPhraseID:'X'}],
    [rQuestProgress('quest_sunny_end',20), rGiveItem('item_sunny_reward')]
  ));

  return {items, monsters, droplists, conversations, quests, actorconditions};
}

// ─── POKEMON / BEAST SYSTEM ──────────────────────────────────────────────────
const BEAST_POOLS = {
  meadow:  ['Meadow sprite','Clover fox','Sunpetal deer','Wind bunny','Grass cub','Dew beetle','Meadowlark spirit','Buttercup toad','Pollen owl','Prairie wolf'],
  forest:  ['Forest sprite','Thornback boar','Treant cub','Mossy lizard','Bark beetle','Root snake','Canopy hawk','Shadow fox','Fern bear','Mushroom gnome'],
  mountain:['Rock sprite','Granite golem','Ice gryphon','Mountain goat spirit','Storm eagle','Crystal wolf','Avalanche bear','Peak dragon','Frost lynx','Boulder crab'],
  ocean:   ['Ocean sprite','Deep shark','Coral crab','Tide serpent','Pearl turtle','Storm whale','Abyssal ray','Current eel','Sea drake','Kraken cub'],
  volcanic:['Lava sprite','Ember lizard','Magma crab','Flame toad','Ash wolf','Cinder hawk','Pyroclast bear','Volcano drake','Heat serpent','Soot gremlin'],
  arctic:  ['Frost sprite','Snow wolf','Ice bear','Blizzard hawk','Glacier tortoise','Tundra fox','Aurora deer','Permafrost crab','Winter drake','Polar gryphon'],
  swamp:   ['Bog sprite','Mire serpent','Mud toad','Swamp fox','Marsh hawk','Peat bear','Sludge crab','Damp drake','Fetid worm',"Bogwitch's cat"],
  sky:     ['Cloud sprite','Storm gryphon','Wind drake','Thunder hawk','Gale fox','Cirrus whale','Sky serpent','Nimbus cub','Cyclone eagle','Zephyr deer'],
  shadow:  ['Shadow sprite','Dark fox','Nightmare cub','Void serpent','Eclipse hawk','Phantom bear','Umbral drake','Ghost crab','Darkness wolf','Abyss toad'],
};
const EVOLUTION_TIERS = ['t1','t2','t3'];

function buildPokemonContent() {
  const items=[], monsters=[], droplists=[], conversations=[], quests=[], actorconditions=[];

  [['beast_orb_1','Spirit orb I','A basic spirit orb. 25% catch rate.',25,50],
   ['beast_orb_2','Spirit orb II','A good spirit orb. 50% catch rate.',100,50],
   ['beast_orb_3','Spirit orb III','A great spirit orb. 75% catch rate.',250,50],
   ['beast_orb_4','Spirit orb IV','A master spirit orb. 95% catch rate.',500,50],
  ].forEach(([id,name,description,base,iconC]) => {
    items.push(makeItem({
      id, name, description,
      iconSheet:'items_necklaces_1', iconRow:19, iconCol:iconC,
      baseMarketCost:base, category:'beastOrb'
    }));
  });

  POKEMON_REGIONS.forEach((region, ri) => {
    const pool = BEAST_POOLS[region] || [];
    pool.forEach((base, bi) => {
      EVOLUTION_TIERS.forEach((tier, ti) => {
        const id = `monster_beast_${region}_${cid(base)}_${tier}`;
        const tierName = ['',', evolved',', fully evolved'][ti];
        monsters.push(makeMonster({
          id, name:`${base}${tierName}`,
          iconSheet:'monsters_newb_1', iconRow:23+ri, iconCol:1+bi,
          maxHP:20+ti*30+bi*5, maxAP:10, moveCost:10, attackCost:10,
          attackChance:60+ti*10+bi*3, dmgMin:2+ti*3, dmgMax:6+ti*8,
          faction:'beasts', spawnGroup:`beasts_${region}_${cid(base)}`,
          monsterClass:'animal',
          phraseID:`conv_beast_${region}_${cid(base)}_${tier}`
        }));
        conversations.push(makeConversation(
          `conv_beast_${region}_${cid(base)}_${tier}`,
          `A wild ${base}${tierName} regards you curiously.`,
          [
            {text:'Try to catch it (use a Spirit Orb)',
             nextPhraseID:`conv_beast_catch_${region}_${cid(base)}_${tier}`,
             requires:[reqInvKeep('beast_orb_1',1)]},
            {text:'Fight', nextPhraseID:'F'},
            {text:'Leave', nextPhraseID:'X'},
          ]
        ));
        conversations.push(makeConversation(
          `conv_beast_catch_${region}_${cid(base)}_${tier}`,
          `You throw the orb... ${ti===0?'success!':'it was a tough capture!'}`,
          [{text:'Great!', nextPhraseID:'X'}],
          [rActorCond(`ac_beast_caught_${id}`), rActorCond(`ac_beast_${region}_${cid(base)}_${tier}`)]
        ));
        actorconditions.push(makeActorCondition({
          id:`ac_beast_caught_${id}`, name:`${base}${tierName} caught`,
          category:'mental', isPositive:true,
          iconSheet:'actorconditions_1', iconRow:11+ri, iconCol:1+bi
        }));
      });
    });
    monsters.push(makeMonster({
      id:`monster_gym_leader_${region}`, name:`${cap(region)} gym leader`,
      iconSheet:'monsters_newb_1', iconRow:33, iconCol:1+ri,
      maxHP:200+ri*30, maxAP:10, moveCost:10, attackCost:10,
      attackChance:85, dmgMin:15, dmgMax:40,
      faction:'beast_trainers', spawnGroup:`gym_leader_${region}_unique`,
      phraseID:`conv_gym_leader_${region}`
    }));
    range(12).forEach(ti => {
      monsters.push(makeMonster({
        id:`monster_trainer_${region}_${ti}`, name:`${cap(region)} trainer ${ti+1}`,
        iconSheet:'monsters_newb_1', iconRow:34, iconCol:1+(ti%8),
        maxHP:80+ri*10+ti*5, maxAP:10, moveCost:10, attackCost:10,
        attackChance:70+ri, dmgMin:8+ti, dmgMax:20+ti,
        faction:'beast_trainers', spawnGroup:`trainers_${region}`,
        phraseID:`conv_trainer_${region}_${ti}`
      }));
      conversations.push(makeConversation(`conv_trainer_${region}_${ti}`,
        `I am a ${cap(region)} beast trainer! Let's battle!`,
        [{text:'Battle!', nextPhraseID:'F'}, {text:'Maybe later.', nextPhraseID:'X'}]
      ));
    });
    conversations.push(makeConversation(`conv_gym_leader_${region}`,
      `I am the ${cap(region)} gym leader! Defeat me to earn the ${cap(region)} Badge.`,
      [{text:'Challenge the gym leader!', nextPhraseID:'F'},{text:'Not ready yet.', nextPhraseID:'X'}]
    ));
    quests.push(makeQuest(`quest_gym_${region}`, `${cap(region)} gym badge`,
      [
        {logText:`Defeat the ${cap(region)} trainer gauntlet.`, exp:200+ri*50},
        {logText:`Defeat the ${cap(region)} gym leader.`, exp:400+ri*100},
      ]
    ));
  });

  monsters.push(makeMonster({
    id:'monster_grand_champion', name:'Grand champion',
    iconSheet:'monsters_newb_1', iconRow:35, iconCol:1,
    maxHP:1000, maxAP:10, moveCost:10, attackCost:10,
    attackChance:95, dmgMin:30, dmgMax:80,
    faction:'beast_trainers', spawnGroup:'grand_champion_unique',
    phraseID:'conv_grand_champion'
  }));
  conversations.push(makeConversation('conv_grand_champion',
    "You've defeated all 9 gym leaders! Face me — the Grand Champion!",
    [
      {text:'I accept your challenge!', nextPhraseID:'F',
       requires:POKEMON_REGIONS.map(r=>reqQuestProgress(`quest_gym_${r}`,20))},
      {text:'I need more preparation.', nextPhraseID:'X'},
    ]
  ));
  quests.push(makeQuest('quest_grand_champion','Grand champion',
    [{logText:'Defeat all 9 gym leaders and challenge the Grand Champion.', exp:5000}]
  ));

  ['npc_beast_professor','npc_beast_scholar','npc_beast_elder','npc_beast_breeder'].forEach((id,i) => {
    const names=['Beast professor','Beast scholar','Beast elder','Beast breeder'];
    const msgs=[
      'I study astral beasts. Catch them all!',
      'Evolution requires investment. Bring me gold and your beast.',
      'The ancient beasts hold great power. Seek them all.',
      'I can breed two beasts into a new one. Bring me a compatible pair.',
    ];
    monsters.push(makeMonster({
      id, name:names[i],
      iconSheet:'monsters_newb_1', iconRow:36, iconCol:1+i,
      maxHP:30, maxAP:10, moveCost:10, attackCost:10,
      attackChance:30, dmgMin:1, dmgMax:3,
      faction:'beast_scholars', spawnGroup:`${id}_unique`,
      phraseID:`conv_${id}`
    }));
    conversations.push(makeConversation(`conv_${id}`, msgs[i],
      [{text:'OK.', nextPhraseID:'S'}, {text:'Thanks.', nextPhraseID:'X'}]
    ));
  });

  conversations.push(makeConversation('conv_prevent_pokemon',
    'You feel your astral beasts retreating to their orbs as you leave the beast realm.',
    [{text:'I understand.', nextPhraseID:'X'}]
  ));
  conversations.push(makeConversation('conv_prevent_overworld',
    'You feel your worldly equipment fading as you enter the beast realm.',
    [{text:'Ready.', nextPhraseID:'X'}]
  ));

  return {items, monsters, droplists, conversations, quests, actorconditions};
}

// ─── ALL MAPS ─────────────────────────────────────────────────────────────────
function makeStandardMap(filename, extraGroups=[], width=30, height=30) {
  _objId = 1;
  const tileLayers = [
    tileLayerXML(1,'Base',width,height),tileLayerXML(2,'Ground',width,height),
    tileLayerXML(3,'Objects',width,height),tileLayerXML(4,'Objects_replace',width,height),
    tileLayerXML(5,'Above',width,height),tileLayerXML(6,'Above_replace',width,height),
    tileLayerXML(7,'Top',width,height),tileLayerXML(8,'Walkable',width,height,false),
  ].join('\n');
  const tilesetXmls = AT_TILESETS.map(tilesetXML).join('\n');
  let layerIdCounter = 9;
  const baseGroups = [
    objectgroupXML(layerIdCounter++,'Mapevents',[],false),
    objectgroupXML(layerIdCounter++,'Spawn',[],true),
    objectgroupXML(layerIdCounter++,'Keys',[],false),
    objectgroupXML(layerIdCounter++,'Replace',[],false),
  ].join('\n');
  const extraGroupXml = extraGroups.map(g => {
    if (g.type === 'objectgroup') {
      const visAttr = g.visible===false ? ' visible="0"' : '';
      const colorAttr = g.color ? ` color="${g.color}"` : '';
      const objsXml = (g.objects||[]).map(buildObject).join('\n');
      if (!objsXml) return ` <objectgroup id="${layerIdCounter++}" name="${g.name}"${colorAttr}${visAttr}/>`;
      return ` <objectgroup id="${layerIdCounter++}" name="${g.name}"${colorAttr}${visAttr}>\n${objsXml}\n </objectgroup>`;
    }
    return '';
  }).join('\n');
  const nextLayerId = layerIdCounter + 1;
  const tmx = `<?xml version="1.0" encoding="UTF-8"?>\n<map version="1.8" tiledversion="1.8.4" orientation="orthogonal" renderorder="right-down"` +
    ` width="${width}" height="${height}" tilewidth="32" tileheight="32"` +
    ` infinite="0" nextlayerid="${nextLayerId}" nextobjectid="${_objId}">\n${tilesetXmls}\n${tileLayers}\n${baseGroups}\n${extraGroupXml}\n</map>`;
  return {path:filename, tmx};
}

function generateAllMaps() {
  const maps = [];

  maps.push(makeStandardMap('template_all.tmx', [
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
       ...MOON_COLORS.flatMap((color,i)=>[
         makeKeyObj(`rocket_${cid(color)}_board_1`,`conv_rocket_${cid(color)}`,224+i*32,700),
         makeKeyObj(`rocket_${cid(color)}_board_2`,`conv_rocket_${cid(color)}`,224+i*32,732),
       ]),
     ]},
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
       makeNPCObj('npc_head_cook','conv_npc_head_cook',64,1052),
       makeNPCObj('npc_librarian','conv_npc_librarian',96,1052),
       makeNPCObj('npc_gardener','conv_npc_gardener',128,1052),
       makeNPCObj('npc_timekeeper','conv_timekeeper',256,1052),
     ]},
    {type:'objectgroup',name:'Spawn_tower_npc',color:'#ffaa00',
     objects:[makeNPCObj('npc_crystal_grandmaster','conv_crystal_grandmaster',64,1200)]},
    ...['haunted_house','haunted_mansion','haunted_prison','graveyard','crypt','mausoleum'].map((place,pi)=>({
      type:'objectgroup',name:`Spawn_${cid(place)}`,color:'#440044',
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

  maps.push(makeStandardMap('template_pokemon.tmx', [
    {type:'objectgroup',name:'Spawn_pokemon_npc',color:'#00ffaa',
     objects:[
       makeNPCObj('npc_beast_professor','conv_npc_beast_professor',64,64),
       makeNPCObj('npc_beast_scholar','conv_npc_beast_scholar',96,64),
       makeNPCObj('npc_beast_elder','conv_npc_beast_elder',128,64),
       makeNPCObj('npc_beast_breeder','conv_npc_beast_breeder',160,64),
       makeNPCObj('monster_grand_champion','conv_grand_champion',192,64),
       ...POKEMON_REGIONS.flatMap((region,ri)=>[
         makeNPCObj(`monster_gym_leader_${region}`,`conv_gym_leader_${region}`,64+ri*48,128),
         ...range(12).map(ti=>makeNPCObj(`monster_trainer_${region}_${ti}`,`conv_trainer_${region}_${ti}`,64+ri*48+ti*4,160)),
       ]),
     ]},
    ...POKEMON_REGIONS.map((region,ri)=>({type:'objectgroup',name:`Spawn_pokemon_${region}`,color:'#00cc88',
      objects:(BEAST_POOLS[region]||[]).slice(0,6).map((base,bi)=>
        makeSpawnObj(`monster_beast_${region}_${cid(base)}_t1`,64+ri*32,300+bi*32))})),
    {type:'objectgroup',name:'Keys_prevent_pokemon',color:'#ff0000',
     objects:[makeKeyObj('pokemon_ban_zone','conv_prevent_pokemon',32,32,[{name:'trigger',value:'onEnter'}])]},
    {type:'objectgroup',name:'Keys_prevent_overworld',color:'#0000ff',
     objects:[makeKeyObj('overworld_ban_zone','conv_prevent_overworld',64,32,[{name:'trigger',value:'onEnter'}])]},
  ], 80, 80));

  maps.push(makeStandardMap('template_holiday.tmx', [
    ...HOLIDAYS.map((h,hi)=>({type:'objectgroup',name:`Keys_holiday_${h.id}`,
      objects:[makeKeyObj(`holiday_trigger_${h.id}`,`conv_holiday_replace_${h.id}`,32,32+hi*32,[
        {name:'replaceLayer_Objects',  value:`Objects_${h.id}`},
        {name:'replaceLayer_Above',    value:`Above_${h.id}`},
        {name:'replaceLayer_Walkable', value:`Walkable_${h.id}`},
        {name:'startDate',             value:h.monthDay},
        {name:'weeksBefore',           value:String(h.weeksBefore)},
        {name:'weeksAfter',            value:String(h.weeksAfter)},
      ])]})),
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
  ], 60, 60));

  maps.push(makeStandardMap('template_overworld.tmx', [
    {type:'objectgroup',name:'Keys_prevent_pokemon',color:'#ff0000',
     objects:[makeKeyObj('pokemon_ban_zone','conv_prevent_pokemon',32,32,[{name:'trigger',value:'onEnter'}])]},
    {type:'objectgroup',name:'Keys_prevent_overworld',color:'#0000ff',
     objects:[makeKeyObj('overworld_ban_zone','conv_prevent_overworld',32,64,[{name:'trigger',value:'onEnter'}])]},
  ], 60, 60));

  maps.push(makeStandardMap('home.tmx', [
    {type:'objectgroup',name:'Objects_home',color:'#ddaa00',
     objects:[
       makeKeyObj('home_console','conv_game_console',64,64),
       makeKeyObj('home_computer','conv_computer',96,64),
       makeKeyObj('home_stove','conv_stove',128,64),
       makeKeyObj('home_garden','conv_garden',160,64),
       makeKeyObj('home_bench','conv_crafting_bench',192,64),
       makeKeyObj('home_forge1','conv_smithing_forge',224,64),
       makeKeyObj('home_forge2','conv_miners_forge',256,64),
       makeKeyObj('home_loom','conv_loom',288,64),
     ]},
    {type:'objectgroup',name:'Spawn_home',color:'#dddd00',
     objects:[
       makeNPCObj('npc_npc_butler','conv_npc_butler',64,96,[{name:'requiresItem',value:'item_deed_luxury_home'}]),
       makeNPCObj('npc_timekeeper','conv_timekeeper',96,96),
     ]},
  ]));

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
  ]));

  maps.push(makeStandardMap('astral_spire.tmx', [
    {type:'objectgroup',name:'Objects_astral',color:'#8800ff',
     objects:[
       makeKeyObj('astral_logout_scroll','conv_logout_scroll',96,96,[{name:'giveItem',value:'item_logout_scroll'}]),
       makeKeyObj('astral_pokemon_ban','conv_prevent_overworld',32,32,[{name:'trigger',value:'onEnter'}]),
     ]},
    {type:'objectgroup',name:'Spawn_astral',color:'#9900ff',
     objects:POKEMON_REGIONS.slice(0,3).flatMap((region,ri)=>
       (BEAST_POOLS[region]||[]).slice(0,2).map((base,bi)=>
         makeSpawnObj(`monster_beast_${region}_${cid(base)}_t1`,64+ri*64+bi*32,160)))},
  ]));

  maps.push(makeStandardMap('lpc_church.tmx', [
    {type:'objectgroup',name:'Objects_church',color:'#ff8800',
     objects:[
       makeKeyObj('church_logout','conv_logout_scroll',96,96,[{name:'giveItem',value:'item_logout_scroll'}]),
       makeKeyObj('church_pokemon_ban','conv_prevent_overworld',32,32,[{name:'trigger',value:'onEnter'}]),
     ]},
    {type:'objectgroup',name:'Spawn_church',color:'#ff9900',
     objects:[
       makeNPCObj('npc_church_priest','conv_church_priest',64,128),
       makeNPCObj('npc_church_monk','conv_church_monk',96,128),
       ...range(5).map(i=>makeSpawnObj(`monster_lloth_guard_${i}`,160+i*32,200)),
     ]},
  ]));

  maps.push(makeStandardMap('ring_clearing.tmx', [
    {type:'objectgroup',name:'Keys_ring_clearing',color:'#ffdd00',
     objects:[
       makeKeyObj('ring_search','conv_sunny_ring_search',96,96),
       makeSignObj('sign_north',128,64,'North: Drow Village'),
       makeSignObj('sign_south',128,128,'South: Rocket Pad'),
       makeSignObj('sign_east',160,96,'East: Forest'),
       makeSignObj('sign_west',96,96,'West: Lake'),
       ...MOON_COLORS.flatMap((color,i)=>[
         makeKeyObj(`rocket_c_${cid(color)}_1`,`conv_rocket_${cid(color)}`,256+i*32,96),
         makeKeyObj(`rocket_c_${cid(color)}_2`,`conv_rocket_${cid(color)}`,256+i*32,128),
       ]),
     ]},
    {type:'objectgroup',name:'Spawn_ring_clearing',color:'#aaddff',
     objects:[makeNPCObj('npc_ring_guard','conv_ring_guard',96,160)]},
  ]));

  maps.push(makeStandardMap('swamp_witch.tmx', [
    {type:'objectgroup',name:'Spawn_witch',color:'#8800ff',
     objects:[makeNPCObj('npc_witch','conv_witch',96,96),...range(4).map(i=>makeSpawnObj(`monster_witch_${i}`,128+i*32,128))]},
    {type:'objectgroup',name:'Keys_witch',color:'#440088',
     objects:[makeKeyObj('witch_search_1','conv_witch_search',192,128),makeKeyObj('witch_search_2','conv_witch_search',224,128)]},
  ]));

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
  ]));

  maps.push(makeStandardMap('lloth_realm.tmx', [
    {type:'objectgroup',name:'Spawn_lloth',color:'#ff00ff',
     objects:[
       makeNPCObj('npc_lloth','conv_lloth',96,96),
       ...range(7).map(i=>makeSpawnObj(`monster_lloth_guard_${i}`,64+i*32,128)),
     ]},
  ]));

  maps.push(makeStandardMap('volcano.tmx', [
    {type:'objectgroup',name:'Spawn_dragon',color:'#ff4400',
     objects:[
       ...DRAGON_TYPES.flatMap((type,ti)=>DRAGON_AGES.map((age,ai)=>
         makeNPCObj(`dragon_${cid(type)}_${age}`,`conv_dragon_${cid(type)}_adult`,64+ti*32,64+ai*32))),
       makeNPCObj('dragon_ancient_platinum','conv_dragon_ancient_platinum',64,192),
       makeNPCObj('dragon_ancient_chromatic','conv_dragon_ancient_chromatic',96,192),
       makeKeyObj('dragon_dispute_complete','conv_dragon_dispute_complete',128,192),
     ]},
  ]));

  maps.push(makeStandardMap('castle.tmx', [
    {type:'objectgroup',name:'Spawn_castle',color:'#884400',
     objects:[
       makeNPCObj('npc_ozzy','conv_npc_ozzy',64,64),
       makeNPCObj('npc_nymph','conv_npc_nymph',96,64),
       makeNPCObj('npc_guard_captain','conv_npc_guard_captain',128,64),
       makeNPCObj('npc_head_cook','conv_npc_head_cook',64,96),
       makeNPCObj('npc_librarian','conv_npc_librarian',96,96),
       makeNPCObj('npc_gardener','conv_npc_gardener',128,96),
       makeNPCObj('npc_castle_weaponer','conv_castle_weaponer',64,128),
       makeNPCObj('npc_castle_armorer','conv_castle_armorer',96,128),
       makeNPCObj('npc_castle_alchemist','conv_castle_alchemist',128,128),
       makeNPCObj('npc_timekeeper','conv_timekeeper',160,128),
     ]},
  ]));

  maps.push(makeStandardMap('crystal_towers.tmx', [
    {type:'objectgroup',name:'Spawn_tower_npc',color:'#ffaa00',
     objects:[makeNPCObj('npc_crystal_grandmaster','conv_crystal_grandmaster',64,64)]},
  ], 50, 50));

  ['haunted_house','haunted_mansion','haunted_prison','graveyard','crypt','mausoleum'].forEach(place => {
    maps.push(makeStandardMap(`${cid(place)}.tmx`, [
      {type:'objectgroup',name:`Spawn_${cid(place)}`,color:'#440044',
       objects:[
         ...range(25).map(gi=>makeSpawnObj(`monster_${cid(place)}_${gi}`,64+gi%8*32,64+Math.floor(gi/8)*32)),
         makeSpawnObj(`monster_boss_${cid(place)}`,96,256),
       ]},
    ]));
  });

  MOON_COLORS.forEach(color => {
    maps.push(makeStandardMap(`moon_${cid(color)}.tmx`, [
      {type:'objectgroup',name:`Spawn_moon_${cid(color)}`,color:'#aaaaff',
       objects:[
         makeNPCObj(`npc_moon_elder_${cid(color)}`,`conv_moon_elder_${cid(color)}`,96,96),
         ...range(12).map(j=>makeSpawnObj(`npc_moon_drow_${cid(color)}_${j}`,64+j%8*32,128+Math.floor(j/8)*32)),
         makeKeyObj(`rocket_back_${cid(color)}`,`conv_rocket_${cid(color)}`,64,192),
         makeNPCObj('npc_sunny','conv_npc_sunny',160,192,[{name:'requiresCondition',value:'all_moon_quests_done'}]),
       ]},
    ]));
  });

  maps.push(makeStandardMap('pokemon_gym.tmx', [
    {type:'objectgroup',name:'Spawn_gym_npcs',color:'#00ffaa',
     objects:POKEMON_REGIONS.flatMap((region,ri)=>[
       makeNPCObj(`monster_gym_leader_${region}`,`conv_gym_leader_${region}`,64+ri*48,64),
       ...range(12).map(ti=>makeNPCObj(`monster_trainer_${region}_${ti}`,`conv_trainer_${region}_${ti}`,64+ri*48,96+ti*32)),
     ])},
  ], 60, 60));

  const extraConvs = [
    makeConversation('conv_logout_scroll','Pick up a logout scroll? It will return you to the room where you entered.',
      [{text:'Take scroll', nextPhraseID:'X'}, {text:'Leave', nextPhraseID:'X'}],
      [rGiveItem('item_logout_scroll')]
    ),
    makeConversation('conv_church_priest','Welcome to the LPC Church virtual world! Seek knowledge and enlightenment here.',
      [{text:'Thank you.', nextPhraseID:'X'}]
    ),
    makeConversation('conv_church_monk','Meditation brings clarity. Stay as long as you wish.',
      [{text:'I will.', nextPhraseID:'X'}]
    ),
    ...MOON_COLORS.map(color=>makeConversation(`conv_rocket_${cid(color)}`,
      `A ${color.toLowerCase()} rocket ship bound for the ${color} Moon!`,
      [{text:'Launch!', nextPhraseID:'X'}, {text:'Not yet.', nextPhraseID:'X'}]
    )),
    ...HOLIDAYS.map(h=>makeConversation(`conv_holiday_replace_${h.id}`,
      `The area has transformed for ${h.name}!`,
      [{text:'Magical!', nextPhraseID:'X'}]
    )),
    ...EVENTS.map(event=>makeConversation(`conv_event_replace_${event}`,
      `The area has been decorated for the ${event}!`,
      [{text:'Lovely!', nextPhraseID:'X'}]
    )),
    makeConversation('conv_npc_gate_guard','I spotted something suspicious outside. Investigate?',
      [{text:'Accept quest', nextPhraseID:'conv_npc_gate_guard_quest'}, {text:'Leave', nextPhraseID:'X'}]
    ),
    makeConversation('conv_npc_gate_guard_quest','Thank you! Return with your findings.',
      [{text:"I'll look into it.", nextPhraseID:'X'}],
      [rQuestProgress('quest_npc_gate_guard',10)]
    ),
    makeConversation('conv_npc_prison_warden','Order is maintained in my prison.',
      [{text:'Accept quest', nextPhraseID:'conv_npc_prison_warden_quest'}, {text:'Leave', nextPhraseID:'X'}]
    ),
    makeConversation('conv_npc_prison_warden_quest','Good. Report back to me.',
      [{text:"I'll handle it.", nextPhraseID:'X'}],
      [rQuestProgress('quest_npc_prison_warden',10)]
    ),
  ];

  return {maps, extraConvs};
}

// ─── LOAD RESOURCES XML (v7 — pattern-based matching for split files) ─────────
function buildLoadResourcesXml(jsonFiles, tmxFiles) {
  function getArrayName(filename) {
    const base = filename.split('/').pop();
    if (base.startsWith('itemcategories_'))   return 'loadresource_itemcategories';
    if (base.startsWith('itemlist_'))         return 'loadresource_items';
    if (base.startsWith('actorconditions_'))  return 'loadresource_actorconditions';
    if (base.startsWith('monsterlist_'))      return 'loadresource_monsters';
    if (base.startsWith('droplists_'))        return 'loadresource_droplists';
    if (base.startsWith('conversationlist_')) return 'loadresource_conversationlists';
    if (base.startsWith('questlist_'))        return 'loadresource_quests';
    return null;
  }
  const groups = {};
  for (const f of jsonFiles) {
    const baseName  = f.split('/').pop();
    const arrayName = getArrayName(f);
    if (!arrayName) continue;
    if (!groups[arrayName]) groups[arrayName] = [];
    groups[arrayName].push(`@raw/${baseName.replace('.json','')}`);
  }
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

// ─── README ──────────────────────────────────────────────────────────────────
function buildReadme(tmxFiles, jsonFiles) {
  const byPrefix = {};
  for (const f of jsonFiles) {
    const b = f.split('/').pop();
    const match = b.match(/^([a-z]+list|actorconditions|droplists|itemcategories)_([a-z_]+)_jasia\.json$/);
    if (match) {
      const cat = match[2];
      if (!byPrefix[cat]) byPrefix[cat] = [];
      byPrefix[cat].push(b);
    }
  }
  const splitSummary = Object.entries(byPrefix)
    .sort(([a],[b])=>a.localeCompare(b))
    .map(([cat,files])=>`- **_${cat}**: ${files.join(', ')}`)
    .join('\n');

  return `# Andor's Trail Extended Content Pack v7
## Developer Reference

### Format Compliance
All JSON files in this pack comply with the Andor's Trail content format specification:
- **Items**: names and descriptions are plain text strings; displaytype field used instead of isQuestItem; equipment stats in equipEffect; iconID uses "spritesheetname:linearIndex" format
- **Monsters/NPCs**: name is plain text; all stats are top-level fields; attackDamage replaces damagePotential
- **Conversations**: message is plain text; replies use nextPhraseID + requires[]; rewards use AT rewardType/rewardID/value
- **Quests**: name and logText are plain text strings
- **Actor conditions**: name is plain text; category field is always set
- **Droplists**: chance is always a string (e.g. "100")
- **No @string/ references** anywhere in JSON content files

### v7 Change — Split JSON Files
In v7, the monolithic *_jasia.json files from v5 are split by content category.
Each category produces its own set of JSON files that are all registered in loadresources.xml.
The loadresources.xml uses pattern-based array name resolution (itemlist_* → loadresource_items, etc.)
so any number of split files can be added without changing the XML structure.

#### Split categories and their files
${splitSummary}

- **_jasia** (no category prefix): quest items, monsters, conversations, droplists

### What's Included

| Category | Count |
|---|---|
| TMX Map Files | ${tmxFiles.length} |
| JSON Data Files | ${jsonFiles.length} |
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
Tilesets: 60 AT tilesets (map_bed_1 … map_transition_5)
Tile Layers (base64+zlib encoded, all blank):
  Base, Ground, Objects, Objects_replace, Above, Above_replace, Top, Walkable
Object Layers — Mapevents, Spawn, Keys, Replace (+ extra named groups)
\`\`\`

---

### Integration Checklist
1. Copy all \`.tmx\` files to your \`maps/\` directory
2. Copy all \`.json\` files to \`res/raw/\` in your game source
3. Add \`values/loadresources.xml\` array entries to your resource loading list
4. Required tileset images: see AT_TILESETS list in the generator source

---

### Content File Naming Convention (per AT spec, v7 split)
- Items:           \`itemlist_<category>.json\` or \`itemlist.json\`
- Monsters/NPCs:   \`monsterlist_<category>.json\` or \`monsterlist.json\`
- Conversations:   \`conversationlist_<category>.json\` or \`conversationlist.json\`
- Quests:          \`questlist_<category>.json\` or \`questlist.json\`
- Actor conditions:\`actorconditions_<category>.json\` or \`actorconditions.json\`
- Droplists:       \`droplists_<category>.json\` or \`droplists.json\`
- Item categories: \`itemcategories.json\` (single file)

---

*Andor's Trail Extended Content Pack v7 — Generated May 2026*
`;
}

// ─── MAIN ─────────────────────────────────────────────────────────────────────
async function main() {
  console.log("=== Andor's Trail Content Generator v7 ===");
  console.log('    Split JSON files by content category (v7 feature)');
  console.log('    All names/descriptions in JSON; no @string/ references');
  console.log('    Correct AT format per ContentFormatReference spec\n');

  console.log('[Building content...]');
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
  const { maps, extraConvs } = generateAllMaps();

  // Deduplicate by id
  const dedup = arr => { const seen=new Set(); return arr.filter(x=>x&&x.id&&!seen.has(x.id)&&seen.add(x.id)); };

  console.log('[Assembling ZIP with split category files...]\n');

  const zipFiles = [];
  function addJson(name, obj) { zipFiles.push({name, data:JSON.stringify(obj, null, 2)}); }
  function addText(name, content) { zipFiles.push({name, data:content}); }

  // ─── ITEM SPLITS ──────────────────────────────────────────────────────────
  addJson('raw/itemlist_animal.json',     dedup(animalData.items));
  addJson('raw/itemlist_forage.json',     dedup(forageData.items));
  addJson('raw/itemlist_mining.json',     dedup(miningData.items));
  addJson('raw/itemlist_crafting.json',   dedup(craftingData.items));
  addJson('raw/itemlist_pickpocket.json', dedup(pickpocket.items));
  addJson('raw/itemlist_holiday.json',    dedup(timekeeper.items));
  addJson('raw/itemlist_beast.json',      dedup(pokemonData.items));
  addJson('raw/itemlist_faction.json',    dedup(factionData.items));

  // Guild items — split door keys, steal items, guild core
  const _guildItemsAll = dedup(guildItems.items);
  const _doorItems     = _guildItemsAll.filter(i => i.category === 'key');
  const _stealItems    = _guildItemsAll.filter(i => i.id && i.id.startsWith('stolen_item_'));
  const _guildCore     = _guildItemsAll.filter(i => !_doorItems.includes(i) && !_stealItems.includes(i));
  addJson('raw/itemlist_door.json',       _doorItems);
  addJson('raw/itemlist_steal.json',      _stealItems);
  addJson('raw/itemlist_guild.json',      _guildCore);
  // Quest items (remaining)
  addJson('raw/itemlist_jasia.json',            dedup(questData.items));

  // ─── MONSTER SPLITS ───────────────────────────────────────────────────────
  addJson('raw/monsterlist_animal.json',     dedup(animalData.monsters));
  addJson('raw/monsterlist_faction.json',    dedup(factionData.monsters));
  addJson('raw/monsterlist_beast.json',      dedup(pokemonData.monsters));
  addJson('raw/monsterlist_pickpocket.json', dedup(pickpocket.monsters));
  addJson('raw/monsterlist_jasia.json',            dedup(questData.monsters));

  // ─── DROPLIST SPLITS ──────────────────────────────────────────────────────
  addJson('raw/droplists_animal.json',     dedup(animalData.droplists));
  addJson('raw/droplists_mining.json',     dedup(miningData.droplists));
  addJson('raw/droplists_beast.json',      dedup(pokemonData.droplists));
  addJson('raw/droplists_pickpocket.json', dedup(pickpocket.droplists));
  addJson('raw/droplists_jasia.json',            dedup(questData.droplists));

  // ─── CONVERSATION SPLITS ──────────────────────────────────────────────────
  // Split guildConvs.conversations by ID prefix
  const _allGuildConvs = dedup(guildConvs.conversations);
  const CRAFTING_CONV_IDS = new Set([
    'conv_loom','conv_stove','conv_garden','conv_smithing_forge','conv_crafting_bench',
    'conv_miners_forge','conv_game_console','conv_computer','conv_fighters_forge',
    'conv_writing_desk','conv_cauldron','conv_crafting_table','conv_crafting_sign',
    'conv_desk_mage','conv_desk_cleric','conv_desk_druid',
  ]);
  const _doorConvs     = _allGuildConvs.filter(c => c.id.startsWith('conv_door'));
  const _bankConvs     = _allGuildConvs.filter(c => c.id.startsWith('conv_bank'));
  const _jailConvs     = _allGuildConvs.filter(c => c.id.startsWith('conv_jail'));
  const _craftingConvs = _allGuildConvs.filter(c => CRAFTING_CONV_IDS.has(c.id));
  const _stealConvs    = _allGuildConvs.filter(c => c.id.startsWith('conv_home_loot'));
  const _guildCoreConvs = _allGuildConvs.filter(c =>
    !_doorConvs.includes(c) && !_bankConvs.includes(c) && !_jailConvs.includes(c) &&
    !_craftingConvs.includes(c) && !_stealConvs.includes(c)
  );

  // Split extraConvs: LPC church vs. rest
  const LPC_CONV_IDS = new Set(['conv_church_priest','conv_church_monk','conv_logout_scroll']);
  const _lpcConvs   = extraConvs.filter(c => LPC_CONV_IDS.has(c.id));
  const _otherConvs = extraConvs.filter(c => !LPC_CONV_IDS.has(c.id));

  addJson('raw/conversationlist_forage.json',     dedup(forageData.conversations));
  addJson('raw/conversationlist_mining.json',     dedup(miningData.conversations));
  addJson('raw/conversationlist_door.json',       _doorConvs);
  addJson('raw/conversationlist_bank.json',       _bankConvs);
  addJson('raw/conversationlist_jail.json',       _jailConvs);
  addJson('raw/conversationlist_crafting.json',   _craftingConvs);
  addJson('raw/conversationlist_steal.json',      _stealConvs);
  addJson('raw/conversationlist_guild.json',      _guildCoreConvs);
  addJson('raw/conversationlist_faction.json',    dedup(factionData.conversations));
  addJson('raw/conversationlist_beast.json',      dedup(pokemonData.conversations));
  addJson('raw/conversationlist_pickpocket.json', dedup(pickpocket.conversations));
  addJson('raw/conversationlist_holiday.json',    dedup(timekeeper.conversations));
  addJson('raw/conversationlist_lpc.json',        dedup(_lpcConvs));
  // Quest conversations + remaining extras
  addJson('raw/conversationlist_jasia.json',            dedup([...questData.conversations, ..._otherConvs]));

  // ─── QUEST SPLITS ─────────────────────────────────────────────────────────
  addJson('raw/questlist_forage.json',  dedup(forageData.quests));
  addJson('raw/questlist_guild.json',   dedup(guildConvs.quests));
  addJson('raw/questlist_faction.json', dedup(factionData.quests));
  addJson('raw/questlist_beast.json',   dedup(pokemonData.quests));
  addJson('raw/questlist_holiday.json', dedup(timekeeper.quests));
  addJson('raw/questlist_jasia.json',         dedup(questData.quests));

  // ─── ACTOR CONDITION SPLITS ───────────────────────────────────────────────
  addJson('raw/actorconditions_guild.json',   dedup(guildItems.actorconditions));
  addJson('raw/actorconditions_faction.json', dedup(factionData.actorconditions));
  addJson('raw/actorconditions_beast.json',   dedup(pokemonData.actorconditions));
  addJson('raw/actorconditions_holiday.json', dedup(timekeeper.actorconditions));
  addJson('raw/actorconditions_jasia.json',         dedup(questData.actorconditions));

  // ─── ITEM CATEGORIES (single file) ────────────────────────────────────────
  addJson('raw/itemcategories_jasia.json', [
    {id:'scroll',        name:'Scroll',        actionType:'use'},
    {id:'potion',        name:'Potion',        actionType:'use'},
    {id:'weapon',        name:'Weapon',        actionType:'equip', size:'std',   inventorySlot:'weapon'},
    {id:'shield',        name:'Shield',        actionType:'equip', size:'large', inventorySlot:'shield'},
    {id:'head',          name:'Head',          actionType:'equip', size:'std',   inventorySlot:'head'},
    {id:'body',          name:'Body',          actionType:'equip', size:'std',   inventorySlot:'body'},
    {id:'hand',          name:'Hand',          actionType:'equip', size:'light', inventorySlot:'hand'},
    {id:'feet',          name:'Feet',          actionType:'equip', size:'light', inventorySlot:'feet'},
    {id:'neck',          name:'Neck',          actionType:'equip', size:'none',  inventorySlot:'neck'},
    {id:'leftring',      name:'Left ring',     actionType:'equip', size:'none',  inventorySlot:'leftring'},
    {id:'rightring',     name:'Right ring',    actionType:'equip', size:'none',  inventorySlot:'rightring'},
    {id:'key',           name:'Key',           actionType:'use'},
    {id:'ingredient',    name:'Ingredient',    actionType:'none'},
    {id:'miscellaneous', name:'Miscellaneous', actionType:'none'},
    {id:'quest',         name:'Quest',         actionType:'none'},
    {id:'beastOrb',      name:'Beast orb',     actionType:'use'},
    {id:'seed',          name:'Seed',          actionType:'use'},
    {id:'produce',       name:'Produce',       actionType:'use'},
    {id:'crystal',       name:'Crystal',       actionType:'none'},
  ]);

  // ─── TMX MAPS ─────────────────────────────────────────────────────────────
  const tmxFileNames = [];
  for (const {path:p, tmx} of maps) {
    addText('xml/'+p, tmx);
    tmxFileNames.push(p);
    console.log('  tmx:', p);
  }

  // ─── XML RESOURCES ────────────────────────────────────────────────────────
  const jsonFileNames = zipFiles.filter(f=>f.name.endsWith('.json')).map(f=>f.name);
  addText('values/loadresources.xml', buildLoadResourcesXml(jsonFileNames, tmxFileNames));

  // ─── README ───────────────────────────────────────────────────────────────
  addText('README.md', buildReadme(tmxFileNames, jsonFileNames));

  // ─── BUILD ZIP ────────────────────────────────────────────────────────────
  const zipBuf = buildZip(zipFiles);
  const outPath = path.join(__dirname, '../andors_trail_content_v7.zip');
  fs.writeFileSync(outPath, zipBuf);

  // ─── STATS ────────────────────────────────────────────────────────────────
  const itemFiles  = jsonFileNames.filter(f=>f.startsWith('itemlist_'));
  const monFiles   = jsonFileNames.filter(f=>f.startsWith('monsterlist_'));
  const convFiles  = jsonFileNames.filter(f=>f.startsWith('conversationlist_'));
  const questFiles = jsonFileNames.filter(f=>f.startsWith('questlist_'));
  const acFiles    = jsonFileNames.filter(f=>f.startsWith('actorconditions_'));
  const dlFiles    = jsonFileNames.filter(f=>f.startsWith('droplists_'));

  console.log('\n=== COMPLETE ===');
  console.log(`  TMX maps:            ${tmxFileNames.length}`);
  console.log(`  JSON files total:    ${jsonFileNames.length}`);
  console.log(`    itemlist_* files:  ${itemFiles.length}  → ${itemFiles.map(f=>f.replace('itemlist_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`    monsterlist_*:     ${monFiles.length}  → ${monFiles.map(f=>f.replace('monsterlist_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`    conversationlist_: ${convFiles.length} → ${convFiles.map(f=>f.replace('conversationlist_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`    questlist_*:       ${questFiles.length}  → ${questFiles.map(f=>f.replace('questlist_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`    actorconditions_*: ${acFiles.length}  → ${acFiles.map(f=>f.replace('actorconditions_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`    droplists_*:       ${dlFiles.length}  → ${dlFiles.map(f=>f.replace('droplists_','').replace('_jasia.json','')).join(', ')}`);
  console.log(`  ZIP size:            ${(zipBuf.length/1024).toFixed(0)}KB`);
  console.log(`  Output:              andors_trail_content_v7.zip`);
}

main().catch(err => { console.error(err); process.exit(1); });



// ─── v7 USER PATCHES ─────────────────────────────────────────────────────────

// D&D inspired animal drop materials
const DND_ANIMAL_PARTS = [
  'wolf_pelt','wolf_claw','wolf_fang',
  'bear_fur','bear_claw','bear_gallbladder',
  'eagle_feather','eagle_talon',
  'spider_eye','venom_sac',
  'boar_tusk','boar_hide',
  'rat_tail','rat_fur',
  'bat_wing','bat_fang',
  'serpent_scale','serpent_fang'
];

// D&D inspired stolen goods
const DND_STOLEN_GOODS = [
  'silver_cutlery',
  'locked_jewelry_box',
  'family_heirloom_ring',
  'merchant_ledger',
  'noble_candelabra',
  'silk_bed_sheets',
  'kitchen_spices',
  'antique_coin_pouch',
  'house_key_ring',
  'gemstone_necklace',
  'wax_sealed_documents',
  'fine_wine_bottle'
];

// Generate itemcategories_at.json
writeJson(
  path.join(OUT_DIR, 'AndorsTrail/res/raw/itemcategories_at.json'),
  {
    categories: [
      'animal_part',
      'stolen_goods',
      'currency',
      'ingredient',
      'miscellaneous'
    ]
  }
);

console.log('Applied user requested D&D loot and category extensions.');
