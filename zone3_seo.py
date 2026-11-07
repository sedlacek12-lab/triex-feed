# -*- coding: utf-8 -*-
"""Zostaví nové názvy, popisy, SEO title a meta description pre ZONE3 produkty na TRIEX.sk.

Použitie: python zone3_seo.py  -> zone3_seo_navrh.json (+ kontrolný výpis)
"""
import html, json, re, sys
from zone3_seo_modely import MODELY

ROOTS = {"Plávanie", "Cyklistika"}   # zle zaradené produkty v koreňových kategóriách

FARBY = {
    "black": "čierna", "red": "červená", "orange": "oranžová", "gun metal": "grafitová", "coral": "koralová",
    "lime": "limetková", "rose pink": "ružová", "blue": "modrá", "navy": "tmavomodrá", "turquoise": "tyrkysová",
    "grey": "sivá", "gray": "sivá", "chalk": "krémovobiela", "forest green": "tmavozelená",
    "eucalyptus green": "eukalyptová zelená", "green": "zelená", "white": "biela", "gold": "zlatá", "teal": "petrolejová",
    "sky": "svetlomodrá", "mint": "mätová", "pink": "ružová", "neon pink": "neónovo ružová", "neon green": "neónovo zelená",
    "purple": "fialová", "yellow": "žltá", "khaki": "kaki", "silver": "strieborná", "hi-vis orange": "reflexná oranžová",
    "hi-vis pink": "reflexná ružová", "hi-vis yellow": "reflexná žltá", "fluro yellow": "neónovo žltá",
    "fluro pink": "neónovo ružová", "copper": "medená", "royal blue": "kráľovská modrá", "clear": "priehľadná",
    "light blue": "svetlomodrá", "teal tie dye": "petrolejová batika", "multi blue": "modrá", "neon": "neónová",
    "print": "s potlačou", "gravel": "sivá", "kona print": "Kona potlač", "tribal print": "Tribal potlač",
    "black/khaki": "čierna/kaki", "colour blast fluro pink": "neónovo ružová", "navy blue": "tmavomodrá",
    "hi-vis orange ": "reflexná oranžová", "charcoal marl": "tmavosivý melír", "blue marl": "modrý melír", "reflective silver": "reflexná strieborná", "relective silver": "reflexná strieborná", "neon orange": "neónovo oranžová", "green revo mirror": "zelená zrkadlová", "multi": "viacfarebná",
}
SK_FARBY = {"čierne": "čierna", "biely": "biela", "modrý": "modrá", "fialové": "fialová", "ružové": "ružová",
            "červené": "červená", "oranžové": "oranžová", "strieborná": "strieborná", "červená": "červená",
            "oranžová": "oranžová", "modrá/oranžová": "modrá/oranžová", "ružové/biele": "ružová/biela",
            "aqua/čierne": "aqua/čierna", "biele": "biela"}
SOSOVKY = {"polarized revo gold": "polarizované zlaté zrkadlové sklá", "tinted blue": "modro tónované sklá",
           "clear": "číre sklá", "polarised": "polarizované sklá", "tinted": "tónované sklá", "polarized lens": "polarizované sklá"}

# pod-modely (dizajn / strih), ktoré sa doplnia k všeobecným modelom
PODMODELY = ["Cosmic 2.0", "Cosmic 3.0", "Cosmic", "Aztec 3.0", "Aztec 2.0", "MF-X", "Prism 3.0", "Prism", "High Jazz 3.0",
             "High-Jazz 2.0", "High Jazz", "Kona Speed", "Performance Speed", "Power Stroke", "Ergo", "Pacific Koa", "Heat-Tech", "Yulex®", "Thermo Tech", "Volare", "Aspect"]
STRIHY = [("bound back", "Bound Back"), ("strap back", "Strap Back"), ("high neck", "High Neck"), ("classic", "Classic"),
          ("tankini", "Tankini")]


