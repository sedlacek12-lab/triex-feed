"""Slovenské názvy, kategórie a texty pre nové ZONE3 produkty (TRIEX.sk).

Poradie zdrojov textu:
 1. ručne napísaný/odsúhlasený text v zone3_texty.json (kľúč = kód produktu alebo model)
 2. úvod k modelovej rade (MODELY nižšie) + šablóna podľa typu produktu
Tvrdenia sú držané všeobecne – nič, čo výrobca neuvádza v názve alebo kategórii.
"""
import html, json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))

# typ produktu: (regex na anglický názov, podstatné meno, rod m/f/n/pl, kategória TRIEX, šablóna)
TYPES = [
    (r"under trisuit", "spodné nohavičky pod kombinézu", "pl", "Cyklistika > Triatlonové dresy", "underwear"),
    (r"changing mat", "prezliekacia podložka", "f", "Plávanie > Plavecké doplnky", "generic"),
    (r"swim[- ]?run.*(wetsuit)|swimrun", "swimrunový neoprén", "m", "Plávanie > Plavecké neoprény a doplnky", "swimrun"),
    (r"wetsuit|^(advance|agile|vanquish|vision|aspire)$", "neoprén", "m", "Plávanie > Plavecké neoprény a doplnky", "wetsuit"),
    (r"swim ?skin", "swimskin", "m", "Plávanie > Plavecké oblečenie", "swimskin"),
    (r"trisuit|aero suit|tri suit|itu design", "triatlonová kombinéza", "f", "Cyklistika > Triatlonové dresy", "trisuit"),
    (r"tri shorts|activate shorts", "triatlonové šortky", "pl", "Cyklistika > Triatlonové dresy", "trishorts"),
    (r"tri top|long distance top|warmth top|activate top", "triatlonový top", "m", "Cyklistika > Triatlonové dresy", "tritop"),
    (r"arm warmers|arm sleeve", "návleky na ruky", "pl", "Cyklistika > Cyklistické oblečenie > Cyklistické doplnky", "armwarmers"),
    (r"goggles|swim mask", "plavecké okuliare", "pl", "Plávanie > Plavecké okuliare", "goggles"),
    (r"heat-tech.*cap|neoprene.*cap|swim beanie", "neoprénová plavecká čiapka", "f", "Plávanie > Plavecké čiapky", "neocap"),
    (r"swim cap", "plavecká čiapka", "f", "Plávanie > Plavecké čiapky", "cap"),
    (r"glove", "neoprénové rukavice", "pl", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"sock|boot", "neoprénové ponožky", "pl", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"balaclava", "neoprénová kukla", "f", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"headband", "neoprénová čelenka", "f", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"buoyancy shorts|yulex.*shorts|swim-?run shorts", "neoprénové šortky", "pl", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"vest|swim-?run top|yulex.*long sleeve swimsuit|long sleeve swimsuit", "neoprénový top", "m", "Plávanie > Plavecké neoprény a doplnky", "neoacc"),
    (r"jammer", "plavky jammery", "pl", "Plávanie > Pánske plavky", "jammer"),
    (r"aqua shorts|brief", "plavky", "pl", "Plávanie > Pánske plavky", "menswim"),
    (r"kneeskin|knee skin", "plavky kneeskin", "pl", "Plávanie > Dámske plavky", "womenswim"),
    (r"costume|swimsuit|tankini", "plavky", "pl", "Plávanie > Dámske plavky", "womenswim"),
    (r"paddles", "plavecké pádla", "pl", "Plávanie > Plavecké tréningové pomôcky > Plavecké pádla", "paddles"),
    (r"snorkel", "plavecký šnorchel", "m", "Plávanie > Plavecké tréningové pomôcky > Plavecké šnorchle", "snorkel"),
    (r"race belt|number belt", "pás na štartové číslo", "m", "Bežecké potreby > Bežecké doplnky", "racebelt"),
    (r"visor", "bežecký šilt", "m", "Bežecké potreby > Bežecké doplnky", "visor"),
    (r"laces", "elastické šnúrky do topánok", "pl", "Bežecké potreby > Bežecké doplnky", "laces"),
    (r"buoy|dry bag", "plavecká bójka a vodotesný vak", "f", "Plávanie > Plavecké bóje", "buoy"),
    (r"towel", "uterák z mikrovlákna", "m", "Plávanie > Plavecké doplnky", "towel"),
    (r"robe|parka", "prezliekací plášť", "m", "Plávanie > Plavecké oblečenie", "robe"),
    (r"backpack", "batoh", "m", "Doplnky > Batohy", "generic"),
    (r"compass|whistle", "kompas a píšťalka na swimrun", "m", "Plávanie > Plavecké doplnky", "generic"),
]

