"""Vyrobí aktualizačný XML feed vo formáte Shoptet pre ZONE3 produkty na TRIEX.sk.

Feed náhrada za Napojse: Shoptet automatický import #9 (párovanie podľa kódu produktu)
si ho sťahuje a aktualizuje sklad, cenu, dostupnosť a viditeľnosť.

- produkty dodávateľa: sklad = sklad dodávateľa, cena podľa pricing_rules.json,
  viditeľné len ak má aspoň jedna veľkosť sklad, inak skryté
- staré produkty, ktoré dodávateľ už nemá (zone3_skryt_stare.json): sklad 0, skryté
- vlastný sklad TRIEX (zone3_vlastny_sklad.json): do feedu sa nedostanú, ostanú bez zmeny

Použitie:
  python build_feed.py <vystup.xml> [--catalog SUBOR_ALEBO_URL] [--avail SUBOR_ALEBO_URL]
Bez parametrov berie URL z config.local.json alebo z premenných prostredia
ZONE3_CATALOG_URL / ZONE3_AVAILABILITY_URL (pre GitHub Actions).
"""
import argparse, json, os, sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

import pricing, zone3_availability, zone3_parse, zone3_texts

HERE = os.path.dirname(os.path.abspath(__file__))
AV_IN = "Skladom (doručenie do 4 dní)"
AV_OUT = "Vypredané"


def cfg_value(key, env):
    if os.environ.get(env):
        return os.environ[env]
    p = os.path.join(HERE, "config.local.json")
    if os.path.exists(p):
        return json.load(open(p))[key]
    sys.exit(f"Chýba {env} alebo config.local.json")


def load_json(name):
    return json.load(open(os.path.join(HERE, name), encoding="utf-8"))


def sub(parent, tag, text=None):
    el = ET.SubElement(parent, tag)
    if text is not None:
        el.text = str(text)
    return el


def stock_block(parent, amount):
    st = sub(parent, "STOCK")
    sub(st, "AMOUNT", amount)


def size_param(el, size):
    ps = sub(el, "PARAMETERS")
    pa = sub(ps, "PARAMETER")
    sub(pa, "NAME", "Veľkosť")
    sub(pa, "VALUE", size or "univerzálna")


def variant_fields(el, amount, price):
    stock_block(el, amount)
    sub(el, "AVAILABILITY_OUT_OF_STOCK", AV_OUT)
    sub(el, "AVAILABILITY_IN_STOCK", AV_IN)
    sub(el, "NEGATIVE_AMOUNT", 0)          # zákaz predaja do mínusu
    if price is not None:
        sub(el, "CURRENCY", "EUR")
        sub(el, "VAT", 23)
        sub(el, "PRICE_VAT", f"{price:.2f}")


APPAREL = {"wetsuit", "swimrun", "trisuit", "trishorts", "tritop", "womenswim", "jammer", "menswim", "swimskin", "neoacc"}


EXTRA_IMG = json.load(open(os.path.join(HERE, "zone3_obrazky.json"))) if os.path.exists(os.path.join(HERE, "zone3_obrazky.json")) else {}


def images_for(p):
    """Fotky dodávateľa; ak chýbajú, oficiálne fotky z zone3.com (zone3_obrazky.json)."""
    return p["images"] or EXTRA_IMG.get(p["code"], [])


def product_details(item, p, texts):
    """Údaje pre založenie nového produktu (pri existujúcich ich Shoptet ignoruje - nie sú zaškrtnuté)."""
    t = zone3_texts.build_texts(p, texts)
    sub(item, "NAME", t["nazov"])
    sub(item, "SHORT_DESCRIPTION", f"<p>{t['kratky_popis']}</p>" if not t["kratky_popis"].startswith("<") else t["kratky_popis"])
    sub(item, "DESCRIPTION", t["popis_html"])
    sub(item, "MANUFACTURER", "Zone3")
    sub(item, "SUPPLIER", "Zone3")
    sub(item, "SEO_TITLE", t["seo_title"])
    sub(item, "META_DESCRIPTION", t["meta_description"])
    cats = sub(item, "CATEGORIES")
    sub(cats, "CATEGORY", t["kategoria"])
    if images_for(p):
        imgs = sub(item, "IMAGES")
        for u in images_for(p)[:10]:
            sub(imgs, "IMAGE", u)
    if zone3_texts.detect(p["name_cs"])[3] in APPAREL:
        tp = sub(sub(item, "TEXT_PROPERTIES"), "TEXT_PROPERTY")
        sub(tp, "NAME", "#sizes_table#")
        sub(tp, "VALUE", "/tabulka-velkosti/")


