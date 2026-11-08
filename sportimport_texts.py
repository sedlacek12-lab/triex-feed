# -*- coding: utf-8 -*-
"""Slovenské názvy, predajné popisy, SEO title/meta a kategórie pre produkty Sportimport na TRIEX.sk."""
import html, re

ACR = {"PRR", "PRS", "PR", "R", "EV1", "RS", "XL", "DNA", "UV", "LS", "SS", "GT", "AI", "OS", "MTB", "XC", "QM", "UPF"}
SHORT_WORDS = {"ME", "UP", "ON", "GO", "MY", "TO", "OF", "IN", "AT", "IT"}
GENDER = r"(pánsk[yaeé]|dámsk[yaeé]|detsk[yaeé]|unisex)"
CZ = re.compile(r"[řůěŘŮĚ]")

FARBY = {
    "black": "čierna", "white": "biela", "blue": "modrá", "navy blue": "tmavomodrá", "grey": "sivá", "gray": "sivá",
    "fluo yellow": "neónovo žltá", "black-fluo yellow": "čierna/neónovo žltá", "pink": "ružová", "red": "červená",
    "army green": "armádna zelená", "rope grey": "svetlosivá", "bordeaux": "bordová", "titanium": "titánová",
    "black-white": "čierna/biela", "midnight blue": "polnočná modrá", "green": "zelená", "fuchsia": "fuchsiová",
    "fucsia": "fuchsiová", "light blue": "svetlomodrá", "bottle green": "fľašová zelená", "blackberry purple": "černicová fialová",
    "ruby red": "rubínová červená", "ink blue": "atramentová modrá", "black-charcoal grey": "čierna/antracitová",
    "flamingo pink": "plameniaková ružová", "beige": "béžová", "moss green": "machová zelená", "powder blue": "púdrová modrá",
    "orange": "oranžová", "reddish purple": "purpurová", "bronze": "bronzová", "slate blue": "bridlicová modrá",
    "fluo pink": "neónovo ružová", "acid green": "kyslá zelená", "steel blue": "oceľová modrá", "yellow": "žltá",
    "burgundy": "burgundská", "ecru": "ekru", "pale blue": "bledomodrá", "charcoal": "antracitová", "smoke grey": "dymová sivá",
    "pale green": "bledozelená", "blue combo": "modrá kombinácia", "pink combo": "ružová kombinácia",
    "orange combo": "oranžová kombinácia", "purple combo": "fialová kombinácia", "multicolor": "viacfarebná",
    "steel": "oceľová", "coffee": "kávová", "dark": "tmavá", "aqua": "aqua", "eucalyptus": "eukalyptová",
    "černá": "čierna", "sedlovka": "", "gripy": "",
}


def e(s):
    return html.escape(s or "", quote=False)


def farba_sk(f):
    if not f:
        return ""
    low = f.strip().lower()
    if low in FARBY:
        return FARBY[low]
    return f.strip().title()


def velkost(nazov, kod):
    """'Veľkosť M/40-43' -> ('Veľkosť', 'M (40–43)'); 'Dĺžka kľučky 170 mm' -> ('Dĺžka kľučky', '170 mm')."""
    n = (nazov or "").strip()
    if not n:
        return "Veľkosť", kod.rsplit("-", 1)[-1]
    m = re.match(r"Veľkosť\s+(.+)", n)
    if m:
        v = m.group(1).strip()
        m2 = re.match(r"([A-Z0-9]+)/(\d+)-(\d+)$", v)
        if m2:
            v = f"{m2.group(1)} ({m2.group(2)}–{m2.group(3)})"
        return "Veľkosť", "univerzálna" if v.upper() in ("ONE SIZE", "UNI") else v
    if n.upper() == "UNI":
        return "Veľkosť", "univerzálna"
    m = re.match(r"Dĺžka kľučky\s+(.+)", n)
    if m:
        return "Dĺžka kľučky", m.group(1)
    m = re.match(r"Dĺžka\s+(.+)", n)
    if m:
        return "Dĺžka kľučky a prevodníky", m.group(1).replace("z", " z").replace("  ", " ")
    return "Prevedenie", n


def tc_word(w):
    parts = re.split(r"([-/])", w)
    out = []
    for p in parts:
        if p.isalpha() and p.isupper() and p not in ACR and (len(p) >= 3 or p in SHORT_WORDS):
            out.append(p.capitalize())
        else:
            out.append(p)
    return "".join(out)