def farba_sk(s):
    s = s.strip(" /-–")
    if not s:
        return ""
    low = s.lower()
    if low in SK_FARBY:
        return SK_FARBY[low]
    if low in FARBY:
        return FARBY[low]
    parts = [p.strip() for p in re.split(r"/", s) if p.strip()]
    out = []
    for p in parts:
        out.append(FARBY.get(p.lower(), SK_FARBY.get(p.lower(), p)))
    # odstránenie duplicít (napr. Black/Gold - Black/Gold)
    seen, res = set(), []
    for o in out:
        if o not in seen:
            seen.add(o); res.append(o)
    return "/".join(res)


def rozober(nazov):
    n = nazov.replace("’", "'")
    sosovka = ""
    m = re.search(r"\s*-\s*lens\s*:\s*(.+?)(\s*/\s*os)?$", n, re.I)
    if m:
        sosovka = m.group(1).strip()
        n = n[:m.start()]
    m = re.search(r"\s*-\s*(polarized lens)\s*-", n, re.I)
    if m:
        sosovka = m.group(1); n = n[:m.start()] + " -" + n[m.end():]
    n = re.sub(r"\s*[-/]\s*os\s*$", "", n, flags=re.I).strip()
    n = re.sub(r"\s*/\s*$", "", n).strip()
    farba = ""
    if " / " in n:
        farba = n.rsplit(" / ", 1)[1]
    elif " – " in n:
        farba = n.rsplit(" – ", 1)[1]
    elif " - " in n:
        farba = n.rsplit(" - ", 1)[1]
    else:
        m = re.search(r"\s([A-Z]{3,}(?:/[A-Z]{3,})+)$", n)
        if m:
            farba = m.group(1)
    if not farba:
        m = re.search(r"(čierne|biely|modrý|fialové|ružové|červené|oranžové|ružové/biele|aqua/čierne|biele)$", n)
        if m:
            farba = m.group(1)
    if re.search(r"\b(48g|60g|tech|recycled|5/3mm|elite)\b", farba, re.I) and "/" not in farba and farba.lower() not in FARBY:
        farba = ""
    if re.search(r"heat-tech", farba, re.I):
        farba = re.sub(r"\s*heat-tech", "", farba, flags=re.I)
    return n, farba_sk(farba), sosovka


def pohlavie(low, rodina):
    if re.search(r"dámsk|women|\bwomen's|womens", low):
        return "f"
    if re.search(r"pánsk|\bmen's|\bmens|men's", low):
        return "m"
    return "u"


def najdi_model(low):
    for d in MODELY:
        if re.search(d["rx"], low):
            return d
    return None


def podmodel(nazov):
    for p in PODMODELY:
        if p.lower().replace("-", " ") in nazov.lower().replace("-", " "):
            return p
    return ""


def strih(low):
    for k, v in STRIHY:
        if k in low:
            return v
    return ""


