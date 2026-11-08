"""Vyrobí XML feed vo formáte Shoptet pre vybrané značky Sportimportu (ALÉ, CYCPLUS, 4iiii, QM Sportscare).

Náhrada za Napojse v Shoptet automatickom importe #15 (párovanie podľa kódu produktu).
- ALÉ: farby jedného modelu sa spoja do jedného produktu (varianty Farba × Veľkosť).
  Nový model sa založí, len ak je z kolekcie >= ale_min_modelovy_rok a dodávateľ má spolu >= ale_min_ks_skladom kusov.
- produkty, ktoré už na TRIEX sú (kód vo verejnom Heureka feede TRIEX), ostávajú vo feede vždy:
  aktualizuje sa sklad a viditeľnosť (bez skladu = skryté).
- cena nových produktov = odporúčaná cena dodávateľa (pricing.py, min. marža, zaokrúhlenie na ,90).

Použitie: python build_sportimport.py <vystup.xml> [--feed SUBOR_ALEBO_URL]
"""
import argparse, json, os, re, sys, urllib.request
import xml.etree.ElementTree as ET
from collections import OrderedDict
from xml.dom import minidom

import pricing, sportimport_texts as T

HERE = os.path.dirname(os.path.abspath(__file__))
AV_IN = "Skladom (doručenie do 4 dní)"
AV_OUT = "Vypredané"
TRIEX_HEUREKA = "https://www.triex.sk/heureka/export/products.xml"
SUPPLIER = "Sportimport.cz"
ZNACKA_SHOPTET = {"ALÉ Cycling Clothing": "ALÉ Cycling Clothing", "CYCPLUS": "CYCPLUS",
                  "4iiii Innovations": "4iiii Innovations", "QM Sportscare": "QM Sportscare"}


def load(src):
    if src.startswith("http"):
        req = urllib.request.Request(src, headers={"User-Agent": "triex-feed/1.0"})
        with urllib.request.urlopen(req, timeout=300) as r:
            return ET.fromstring(r.read())
    return ET.parse(src).getroot()


def n(x):
    try:
        return int(float(x or 0))
    except ValueError:
        return 0


def sub(parent, tag, text=None):
    el = ET.SubElement(parent, tag)
    if text is not None:
        el.text = str(text)
    return el


def triex_kody(url=TRIEX_HEUREKA):
    """Kódy variantov viditeľných na TRIEX (Heureka feed nahrádza v kódoch medzery a lomky podčiarkovníkom)."""
    try:
        with urllib.request.urlopen(url, timeout=120) as r:
            root = ET.fromstring(r.read())
        return {(i.findtext("ITEM_ID") or "").strip() for i in root.iter("SHOPITEM")} - {""}
    except Exception as ex:
        print("Upozornenie: TRIEX feed nedostupný:", ex, file=sys.stderr)
        return None


def heureka_kod(k):
    return re.sub(r"[ /]", "_", k)


def obrazky(it):
    out = []
    for im in it.findall("allImages/image"):
        u = (im.text or "").strip()
        if not u:
            continue
        ext = "png" if im.get("mime-type") == "2" else "jpg"
        out.append(f"{u}?f={u.rsplit('/', 1)[-1]}.{ext}")   # Shoptet potrebuje príponu v URL
    if not out and it.findtext("image"):
        out.append(it.findtext("image").strip() + "?f=1.jpg")
    return out


def ceny(it, rules):
    moc = float(it.findtext("price") or 0)
    dp = it.find("dealerPrices")
    nakup = None
    if dp is not None:
        for pr in dp.findall("price"):
            if pr.get("currency") == "EUR":
                nakup = float(pr.text)
    if not moc:
        return None
    if nakup is None:
        return round(moc, 2)
    return pricing.propose(nakup, moc, [], rules)["cena"]


def varianty_polozky(it):
    """[(kod, ean, nazov_variantu, sklad)] – produkt bez variantov má jediný 'variant'."""
    vs = it.findall("variants/variant")
    if vs:
        return [(v.get("code"), (v.get("ean") or "").strip(), v.findtext("name") or "", n(v.findtext("inStock"))) for v in vs]
    return [(it.findtext("code"), (it.findtext("ean") or "").strip(), "", n(it.findtext("inStock")))]


def variant_fields(el, amount, price):
    st = sub(el, "STOCK")
    sub(st, "AMOUNT", amount)
    sub(el, "AVAILABILITY_OUT_OF_STOCK", AV_OUT)
    sub(el, "AVAILABILITY_IN_STOCK", AV_IN)
    sub(el, "NEGATIVE_AMOUNT", 0)
    if price is not None:
        sub(el, "CURRENCY", "EUR")
        sub(el, "VAT", 23)
        sub(el, "PRICE_VAT", f"{price:.2f}")


def ean13(x):
    return x.zfill(13) if x and len(x) < 13 else x


