#!/usr/bin/env python3

import csv
import os
import random
import string
import sys
from datetime import date, datetime, timedelta

# -------------------------------
# CONFIGURACIÓ
# -------------------------------

N_PRODUCTES_DEPARTAMENT = 100
N_BOTIGUES = 30
FILE_PRODUCTES = "data/productes.csv"

multiplicador_ciutat = {"Barcelona": 3, "Lleida": 3, "Tarragona": 3}

ciutats = {
    "Barcelona": "BCN",
    "Lleida": "LLE",
    "Tarragona": "TGN",
    "Girona": "GIR",
    "Sabadell": "SBD",
    "Terrassa": "TRR",
    "Reus": "REU",
    "Mataró": "MAT",
    "Manresa": "MAN",
    "Vic": "VIC",
    "Figueres": "FIG",
    "Amposta": "AMP",
    "Rubí": "RUB",
    "Cerdanyola": "CER",
    "Granollers": "GRA",
    "Santa Coloma": "STA",
    "Vilanova i la Geltrú": "VNG",
    "Castelldefels": "CAT",
    "Mollet del Vallès": "MOL",
    "Igualada": "IGU",
}

departaments = ["home", "dona", "nen", "nena"]
talles = ["S", "M", "L", "X", "XL", "XXL"]
colors = ["blau", "vermell", "negre", "blanc", "verd", "groc"]

peces = [
    "samarreta",
    "pantalons",
    "jaqueta",
    "abric",
    "dessuadora",
    "camisa",
    "bermudes",
    "faldilla",
    "vestit",
    "top",
    "jersei",
    "parka",
    "anorac",
    "texans",
    "pantalons curts",
]

teixits = [
    "cotó suau",
    "lli transpirable",
    "polièster lleuger",
    "punt elàstic",
    "denim resistent",
    "teixit tèrmic",
    "teixit impermeable",
    "llana càlida",
]

beneficis = [
    "pensat per oferir el màxim confort",
    "ideal per al dia a dia",
    "perfecte per completar qualsevol look",
    "dissenyat per garantir llibertat de moviment",
    "amb un estil modern i atemporal",
    "pensat per resistir l’ús continuat",
    "amb un acabat d’alta qualitat",
]

adjectius = [
    "elegant",
    "modern",
    "sofisticat",
    "casual",
    "atemporal",
    "versàtil",
    "còmode",
    "refinat",
    "actual",
    "urbà",
]

# -------------------------------
# PREUS SEGONS TIPUS DE PEÇA
# -------------------------------

PREU_ALT = ["abric", "parka", "anorac"]
PREU_MIG = ["jaqueta", "dessuadora", "jersei", "texans"]


def preu_per_peça(peça: str) -> float:
    """Retorna un preu realista per a una peça de roba segons el seu tipus.

    Args:
        peça: El tipus de peça de roba (ex: "samarreta", "jaqueta", etc.)

    Returns:
        float: El preu realista per a la peça, amb decimals acabats en .95, .25, .75 o .50 per simular preus reals.

    Les peces d'abric, parka i anorac són les més cares, seguides de les
    jaquetes, dessuadores, jerseis i texans. La resta de peces tenen preus més
    assequibles.
    """
    # Es determina el preu base de la peça segons el seu tipus, amb rangs de
    # preus diferents per a les peces més cares, les de preu mig i les més
    # assequibles.
    if peça in PREU_ALT:
        preu = round(random.uniform(60, 120), 0)
    elif peça in PREU_MIG:
        preu = round(random.uniform(25, 60), 0)
    else:
        preu = round(random.uniform(10, 25), 0)

    # S'afegeixen els decimals al preu per simular valors reals, amb decimals
    # acabats en .95, .25, .75 o .50, segons la unitat del preu base.
    unitat = preu % 10
    if unitat == 9 or unitat == 4:
        preu += 0.95
    elif unitat == 0:
        preu += random.choice([0, 0.5])
    else:
        preu += random.choice([0.25, 0.75])

    return preu