def build(catalog, avail, rules, own_codes, hide_items, known_codes=frozenset(), texts=None):
    texts = texts or {}
    root = ET.Element("SHOP")
    stats = {"produkty": 0, "viditelne": 0, "skryte_dodavatel": 0, "skryte_stare": 0, "varianty": 0, "bez_ceny": 0}
    for p in catalog:
        variants = [v for v in p["variants"] if v["code"] not in own_codes]
        if not variants:
            continue
        in_stock = any(avail.get(v["code"], {}).get("sklad", 0) > 0 for v in variants)
        if not in_stock and not any(v["code"] in known_codes for v in variants):
            continue  # nemáme ho a dodávateľ ho nemá -> nezakladať
        item = sub(root, "SHOPITEM")
        any_stock = False
        rows = []
        for v in variants:
            a = avail.get(v["code"])
            amount = a["sklad"] if a else 0
            price = None
            if a and a["moc_eur"]:
                price = pricing.propose(a["nakup_eur"], a["moc_eur"], [], rules)["cena"]
            else:
                stats["bez_ceny"] += 1
            any_stock |= amount > 0
            rows.append((v, amount, price))
        fallback = next((r[2] for r in rows if r[2] is not None), None)
        rows = [(v, a, pr if pr is not None else fallback) for v, a, pr in rows]
        if any_stock:
            product_details(item, p, texts)
        exists = any(v["code"] in known_codes for v in variants)
        show = any_stock and (exists or bool(images_for(p)))   # nový produkt bez fotky nepredávame
        sub(item, "VISIBILITY", "visible" if show else "hidden")
        if len(rows) == 1 and (rows[0][0]["variant"] in (None, "", "OS")):
            v, amount, price = rows[0]
            sub(item, "CODE", v["code"])
            variant_fields(item, amount, price)
        else:
            vs = sub(item, "VARIANTS")
            for v, amount, price in rows:
                ve = sub(vs, "VARIANT")
                sub(ve, "CODE", v["code"])
                size_param(ve, v["variant"])
                variant_fields(ve, amount, price)
        stats["produkty"] += 1
        stats["varianty"] += len(rows)
        stats["viditelne" if show else "skryte_dodavatel"] += 1

    for h in hide_items:  # staré modely, ktoré dodávateľ už nemá
        item = sub(root, "SHOPITEM")
        sub(item, "VISIBILITY", "hidden")
        if len(h["kody"]) == 1:
            sub(item, "CODE", h["kody"][0])
            variant_fields(item, 0, None)
        else:
            vs = sub(item, "VARIANTS")
            for c in h["kody"]:
                ve = sub(vs, "VARIANT")
                sub(ve, "CODE", c)
                size_param(ve, c.split("/")[-1].split("_")[-1].strip(" -") if ("/" in c or "_" in c) else c)
                variant_fields(ve, 0, None)
        stats["skryte_stare"] += 1
    return root, stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--catalog")
    ap.add_argument("--avail")
    args = ap.parse_args()
    catalog = zone3_parse.group(zone3_parse.load(args.catalog or cfg_value("zone3_catalog_url", "ZONE3_CATALOG_URL")))
    avail = zone3_availability.load(args.avail or cfg_value("zone3_availability_url", "ZONE3_AVAILABILITY_URL"))
    # na GitHube sú cenové pravidlá v tajnom nastavení PRICING_RULES_JSON (kód je verejný)
    rules = json.loads(os.environ["PRICING_RULES_JSON"]) if os.environ.get("PRICING_RULES_JSON") else load_json("pricing_rules.json")
    own_codes = {c for o in load_json("zone3_vlastny_sklad.json") for c in o["kody"]}
    hide_items = load_json("zone3_skryt_stare.json")
    known = set(load_json("triex_zname_kody.json")) if os.path.exists(os.path.join(HERE, "triex_zname_kody.json")) else set()
    root, stats = build(catalog, avail, rules, own_codes, hide_items, known, zone3_texts.load_overrides())
    xml = minidom.parseString(ET.tostring(root, encoding="utf-8")).toprettyxml(indent=" ", encoding="utf-8")
    open(args.out, "wb").write(xml)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