GENDER_ADJ = {  # (pánsky, dámsky, detský, unisex) podľa rodu
    "m": ("Pánsky", "Dámsky", "Detský", ""), "f": ("Pánska", "Dámska", "Detská", ""),
    "pl": ("Pánske", "Dámske", "Detské", ""), "n": ("Pánske", "Dámske", "Detské", ""),
}

TEMPLATES = {
    "wetsuit": ["Pružný neoprén pre voľnosť pohybu pri zábere.",
                "Vztlakové panely pomáhajú udržať nohy a boky vysoko pri hladine.",
                "Hladký povrch znižuje odpor vody a urýchľuje plávanie.",
                "Rýchle a jednoduché vyzliekanie v depe.",
                "Vhodný na triatlon, plávanie v otvorenej vode aj tréning."],
    "swimrun": ["Navrhnutý pre swimrun – plávanie aj beh v jednom obleku.",
                "Pružný materiál, ktorý neobmedzuje pri behu.",
                "Odolný v náročnom teréne."],
    "swimskin": ["Plavecký oblek bez neoprénu pre preteky, kde neoprén nie je povolený.",
                 "Hydrodynamický materiál znižuje odpor vody.",
                 "Obopína telo a podporuje správnu polohu vo vode."],
    "trisuit": ["Jednodielna kombinéza na plávanie, bicykel aj beh bez prezliekania.",
                "Vložka určená pre triatlon – pohodlná na bicykli, nezavadzia pri behu.",
                "Rýchloschnúci a priedušný materiál."],
    "trishorts": ["Triatlonové šortky s vložkou vhodnou na plávanie, bicykel aj beh.",
                  "Rýchloschnúci materiál."],
    "tritop": ["Triatlonový top z rýchloschnúceho a priedušného materiálu.",
               "Kombinuje sa s triatlonovými šortkami.",
               "Pohodlný strih pre plávanie, bicykel aj beh."],
    "armwarmers": ["Návleky na ruky pre chladnejšie rána a zjazdy.",
                   "Ľahko sa dajú stiahnuť a odložiť do vrecka.",
                   "Elastický materiál, ktorý drží na mieste."],
    "goggles": ["Plavecké okuliare pre bazén aj otvorenú vodu.",
                "Úprava proti zahmlievaniu a ochrana proti UV žiareniu.",
                "Pohodlné tesnenie a nastaviteľný pásik."],
    "cap": ["Silikónová plavecká čiapka – odolná a príjemná na nosenie.",
            "Výrazná farba pre lepšiu viditeľnosť v otvorenej vode."],
    "neocap": ["Neoprénová čiapka udrží teplo hlavy v studenej vode.",
               "Upínanie pod bradou drží čiapku na mieste."],
    "neoacc": ["Neoprénový doplnok pre plávanie v chladnej vode.",
               "Pomáha udržať telo v teple a predĺžiť sezónu v otvorenej vode."],
    "jammer": ["Pánske plavky v strihu jammer po kolená.",
               "Vhodné na tréning aj preteky."],
    "menswim": ["Pánske plavky na tréning aj voľný čas.",
                "Pohodlný strih na tréning v bazéne."],
    "womenswim": ["Dámske jednodielne plavky na tréning v bazéne aj otvorenej vode.",
                  "Odolný materiál, ktorý si drží tvar.",
                  "Pohodlný strih, ktorý neobmedzuje pri plávaní."],
    "paddles": ["Plavecké pádla na posilnenie záberu a zlepšenie techniky.",
                "Vhodné pre začiatočníkov aj skúsených plavcov."],
    "snorkel": ["Čelný plavecký šnorchel – sústredíte sa na techniku bez otáčania hlavy.",
                "Nastaviteľný držiak na hlavu."],
    "racebelt": ["Pás na štartové číslo pre triatlon a beh.",
                 "Číslo rýchlo otočíte medzi bicyklom a behom.",
                 "Nastaviteľná dĺžka."],
    "visor": ["Ľahký bežecký šilt chráni oči pred slnkom.", "Absorbuje pot a rýchlo schne."],
    "laces": ["Elastické šnúrky – topánky obujete bez zaväzovania.", "Ušetrí čas v depe pri triatlone."],
    "buoy": ["Bójka zvyšuje vašu viditeľnosť v otvorenej vode.",
             "Zároveň slúži ako vodotesný vak na osobné veci.",
             "Pripína sa okolo pásu a pri plávaní nezavadzia."],
    "towel": ["Ľahký uterák z mikrovlákna, ktorý rýchlo schne.", "Zaberie málo miesta v taške."],
    "robe": ["Prezliekací plášť na prezliekanie pri vode.", "Udrží teplo pred a po plávaní."],
    "underwear": ["Spodné nohavičky určené pod triatlonovú kombinézu."],
    "generic": ["Praktický doplnok značky Zone3."],
}