SPOLOCNE = {
    "neopren": [
        ("Ako vybrať správnu veľkosť neoprénu",
         "Triatlonový neoprén má sedieť tesne ako druhá koža – nesmú v ňom vznikať záhyby a vzduchové bubliny, inak doň bude pretekať voda. "
         "Veľkosť vyberajte podľa výšky a hmotnosti v tabuľke veľkostí Zone3. Ak ste na hranici dvoch veľkostí, zvoľte tú, ktorá lepšie zodpovedá vašej výške. "
         "Pri prvom obliekaní si dajte čas, vyťahujte neoprén postupne od členkov nahor a používajte bavlnené rukavice, aby ste ho nepoškodili nechtami. "
         "Ak si nie ste istí, napíšte nám – radi vám s výberom poradíme."),
        ("Starostlivosť o neoprén",
         "Po každom plávaní neoprén opláchnite sladkou vodou, najmä po mori či chlórovanej vode. Sušte ho naruby v tieni na širokom ramienku, nikdy nie na priamom slnku alebo pri radiátore. "
         "Neskladajte ho do ostrých prehybov a nepoužívajte horúcu vodu ani bežné pracie prostriedky. Pri správnej starostlivosti vám vydrží mnoho sezón."),
    ],
    "swimrun": [
        ("Ako vybrať veľkosť",
         "Swimrunový neoprén má sedieť tesne, no musí umožňovať pohodlný bežecký krok. Riaďte sa tabuľkou veľkostí Zone3 podľa výšky a hmotnosti; ak váhate, radi poradíme."),
        ("Starostlivosť",
         "Po pretekoch oblek opláchnite sladkou vodou, vyprázdnite vrecká a sušte naruby v tieni. Nepoužívajte horúcu vodu ani sušičku."),
    ],
    "swimskin": [
        ("Kedy použiť swimskin",
         "Na triatlonových pretekoch je pri vyššej teplote vody neoprén zakázaný. Práve vtedy prichádza na rad swimskin – oblečiete si ho cez kombinézu a po plávaní ho v depe rýchlo vyzlečiete. "
         "Swimskin je povolený aj na mnohých pretekoch v otvorenej vode a hodí sa aj na tréning v jazere."),
        ("Veľkosť a starostlivosť",
         "Swimskin má sedieť tesne, aby pod ním nevznikali záhyby. Vyberajte podľa tabuľky veľkostí. Po použití opláchnite v sladkej vode a sušte v tieni."),
    ],
    "trisuit": [
        ("Ako vybrať veľkosť",
         "Triatlonové oblečenie má sedieť tesne – kompresia podporuje svaly a látka bez záhybov znižuje odpor vody aj vzduchu. Riaďte sa tabuľkou veľkostí Zone3; "
         "medzi dvoma veľkosťami zvoľte menšiu, ak chcete pretekársky strih, a väčšiu, ak preferujete pohodlie na dlhých tratiach."),
        ("Starostlivosť",
         "Po tréningu opláchnite v čistej vode. Perte pri 30 °C v sieťke na pranie, bez aviváže a bez sušičky. Sušte v tieni. Tak si kombinéza dlho zachová kompresiu aj farbu."),
    ],
    "cyklodop": [
        ("Veľkosť a starostlivosť",
         "Návleky majú sedieť tesne, aby sa počas jazdy neposúvali. Perte pri 30 °C, bez aviváže a sušte v tieni."),
    ],
    "plavky": [
        ("Prečo plavky Zone3",
         "Zone3 je britská značka, ktorú založili triatlonisti a plavci. Plavky vyrába z látok odolných voči chlóru, ktoré si zachovajú tvar aj farbu výrazne dlhšie ako bežné plavky z obchodných reťazcov. "
         "Investícia do kvalitných plaviek sa vráti – vydržia stovky tréningov."),
        ("Veľkosť a starostlivosť",
         "Športové plavky majú sedieť tesne, aby sa pri plávaní a odrazoch nehýbali. Riaďte sa tabuľkou veľkostí. "
         "Po každom plávaní plavky opláchnite v studenej sladkej vode, neždímajte ich a sušte v tieni. Nesušte na radiátore a neperte s avivážou."),
    ],
    "plavky_ows": [
        ("Plávanie v otvorenej vode",
         "Kolekcia pre otvorenú vodu Zone3 je navrhnutá tak, aby vydržala slanú vodu, piesok, slnko aj chlór. Plavky sú pohodlné na dlhé plávanie a dobre vyzerajú aj na pláži."),
        ("Veľkosť a starostlivosť",
         "Vyberajte podľa tabuľky veľkostí. Po plávaní opláchnite v sladkej vode a sušte v tieni, nie na priamom slnku."),
    ],
    "neodop": [
        ("Starostlivosť",
         "Po plávaní opláchnite sladkou vodou a nechajte vyschnúť v tieni. Nesušte na radiátore ani na priamom slnku – neoprén by stratil pružnosť."),
    ],
    "okuliare": [
        ("Starostlivosť o okuliare",
         "Vnútornú stranu skiel neutierajte prstami ani uterákom – poškodili by ste protizahmlievaciu vrstvu. Po plávaní okuliare opláchnite v studenej sladkej vode, nechajte vyschnúť a uložte do puzdra. "
         "Nenechávajte ich na priamom slnku ani v rozpálenom aute."),
    ],
    "ciapka": [
        ("Starostlivosť",
         "Po plávaní čiapku opláchnite v studenej vode, osušte a skladujte mimo priameho slnka. Silikónová čiapka tak vydrží roky."),
    ],
    "trening": [
        ("Tip na tréning",
         "Pomôcky zaraďujte do tréningu postupne – najprv kratšie série, aby si ramená a kĺby zvykli na vyššiu záťaž. Kombinácia piškóty a pádiel je klasikou silových sérií, plutvy a šnorchel zasa technických cvičení."),
    ],
    "boja": [
        ("Bezpečnosť v otvorenej vode",
         "Bójka nenahrádza plavecké schopnosti ani dohľad. Plávajte vždy v známych vodách, informujte niekoho o svojom pláne a pri studenej vode používajte neoprén."),
    ],
    "beh": [], "ostatne": [],
}


