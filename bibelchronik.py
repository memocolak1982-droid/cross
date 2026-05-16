# -*- coding: utf-8 -*-
"""
Bibelchronik - Die sieben Zeitalter (Heilszeitalter)
=====================================================
Erzeugt eine druckbare Chronik im A3-Querformat (PDF) nach der Vorlage
"Das zweite Zeitalter - Vor der Flut".

Jedes der sieben Zeitalter wird auf einem eigenen A3-Blatt dargestellt:
Kopfbanner, Navigation, zwei genealogische Baender mit Medaillons,
eine Gerichts-Karte und eine Zeitleiste.

Aufruf:  python3 bibelchronik.py
Ergebnis: bibelchronik.pdf  und  bibelchronik.html
"""

from weasyprint import HTML

# ---------------------------------------------------------------------------
# DATEN: Die sieben Zeitalter
# ---------------------------------------------------------------------------

ZEITALTER = [
    {
        "nummer": "DAS ERSTE ZEITALTER",
        "tagline": "IM PARADIES",
        "titel": "UNSCHULD",
        "vorher": None,
        "referenz": "1. Mose 1-3",
        "gericht_satz": "Das erste Zeitalter endet im Gericht: Der Suendenfall",
        "fusszeile": "1. MOSE 1-3",
        "baender": [
            {
                "label": "Die Schoepfung und der Mensch",
                "stil": "licht",
                "knoten": [
                    {"name": "Die Schoepfung", "untertitel": "Gott schafft Himmel und Erde",
                     "zitat": "Im Anfang schuf Gott Himmel und Erde.", "quelle": "1.Mo 1,1"},
                    {"name": "Adam", "untertitel": "Der erste Mensch nach Gottes Bild",
                     "zitat": "Und Gott schuf den Menschen ihm zum Bilde.", "quelle": "1.Mo 1,27"},
                    {"name": "Der Garten Eden", "untertitel": "Der Mensch im Paradies",
                     "zitat": "Und Gott der HERR pflanzte einen Garten in Eden.", "quelle": "1.Mo 2,8"},
                    {"name": "Eva", "untertitel": "Die Frau, dem Mann zur Seite",
                     "zitat": "Es ist nicht gut, dass der Mensch allein sei.", "quelle": "1.Mo 2,18"},
                    {"name": "Das Gebot", "untertitel": "Gottes einzige Schranke",
                     "zitat": "Von dem Baum der Erkenntnis sollst du nicht essen.", "quelle": "1.Mo 2,17"},
                ],
            },
            {
                "label": "Die Versuchung und der Fall",
                "stil": "dunkel",
                "knoten": [
                    {"name": "Die Schlange", "untertitel": "Der Zweifel an Gottes Wort",
                     "zitat": "Sollte Gott gesagt haben: Ihr sollt nicht essen?", "quelle": "1.Mo 3,1"},
                    {"name": "Der Suendenfall", "untertitel": "Der Ungehorsam des Menschen",
                     "zitat": "Sie nahm von der Frucht und ass und gab ihrem Mann.", "quelle": "1.Mo 3,6"},
                    {"name": "Die Vertreibung", "untertitel": "Aus Gottes Gegenwart verbannt",
                     "zitat": "Da wies ihn Gott der HERR aus dem Garten Eden.", "quelle": "1.Mo 3,23"},
                ],
            },
        ],
        "gericht": {
            "titel": "Der Suendenfall",
            "zitat": "Verflucht sei der Acker um deinetwillen ... im Schweisse deines Angesichts sollst du dein Brot essen.",
            "quelle": "1.Mo 3,17.19",
            "datum": "vor 4000 v. Chr.",
        },
        "zeitstrahl": {
            "ereignisse": ["Erschaffung der Welt", "Erschaffung des Menschen",
                           "Der Garten Eden", "Das Gebot Gottes", "Der Suendenfall"],
            "daten": ["Im Anfang", "Das Paradies", "Der Fall"],
        },
    },

    {
        "nummer": "DAS ZWEITE ZEITALTER",
        "tagline": "VOR DER FLUT",
        "titel": "GEWISSEN",
        "vorher": "UNSCHULD",
        "referenz": "1. Mose 3-7",
        "gericht_satz": "Das zweite Zeitalter endet im Gericht: Die Flut",
        "fusszeile": "1. MOSE 3-7",
        "baender": [
            {
                "label": "Nachkommen Kains",
                "stil": "grau",
                "knoten": [
                    {"name": "Kain", "untertitel": "Brudermord",
                     "zitat": "Und Kain erhob sich gegen seinen Bruder Abel und toetete ihn.", "quelle": "1.Mo 4,8"},
                    {"name": "Henoch (Sohn Kains)", "untertitel": "Erste Stadt gebaut",
                     "zitat": "Und er baute eine Stadt und nannte sie nach seinem Sohn Henoch.", "quelle": "1.Mo 4,17"},
                    {"name": "Lamech", "untertitel": "Erste Vielehe, Gewalt und Rache",
                     "zitat": "Lamech sprach zu seinen Frauen: Ich habe einen Mann erschlagen.", "quelle": "1.Mo 4,23"},
                    {"name": "Verderbtheit der Welt", "untertitel": "Totale Korruption der Menschheit",
                     "zitat": "Gott sah, dass die Bosheit des Menschen gross war, und es reute ihn.", "quelle": "1.Mo 6,5-6"},
                ],
            },
            {
                "label": "Nachkommen Seths",
                "stil": "gold",
                "knoten": [
                    {"name": "Seth", "untertitel": "Neuer Anfang nach Abel",
                     "zitat": "Adam zeugte einen Sohn und nannte ihn Seth.", "quelle": "1.Mo 4,25"},
                    {"name": "Enosch", "untertitel": "Beginn des Rufens zum HERRN",
                     "zitat": "Damals begann man, den Namen des HERRN anzurufen.", "quelle": "1.Mo 4,26"},
                    {"name": "Kenan", "untertitel": "Treue Linie Gottes",
                     "zitat": "Und Kenan lebte 70 Jahre und zeugte Mahalalel.", "quelle": "1.Mo 5,12"},
                    {"name": "Mahalalel", "untertitel": "Die treue Linie setzt sich fort",
                     "zitat": "Und Mahalalel lebte 65 Jahre und zeugte Jared.", "quelle": "1.Mo 5,15"},
                    {"name": "Jared", "untertitel": "Vater Henochs",
                     "zitat": "Und Jared lebte 162 Jahre und zeugte Henoch.", "quelle": "1.Mo 5,18"},
                    {"name": "Henoch", "untertitel": "Entrueckt - wandelte mit Gott",
                     "zitat": "Henoch wandelte mit Gott, und Gott nahm ihn hinweg.", "quelle": "1.Mo 5,24"},
                    {"name": "Methusalah", "untertitel": "Aeltester Mensch - 969 Jahre",
                     "zitat": "Und alle Tage Methusalahs waren 969 Jahre.", "quelle": "1.Mo 5,27"},
                    {"name": "Lamech", "untertitel": "Vater Noahs - sieht die Hoffnung",
                     "zitat": "Dieser wird uns troesten ueber die Muehsal unserer Haende.", "quelle": "1.Mo 5,29"},
                    {"name": "Noah", "untertitel": "Gerecht und untadelig - baut die Arche",
                     "zitat": "Noah war gerecht und untadelig und wandelte mit Gott.", "quelle": "1.Mo 6,9"},
                ],
            },
        ],
        "gericht": {
            "titel": "Die Flut",
            "zitat": "Mache dir eine Arche aus Zypressenholz ... denn ich will eine Sintflut ueber die Erde bringen.",
            "quelle": "1.Mo 6,14.17",
            "datum": "um 2500 v. Chr.",
        },
        "zeitstrahl": {
            "ereignisse": ["Erschaffung", "Kain und Abel", "Verderbtheit der Welt",
                           "Henoch entrueckt", "Methusalah", "Noah", "Die Flut"],
            "daten": ["4000 v.Chr.", "3500 v.Chr.", "3000 v.Chr.", "2500 v.Chr."],
        },
    },

    {
        "nummer": "DAS DRITTE ZEITALTER",
        "tagline": "DIE NEUE WELT",
        "titel": "MENSCHLICHE REGIERUNG",
        "vorher": "GEWISSEN",
        "referenz": "1. Mose 8-11",
        "gericht_satz": "Das dritte Zeitalter endet im Gericht: Die Sprachverwirrung von Babel",
        "fusszeile": "1. MOSE 8-11",
        "baender": [
            {
                "label": "Der neue Anfang nach der Flut",
                "stil": "licht",
                "knoten": [
                    {"name": "Noah verlaesst die Arche", "untertitel": "Neuanfang der Menschheit",
                     "zitat": "Geh aus der Arche, du und deine Frau und deine Soehne.", "quelle": "1.Mo 8,16"},
                    {"name": "Der Altar", "untertitel": "Dank und Anbetung",
                     "zitat": "Und Noah baute dem HERRN einen Altar.", "quelle": "1.Mo 8,20"},
                    {"name": "Der Bund", "untertitel": "Gottes Verheissung mit dem Regenbogen",
                     "zitat": "Meinen Bogen habe ich gesetzt in die Wolken.", "quelle": "1.Mo 9,13"},
                    {"name": "Die Regierung", "untertitel": "Der Mensch erhaelt Verantwortung",
                     "zitat": "Wer Menschenblut vergiesst, dessen Blut soll vergossen werden.", "quelle": "1.Mo 9,6"},
                ],
            },
            {
                "label": "Die Voelker und der Hochmut",
                "stil": "grau",
                "knoten": [
                    {"name": "Sem, Ham und Jafet", "untertitel": "Stammvaeter aller Voelker",
                     "zitat": "Von ihnen sind ausgebreitet alle Voelker auf Erden.", "quelle": "1.Mo 9,19"},
                    {"name": "Nimrod", "untertitel": "Erster Gewaltherrscher der Erde",
                     "zitat": "Er war der erste, der Macht gewann auf Erden.", "quelle": "1.Mo 10,8"},
                    {"name": "Der Turmbau zu Babel", "untertitel": "Hochmut: ein Name ohne Gott",
                     "zitat": "Lasst uns einen Turm bauen, dass wir uns einen Namen machen.", "quelle": "1.Mo 11,4"},
                    {"name": "Die Sprachverwirrung", "untertitel": "Gott zerstreut die Menschheit",
                     "zitat": "Der HERR hat daselbst verwirrt aller Welt Sprache.", "quelle": "1.Mo 11,9"},
                ],
            },
        ],
        "gericht": {
            "titel": "Babel",
            "zitat": "Und der HERR zerstreute sie von dort ueber die ganze Erde, sodass sie aufhoeren mussten, die Stadt zu bauen.",
            "quelle": "1.Mo 11,8",
            "datum": "um 2300 v. Chr.",
        },
        "zeitstrahl": {
            "ereignisse": ["Die Flut", "Noahs Altar", "Der Bund Gottes",
                           "Die Voelkertafel", "Nimrod", "Turmbau zu Babel"],
            "daten": ["2500 v.Chr.", "2400 v.Chr.", "2300 v.Chr."],
        },
    },

    {
        "nummer": "DAS VIERTE ZEITALTER",
        "tagline": "DIE ZEIT DER VAETER",
        "titel": "VERHEISSUNG",
        "vorher": "MENSCHL. REGIERUNG",
        "referenz": "1. Mose 12 - 2. Mose 19",
        "gericht_satz": "Das vierte Zeitalter endet im Gericht: Die Knechtschaft in Aegypten",
        "fusszeile": "1. MOSE 12 - 2. MOSE 19",
        "baender": [
            {
                "label": "Die Erzvaeter",
                "stil": "gold",
                "knoten": [
                    {"name": "Abraham", "untertitel": "Vater des Glaubens - berufen aus Ur",
                     "zitat": "Geh aus deinem Vaterland in ein Land, das ich dir zeigen will.", "quelle": "1.Mo 12,1"},
                    {"name": "Der Bund", "untertitel": "Gott verheisst Land und Nachkommen",
                     "zitat": "Ich will dich zum grossen Volk machen und dich segnen.", "quelle": "1.Mo 12,2"},
                    {"name": "Isaak", "untertitel": "Der Sohn der Verheissung",
                     "zitat": "Sara wird dir einen Sohn gebaeren, den sollst du Isaak nennen.", "quelle": "1.Mo 17,19"},
                    {"name": "Jakob (Israel)", "untertitel": "Vater der zwoelf Staemme",
                     "zitat": "Du sollst nicht mehr Jakob heissen, sondern Israel.", "quelle": "1.Mo 32,29"},
                ],
            },
            {
                "label": "Der Weg nach Aegypten",
                "stil": "erde",
                "knoten": [
                    {"name": "Josef", "untertitel": "Verkauft - doch von Gott erhoeht",
                     "zitat": "Ihr gedachtet es boese, aber Gott gedachte es gut zu machen.", "quelle": "1.Mo 50,20"},
                    {"name": "Israel in Aegypten", "untertitel": "Das Volk waechst im fremden Land",
                     "zitat": "Die Kinder Israel waren fruchtbar, und das Land ward voll.", "quelle": "2.Mo 1,7"},
                    {"name": "Die Knechtschaft", "untertitel": "Ein neuer Pharao unterdrueckt das Volk",
                     "zitat": "Man setzte Fronvoegte ueber sie, um sie mit Arbeit zu druecken.", "quelle": "2.Mo 1,11"},
                ],
            },
        ],
        "gericht": {
            "titel": "Die Knechtschaft",
            "zitat": "Und die Kinder Israel seufzten ueber ihre Arbeit und schrien, und ihr Schreien kam vor Gott.",
            "quelle": "2.Mo 2,23",
            "datum": "um 1500 v. Chr.",
        },
        "zeitstrahl": {
            "ereignisse": ["Babel", "Berufung Abrahams", "Isaak", "Jakob",
                           "Josef in Aegypten", "Die Knechtschaft"],
            "daten": ["2000 v.Chr.", "1800 v.Chr.", "1600 v.Chr.", "1500 v.Chr."],
        },
    },

    {
        "nummer": "DAS FUENFTE ZEITALTER",
        "tagline": "DAS GESETZ UND DIE PROPHETEN",
        "titel": "GESETZ",
        "vorher": "VERHEISSUNG",
        "referenz": "2. Mose 19 - Maleachi",
        "gericht_satz": "Das fuenfte Zeitalter endet im Gericht: Die Verwerfung des Messias",
        "fusszeile": "2. MOSE 19 - MALEACHI",
        "baender": [
            {
                "label": "Gesetz und Koenige",
                "stil": "gold",
                "knoten": [
                    {"name": "Mose", "untertitel": "Befreier - empfaengt das Gesetz am Sinai",
                     "zitat": "Gott redete: Ich bin der HERR, dein Gott.", "quelle": "2.Mo 20,1-2"},
                    {"name": "Josua", "untertitel": "Einzug in das verheissene Land",
                     "zitat": "Sei getrost und unverzagt, der HERR ist mit dir.", "quelle": "Josua 1,9"},
                    {"name": "David", "untertitel": "Koenig nach dem Herzen Gottes",
                     "zitat": "Der HERR hat sich einen Mann nach seinem Herzen ersehen.", "quelle": "1.Sam 13,14"},
                    {"name": "Salomo", "untertitel": "Erbaut den Tempel des HERRN",
                     "zitat": "Salomo baute dem HERRN das Haus und vollendete es.", "quelle": "1.Koen 6,14"},
                ],
            },
            {
                "label": "Propheten und Gericht",
                "stil": "dunkel",
                "knoten": [
                    {"name": "Die Propheten", "untertitel": "Gott ruft sein Volk zur Umkehr",
                     "zitat": "Der HERR sandte zu ihnen seine Propheten, frueh und immerfort.", "quelle": "2.Chr 36,15"},
                    {"name": "Das Exil", "untertitel": "Gericht ueber Israels Untreue",
                     "zitat": "Er fuehrte hinweg gen Babel, was vom Schwert uebrig war.", "quelle": "2.Chr 36,20"},
                    {"name": "Johannes der Taeufer", "untertitel": "Die Stimme des Rufers in der Wueste",
                     "zitat": "Bereitet dem HERRN den Weg und macht seine Steige eben!", "quelle": "Mt 3,3"},
                    {"name": "Der Messias verworfen", "untertitel": "Er kam in sein Eigentum",
                     "zitat": "Er kam in sein Eigentum, und die Seinen nahmen ihn nicht auf.", "quelle": "Joh 1,11"},
                ],
            },
        ],
        "gericht": {
            "titel": "Das Kreuz",
            "zitat": "Christus hat uns erloest von dem Fluch des Gesetzes, da er ward ein Fluch fuer uns.",
            "quelle": "Galater 3,13",
            "datum": "um 30 n. Chr.",
        },
        "zeitstrahl": {
            "ereignisse": ["Knechtschaft", "Gesetz am Sinai", "Einzug ins Land",
                           "Koenig David", "Tempel Salomos", "Das Exil", "Der Messias"],
            "daten": ["1500 v.Chr.", "1000 v.Chr.", "586 v.Chr.", "30 n.Chr."],
        },
    },

    {
        "nummer": "DAS SECHSTE ZEITALTER",
        "tagline": "DIE ZEIT DER GNADE",
        "titel": "GNADE",
        "vorher": "GESETZ",
        "referenz": "Apg 2 - Offenbarung 19",
        "gericht_satz": "Das sechste Zeitalter endet im Gericht: Die grosse Truebsal",
        "fusszeile": "APOSTELGESCHICHTE 2 - OFFENBARUNG 19",
        "baender": [
            {
                "label": "Die Gemeinde",
                "stil": "geist",
                "knoten": [
                    {"name": "Pfingsten", "untertitel": "Der Heilige Geist wird ausgegossen",
                     "zitat": "Sie wurden alle erfuellt von dem Heiligen Geist.", "quelle": "Apg 2,4"},
                    {"name": "Die erste Gemeinde", "untertitel": "Lehre, Gemeinschaft und Gebet",
                     "zitat": "Sie blieben bestaendig in der Lehre der Apostel.", "quelle": "Apg 2,42"},
                    {"name": "Paulus", "untertitel": "Apostel der Heiden",
                     "zitat": "Aus Gnaden seid ihr selig geworden durch den Glauben.", "quelle": "Eph 2,8"},
                    {"name": "Das Evangelium der Welt", "untertitel": "Der Auftrag der Gemeinde",
                     "zitat": "Gehet hin in alle Welt und predigt das Evangelium.", "quelle": "Mk 16,15"},
                ],
            },
            {
                "label": "Die Vollendung",
                "stil": "dunkel",
                "knoten": [
                    {"name": "Die Entrueckung", "untertitel": "Der Herr holt die Seinen heim",
                     "zitat": "Wir werden dem Herrn entgegen entrueckt in der Luft.", "quelle": "1.Thess 4,17"},
                    {"name": "Die grosse Truebsal", "untertitel": "Gericht ueber eine gottlose Welt",
                     "zitat": "Es wird eine grosse Truebsal sein, wie nie gewesen ist.", "quelle": "Mt 24,21"},
                    {"name": "Die Wiederkunft Christi", "untertitel": "Der Koenig kehrt sichtbar zurueck",
                     "zitat": "Siehe, er kommt mit den Wolken, und alle Augen werden ihn sehen.", "quelle": "Offb 1,7"},
                ],
            },
        ],
        "gericht": {
            "titel": "Die Wiederkunft",
            "zitat": "Und ich sah den Himmel aufgetan; und siehe, ein weisses Pferd. Und der darauf sass, richtet und streitet mit Gerechtigkeit.",
            "quelle": "Offenbarung 19,11",
            "datum": "Zeit unbekannt",
        },
        "zeitstrahl": {
            "ereignisse": ["Das Kreuz", "Pfingsten", "Die Gemeinde",
                           "Ausbreitung des Evangeliums", "Die Entrueckung", "Wiederkunft Christi"],
            "daten": ["30 n.Chr.", "Heute", "Die Zukunft"],
        },
    },

    {
        "nummer": "DAS SIEBTE ZEITALTER",
        "tagline": "DAS REICH DES MESSIAS",
        "titel": "KOENIGREICH",
        "vorher": "GNADE",
        "referenz": "Offenbarung 20-22",
        "gericht_satz": "Das siebte Zeitalter endet im Gericht: Der grosse weisse Thron",
        "fusszeile": "OFFENBARUNG 20-22",
        "baender": [
            {
                "label": "Das tausendjaehrige Reich",
                "stil": "gold",
                "knoten": [
                    {"name": "Satan gebunden", "untertitel": "Tausend Jahre ohne den Verfuehrer",
                     "zitat": "Er ergriff den Drachen und band ihn tausend Jahre.", "quelle": "Offb 20,2"},
                    {"name": "Christus regiert", "untertitel": "Der Koenig herrscht in Gerechtigkeit",
                     "zitat": "Sie wurden lebendig und regierten mit Christo tausend Jahre.", "quelle": "Offb 20,4"},
                    {"name": "Friede auf Erden", "untertitel": "Die Schoepfung kommt zur Ruhe",
                     "zitat": "Da wird der Wolf bei dem Lamm wohnen.", "quelle": "Jesaja 11,6"},
                    {"name": "Erkenntnis Gottes", "untertitel": "Gott wird allen offenbar",
                     "zitat": "Das Land wird voll Erkenntnis des HERRN sein.", "quelle": "Jesaja 11,9"},
                ],
            },
            {
                "label": "Das letzte Gericht und die Ewigkeit",
                "stil": "dunkel",
                "knoten": [
                    {"name": "Satans letztes Ende", "untertitel": "Der Verfuehrer endgueltig gerichtet",
                     "zitat": "Der Teufel ward geworfen in den feurigen Pfuhl.", "quelle": "Offb 20,10"},
                    {"name": "Der grosse weisse Thron", "untertitel": "Das Gericht ueber alle Toten",
                     "zitat": "Ich sah einen grossen, weissen Thron, und die Toten wurden gerichtet.", "quelle": "Offb 20,11-12"},
                    {"name": "Neuer Himmel, neue Erde", "untertitel": "Gott wohnt bei den Menschen",
                     "zitat": "Gott wird abwischen alle Traenen, und der Tod wird nicht mehr sein.", "quelle": "Offb 21,4"},
                ],
            },
        ],
        "gericht": {
            "titel": "Die Ewigkeit",
            "zitat": "Siehe, ich mache alles neu ... Ich bin das A und das O, der Anfang und das Ende.",
            "quelle": "Offenbarung 21,5; 22,13",
            "datum": "Die Ewigkeit",
        },
        "zeitstrahl": {
            "ereignisse": ["Wiederkunft", "Satan gebunden", "Christus regiert 1000 Jahre",
                           "Satans Ende", "Der grosse weisse Thron", "Neue Schoepfung"],
            "daten": ["Beginn", "1000 Jahre", "Die Ewigkeit"],
        },
    },
]

