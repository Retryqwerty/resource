
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timezone
import hashlib
import sqlite3

db = sqlite3.connect("game.db", check_same_thread=False)
db.execute('''CREATE TABLE IF NOT EXISTS claims(
  cell TEXT PRIMARY KEY,
  user TEXT NOT NULL,
  resource TEXT NOT NULL,
  richness INTEGER NOT NULL,
  quality INTEGER NOT NULL,
  claimed_at TEXT NOT NULL
)''')

app = FastAPI(title="Geo Resource MVP API", version="0.1.0")

def seeded_randints(key: str, n: int) -> list[int]:
    h = hashlib.sha256(key.encode("utf-8")).digest()
    out = []
    for i in range(n):
        b = hashlib.sha256(h + bytes([i])).digest()
        out.append(int.from_bytes(b[:4], "big"))
    return out

def scan_cell(cell_id: str) -> Dict[str, Any]:
    r = seeded_randints(cell_id, 3)
    pick = r[0] % 1000
    if pick < 300: res = "IRON"
    elif pick < 520: res = "COPPER"
    elif pick < 770: res = "OIL"
    elif pick < 930: res = "GAS"
    elif pick < 975: res = "CRYSTAL"
    else: res = "URANIUM"
    richness = 50 + (r[1] % 350)
    quality  = 1 + (r[2] % 6)
    return {"cell": cell_id, "resource": res, "richness": richness, "quality": quality}

class ScanReq(BaseModel):
    lat: float
    lon: float
    precision: int = 7

class ClaimReq(BaseModel):
    user: str
    cell: str

BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"
def geohash(lat: float, lon: float, precision: int = 7) -> str:
    lat_int = [-90.0, 90.0]
    lon_int = [-180.0, 180.0]
    bits = []
    even = True
    while len(bits) < precision * 5:
        if even:
            mid = (lon_int[0] + lon_int[1]) / 2
            if lon > mid:
                bits.append(1); lon_int[0] = mid
            else:
                bits.append(0); lon_int[1] = mid
        else:
            mid = (lat_int[0] + lat_int[1]) / 2
            if lat > mid:
                bits.append(1); lat_int[0] = mid
            else:
                bits.append(0); lat_int[1] = mid
        even = not even
    h = ""
    for i in range(0, len(bits), 5):
        val = 0
        for b in bits[i:i+5]:
            val = (val << 1) | b
        h += BASE32[val]
    return h

@app.post("/scan")
def scan(req: ScanReq):
    cell = geohash(req.lat, req.lon, req.precision)
    info = scan_cell(cell)
    return {"cell": cell, "scan": info}

@app.post("/claim")
def claim(req: ClaimReq):
    info = scan_cell(req.cell)
    try:
        db.execute("INSERT INTO claims(cell, user, resource, richness, quality, claimed_at) VALUES(?,?,?,?,?,?)",
                   (req.cell, req.user, info["resource"], info["richness"], info["quality"],
                    datetime.now(timezone.utc).isoformat()))
        db.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Cell already claimed")
    return {"ok": True, "claimed": info}

@app.get("/claims")
def list_claims():
    cur = db.execute("SELECT cell, user, resource, richness, quality, claimed_at FROM claims ORDER BY claimed_at DESC LIMIT 500")
    rows = [
        {"cell": cell, "user": user, "resource": resource, "richness": richness, "quality": quality, "claimed_at": ts}
        for (cell, user, resource, richness, quality, ts) in cur
    ]
    return {"claims": rows}
