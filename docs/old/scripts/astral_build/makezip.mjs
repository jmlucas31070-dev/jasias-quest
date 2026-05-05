// Minimal pure-Node ZIP writer (deflate). No external deps.
import { readFileSync, writeFileSync, statSync, readdirSync } from "node:fs";
import { join, relative, sep } from "node:path";
import { deflateRawSync } from "node:zlib";

const ROOT = process.argv[2];
const OUT  = process.argv[3];
if (!ROOT || !OUT) { console.error("usage: makezip.mjs <root> <out.zip>"); process.exit(2); }

function walk(dir, acc = []) {
  for (const ent of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, ent.name);
    if (ent.isDirectory()) walk(p, acc);
    else if (ent.isFile()) acc.push(p);
  }
  return acc;
}

// CRC32
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1;
    t[n] = c >>> 0;
  }
  return t;
})();
function crc32(buf) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) c = CRC_TABLE[(c ^ buf[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

function dosTime(d = new Date()) {
  const time = ((d.getHours() & 0x1F) << 11) | ((d.getMinutes() & 0x3F) << 5) | ((d.getSeconds() / 2) & 0x1F);
  const date = (((d.getFullYear() - 1980) & 0x7F) << 9) | (((d.getMonth() + 1) & 0x0F) << 5) | (d.getDate() & 0x1F);
  return { time, date };
}

const files = walk(ROOT).sort();
const localChunks = [];
const central = [];
let offset = 0;

for (const filePath of files) {
  const rel = relative(ROOT, filePath).split(sep).join("/");
  const data = readFileSync(filePath);
  const crc = crc32(data);
  const compressed = deflateRawSync(data, { level: 9 });
  const useDeflate = compressed.length < data.length;
  const payload = useDeflate ? compressed : data;
  const method = useDeflate ? 8 : 0;
  const { time, date } = dosTime(new Date(statSync(filePath).mtime));
  const nameBuf = Buffer.from(rel, "utf8");

  const local = Buffer.alloc(30 + nameBuf.length);
  local.writeUInt32LE(0x04034b50, 0);          // local file header sig
  local.writeUInt16LE(20, 4);                  // version needed
  local.writeUInt16LE(0x0800, 6);              // gp flags: bit 11 = utf-8 names
  local.writeUInt16LE(method, 8);
  local.writeUInt16LE(time, 10);
  local.writeUInt16LE(date, 12);
  local.writeUInt32LE(crc, 14);
  local.writeUInt32LE(payload.length, 18);
  local.writeUInt32LE(data.length, 22);
  local.writeUInt16LE(nameBuf.length, 26);
  local.writeUInt16LE(0, 28);                  // extra field len
  nameBuf.copy(local, 30);

  localChunks.push(local, payload);

  const cd = Buffer.alloc(46 + nameBuf.length);
  cd.writeUInt32LE(0x02014b50, 0);             // central dir sig
  cd.writeUInt16LE(0x031E, 4);                 // version made by (Unix, v3.0)
  cd.writeUInt16LE(20, 6);                     // version needed
  cd.writeUInt16LE(0x0800, 8);                 // gp flags
  cd.writeUInt16LE(method, 10);
  cd.writeUInt16LE(time, 12);
  cd.writeUInt16LE(date, 14);
  cd.writeUInt32LE(crc, 16);
  cd.writeUInt32LE(payload.length, 20);
  cd.writeUInt32LE(data.length, 24);
  cd.writeUInt16LE(nameBuf.length, 28);
  cd.writeUInt16LE(0, 30);                     // extra
  cd.writeUInt16LE(0, 32);                     // comment
  cd.writeUInt16LE(0, 34);                     // disk no
  cd.writeUInt16LE(0, 36);                     // int attrs
  cd.writeUInt32LE(0o644 << 16, 38);           // ext attrs (unix mode 0644)
  cd.writeUInt32LE(offset, 42);                // offset of local header
  nameBuf.copy(cd, 46);
  central.push(cd);

  offset += local.length + payload.length;
}

const cdStart = offset;
const cdBuf = Buffer.concat(central);
const eocd = Buffer.alloc(22);
eocd.writeUInt32LE(0x06054b50, 0);             // EOCD sig
eocd.writeUInt16LE(0, 4);                      // disk no
eocd.writeUInt16LE(0, 6);                      // disk start of cd
eocd.writeUInt16LE(central.length, 8);         // entries this disk
eocd.writeUInt16LE(central.length, 10);        // total entries
eocd.writeUInt32LE(cdBuf.length, 12);          // cd size
eocd.writeUInt32LE(cdStart, 16);               // cd offset
eocd.writeUInt16LE(0, 20);                     // comment len

writeFileSync(OUT, Buffer.concat([...localChunks, cdBuf, eocd]));
console.log(`wrote ${OUT}: ${central.length} entries, ${(statSync(OUT).size / 1024).toFixed(1)} KB`);