# -------------------------------
# GENERACIÓ DE PRODUCTES
# -------------------------------


def generar_id_producte() -> str:
    """
    Genera un ID de producte únic format per 12 caràcters alfanumèrics.

    Returns:
        str: Un ID de producte com ara "A1B2C3D4E5F6".
    """
    # Es genera un ID de producte combinant lletres majúscules i dígits, amb
    # una longitud de 12 caràcters, per assegurar que cada producte té un
    # identificador únic i fàcil de reconèixer. Aquest ID es pot utilitzar per
    # relacionar les vendes amb els productes.
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=12))


def generar_descripcio() -> tuple:
    """Genera una descripció realista per a una peça de roba combinant elements com el tipus de peça, el teixit, els beneficis i un adjectiu.

    Returns:
        tuple: Una tupla que conté el nom de la peça i la descripció completa.
    """
    # Se selecciona aleatòriament un tipus de peça, un teixit, un benefici i un
    # adjectiu de les llistes predefinides, i es combina tot en una descripció
    # simulada que destaca les característiques i avantatges de la peça de roba.
    peça = random.choice(peces)
    teixit = random.choice(teixits)
    benefici = random.choice(beneficis)
    adj = random.choice(adjectius)
    text = f"{peça.capitalize()} de {teixit}, {benefici} i un toc {adj}."
    return peça, text


def generar_base_productes() -> list:
    """Genera una base de dades de productes amb descripcions i preus realistes per a cada peça de roba.

    Returns:
        list: Una llista de diccionaris, on cada diccionari representa un producte amb les següents claus: "id_producte", "departament", "descripcio", "preu".
    """
    # Es genera una llista de productes, on per cada departament es creen
    # N_PRODUCTES_DEPARTAMENT productes diferents. Cada producte té un ID únic,
    # un departament associat, una descripció generada de forma realista i un
    # preu calculat segons el tipus de peça.
    productes = []
    for dept in departaments:
        for _ in range(N_PRODUCTES_DEPARTAMENT):
            # Es genera una descripció realista per a la peça de roba, que
            # inclou el tipus de peça, el teixit, els beneficis i un adjectiu.
            peça, descripcio = generar_descripcio()
            preu = preu_per_peça(peça)
            # Es crea un diccionari per al producte amb un ID únic, el
            # departament, la descripció i el preu, i s'afegeix a la llista de
            # productes.
            productes.append(
                {
                    "id_producte": generar_id_producte(),
                    "departament": dept,
                    "descripcio": descripcio,
                    "preu": preu,
                }
            )
    return productes


def desar_productes(productes: list) -> None:
    """Desa la base de dades de productes en un fitxer CSV.
    Args:
        productes: Una llista de diccionaris, on cada diccionari representa un producte amb les següents claus: "id_producte", "departament", "descripcio", "preu".
    """
    # Comprovar que el directori "data" existeix abans de desar el fitxer de
    # productes. Si no existeix, es crea.
    if not os.path.exists("data"):
        os.makedirs("data")

    # Desa la base de dades de productes en un fitxer CSV amb les columnes:
    # "id_producte", "departament", "descripcio" i "preu". Cada fila del CSV
    # correspon a un producte diferent, amb les dades generades de forma
    # simulada.
    with open(FILE_PRODUCTES, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f, fieldnames=["id_producte", "departament", "descripcio", "preu"]
        )
        writer.writeheader()
        writer.writerows(productes)


# -------------------------------
# GENERACIÓ DE VENDES
# -------------------------------