FAQ = {
    "neopren": [("Môžem v triatlonovom neopréne plávať aj prsia?", "Áno, no triatlonové neoprény sú optimalizované na kraul – vztlak na nohách drží telo vodorovne. Na časté plávanie prsiami sú vhodnejšie univerzálne modely ako Active-Flex."),
                ("Je neoprén povolený na každom triatlone?", "Nie. O povolení rozhoduje teplota vody – pri teplej vode je neoprén zakázaný a vtedy sa používa swimskin. Pri studenej vode býva naopak povinný."),
                ("Ako dlho vydrží kvalitný neoprén?", "Pri správnej starostlivosti niekoľko sezón. Najčastejšie poškodenie spôsobia nechty pri obliekaní – preto odporúčame bavlnené rukavice.")],
    "swimrun": [("Môžem swimrunový oblek použiť aj na triatlon?", "Áno, na tréning určite. Na triatlonové preteky je však rýchlejší klasický triatlonový neoprén s dlhými nohavicami."),
                ("Ako sa v ňom beží?", "Swimrunové obleky majú kratšie nohavice, tenší a pružnejší materiál na nohách a predný zips, takže sa v nich beží výrazne pohodlnejšie ako v triatlonovom neopréne.")],
    "swimskin": [("Oblieka sa swimskin cez kombinézu?", "Áno, swimskin sa oblieka cez triatlonovú kombinézu a po plávaní sa v depe vyzlečie."),
                 ("Je swimskin povolený na pretekoch?", "Áno, swimskin je povolený aj vtedy, keď je neoprén zakázaný. Vždy si však overte pravidlá konkrétnych pretekov.")],
    "trisuit": [("Mám pod kombinézu niečo obliecť?", "Nie, triatlonová kombinéza sa nosí priamo na telo. Vložka je navrhnutá tak, aby bola pohodlná bez spodnej bielizne."),
                ("Môžem v kombinéze plávať v bazéne?", "Áno, kombinézu môžete použiť aj na tréning plávania. Po chlórovanej vode ju dôkladne opláchnite."),
                ("Je vložka vhodná aj na dlhé cyklistické úseky?", "Triatlonová vložka je tenšia ako cyklistická, aby nebránila pri behu. Na tréningové jazdy nad tri hodiny odporúčame klasické cyklistické nohavice.")],
    "plavky": [("Sú plavky odolné voči chlóru?", "Áno, plavky Zone3 sú vyrobené z látok odolných voči chlóru, preto sú vhodné na pravidelný tréning v bazéne."),
               ("Akú veľkosť si mám vybrať?", "Športové plavky majú sedieť tesne. Ak ste medzi dvoma veľkosťami, na tréning zvoľte menšiu, na pohodlné plávanie väčšiu. Radi poradíme.")],
    "plavky_ows": [("Sú vhodné aj do bazéna?", "Áno, plavky z kolekcie pre otvorenú vodu sú odolné voči chlóru aj slanej vode."),
                   ("Nahradia neoprén?", "Pri teplejšej vode áno. Do studenej vody odporúčame termo plavky Ti+ alebo neoprén.")],
    "neodop": [("Môžem doplnok použiť na triatlonových pretekoch?", "Závisí od pravidiel konkrétnych pretekov a teploty vody. Pri studenej vode sú neoprénové čiapky, ponožky či rukavice často povolené."),
               ("Hodí sa aj na otužovanie?", "Áno, neoprénové doplnky výrazne predĺžia čas, ktorý vydržíte v studenej vode.")],
    "okuliare": [("Aké sklá si vybrať?", "Do otvorenej vody a na slnko polarizované alebo zrkadlové, na bazén a šero číre, na premenlivé podmienky fotochromatické alebo tónované."),
                 ("Čo robiť, keď sa okuliare zahmlievajú?", "Neutierajte vnútornú stranu skiel. Po plávaní ich opláchnite v studenej vode a nechajte vyschnúť. Protizahmlievacia vrstva tak vydrží dlhšie.")],
    "ciapka": [("Prečo silikón namiesto latexu?", "Silikón je odolnejší, príjemnejší na hlave, netrhá vlasy a vydrží výrazne dlhšie ako latex. Navyše je vhodný aj pre alergikov na latex."),
               ("Prečo reflexná farba?", "V otvorenej vode je hlava jediné, čo z vás vidno. Reflexná čiapka zvyšuje vašu bezpečnosť.")],
    "trening": [("Ako často používať plavecké pomôcky?", "Pomôcky zaraďte do časti tréningu – napríklad 20 až 30 % objemu. Plávanie bez pomôcok by malo zostať základom.")],
    "boja": [("Prekáža bójka pri plávaní?", "Nie. Bójka visí za vami na krátkom popruhu a pri plávaní ju takmer necítite."),
             ("Môžem sa o bójku oprieť?", "Áno, v prípade únavy alebo kŕča sa o ňu môžete oprieť a oddýchnuť si.")],
    "beh": [("Je doplnok povolený na pretekoch?", "Áno, doplnky Zone3 sú navrhnuté pre triatlonové a bežecké preteky a sú v súlade s bežnými pravidlami.")],
    "cyklodop": [("Sú návleky povolené na triatlone?", "Áno, návleky na ruky sú bežne povolené. Pri pretekoch bez neoprénu si overte pravidlá ohľadom odevu na plávanie.")],
    "ostatne": [("Je produkt vhodný aj ako darček?", "Áno, doplnky Zone3 sú obľúbeným darčekom pre triatlonistov, plavcov a otužilcov. Radi vám poradíme s výberom.")],
}


