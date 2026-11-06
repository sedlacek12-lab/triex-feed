"""Načíta dostupnostný feed ZONE3 (sklad + ceny). Položky, ktoré vo feede nie sú, majú sklad 0."""
import json, urllib.request
import xml.etree.ElementTree as ET


def _num(s):
    return float(s.replace(",", ".")) if s and s.strip() else None


def load(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=120) as r:
            data = r.read()
    else:
        data = open(src, "rb").read()
    out = {}
    for i in ET.fromstring(data).iter("item"):
        wsp = _num(i.findtext("PRICE_WSP"))
        voc, akcia = _num(i.findtext("PRICE_VOC")), _num(i.findtext("PRICE_ACTION/actionPrice/price"))
        # akciová cena je vo feede len v CZK -> prepočet pomerom k bežnej nákupnej cene v CZK
        akcia_eur = round(wsp * akcia / voc, 2) if (wsp and voc and akcia) else None
        out[i.findtext("PRODUCTCODE")] = {
            "sklad": int(_num(i.findtext("STOCK_ITEM")) or 0),
            "nakup_eur": akcia_eur or wsp,          # nákupná cena bez DPH (berie akciovú, ak je)
            "nakup_bezna_eur": wsp,
            "moc_eur": _num(i.findtext("PRICE_RRP")),  # odporúčaná predajná cena s DPH
            "akcia_do": i.findtext("PRICE_ACTION/actionPrice/dateTo"),
        }
    return out


if __name__ == "__main__":
    import sys
    cfg = json.load(open("config.local.json"))
    data = load(sys.argv[1] if len(sys.argv) > 1 else cfg["zone3_availability_url"])
    print(len(data), "položiek skladom")
