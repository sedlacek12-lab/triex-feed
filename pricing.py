"""Výpočet predajnej ceny: priemer cien konkurencie na SK, ohraničený minimálnou maržou a MOC."""
import math


def round_to_ending(price, ending=0.90):
    base = math.floor(price)
    cands = [base - 1 + ending, base + ending]
    return min(cands, key=lambda c: abs(c - price))


def propose(nakup_bez_dph, moc, konkurencia, rules):
    """konkurencia = zoznam cien s DPH (len nové, aktuálne ponuky rovnakého modelu)."""
    dph, mm = rules["dph"], rules["min_marza"]
    podlaha = nakup_bez_dph / (1 - mm) * (1 + dph)          # najnižšia povolená cena s DPH
    if konkurencia:
        ciel, dovod = sum(konkurencia) / len(konkurencia), "priemer konkurencie"
    else:
        ciel, dovod = moc, "bez konkurencie na SK – odporúčaná cena dodávateľa"
    cena = round_to_ending(ciel, rules["zaokruhlenie_koncovka"])
    if cena < podlaha:
        cena = math.ceil(podlaha - rules["zaokruhlenie_koncovka"]) + rules["zaokruhlenie_koncovka"]
        dovod = "konkurencia je lacnejšia – zdvihnuté na minimálnu maržu"
    if rules.get("nad_moc_nepredavat") and moc and cena > moc:
        end = rules["zaokruhlenie_koncovka"]
        cena, dovod = math.floor(moc - end) + end, dovod + " (obmedzené na MOC)"
    bez_dph = cena / (1 + dph)
    return {
        "cena": round(cena, 2),
        "priemer_konkurencie": round(ciel, 2) if konkurencia else None,
        "podlaha": round(podlaha, 2),
        "marza_pct": round((bez_dph - nakup_bez_dph) / bez_dph * 100, 1),
        "zisk_ks": round(bez_dph - nakup_bez_dph, 2),
        "dovod": dovod,
    }