def carregar_productes() -> list:
    """Carrega la base de dades de productes des d'un fitxer CSV.

    Returns:
        list: Una llista de diccionaris, on cada diccionari representa un producte amb les següents claus: "id_producte", "departament", "descripcio", "preu".
    """
    # Comprovar que el fitxer de productes existeix abans de carregar-lo. Si no
    # existeix, mostrar un missatge d'error i suggerir executar l'script amb
    # l'argument "-p" per generar-lo.
    if not os.path.exists(FILE_PRODUCTES):
        print(
            "ERROR: El fitxer " + FILE_PRODUCTES + " no existeix.\n"
            f"Executeu '{sys.argv[0]} -p' per generar-lo."
        )
        sys.exit(1)

    # Carregar els productes del fitxer CSV i els retorna com una llista de
    # diccionaris, on cada diccionari representa un producte amb les claus:
    # "id_producte", "departament", "descripcio" i "preu".
    productes = []
    with open(FILE_PRODUCTES, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            productes.append(row)
    return productes


# -------------------------------
# GENERACIÓ D'HORA REALISTA
# -------------------------------


def generar_hora() -> str:
    """Genera una hora realista per a una venda, amb més probabilitat durant les hores punta (11:30-12:30 i 17:30-18:30) i menys probabilitat en altres hores del dia.

    Returns:
        str: Una hora en format "HH:MM:SS".
    """
    r = random.random()

    if r < 0.25:
        inici = datetime.strptime("11:30:00", "%H:%M:%S")
        final = datetime.strptime("12:30:00", "%H:%M:%S")

    elif r < 0.50:
        inici = datetime.strptime("17:30:00", "%H:%M:%S")
        final = datetime.strptime("18:30:00", "%H:%M:%S")

    else:
        inici = datetime.strptime("09:00:00", "%H:%M:%S")
        final = datetime.strptime("21:00:00", "%H:%M:%S")

    # Es calcula un nombre aleatori de segons entre l'hora d'inici i l'hora
    # final, i s'afegeix aquest nombre de segons a l'hora d'inici per obtenir
    # una hora aleatòria dins de l'interval seleccionat.
    delta = final - inici
    segons = random.randint(0, int(delta.total_seconds()))
    hora = inici + timedelta(seconds=segons)
    return hora.strftime("%H:%M:%S")


def random_unitats() -> int:
    """Genera un nombre d'unitats venudes per a una venda, amb més probabilitat de vendre 1 unitat i menys probabilitat de vendre més unitats.

    Returns:
        int: Un nombre d'unitats venudes, entre 1 i 7, on 1 és el més probable i 7 el menys probable.
    """
    # Es defineixen els valors possibles (1 a 7 unitats) i els pesos associats a
    # cada valor, de manera que vendre 1 unitat és molt més probable que vendre
    # 7 unitats. Els pesos s'han ajustat per simular una distribució realista de
    # vendes, on la majoria de les vendes són d'1 unitat, seguides de 2 unitats,
    # i així successivament fins a 7 unitats, que són molt rares (el nombre de
    # peces es pot relacionar amb el nombre de fills d'una família, però no té
    # perquè ser així, s'ha agafat com a referència).
    valors = [1, 2, 3, 4, 5, 6, 7]
    pesos = [81, 15, 2, 1, 0.5, 0.3, 0.2]
    return random.choices(valors, weights=pesos, k=1)[0]


def generar_fila_venda(productes: list, botiga: str, data: str) -> dict:
    """Genera una fila de venda amb dades realistes, seleccionant un producte aleatori de la base de dades i combinant-lo amb altres atributs com l'hora, les unitats venudes, el color i la talla.

    Args:
        productes: Una llista de diccionaris, on cada diccionari representa un producte amb les següents claus: "id_producte", "departament", "descripcio", "preu".
        botiga: El codi de la botiga.
        data: La data de la venda.

    Returns:
        dict: Un diccionari que representa una fila de venda amb les dades generades.
    """
    # Seleccionar un producte aleatori de la base de dades de productes
    p = random.choice(productes)
    return {
        "id_botiga": botiga,
        "data": data,
        "hora": generar_hora(),
        "id_producte": p["id_producte"],
        "departament": p["departament"],
        "talla": random.choice(talles),
        "preu": p["preu"],
        "unitats": random_unitats(),
        "color": random.choice(colors),
        "descripcio": p["descripcio"],
    }


# -------------------------------
# CSV ORDENAT PER HORA
# -------------------------------


def generar_csv(
    botiga: str, ciutat_real: str, data: str, productes: list, num_files: int = 2000
) -> None:
    """Genera un fitxer CSV de vendes per a una botiga concreta, amb les vendes ordenades per hora i amb un nombre de files ajustat segons la ciutat.

    Args:
        botiga: El codi de la botiga.
        ciutat_real: El nom real de la ciutat on es troba la botiga.
        data: La data de les vendes.
        productes: Una llista de diccionaris, on cada diccionari representa un producte amb les següents claus: "id_producte", "departament", "descripcio", "preu".
        num_files: El nombre base de files a generar per a una botiga, que es multiplicarà segons la ciutat.
    """
    factor = multiplicador_ciutat.get(ciutat_real, 1)
    num_files = num_files * factor

    nom_fitxer = f"data/{botiga}_{data}.csv"

    # Generar totes les vendes
    vendes = [generar_fila_venda(productes, botiga, data) for _ in range(num_files)]

    # Ordenar les vendes per hora
    vendes.sort(key=lambda x: x["hora"])

    # Escriure les vendes al CSV
    with open(nom_fitxer, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id_botiga",
                "data",
                "hora",
                "id_producte",
                "departament",
                "talla",
                "preu",
                "unitats",
                "color",
                "descripcio",
            ],
        )
        writer.writeheader()
        writer.writerows(vendes)

    print(f"Generat fitxer per a {ciutat_real} [{botiga}] → {num_files} vendes")