def zostav(guid, nazov, kat_nazov):
    low = nazov.lower().replace("’", "'")
    d = najdi_model(low)
    if not d:
        return None
    zakl, farba, sosovka = rozober(nazov)
    g = pohlavie(low, d["rodina"])
    typ = d["typ"].get(g, d["typ"]["u"])
    model = d["model"]
    if not model:
        model = podmodel(nazov)
    if d["rodina"] in ("plavky",) and d["k"] in ("women_swim", "tie_dye_swim", "iconic"):
        s = strih(low)
        if s and s.lower() not in model.lower():
            model = (model + " " + s).strip()
    if d["k"] == "heat_tech_cap" and "heat" not in low:
        model = ""
    if d["k"] in ("ht_gloves", "ht_socks"):
        model = "Yulex®" if "yulex" in low else ("Heat-Tech" if "heat" in low else "")
    if d["k"] == "ti_plus" and "long sleeve" in low:
        model = "OWS Ti+ Thermal High Neck Long Sleeve"
    if d["k"] == "yulex_top":
        model = "Yulex® Vest" if "vest" in low else ("Yulex® Long Sleeve" if "long sleeve" in low else "Yulex®")
    if d["k"] == "ht_gloves" and "mitts" in low:
        typ, model = "Neoprénové plavecké palčiaky", "Thermo Tech"
    if d["k"] == "buoyancy_shorts" and "original" in low:
        model = "Buoyancy Shorts Originals 5/3 mm"
    if d["k"] == "lava_top":
        model = "Lava Long Distance" if "long distance" in low else "Lava Aero 3/4 Sleeve"
    if d["k"] == "balaclava":
        model = "Thermo Tech Balaclava V2" if "v2" in low else "Balaclava"
    if d["k"] == "aero_sleeves":
        model = "Aeroforce-X" if "aeroforce" in low else ("Aquaflo Plus" if "aquaflo" in low else "Aero")
        typ = {"m": "Pánske návleky na ruky", "f": "Dámske návleky na ruky"}.get(g, "Návleky na ruky")
    if d["k"] == "race_belt_pouch":
        model = "Race Belt"
    if d["k"] == "ls_top" and "renew" in low:
        model = "Long Sleeve OWS Renew"
    sosovka_sk = SOSOVKY.get(sosovka.lower(), sosovka) if sosovka else ""
    if d["k"] in ("venator",):
        if "polarised" in low: sosovka_sk = sosovka_sk or "polarizované sklá"
        if "tinted" in low and not sosovka_sk: sosovka_sk = "tónované sklá"
    meno = f"{typ} Zone3 {model}".replace("  ", " ").strip()
    if sosovka_sk:
        meno += f", {sosovka_sk}"
    if farba:
        meno += f" – {farba}"
    meno = re.sub(r"\s+", " ", meno)

    # ---- popis ----
    e = html.escape
    nadpis = f"{typ} Zone3 {model}".replace("  ", " ").strip()
    p = [f"<h2>{e(nadpis)}</h2>", f"<p>{e(d['uvod'])}</p>"]
    if farba or sosovka_sk:
        det = []
        if farba: det.append(f"farba <strong>{e(farba)}</strong>")
        if sosovka_sk: det.append(f"<strong>{e(sosovka_sk)}</strong>")
        p.append(f"<p>Prevedenie tohto produktu: {', '.join(det)}. Ďalšie farby a varianty nájdete v kategórii.</p>")
    p.append("<h3>Hlavné výhody</h3><ul>" + "".join(f"<li>{e(v)}</li>" for v in d["vyhody"]) + "</ul>")
    p.append(f"<h3>Technológia a konštrukcia</h3><p>{e(d['tech'])}</p>")
    p.append(f"<h3>Pre koho je určený</h3><p>{e(d['pre_koho'])}</p>")
    for h, t in SPOLOCNE.get(d["rodina"], []):
        p.append(f"<h3>{e(h)}</h3><p>{e(t)}</p>")
    if FAQ.get(d["rodina"]):
        p.append("<h3>Často kladené otázky</h3>" + "".join(f"<p><strong>{e(q)}</strong><br>{e(a)}</p>" for q, a in FAQ[d["rodina"]]))
    p.append("<h3>Prečo nakúpiť v TRIEX.sk</h3><p>TRIEX je slovenský e-shop zameraný na triatlon, plávanie, cyklistiku a beh. "
             "Výbavu Zone3 sami používame a radi vám poradíme s výberom modelu aj veľkosti – stačí nám napísať alebo zavolať.</p>")
    popis = "\n".join(p)
    kratky = f"<p>{e(d['kratky'])}</p>"

    # ---- SEO ----
    farba_kr = f" {farba}" if farba and len(nadpis) + len(farba) < 52 else ""
    title = f"{nadpis}{farba_kr} | TRIEX.sk"
    if len(title) > 65:
        title = f"{nadpis} | TRIEX"
    meta = f"{d['kratky'].split('. ')[0].rstrip('.')}. ✅ Originál Zone3 ✅ Poradíme s veľkosťou ✅ Triatlonový e-shop TRIEX.sk"
    if len(meta) > 160:
        meta = f"{nadpis} – {d['kw']}. ✅ Originál Zone3 ✅ Poradíme s veľkosťou ✅ TRIEX.sk"
    out = {"guid": guid, "stary_nazov": nazov, "nazov": meno, "kratky": kratky, "popis": popis, "metaTitle": title,
           "metaDescription": meta, "model": d["k"], "kat_teraz": kat_nazov}
    if kat_nazov in ROOTS and d.get("kat"):
        out["defaultCategoryGuid"] = d["kat"]
    if d["k"] == "kids_trisuit" and kat_nazov != "Triatlonové dresy":
        out["defaultCategoryGuid"] = d["kat"]
    return out


if __name__ == "__main__":
    rows, chyby = [], []
    for line in open("triex_zone3_produkty.txt", encoding="utf-8"):
        guid, nazov, kat = line.rstrip("\n").split("|")
        r = zostav(guid, nazov, kat)
        (rows.append(r) if r else chyby.append(nazov))
    json.dump(rows, open("zone3_seo_navrh.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for r in rows:
        print(f"{r['model'][:14]:14} | {r['stary_nazov'][:55]:55} -> {r['nazov']}" + (" [KAT]" if "defaultCategoryGuid" in r else ""))
    print("BEZ MODELU:", chyby)
    print(len(rows), "produktov;", sum(1 for r in rows if "defaultCategoryGuid" in r), "presun kategórie")