def zostav_produkty(root, cfg):
    """Vráti zoznam produktov: dict(znacka, polozky=[item...], texty)."""
    produkty = []
    vynechat = set(cfg["vynechat_kody"])
    for b in root.findall("brand"):
        znacka = cfg["znacky"].get(b.get("id"))
        if not znacka:
            continue
        items = [i for i in b.findall("items/item") if i.get("active") == "1" and i.findtext("code") not in vynechat]
        if znacka == "ALÉ Cycling Clothing":
            # jeden model = rovnaký kód modelu (bez 2-miestneho kódu farby) ALEBO rovnaký názov aj popis
            # (dodávateľ ten istý model v novej kolekcii niekedy prečísluje); rovnaký názov s iným popisom = iný produkt
            skup = []
            for it in items:
                nazov = T.ale_nazov(it.findtext("name") or "", "")[0].lower()
                popis = re.sub(r"\W+", "", (it.findtext("description") or "").lower())[:150]
                model = it.findtext("code")[:-2]
                g = next((g for g in skup if model in g["kody"]), None) or \
                    next((g for g in skup if g["nazov"] == nazov and g["popis"] == popis), None)
                if g is None:
                    g = {"nazov": nazov, "popis": popis, "kody": set(), "its": []}
                    skup.append(g)
                g["kody"].add(model)
                g["its"].append(it)
            for g in skup:
                produkty.append({"znacka": znacka, "polozky": g["its"], "ale": True, "kluc": "+".join(sorted(g["kody"]))})
        else:
            for it in items:
                produkty.append({"znacka": znacka, "polozky": [it], "ale": False, "kluc": it.findtext("code")})
    return produkty


def rok(it):
    for pr in it.iter("property"):
        if pr.findtext("name") == "Modelový rok":
            return n(pr.findtext("value"))
    return 0


def farba(it):
    for pr in it.iter("property"):
        if pr.findtext("name") == "Farba":
            return pr.findtext("value") or ""
    return ""