# ---------------------------------------------------------------------------
# HILFSFUNKTIONEN
# ---------------------------------------------------------------------------

ARTIKEL = {"der", "die", "das", "den", "dem", "des", "ein", "eine", "einen"}


def initiale(name):
    """Liefert den Anfangsbuchstaben des ersten bedeutungstragenden Wortes."""
    for wort in name.replace("(", "").replace(",", "").split():
        if wort.lower() not in ARTIKEL:
            return wort[0].upper()
    return name[0].upper()


def knoten_html(knoten):
    teile = []
    for k in knoten:
        teile.append(
            '<div class="knoten">'
            f'<div class="disc"><span class="disc-init">{initiale(k["name"])}</span></div>'
            '<div class="knoten-text">'
            f'<div class="kn-name">{k["name"]}</div>'
            f'<div class="kn-unter">{k["untertitel"]}</div>'
            f'<div class="kn-zitat">&bdquo;{k["zitat"]}&ldquo;</div>'
            f'<div class="kn-quelle">{k["quelle"]}</div>'
            '</div></div>'
        )
    return "".join(teile)

def band_html(band):
    return (
        f'<div class="band band-{band["stil"]}">'
        f'<div class="band-label">{band["label"]}</div>'
        '<div class="band-knoten">'
        '<div class="linie"></div><div class="linie-spitze"></div>'
        f'{knoten_html(band["knoten"])}'
        '</div></div>'
    )


