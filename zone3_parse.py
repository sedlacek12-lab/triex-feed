"""Načíta katalógový feed ZONE3 (Sportkoncept) a zoskupí varianty do produktov.

Použitie:  python zone3_parse.py <cesta_k_xml_alebo_url> <vystup.json>
"""
import json, re, sys, html, urllib.request
import xml.etree.ElementTree as ET

FEED_URL = "https://b2b.levelsportkoncept.cz/files/RESULT26_ZONE3.xml"


def load(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=120) as r:
            data = r.read()
    else:
        data = open(src, "rb").read()
    return ET.fromstring(data)  # hlavička XML hovorí windows-1250, ElementTree to dekóduje sám


def clean_html(s):
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"(?i)</?div[^>]*>", "", s)
    s = re.sub(r"<p>(\s|&nbsp;|\xa0)*</p>", "", s)
    return s.strip()


def base_name(name):
    # "Men's Vision / Black/Lime / S" -> "Men's Vision"
    return name.split(" / ")[0].strip()


def item_dict(it):
    imgs = [i.text for i in it.findall("images/image") if i.text]
    params = {p.findtext("name"): p.findtext("value") for p in it.findall("params/param")
              if p.findtext("name") != "Fotografie"}
    return {
        "oid": it.findtext("OID"),
        "code": it.findtext("PRODUCTCODE"),
        "name": it.findtext("PRODUCTNAME"),
        "ean": (it.findtext("EAN") or "").lstrip("0") or None,
        "category": it.findtext("CATEGORYTEXT"),
        "variant": it.findtext("VARIANT"),
        "colour": it.findtext("COLOUR"),
        "weight": float(it.findtext("WEIGHT") or 0),
        "tags": [t.strip() for t in (it.findtext("SPECIFICATIONS") or "").split(",")
                 if t.strip() and t.strip() != "xml"],
        "params": params,
        "images": imgs,
        "description_cs": clean_html(it.findtext("DESCRIPTION")),
        "parent": it.findtext("PARENT"),
    }


def group(root):
    items = [item_dict(i) | {"is_parent": i.findtext("PARENTITEM") == "1"} for i in root.iter("item")]
    parents = {i["oid"]: i for i in items if i["is_parent"]}
    products = {}
    for it in items:
        if it["is_parent"]:
            continue
        key = it["parent"] if it["parent"] in parents else "solo:" + it["oid"]
        p = products.get(key)
        if not p:
            src = parents.get(it["parent"], it)
            p = products[key] = {
                "code": src["code"].split("_")[0],
                "name_cs": base_name(src["name"]),
                "colour": src["colour"],
                "category": src["category"],
                "images": list(src["images"]),
                "description_cs": src["description_cs"],
                "variants": [],
            }
        if not p["description_cs"] and it["description_cs"]:
            p["description_cs"] = it["description_cs"]
        for img in it["images"]:
            if img not in p["images"]:
                p["images"].append(img)
        p["variants"].append({k: it[k] for k in ("code", "ean", "variant", "weight", "params", "tags")})
    return list(products.values())


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else FEED_URL
    out = sys.argv[2] if len(sys.argv) > 2 else "zone3_products.json"
    prods = group(load(src))
    json.dump(prods, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(prods)} produktov, {sum(len(p['variants']) for p in prods)} variantov -> {out}")