def build(root, cfg, rules, na_triex):
    shop = ET.Element("SHOP")
    stats = {"produkty": 0, "nove": 0, "existujuce": 0, "varianty": 0, "skryte": 0, "cesky_popis": 0}
    report = []
    kandidati = []
    for p in zostav_produkty(root, cfg):
        its = p["polozky"]
        kody = [heureka_kod(k) for it in its for k, *_ in varianty_polozky(it)]
        existuje = na_triex is not None and any(k in na_triex for k in kody)
        sklad = {id(it): sum(v[3] for v in varianty_polozky(it)) for it in its}
        if p["ale"]:
            nove_ok = any(rok(it) >= cfg["ale_min_modelovy_rok"] for it in its) and \
                sum(sklad.values()) >= cfg["ale_min_ks_skladom"]
            # farby: tie so skladom; ak model existuje, všetky farby (aby sa dal aktualizovať sklad aj na 0)
            pouzite = its if existuje else [it for it in its if sklad[id(it)] > 0]
        else:
            nove_ok = sum(sklad.values()) > 0
            pouzite = its
        if not existuje and not nove_ok:
            continue
        if not pouzite:
            continue
        # reprezentatívna farba = najnovšia kolekcia s najväčším skladom
        hlavna = max(pouzite, key=lambda it: (rok(it), sklad[id(it)]))
        zaklad = T.ale_nazov(hlavna.findtext("name") or "", "")[0] if p["ale"] else p["kluc"]
        kandidati.append((p, existuje, sklad, pouzite, hlavna, zaklad))

    # rovnaký názov pre rôzne produkty -> doplniť rozlišovací údaj
    from collections import Counter
    pocet = Counter(k[5] for k in kandidati)
    pripony = {}
    for zaklad in [z for z, c in pocet.items() if c > 1]:
        skupina = [k for k in kandidati if k[5] == zaklad]
        navrhy = [T.rozlisenie(k[4].findtext("description") or "", rok(k[4])) for k in skupina]
        for i, (k, nv) in enumerate(zip(skupina, navrhy)):
            if not nv or navrhy.count(nv) > 1:
                nv = "" if (not nv or nv.startswith("kolekcia")) else nv + " "
                nv += f"(model {k[0]['kluc'].split('+')[0]})"
            pripony[id(k[0])] = nv

    for p, existuje, sklad, pouzite, hlavna, zaklad in kandidati:
        presny = next((cfg.get("ale_nazvy", {})[k] for k in p["kluc"].split("+") if k in cfg.get("ale_nazvy", {})), "")
        tx = T.ale_texty(pouzite, hlavna, "" if presny else pripony.get(id(p), ""), presny) if p["ale"] \
            else T.ina_texty(p["znacka"], hlavna)
        any_stock = any(sklad[id(it)] > 0 for it in pouzite)
        item = sub(shop, "SHOPITEM")
        if any_stock and not existuje:
            sub(item, "NAME", tx["nazov"])
            sub(item, "SHORT_DESCRIPTION", f"<p>{T.e(tx['kratky'])}</p>")
            sub(item, "DESCRIPTION", tx["popis"])
            sub(item, "MANUFACTURER", ZNACKA_SHOPTET[p["znacka"]])
            sub(item, "SUPPLIER", SUPPLIER)
            sub(item, "SEO_TITLE", tx["seo_title"])
            sub(item, "META_DESCRIPTION", tx["meta"])
            cats = sub(item, "CATEGORIES")
            sub(cats, "CATEGORY", tx["kategoria"])
            imgs_all = []
            for it in sorted(pouzite, key=lambda it: it is not hlavna):
                for u in obrazky(it)[: (10 if it is hlavna else 4)]:
                    if u not in imgs_all:
                        imgs_all.append(u)
            if imgs_all:
                im = sub(item, "IMAGES")
                for u in imgs_all[:30]:
                    sub(im, "IMAGE", u)
        sub(item, "VISIBILITY", "visible" if any_stock else "hidden")
        riadky = []
        pouzite_farby = {}
        for it in sorted(pouzite, key=lambda it: (-rok(it), -sklad[id(it)])):
            cena = ceny(it, rules)
            f = T.farba_sk(farba(it)) if p["ale"] else ""
            if p["ale"]:
                f = f or "základná"
                if f in pouzite_farby:      # rovnaká farba z inej kolekcie -> odlíšiť rokom
                    if sklad[id(it)] == 0 and not existuje:
                        continue
                    f = f"{f} (kolekcia {rok(it) or 'staršia'})"
                pouzite_farby[f] = it
            img = (obrazky(it) or [None])[0]
            for kod, ean, vnazov, ks in varianty_polozky(it):
                riadky.append((kod, ean, vnazov, ks, cena, f, img))
        jednoduchy = len(riadky) == 1 and not riadky[0][2] and not p["ale"]
        if jednoduchy:
            kod, ean, _, ks, cena, _, _ = riadky[0]
            sub(item, "CODE", kod)
            if ean:
                sub(item, "EAN", ean13(ean))
            variant_fields(item, ks, cena)
        else:
            vs = sub(item, "VARIANTS")
            videne = set()
            viac_farieb = len({r[5] for r in riadky}) > 1 or p["ale"]
            for kod, ean, vnazov, ks, cena, f, img in riadky:
                if kod in videne:
                    continue
                videne.add(kod)
                ve = sub(vs, "VARIANT")
                sub(ve, "CODE", kod)
                if ean:
                    sub(ve, "EAN", ean13(ean))
                ps = sub(ve, "PARAMETERS")
                if viac_farieb and f:
                    pa = sub(ps, "PARAMETER")
                    sub(pa, "NAME", "Farba")
                    sub(pa, "VALUE", f)
                pn, pv = T.velkost(vnazov, kod)
                pa = sub(ps, "PARAMETER")
                sub(pa, "NAME", pn)
                sub(pa, "VALUE", pv)
                variant_fields(ve, ks, cena)
                if img and any_stock and not existuje:
                    sub(ve, "IMAGE_REF", img)
        stats["produkty"] += 1
        stats["varianty"] += len(riadky)
        stats["existujuce" if existuje else "nove"] += 1
        stats["skryte"] += 0 if any_stock else 1
        stats["cesky_popis"] += 1 if tx["cesky"] else 0
        report.append({"znacka": p["znacka"], "kluc": p["kluc"], "nazov": tx["nazov"], "existuje": existuje,
                       "kategoria": tx["kategoria"], "farby": len({r[5] for r in riadky}), "varianty": len(riadky),
                       "ks": sum(r[3] for r in riadky), "cena": riadky[0][4], "obrazky": len(obrazky(hlavna)),
                       "cesky": tx["cesky"], "kratky": tx["kratky"], "popis": tx["popis"],
                       "seo_title": tx["seo_title"], "meta": tx["meta"]})
    return shop, stats, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--feed")
    ap.add_argument("--report")
    args = ap.parse_args()
    cfg = json.load(open(os.path.join(HERE, "sportimport_config.json"), encoding="utf-8"))
    rules = json.loads(os.environ["PRICING_RULES_JSON"]) if os.environ.get("PRICING_RULES_JSON") else \
        json.load(open(os.path.join(HERE, "pricing_rules.json")))
    root = load(args.feed or cfg["feed_url"])
    na_triex = triex_kody()
    if na_triex is None:
        sys.exit("TRIEX feed nedostupný – feed radšej nevyrábam (inak by mohol zakladať duplicity).")
    shop, stats, report = build(root, cfg, rules, na_triex)
    xml = minidom.parseString(ET.tostring(shop, encoding="utf-8")).toprettyxml(indent=" ", encoding="utf-8")
    open(args.out, "wb").write(xml)
    if args.report:
        json.dump(report, open(args.report, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(stats, ensure_ascii=False))


if __name__ == "__main__":
    main()