def zeitstrahl_html(zs):
    ereignisse = "".join(f'<div class="zs-ev">{e}</div>' for e in zs["ereignisse"])
    daten = "".join(f'<div class="zs-datum">{d}</div>' for d in zs["daten"])
    return (
        '<div class="zeitstrahl">'
        f'<div class="zs-titel">Zeitleiste</div>'
        f'<div class="zs-ereignisse">{ereignisse}</div>'
        '<div class="zs-linie-wrap"><div class="zs-linie"></div>'
        '<div class="zs-spitze"></div></div>'
        f'<div class="zs-daten">{daten}</div>'
        '</div>'
    )


def navigation_html(za):
    if za["vorher"]:
        vorher = f'<span class="nav-vorher">&lsaquo; {za["vorher"]} &rsaquo;</span>'
        pfeil = '<span class="nav-pfeil">&#8594;</span>'
    else:
        vorher = '<span class="nav-vorher nav-leer">&lsaquo; Der Anfang &rsaquo;</span>'
        pfeil = '<span class="nav-pfeil">&#8594;</span>'
    return (
        '<div class="navigation">'
        '<div class="nav-links">'
        f'{vorher}{pfeil}'
        f'<span class="nav-aktuell">&lsaquo; {za["titel"]} &rsaquo;</span>'
        f'<span class="nav-ref">{za["referenz"]}</span>'
        '</div>'
        f'<div class="nav-gericht">{za["gericht_satz"]}</div>'
        '</div>'
    )