# -------------------------------
# GENERACIÓ DE BOTIGUES
# -------------------------------


def generar_botigues(num_botigues: int = N_BOTIGUES) -> list:
    """Genera una llista de botigues amb codis únics i associats a ciutats reals.

    Args:
        num_botigues: El nombre total de botigues a generar.

    Returns:
        list: Una llista de tuples, on cada tuple conté el codi de la botiga i el nom real de la ciutat associada.
    """
    botigues = []
    comptadors = {c: 1 for c in ciutats}

    for _ in range(num_botigues):
        # Seleccionar una ciutat real aleatòriament i obtenir el seu codi
        ciutat_real = random.choice(list(ciutats.keys()))
        codi = ciutats[ciutat_real]

        # Generar un número seqüencial per a la botiga dins de la ciutat, amb
        # format de dos dígits (ex: "01", "02", etc.)
        num = str(comptadors[ciutat_real]).zfill(2)
        comptadors[ciutat_real] += 1

        # El codi de la botiga es forma per l'abreviatura de la ciutat seguida
        # d'un número seqüencial (ex: "BCN01", "LLE02", etc.)
        botigues.append((f"{codi}{num}", ciutat_real))

    return botigues


# -------------------------------
# EXECUCIÓ PRINCIPAL
# -------------------------------

if __name__ == "__main__":

    # Si s'executa el script amb l'argument "-p", es genera la base de dades de
    # productes i es desa en un fitxer CSV. Si no, es carrega la base de dades
    # de productes des del fitxer.
    if "-p" in sys.argv:
        print("Generant base de dades de productes…")
        productes = generar_base_productes()
        desar_productes(productes)
        print("S'ha generat el fitxer " + FILE_PRODUCTES + ".")

    # Si s'executa l'script sense arguments, es carrega la base de dades de
    # productes i es generen els fitxers de vendes per a cada botiga.
    print("Carregant productes…")
    productes = carregar_productes()

    # Generar els fitxers de vendes per a cada botiga, amb les vendes ordenades
    # per hora i ajustant el nombre de files segons la ciutat.
    print("Generant fitxers de vendes…")
    botigues = generar_botigues()
    data_avui = date.today().strftime("%Y-%m-%d")
    for botiga, ciutat_real in botigues:
        generar_csv(botiga, ciutat_real, data_avui, productes)