def model_nazov(s):
    s = re.sub(r"\s+", " ", s).strip(" -–")
    s = re.sub(r"OFF ROAD - GRAVEL", "Off-Road Gravel", s)
    return " ".join(tc_word(w) for w in s.split())


# ---------------- ALÉ ----------------
DRUH = {  # Druh -> (kategória, kľúčové slovo, typ oblečenia pre texty)
    "Krátke dresy ALÉ": ("Cyklistika > Cyklistické oblečenie > Krátke dresy", "cyklistický dres s krátkym rukávom", "dres"),
    "Dlhé dresy ALÉ": ("Cyklistika > Cyklistické oblečenie > Dlhé dresy", "cyklistický dres s dlhým rukávom", "dres"),
    "Bundy ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické bundy", "cyklistická bunda", "bunda"),
    "Krátke nohavice ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické nohavice", "krátke cyklistické nohavice", "nohavice"),
    "Dlhé nohavice ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické nohavice", "dlhé cyklistické nohavice", "nohavice"),
    "Kombinézy ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické nohavice", "cyklistická kombinéza", "kombineza"),
    "Vesty ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické vesty", "cyklistická vesta", "vesta"),
    "Spodné vrstvy ALÉ": ("Cyklistika > Cyklistické oblečenie > Funkčné prádlo", "funkčné cyklistické prádlo", "pradlo"),
    "Ponožky ALÉ": ("Cyklistika > Cyklistické ponožky", "cyklistické ponožky", "ponozky"),
    "Pokrývky hlavy ALÉ": ("Cyklistika > Cyklistické oblečenie > Čelenky a šatky", "cyklistická čiapka", "hlava"),
    "Rukavice ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické doplnky", "cyklistické rukavice", "rukavice"),
    "Návleky na ruky a nohy ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické doplnky", "cyklistické návleky", "navleky"),
    "Návleky na obuv ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické doplnky", "návleky na tretry", "tretry"),
    "Doplnkový sortiment ALÉ": ("Cyklistika > Cyklistické oblečenie > Cyklistické doplnky", "cyklistické doplnky", "doplnok"),
    "Triatlonové oblečenie ALÉ": ("Cyklistika > Triatlonové dresy", "triatlonové oblečenie", "triatlon"),
    "Bežecké oblečenie ALÉ": ("Bežecké potreby > {pohlavie} oblečenie", "bežecké oblečenie", "beh"),
}

STRIH = {
    "Závodné": ("závodný strih (Racing)", "Závodný strih Racing sedí na tele ako druhá koža – minimum vlajúcej látky, maximum aerodynamiky. Ocenia ho pretekári aj jazdci, ktorí chcú z každého tréningu vyťažiť čo najviac."),
    "Výkonnostné": ("výkonnostný strih (Performance)", "Výkonnostný strih Performance je priliehavý a športový, no stále pohodlný aj na niekoľkohodinové tréningy. Ideálna voľba pre pravidelných jazdcov a gran fondo."),
    "Pohodlný": ("pohodlný strih (Comfort)", "Pohodlný strih Comfort je o niečo voľnejší, nikde netlačí a skvele sa hodí na dlhé vyjazdky, cykloturistiku a rekreačnú jazdu."),
}

SEZONA = {
    "Leto": "na letnú sezónu",
    "Zima": "do chladného počasia",
    "Celoročné": "na celoročné ježdenie",
}

