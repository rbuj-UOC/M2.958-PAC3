#!/usr/bin/env python3
import csv
import io
import os
from datetime import datetime

# Definir les columnes esperades al CSV
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


def process_csv_local(
    filepath: str, entrada_dir: str, validat_dir: str, error_dir: str
):
    filename = os.path.basename(filepath)
    print(f"Fitxer rebut: {filepath}")

    is_valid = False

    # Llegir el fitxer CSV local
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = f.read()
    except Exception as e:
        print(f"Error llegint el fitxer: {e}")
        return {"status": "error"}

    csv_reader = csv.reader(io.StringIO(data))

    # Llegir capçalera
    try:
        header = next(csv_reader)
    except StopIteration:
        print("Error: CSV buit")
        # Mou el fitxer a error/
        dest = os.path.join(error_dir, filename)
        try:
            os.rename(filepath, dest)
            print(f"El fitxer s'ha mogut a: {dest}")
        except Exception as e:
            print(f"Error en moure el fitxer: {e}")
            return {"status": "error"}
        return {"status": "invalid"}

    # Validar capçalera
    if header != EXPECTED_COLUMNS:
        print("Error: format incorrecte")
        print(f"Esperat: {EXPECTED_COLUMNS}")
        print(f"Trobat:  {header}")
        is_valid = False
    else:
        is_valid = True

    # Validar files
    if is_valid:
        for row_number, row in enumerate(csv_reader, start=2):
            if len(row) != len(EXPECTED_COLUMNS):
                print(f"Error: fila {row_number} té un nombre incorrecte de columnes")
                is_valid = False
                break

            values = dict(zip(EXPECTED_COLUMNS, row))

            # Validar camps buits
            for column in EXPECTED_COLUMNS:
                if not values[column].strip():
                    print(f"Error: fila {row_number} té {column} buit")
                    is_valid = False
                    break
            if not is_valid:
                break

            # Validar preu
            try:
                preu = float(values["preu"])
                if preu <= 0:
                    print(
                        f"Error: fila {row_number} té preu no vàlid ({values['preu']})"
                    )
                    is_valid = False
                    break
            except ValueError:
                print(f"Error: fila {row_number} té preu no vàlid ({values['preu']})")
                is_valid = False
                break

            # Validar unitats
            try:
                unitats = int(values["unitats"])
                if unitats <= 0:
                    print(
                        f"Error: fila {row_number} té unitats no vàlid ({values['unitats']})"
                    )
                    is_valid = False
                    break
            except ValueError:
                print(
                    f"Error: fila {row_number} té unitats no vàlid ({values['unitats']})"
                )
                is_valid = False
                break

            # Validar data
            try:
                datetime.strptime(values["data"], "%Y-%m-%d")
            except ValueError:
                print(f"Error: fila {row_number} té data no vàlida ({values['data']})")
                is_valid = False
                break

            # Validar hora
            try:
                datetime.strptime(values["hora"], "%H:%M:%S")
            except ValueError:
                print(f"Error: fila {row_number} té hora no vàlida ({values['hora']})")
                is_valid = False
                break

    # Determinar la carpeta de destinació
    if is_valid:
        dest = os.path.join(validat_dir, filename)
        print("CSV vàlid")
    else:
        dest = os.path.join(error_dir, filename)
        print("CSV NO vàlid")

    # Moure fitxer
    try:
        os.rename(filepath, dest)
        print(f"El fitxer s'ha mogut a: {dest}")
    except Exception as e:
        print(f"Error en moure el fitxer: {e}")
        return {"status": "error"}

    return {"status": "ok", "validated_file": dest}


def main():
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data"))
    entrada_dir = os.path.join(base, "entrada")
    validat_dir = os.path.join(base, "validat")
    error_dir = os.path.join(base, "error")

    os.makedirs(validat_dir, exist_ok=True)
    os.makedirs(error_dir, exist_ok=True)

    csv_files = [
        os.path.join(entrada_dir, f)
        for f in os.listdir(entrada_dir)
        if f.endswith(".csv")
    ]

    if not csv_files:
        print("No hi ha fitxers per processar")
        return

    for filepath in csv_files:
        process_csv_local(filepath, entrada_dir, validat_dir, error_dir)


if __name__ == "__main__":
    main()