def gericht_html(g):
    return (
        '<div class="gericht">'
        '<div class="gericht-kreuz">&#10013;</div>'
        '<div class="gericht-inhalt">'
        '<div class="gericht-marke">Das Zeitalter endet im Gericht</div>'
        f'<div class="gericht-titel">{g["titel"]}</div>'
        f'<div class="gericht-zitat">&bdquo;{g["zitat"]}&ldquo;</div>'
        f'<div class="gericht-quelle">{g["quelle"]}</div>'
        '</div>'
        f'<div class="gericht-datum">{g["datum"]}</div>'
        '</div>'
    )


def seite_html(za, index, gesamt):
    baender = "".join(band_html(b) for b in za["baender"])
    return (
        '<div class="seite"><div class="rahmen">'
        # Kopf
        '<div class="kopf">'
        '<div class="kopf-ornament">&#10070; &#8212; &#10070;</div>'
        f'<div class="kopf-titel">{za["nummer"]} &ndash; {za["tagline"]}</div>'
        '<div class="kopf-ornament">&#10070; &#8212; &#10070;</div>'
        '</div>'
        # Navigation
        f'{navigation_html(za)}'
        # Baender
        f'<div class="baender">{baender}</div>'
        # Gericht
        f'{gericht_html(za["gericht"])}'
        # Zeitstrahl
        f'{zeitstrahl_html(za["zeitstrahl"])}'
        # Fuss
        '<div class="fuss">'
        '<div class="fuss-seite">Die sieben Zeitalter der Bibel</div>'
        f'<div class="fuss-ref"><span class="fuss-rule"></span>'
        f'<span class="fuss-text">{za["fusszeile"]}</span>'
        '<span class="fuss-rule"></span></div>'
        f'<div class="fuss-seite fuss-rechts">Blatt {index} von {gesamt}</div>'
        '</div>'
        '</div></div>'
    )


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CSS = """
@page { size: A3 landscape; margin: 0; }
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { background: #f3ecd9; }
body { font-family: serif; }

.seite {
  width: 420mm; height: 297mm; padding: 6mm;
  background: #faf6ec; overflow: hidden;
}
.rahmen {
  width: 100%; height: 100%;
  border: 1.6pt double #c9a227;
  padding: 6mm 9mm 5mm 9mm;
  display: flex; flex-direction: column;
  background:
    radial-gradient(ellipse at 50% 0%, #fffdf6 0%, #f7f0dd 60%, #f1e7cc 100%);
}

/* ---- Kopf ---- */
.kopf {
  display: flex; align-items: center; justify-content: center;
  gap: 6mm;
  background: linear-gradient(180deg, #9d1f1f 0%, #7a1414 100%);
  border-radius: 2mm;
  border-top: 1pt solid #d8a93a; border-bottom: 1pt solid #d8a93a;
  padding: 3.4mm 6mm;
}
.kopf-titel {
  color: #fdf3da; font-size: 8.2mm; font-weight: bold;
  letter-spacing: 1.4pt; font-variant: small-caps;
  text-align: center;
}
.kopf-ornament { color: #e6b94e; font-size: 4mm; letter-spacing: 1pt; }

/* ---- Navigation ---- */
.navigation {
  display: flex; align-items: center; justify-content: space-between;
  padding: 2.6mm 1mm 1mm 1mm;
}
.nav-links { display: flex; align-items: baseline; gap: 3mm; }
.nav-vorher { font-variant: small-caps; font-size: 3.7mm; color: #9a9388;
  letter-spacing: .6pt; }
.nav-pfeil { color: #9d1f1f; font-size: 4mm; }
.nav-aktuell { font-variant: small-caps; font-size: 4.6mm; font-weight: bold;
  color: #9d1f1f; letter-spacing: .8pt; }
.nav-ref { font-size: 3.6mm; color: #4a4034; font-style: italic;
  border-left: .8pt solid #c9a227; padding-left: 3mm; margin-left: 1mm;
  white-space: nowrap; }
.nav-gericht { font-style: italic; font-size: 3.5mm; color: #7a1414; }

/* ---- Baender ---- */
.baender { display: flex; flex-direction: column; gap: 3.4mm;
  flex: 1 1 auto; padding: 1.5mm 0; }
.band {
  flex: 1 1 0; border-radius: 3mm; padding: 4.5mm 7mm 4mm 7mm;
  display: flex; flex-direction: column;
  border: .7pt solid rgba(120,90,30,.35);
}
.band-label {
  font-family: sans-serif; font-size: 3.5mm; font-weight: bold;
  text-transform: uppercase; letter-spacing: 1.6pt;
  margin-bottom: 1mm;
}
.band-knoten {
  flex: 1 1 auto; display: flex; align-items: flex-start;
  justify-content: space-between; position: relative;
  padding-top: 6mm;
}
.linie {
  position: absolute; left: 1.5%; right: 3%; top: 16mm;
  height: 1.1mm; background: #9d1f1f; border-radius: 1mm;
}
.linie-spitze {
  position: absolute; right: 0; top: 13.6mm;
  width: 0; height: 0;
  border-top: 3mm solid transparent; border-bottom: 3mm solid transparent;
  border-left: 4.4mm solid #9d1f1f;
}
.knoten {
  flex: 1 1 0; display: flex; flex-direction: column; align-items: center;
  padding: 0 1.6mm; position: relative; z-index: 2;
}
.disc {
  width: 20mm; height: 20mm; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  border: 1.1mm solid #c9a227;
  margin-bottom: 2mm;
}
.disc-init {
  font-size: 9mm; font-weight: bold; color: rgba(255,255,255,.78);
  font-family: serif;
}
.knoten-text { text-align: center; max-width: 52mm; }
.kn-name { font-size: 3.5mm; font-weight: bold; color: #2c2419;
  line-height: 1.12; }
.kn-unter { font-size: 2.7mm; font-style: italic; line-height: 1.18;
  margin: .6mm 0 1mm 0; }
.kn-zitat { font-size: 2.55mm; font-style: italic; color: #5a5044;
  line-height: 1.22; }
.kn-quelle { font-size: 2.6mm; font-weight: bold; color: #9d1f1f;
  margin-top: .5mm; }

/* Bandstile */
.band-licht { background: linear-gradient(165deg, #eef4fb, #d9e6f5); }
.band-licht .band-label { color: #345b86; }
.band-licht .disc { background: radial-gradient(circle at 38% 32%, #e7f1fc, #7c9ec8); }
.band-licht .kn-unter { color: #345b86; }

.band-gold { background: linear-gradient(165deg, #fdf7e1, #f4e6a6); }
.band-gold .band-label { color: #92711b; }
.band-gold .disc { background: radial-gradient(circle at 38% 32%, #fbeeb6, #c29a36); }
.band-gold .kn-unter { color: #92711b; }

.band-grau { background: linear-gradient(165deg, #ecebeb, #d4d3d5); }
.band-grau .band-label { color: #595959; }
.band-grau .disc { background: radial-gradient(circle at 38% 32%, #e2e2e4, #84848b); }
.band-grau .kn-unter { color: #5d5d5d; }

.band-dunkel { background: linear-gradient(165deg, #ecddd5, #d3b6a6); }
.band-dunkel .band-label { color: #7a3b2a; }
.band-dunkel .disc { background: radial-gradient(circle at 38% 32%, #d9b7a5, #7a4734); }
.band-dunkel .kn-unter { color: #7a3b2a; }

.band-erde { background: linear-gradient(165deg, #f6ecd3, #e5cc97); }
.band-erde .band-label { color: #87611e; }
.band-erde .disc { background: radial-gradient(circle at 38% 32%, #efdca8, #b58a3f); }
.band-erde .kn-unter { color: #87611e; }

.band-geist { background: linear-gradient(165deg, #fffdf2, #f3e8c8); }
.band-geist .band-label { color: #97791d; }
.band-geist .disc { background: radial-gradient(circle at 38% 32%, #fff7d4, #ddbe55); }
.band-geist .kn-unter { color: #97791d; }

/* ---- Gericht ---- */
.gericht {
  display: flex; align-items: center; gap: 6mm;
  background: #571414;
  border: 1pt solid #c9a227; border-radius: 2.5mm;
  padding: 3.6mm 8mm; margin: 1mm 0 1mm 0;
}
.gericht-kreuz { color: #e6b94e; font-size: 9mm; }
.gericht-inhalt { flex: 1 1 auto; text-align: center; }
.gericht-marke {
  font-family: sans-serif; font-size: 2.6mm; letter-spacing: 2pt;
  text-transform: uppercase; color: #d79c9c;
}
.gericht-titel {
  font-size: 6.6mm; font-weight: bold; font-variant: small-caps;
  color: #e6b94e; letter-spacing: 1pt; margin: .3mm 0 1mm 0;
}
.gericht-zitat {
  font-style: italic; font-size: 3.3mm; color: #f3e6d2; line-height: 1.3;
}
.gericht-quelle {
  font-size: 2.8mm; font-weight: bold; color: #e0b96b; margin-top: 1mm;
}
.gericht-datum {
  font-size: 3.4mm; font-weight: bold; color: #3a0e0e;
  background: #e6b84e;
  border-radius: 8mm; padding: 2.4mm 5mm; white-space: nowrap;
  text-align: center;
}

/* ---- Zeitstrahl ---- */
.zeitstrahl {
  background: linear-gradient(165deg, #f6dcc0, #ecbf95);
  border: .7pt solid #c98f54; border-radius: 2.5mm;
  padding: 2.6mm 8mm 3mm 8mm;
}
.zs-titel {
  font-family: sans-serif; font-size: 2.7mm; letter-spacing: 2.4pt;
  text-transform: uppercase; color: #8a4f22; text-align: center;
  margin-bottom: 1.4mm;
}
.zs-ereignisse { display: flex; justify-content: space-between; }
.zs-ev {
  flex: 1 1 0; text-align: center; font-size: 3mm; font-weight: bold;
  color: #5e3414; padding: 0 1.5mm; line-height: 1.15;
}
.zs-linie-wrap { position: relative; height: 3mm; margin: 1.6mm 0; }
.zs-linie {
  position: absolute; left: 0; right: 2.4%; top: 1mm;
  height: 1.1mm; background: #9d1f1f; border-radius: 1mm;
}
.zs-spitze {
  position: absolute; right: 0; top: -1.2mm;
  width: 0; height: 0;
  border-top: 2.6mm solid transparent; border-bottom: 2.6mm solid transparent;
  border-left: 4mm solid #9d1f1f;
}
.zs-daten { display: flex; justify-content: space-between; }
.zs-datum {
  flex: 1 1 0; text-align: center; font-size: 3mm; font-style: italic;
  color: #7a1414; font-weight: bold;
}

/* ---- Fuss ---- */
.fuss {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 2.2mm;
}
.fuss-seite {
  font-size: 2.8mm; font-style: italic; color: #9a9082;
  width: 60mm;
}
.fuss-rechts { text-align: right; }
.fuss-ref { display: flex; align-items: center; gap: 4mm; flex: 1 1 auto;
  justify-content: center; }
.fuss-rule { display: block; width: 34mm; height: 0;
  border-top: .8pt solid #c9a227; }
.fuss-text {
  font-size: 4mm; font-weight: bold; font-variant: small-caps;
  letter-spacing: 1.4pt; color: #9d1f1f;
}
"""


# ---------------------------------------------------------------------------
# AUFBAU & RENDERING
# ---------------------------------------------------------------------------

def baue_html():
    gesamt = len(ZEITALTER)
    seiten = "".join(
        seite_html(za, i + 1, gesamt) for i, za in enumerate(ZEITALTER)
    )
    return (
        '<!DOCTYPE html><html lang="de"><head><meta charset="utf-8">'
        '<title>Bibelchronik - Die sieben Zeitalter</title>'
        f'<style>{CSS}</style></head><body>{seiten}</body></html>'
    )


def main():
    html = baue_html()
    with open("bibelchronik.html", "w", encoding="utf-8") as fh:
        fh.write(html)
    HTML(string=html).write_pdf("bibelchronik.pdf")
    print("Erstellt: bibelchronik.pdf  (7 Blatt, A3 quer)")
    print("Erstellt: bibelchronik.html")


if __name__ == "__main__":
    main()