TYP_BLOK = {
    "dres": ("Ako vybrať správny dres",
             "Talianske strihy ALÉ sú športovo priliehavé. Ak ste medzi dvoma veľkosťami a preferujete voľnejší pocit, siahnite po väčšej. "
             "Dres skvele doplnia cyklistické nohavice ALÉ z rovnakej kolekcie – farby a materiály sú navrhnuté tak, aby spolu ladili."),
    "bunda": ("Kedy siahnuť po bunde",
              "Bunda je vaša ochrana pred vetrom, chladom a dažďom. Pod ňu odporúčame funkčnú spodnú vrstvu, ktorá odvedie pot od tela, "
              "a pri prechodnom počasí kombináciu s dresom s dlhým rukávom. Strih je prispôsobený jazdnej polohe – vpredu kratší, vzadu predĺžený."),
    "nohavice": ("Pohodlie v sedle",
                 "Kvalitná vložka je pri cyklistických nohaviciach to najdôležitejšie. Nohavice noste bez spodnej bielizne priamo na tele a pri dlhých vyjazdkách "
                 "doprajte pokožke ochranný krém na vložku (napríklad QM Sportscare), ktorý znižuje trenie."),
    "kombineza": ("Pohodlie v sedle",
                  "Kombinéza spája dres a nohavice do jedného kusu – nič sa nevyhŕňa, nič netlačí v páse a v pretekoch aj na tréningu ušetríte sekundy aj nervy."),
    "vesta": ("Univerzálny pomocník",
              "Vesta chráni trup pred vetrom pri zjazdoch a ranných štartoch, a keď sa oteplí, zbalíte ju do zadného vrecka dresu."),
    "pradlo": ("Základ každej vrstvy",
               "Funkčná spodná vrstva odvádza pot od pokožky, a tak zostanete v suchu aj pri intenzívnej jazde. V lete chladí, v zime pomáha udržať teplo pod dresom či bundou."),
    "ponozky": ("Detail, ktorý rozhoduje",
                "Cyklistické ponožky sú tenšie a lepšie sedia v tretre. Vystužené zóny a priedušný úplet chránia nohu pred otlakmi aj na dlhých trasách."),
    "hlava": ("Pod prilbu",
              "Tenká čiapka či čelenka sa pohodlne zmestí pod prilbu, chráni uši a čelo pred vetrom a odvádza pot."),
    "rukavice": ("Istý úchop riadidiel",
                 "Rukavice chránia dlane pri páde, tlmia vibrácie a zlepšujú úchop riadidiel aj za mokra."),
    "navleky": ("Flexibilita počas jazdy",
                "Návleky premenia krátky dres a nohavice na teplejšiu výbavu. Keď sa oteplí, stiahnete ich a odložíte do vrecka."),
    "tretry": ("Teplé a suché nohy",
               "Návleky na tretry chránia nohy pred vetrom, chladom aj vodou od kolesa – v jeseni a v zime ich oceníte už po prvej vyjazdke."),
    "doplnok": ("Praktický doplnok", "Drobnosť, ktorá spríjemní každú jazdu a doplní vašu výbavu ALÉ."),
    "triatlon": ("Pre triatlon",
                 "Triatlonové oblečenie ALÉ je navrhnuté na plávanie, bicykel aj beh – rýchlo schne, prilieha a vložka neprekáža ani pri behu."),
    "beh": ("Na beh", "Ľahké, priedušné a rýchloschnúce oblečenie pre tréning aj preteky."),
}

FAQ_VELKOST = ("<p><strong>Akú veľkosť si vybrať?</strong> ALÉ šije podľa talianskych strihov, ktoré sú priliehavejšie. "
               "Ak si nie ste istí, napíšte nám vaše miery (hrudník, pás, výška) a radi vám veľkosť odporučíme.</p>")
PRECO = ("<h3>Prečo nakúpiť v TRIEX.sk</h3><p>TRIEX je slovenský e-shop zameraný na triatlon, cyklistiku, plávanie a beh. "
         "Predávame iba originálny tovar od overených distribútorov a radi vám poradíme s výberom modelu aj veľkosti – stačí nám napísať alebo zavolať.</p>")


def cisti_popis(s):
    s = s or ""
    s = re.sub(r'\s+class="marginTop"', "", s)
    s = re.sub(r"\s+([.,;:!?])", r"\1", s)
    s = s.replace(" as ňou", " a s ňou").replace("výkonostný", "výkonnostný").replace("htmotnosť", "hmotnosť")
    s = re.sub(r"<li>\s+", "<li>", s)
    s = re.sub(r"<p>\s+", "<p>", s)
    s = re.sub(r"(<br\s*/?>\s*){3,}", "<br><br>", s)
    s = re.sub(r"[ \t]{2,}", " ", s)
    return s.strip()


def teplota(desc):
    m = re.search(r"(-?\d+)\s*°C\s*(?:/|do|až|-|–)\s*(-?\d+)\s*°C", desc or "")
    return (int(m.group(1)), int(m.group(2))) if m else None


