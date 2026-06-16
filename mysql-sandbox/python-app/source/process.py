#!/usr/bin/env python3
import csv
import pymysql
import os

EXPECTED_COLUMNS = [
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
]


def lambda_handler(event=None, _context=None) -> dict:

    RDS_HOST = "mysql"
    RDS_USER = "uoc"
    RDS_PASSWORD = "examplepass"
    RDS_DB = "botigues"

    # Connectar a MySQL
    print("S'està connectant a MySQL...")
    connection = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
    )

    if not connection.open:
        print("No s'ha pogut establir la connexió a MySQL")
        return {"status": "error"}

    print("S'ha establert la connexió a MySQL")

    # Carpetes locals
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    validat_path = os.path.join(base_path, "validat")
    processat_path = os.path.join(base_path, "processat")

    # Crear la carpeta processat si no existeix
    os.makedirs(processat_path, exist_ok=True)

    # Llistar els fitxers CSV
    csv_files = [f for f in os.listdir(validat_path) if f.endswith(".csv")]

    if not csv_files:
        print("No hi ha fitxers per processar")
        return {"status": "ok"}

    for filename in csv_files:
        file_path = os.path.join(validat_path, filename)
        print(f"S'està processant el fitxer local: {file_path}")

        try:
            # Llegir el fitxer CSV
            with open(file_path, "r", encoding="utf-8") as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Saltar la capçalera
                print("Inserint vendes a la base de dades...")
                with connection.cursor() as cursor:
                    for row in csv_reader:
                        values = dict(zip(EXPECTED_COLUMNS, row))
                        sql = """
                            INSERT INTO vendes (id_botiga, id_producte, quantitat, data, hora)
                            VALUES (%s, %s, %s, %s, %s)
                        """
                        cursor.execute(
                            sql,
                            (
                                values["id_botiga"],
                                values["id_producte"],
                                values["unitats"],
                                values["data"],
                                values["hora"],
                            ),
                        )
                connection.commit()

            print("Inserció completada correctament")

            # Moure el fitxer a processat
            os.rename(file_path, os.path.join(processat_path, filename))
            print(
                f"S'ha processat correctament el fitxer {filename} i "
                f"s'ha mogut a {processat_path}"
            )

        except Exception as e:
            print(f"Error en processar {filename}: {e}")

    connection.close()
    return {"status": "ok"}


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    print("Prova de processament local de fitxers CSV de vendes...")
    result = lambda_handler()
    print("Resultat:", result)