# krátky úvod k modelovým radám (overené všeobecné informácie o rade)
MODELY = {
    "aspire": "Zone3 Aspire je neoprén strednej triedy pre triatlonistov, ktorí chcú viac pružnosti a rýchlosti než pri vstupných modeloch.",
    "active-flex": "Rada Zone3 Active-Flex je určená na plávanie v otvorenej vode a triatlon – dôraz kladie na pohodlie a voľnosť pohybu.",
    "versa": "Zone3 Versa je univerzálny swimrunový neoprén s odopínateľnými rukávmi.",
    "evolution": "Zone3 Evolution je swimrunový neoprén pre preteky, ktoré striedajú plávanie a beh v teréne.",
    "vanquish": "Zone3 Vanquish je vrcholový pretekársky neoprén značky Zone3.",
    "agile": "Zone3 Agile je pohodlný neoprén pre začínajúcich aj pokročilých triatlonistov.",
    "advance": "Zone3 Advance patrí medzi najobľúbenejšie vstupné neoprény na trhu.",
    "vision": "Zone3 Vision je neoprén strednej triedy s výborným pomerom ceny a výkonu.",
    "yulex": "Rada Zone3 Yulex® je vyrobená z prírodného kaučuku Yulex namiesto klasického neoprénu.",
    "activate": "Rada Zone3 Activate je určená pre triatlonistov, ktorí hľadajú pohodlné a cenovo dostupné oblečenie na preteky.",
    "lava": "Rada Zone3 Lava je navrhnutá na dlhé triatlonové preteky a teplé podmienky.",
    "aeroforce": "Rada Zone3 Aeroforce je pretekárska aerodynamická rada pre rýchly triatlon.",
    "venator": "Okuliare Zone3 Venator-X majú široké zorné pole a nízky profil pre pretekárov.",
    "vapour": "Okuliare Zone3 Vapour ponúkajú široké zorné pole a pohodlie na dlhé plávanie.",
    "attack": "Okuliare Zone3 Attack sú obľúbené tréningové a pretekárske okuliare.",
    "volaire": "Okuliare Zone3 Volaire Streamline sú nízkoprofilové pretekárske okuliare.",
    "aquahero": "Okuliare Zone3 Aquahero sú určené pre triatlon a plávanie v otvorenej vode.",
    "heat-tech": "Rada Zone3 Heat-Tech je určená na plávanie v studenej vode.",
    "thermo": "Rada Zone3 Thermo-Tech udrží teplo pri plávaní v studenej vode.",
    "ows ti+": "Rada Zone3 OWS Ti+ má podšívku s titánom, ktorá odráža teplo späť k telu – ideálna do studenej otvorenej vody.",
    "ows renew": "Rada Zone3 OWS Renew je vyrobená z recyklovaných materiálov.",
    "cosmic": "Rada Zone3 Cosmic zaujme výraznými farebnými vzormi.",
    "prism": "Rada Zone3 Prism má výrazný geometrický dizajn.",
    "aztec": "Rada Zone3 Aztec má výrazný farebný vzor.",
    "iconic": "Rada Zone3 Iconic ponúka nadčasový dizajn na každodenný tréning.",
    "mf-x": "Rada Zone3 MF-X Performance Gold je pretekárska rada plaviek.",
    "fina": "Plavky so schválením FINA (World Aquatics) sú povolené na oficiálnych pretekoch.",
    "kona": "Rada Zone3 Kona Speed je inšpirovaná legendárnymi pretekmi na Havaji.",
    "pacific koa": "Rada Zone3 Pacific Koa má motív inšpirovaný havajskou prírodou.",
}

UK_TO_EU = {"6": "34", "8": "36", "10": "38", "12": "40", "14": "42", "16": "44", "18": "46", "20": "48"}
COLOR_SK = {}  # farby ostávajú v angličtine, ako ich používa výrobca aj TRIEX


def detect(name):
    low = model_name(name).lower()
    for rx, noun, rod, cat, tpl in TYPES:
        if re.search(rx, low):
            return noun, rod, cat, tpl
    return "doplnok", "m", "Plávanie > Plavecké doplnky", "generic"