def ale_nazov(nazov_dod, pohlavie):
    """'Letný cyklistický dres ALÉ pánsky PR-E MEGABYTE 2.0' -> 'Pánsky letný cyklistický dres ALÉ PR-E Megabyte 2.0'"""
    n = html.unescape(re.sub(r"\s+", " ", nazov_dod)).strip()
    n = re.sub(r"\bALE'\s*", "", n)
    n = re.sub(r"\bAccessori\b\s*", "", n)
    n = re.sub(r"\bKlimat[íi]k\b", "Klimatik", n, flags=re.I)
    n = re.sub(r"\bKID Kid\b|\bKid Kid\b", "Kid", n, flags=re.I).replace(" / ", "/").replace("Detske ", "Detské ")
    n = re.sub(r"\bAl[ée]\b", "ALÉ", n)
    if "ALÉ" not in n:   # 'Pánska termobielizeň SEAMLESS WOOL MAN' -> ALÉ pred prvé slovo veľkými
        m = re.search(r"\b[A-Z][A-Z0-9-]{2,}\b", n)
        n = (n[:m.start()] + "ALÉ " + n[m.start():]) if m else n + " ALÉ"
    pred, za = n.split("ALÉ", 1)
    pred, za = pred.strip(), za.strip()
    g = re.search(r"\b" + GENDER + r"\b", za, re.I)
    rod = ""
    if g:
        rod = g.group(1)
        za = (za[:g.start()] + za[g.end():]).strip()
    model = model_nazov(za)
    if rod and not re.search(r"\b" + GENDER + r"\b", pred, re.I):
        typ = f"{rod.capitalize()} {pred[:1].lower()}{pred[1:]}"
    else:
        typ = pred[:1].upper() + pred[1:]
    typ = zhoda_rodu(typ)
    full = f"{typ} ALÉ {model}".strip()
    return full, typ, model


ROD = [  # podstatné meno -> koncovka prídavného mena (pánsk|dámsk|detsk + ...)
    (r"\b(dres|nákrčník|pás)\b", "y"),
    (r"\b(bunda|vesta|kombinéza|vrstva|bielizeň|termobielizeň|mikina|čiapka|čelenka|kukla|maska|fľaša)\b", "a"),
    (r"\b(tričko)\b", "e"),
    (r"\b(nohavice|ponožky|rukavice|návleky)\b", "e"),
]


def zhoda_rodu(typ):
    """Opraví zhodu prvého slova s podstatným menom: 'Pánske vodeodolná vesta' -> 'Pánska vodeodolná vesta'."""
    m = re.match(r"(Pánsk|Dámsk|Detsk)[yaeé]\b", typ)
    if not m:
        return typ
    for rx, kon in ROD:
        if re.search(rx, typ, re.I):
            if m.group(1) == "Detsk":
                kon = {"y": "ý", "a": "á", "e": "é"}[kon]
            return m.group(1) + kon + typ[m.end():]
    return typ


ROZLISENIE = [
    (r"bibknicker|3/4", "3/4 s trakmi"),
    (r"bibtight|bib short|s trakmi|na traky", "s trakmi"),
    (r"bez trakov|do pásu|waist", "do pásu"),
    (r"bez rukávov|sleeveless", "bez rukávov"),
    (r"dlhým rukávom|long sleeve", "s dlhým rukávom"),
    (r"krátkym rukávom|short sleeve", "s krátkym rukávom"),
    (r"merino", "merino"),
]


def rozlisenie(desc, rok):
    d = (desc or "").lower()
    for rx, txt in ROZLISENIE:
        if re.search(rx, d):
            return txt
    return f"kolekcia {rok}" if rok else ""


def ale_texty(polozky, vybrana, pripona=""):
    """polozky = všetky farby modelu (ET elementy), vybrana = reprezentatívna farba."""
    p = {pr.findtext("name"): pr.findtext("value") for pr in vybrana.iter("property")}
    druh = p.get("Druh") or "Doplnkový sortiment ALÉ"
    kat, kw, typ_txt = DRUH.get(druh, DRUH["Doplnkový sortiment ALÉ"])
    pohl = p.get("Pohlavie") or ""
    if "{pohlavie}" in kat:
        kat = kat.format(pohlavie="Dámske" if pohl == "Ženy" else "Pánske")
    nazov, typ, model = ale_nazov(vybrana.findtext("name"), pohl)
    if pripona:
        nazov = f"{nazov} {pripona}" if pripona.startswith("(") else f"{nazov} – {pripona}"
        model = f"{model} ({pripona.strip('()')})" if model else model
    desc_raw = vybrana.findtext("description") or ""
    cesky = bool(CZ.search(desc_raw))
    desc = "" if cesky else cisti_popis(desc_raw)
    t = teplota(desc_raw)
    strih_k, strih_txt = STRIH.get(p.get("Strih") or "", ("", ""))
    sez = SEZONA.get(p.get("Sezóna") or "", "")
    farby = [farba_sk(i.findtext(".//property[name='Farba']/value") or "") for i in polozky]
    farby = [f for f in dict.fromkeys(farby) if f]
    pre = {"Muži": "pre mužov", "Ženy": "pre ženy", "Deti": "pre deti"}.get(pohl, "")

    veta = f"{typ} ALÉ {model}".strip() + (f" {pre}" if pre and not re.search(GENDER, typ, re.I) else "")
    kratky = veta + (f" {sez}" if sez else "") + (f" – {strih_k}" if strih_k else "") + "."
    if t:
        kratky += f" Ideálny teplotný rozsah {t[0]} až {t[1]} °C."
    kratky += " Talianska kvalita ALÉ, prémiové materiály a strih, v ktorom sa budete cítiť skvele aj na dlhej trase."

    h = [f"<h2>{e(nazov)}</h2>"]
    uvod = (f"<p><strong>{e(veta)}</strong> je {e(kw)} od talianskej značky ALÉ Cycling, ktorá neďaleko Verony vyrába cyklistické oblečenie "
            f"pre profesionálne tímy aj náročných amatérov. ")
    if sez:
        uvod += f"Model je určený {e(sez)}"
        uvod += f" a najlepšie sa cíti pri teplotách od {t[0]} do {t[1]} °C. " if t else ". "
    if strih_txt:
        uvod += e(strih_txt)
    h.append(uvod.strip() + "</p>")
    if farby:
        h.append(f"<p><strong>Dostupné farby:</strong> {e(', '.join(farby))}.</p>")
    if desc:
        h.append("<h3>Popis a technológie</h3>")
        h.append(desc if desc.startswith("<") else f"<p>{desc}</p>")
    nadpis, blok = TYP_BLOK.get(typ_txt, TYP_BLOK["doplnok"])
    h.append(f"<h3>{e(nadpis)}</h3><p>{e(blok)}</p>")
    h.append("<h3>Často kladené otázky</h3>" + FAQ_VELKOST +
             "<p><strong>Ako sa o oblečenie starať?</strong> Perte pri 30 °C naruby, bez aviváže a nesušte v sušičke – materiály si tak dlho zachovajú svoje vlastnosti.</p>")
    h.append(PRECO)
    return {
        "nazov": nazov, "kratky": kratky, "popis": "\n".join(h), "kategoria": kat,
        "seo_title": seo_title(nazov), "meta": meta(kratky, nazov, kw, "ALÉ"), "cesky": cesky,
    }


# ---------------- ostatné značky ----------------
def ina_kategoria(znacka, it, nazov):
    n = nazov.lower()
    if znacka == "QM Sportscare":
        return "Cyklistika > Cyklistická kozmetika"
    if znacka == "4iiii Innovations":
        if "hrudný pás" in n:
            return "Cyklistika > GPS cyklopočítače"
        return "Cyklistika > Cyklistické wattmetre"
    # CYCPLUS
    if any(k in n for k in ("trenažér", "virtuálne radenie", "rotor", "ventilátor", "smart bike", "mini trenažér")):
        return "Cyklistika > Cyklotrenažéry a príslušenstvo"
    if any(k in n for k in ("cyklopočítač", "monitor srdcovej", "snímač")):
        return "Cyklistika > GPS cyklopočítače"
    return "Cyklistika > Cyklistické doplnky"