def gender(name):
    name = name.replace("’", "'")
    if re.search(r"jammer", name, re.I) or re.search(r"\bmen'?s\b", name, re.I) and not re.match(r"wom", name, re.I): return 0
    if re.match(r"(men|mens|boy)", name, re.I): return 0
    if re.match(r"(women|womens|girl|ladies)", name, re.I) or re.search(r"\bwomen'?s\b", name, re.I): return 1
    if re.match(r"kid", name, re.I): return 2
    return 3


STRIP_WORDS = r"\b(Triathlon/Open Water Swimming Wetsuit|Swim Goggles|Goggles|Wetsuit|Trisuit|Swimsuit|Costume|Jammers?|Hand Paddles|Swim Cap|Towel|Swimskin|Swim Skin|Arm Warmers|Robe)\b"


def clean_model(name):
    m = re.sub(STRIP_WORDS, "", model_name(name), flags=re.I)
    m = re.sub(r"\bFina Approved\b", "FINA", m, flags=re.I)
    m = re.sub(r"\b(Men|Women)'?s\b", "", m, flags=re.I)
    m = re.sub(r"\s*-\s*$|^\s*-\s*", "", re.sub(r"\s+", " ", m)).strip(" -")
    return m or model_name(name)


def model_name(name):
    m = re.sub(r"\s+/\s.*$", "", name)
    m = re.sub(r"^(Men'?s|Women'?s|Mens|Womens|Unisex|Boy'?s|Girl'?s|Kid'?s)\s+", "", m, flags=re.I)
    return re.sub(r"\s+", " ", m.replace("’", "'")).strip()


def sk_name(p):
    noun, rod, _, _ = detect(p["name_cs"])
    g = GENDER_ADJ[rod][gender(p["name_cs"])]
    title = f"{g} {noun}".strip()
    title = title[0].upper() + title[1:]
    col = p.get("colour") or ""
    color = f" / {col}" if col and "uveden" not in col else ""
    return f"{title} Zone3 {clean_model(p['name_cs'])}{color}"


def intro(name):
    low = name.lower()
    for k, t in MODELY.items():
        if k in low:
            return t
    return ""


def sizes_label(p, tpl):
    out = []
    for v in p["variants"]:
        s = v["variant"] or ""
        if tpl == "womenswim" and s in UK_TO_EU:
            s = f"UK {s} / EU {UK_TO_EU[s]}"
        out.append(s)
    return ", ".join(x for x in out if x and x != "OS") or "univerzálna"


def build_texts(p, overrides):
    noun, rod, cat, tpl = detect(p["name_cs"])
    name = sk_name(p)
    ov = overrides.get(p["code"]) or overrides.get(model_name(p["name_cs"]).lower())
    if ov:
        return {"nazov": ov.get("nazov", name), "kategoria": ov.get("kategoria", cat), **{k: ov[k] for k in ("kratky_popis", "popis_html") if k in ov},
                "seo_title": ov.get("seo_title", f"{name.split(' / ')[0]} | TRIEX.sk"),
                "meta_description": ov.get("meta_description", ov.get("kratky_popis", "")[:155])}
    e = html.escape
    bullets = TEMPLATES[tpl]
    lead = intro(p["name_cs"])
    short = f"{lead} " if lead else ""
    short += bullets[0]
    col = p.get("colour") or ""
    params = [f"<li><strong>Farba:</strong> {e(col)}</li>" if col and "uveden" not in col else "",
              f"<li><strong>Veľkosti:</strong> {e(sizes_label(p, tpl))}</li>",
              "<li><strong>Značka:</strong> Zone3 (Veľká Británia)</li>"]
    desc = (f"<p><strong>{e(name.split(' / ')[0])}</strong></p>"
            + (f"<p>{e(lead)}</p>" if lead else "")
            + "<ul>" + "".join(f"<li>{e(b)}</li>" for b in bullets) + "</ul>"
            + "<p><strong>Parametre</strong></p><ul>" + "".join(params) + "</ul>")
    if tpl in ("wetsuit", "swimrun", "trisuit", "trishorts", "tritop", "womenswim", "jammer", "menswim", "swimskin", "neoacc"):
        desc += "<p>Správnu veľkosť nájdete v <a href=\"/tabulka-velkosti/\">tabuľke veľkostí</a>.</p>"
    meta = f"{name.split(' / ')[0]}. {bullets[0]} Skladom v TRIEX.sk."
    return {"nazov": name, "kategoria": cat, "kratky_popis": short, "popis_html": desc,
            "seo_title": f"{name.split(' / ')[0]} | TRIEX.sk", "meta_description": meta[:160]}


def load_overrides():
    p = os.path.join(HERE, "zone3_texty.json")
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else {}