def ina_nazov(znacka, it):
    n = re.sub(r"\s+", " ", it.findtext("name") or "").strip()
    p = {pr.findtext("name"): pr.findtext("value") for pr in it.iter("property")}
    kod = it.findtext("code")
    if not n:
        n = {"CPLUSDC1": "Mini trenažér pod stôl Cycplus DC1", "CPLUSBC2": "Virtuálne radenie Cycplus BC2"}.get(kod, f"Cycplus {p.get('Model', kod)}")
    n = n.replace("PRE DUAL", "PRO DUAL")
    if znacka == "4iiii Innovations":
        if n.startswith("Shimano"):
            n = f"Wattmeter 4iiii {n.replace('Shimano ', '').strip()} pre kľuky Shimano".replace("  ", " ")
            n = re.sub(r"^Wattmeter 4iiii (.+?) (Precision 3\+(?: PRO DUAL)?)( pre kľuky Shimano)$", r"Wattmeter 4iiii \2 – Shimano \1", n)
        elif "4iiii" not in n:
            n = n.replace("Viiiiva", "4iiii Viiiiva")
    if znacka == "QM Sportscare" and "QM Sportscare" not in n:
        n = f"{n} – QM Sportscare"
    if znacka == "4iiii Innovations":
        n = n.replace("(right-side)", "(pravá strana)").replace("(left-side)", "(ľavá strana)")
        n = n.replace("wattmetre Precision", "wattmetre 4iiii Precision")
    if znacka == "CYCPLUS":
        n = re.sub(r"\bCYCPLUS\b", "Cycplus", n, flags=re.I).replace("pre trenažérov", "pre trenažéry")
        if "cycplus" not in n.lower():
            n = re.sub(r"\b([A-Z]+\d+\w*)", r"Cycplus \1", n, count=1)
    return n


INTRO = {
    "QM Sportscare": ("QM Sportscare je belgická značka športovej kozmetiky, ktorú používajú profesionálne cyklistické tímy aj triatlonisti. "
                      "Prípravky sú vyvinuté pre športovcov – na zahriatie pred výkonom, ochranu pokožky počas tréningu aj na regeneráciu po ňom.", "športová kozmetika"),
    "4iiii Innovations": ("4iiii je kanadský výrobca wattmetrov a snímačov, ktorý patrí k lídrom v meraní výkonu na kľukách. "
                          "Precision wattmetre sú ľahké, presné a pripojíte ich k akémukoľvek cyklopočítaču s ANT+ alebo Bluetooth.", "wattmeter"),
    "CYCPLUS": ("Cycplus prináša chytré cyklistické vychytávky s výborným pomerom ceny a výkonu – od elektronických púmp cez radary a cyklopočítače "
                "až po smart trenažéry kompatibilné so Zwiftom a ďalšími aplikáciami.", "cyklistické príslušenstvo"),
}


def ina_texty(znacka, it):
    nazov = ina_nazov(znacka, it)
    desc_raw = it.findtext("description") or ""
    cesky = bool(CZ.search(desc_raw))
    desc = "" if cesky else cisti_popis(desc_raw)
    intro, kw = INTRO[znacka]
    prvy = re.sub(r"<[^>]+>", " ", desc)
    prvy = re.sub(r"\s+", " ", prvy).strip()
    veta = re.split(r"(?<=[.!?])\s", prvy, 1)[0] if prvy else ""
    if len(veta) > 170 or len(veta) < 25:
        veta = ""
    kratky = (veta + " " if veta else "") + f"Originálny produkt {znacka.replace(' Innovations', '').replace(' Sportscare', '')} s rýchlym doručením a odborným poradenstvom TRIEX.sk."
    h = [f"<h2>{e(nazov)}</h2>", f"<p>{e(intro)}</p>"]
    if desc:
        h.append("<h3>Popis produktu</h3>")
        h.append(desc if desc.lstrip().startswith("<") else f"<p>{desc}</p>")
    h.append(PRECO)
    return {
        "nazov": nazov, "kratky": kratky, "popis": "\n".join(h), "kategoria": ina_kategoria(znacka, it, nazov),
        "seo_title": seo_title(nazov), "meta": meta(kratky, nazov, kw, znacka.split()[0]), "cesky": cesky,
    }


def seo_title(nazov):
    t = f"{nazov} | TRIEX.sk"
    if len(t) > 65:
        t = f"{nazov} | TRIEX"
    return t


def meta(kratky, nazov, kw, znacka):
    znacka = {"CYCPLUS": "Cycplus", "QM": "QM Sportscare"}.get(znacka, znacka)
    prva = kratky.split(". ")[0].rstrip(".")
    m = f"{prva}. ✅ Originál {znacka} ✅ Poradíme s výberom ✅ TRIEX.sk"
    if len(m) > 160:
        m = f"{nazov} – {kw}. ✅ Originál {znacka} ✅ Poradíme s výberom ✅ TRIEX.sk"
    if len(m) > 160:
        m = f"{nazov}. ✅ Originál {znacka} ✅ TRIEX.sk"
    return m
