import json
import boto3
import csv
import io
from datetime import datetime

# Crear un client de S3
s3 = boto3.client("s3")

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


def lambda_handler(event, context):
    """Funció Lambda que es desencadena quan es puja un fitxer CSV a la carpeta 'entrada/' del bucket S3.

    Args:
        event (dict): L'event que desencadena la funció Lambda, que conté informació sobre el fitxer CSV pujat a S3.
        context (object): L'objecte context que proporciona informació sobre l'execució de la funció Lambda.
    Returns:
        dict: Un objecte JSON amb l'estat de la validació i la ubicació del fitxer validat o amb error.

    La funció valida el format i les dades del fitxer CSV, i mou el fitxer a la
    carpeta 'validat/' si és vàlid o a la carpeta 'error/' si no ho és. Es
    retorna un objecte JSON amb l'estat de la validació i la ubicació del fitxer
    validat o amb error.
    """
    # Processar només el primer registre de l'event, ja que s'espera que cada
    # event contingui un sol fitxer CSV
    record = event["Records"][0]

    # Obtenir el bucket i la clau del fitxer CSV que ha desencadenat
    # l'esdeveniment
    bucket = record["s3"]["bucket"]["name"]
    key = record["s3"]["object"]["key"]

    # Es mostra un missatge de registre amb la ubicació del fitxer rebut per
    # facilitar el seguiment i la depuració.
    print(f"Fitxer rebut: s3://{bucket}/{key}")

    # Inicialitzar les variables per a la carpeta destí del fitxer un cop
    # validat i l'estat de la validació
    validated_key = ""
    is_valid = False

    # Llegir el fitxer CSV des de S3 i decodificar-lo com a text. Si hi ha un
    # error en la lectura del fitxer, es registra l'error i es retorna un estat
    # d'error.
    try:
        obj = s3.get_object(Bucket=bucket, Key=key)
        data = obj["Body"].read().decode("utf-8")
    except Exception as e:
        print(f"Error llegint el fitxer: {e}")
        return {"status": "error"}

    # Utilitza el mòdul csv per llegir el contingut del fitxer CSV i validar que
    # les columnes del fitxer coincideixen amb les columnes esperades. Si el
    # fitxer està buit o les columnes no coincideixen, es registra l'error i es
    # marca el fitxer com a no vàlid.
    csv_reader = csv.reader(io.StringIO(data))
    try:
        header = next(csv_reader)
    except StopIteration:
        print("Error: CSV buit")
        return {"status": "invalid"}

    if header != EXPECTED_COLUMNS:
        print("Error: format incorrecte")
        print(f"Esperat: {EXPECTED_COLUMNS}")
        print(f"Trobat:  {header}")
        is_valid = False
    else:
        is_valid = True

    # Si les columnes són correctes, es procedeix a validar cada fila del CSV.
    # Es comprova que cada fila té el nombre correcte de columnes, que els camps
    # no són buits i que els camps "preu" i "unitats" contenen valors numèrics
    # vàlids. També es valida que els camps "data" i "hora" contenen valors en
    # formats correctes. Si es detecta qualsevol error en les dades, es registra
    # l'error i es marca el fitxer com a no vàlid, i es deté la validació de les
    # files restants per evitar errors addicionals.
    if is_valid:
        for row_number, row in enumerate(csv_reader, start=2):
            if len(row) != len(EXPECTED_COLUMNS):
                print(f"Error: fila {row_number} té un nombre incorrecte de columnes")
                is_valid = False
                break

            values = dict(zip(EXPECTED_COLUMNS, row))

            # Validar que cada camp no és buit
            for column in EXPECTED_COLUMNS:
                if not values[column].strip():
                    print(f"Error: fila {row_number} té {column} buit")
                    is_valid = False
                    break
            if not is_valid:
                break

            # validar que preu és un número decimal més gran que 0
            try:
                preu = float(values["preu"])
                if preu <= 0:
                    print(
                        f"Error: fila {row_number} té preu no vàlid ({values['preu']!r})"
                    )
                    is_valid = False
                    break
            except ValueError:
                print(f"Error: fila {row_number} té preu no vàlid ({values['preu']!r})")
                is_valid = False
                break

            # validar que unitats és un número enter més gran que 0
            try:
                unitats = int(values["unitats"])
                if unitats <= 0:
                    print(
                        f"Error: fila {row_number} té unitats no vàlid ({values['unitats']!r})"
                    )
                    is_valid = False
                    break
            except ValueError:
                print(
                    f"Error: fila {row_number} té unitats no vàlid ({values['unitats']!r})"
                )
                is_valid = False
                break

            # validar el camp data es una data vàlida en format YYYY-MM-DD
            try:
                datetime.strptime(values["data"], "%Y-%m-%d")
            except ValueError:
                print(
                    f"Error: fila {row_number} té data no vàlida ({values['data']!r})"
                )
                is_valid = False
                break

            # validar el camp hora es una hora vàlida en format HH:MM:SS
            try:
                datetime.strptime(values["hora"], "%H:%M:%S")
            except ValueError:
                print(
                    f"Error: fila {row_number} té hora no vàlida ({values['hora']!r})"
                )
                is_valid = False
                break

    # Un cop finalitzada la validació, es determina la carpeta destí del fitxer
    # segons si el fitxer és vàlid o no, i s'imprimeix un missatge indicant si
    # el fitxer és vàlid o no. Si el fitxer és vàlid,
    if is_valid:
        validated_key = key.replace("entrada/", "validat/")
        print("CSV vàlid")
    else:
        validated_key = key.replace("entrada/", "error/")
        print("CSV NO vàlid")

    # Es mou el fitxer a la carpeta destí corresponent a l'estat de la
    # validació. Si hi ha un error en el procés en què es mou el fitxer, es
    # registra l'error i es retorna un estat d'error.
    try:
        # Copiar
        s3.copy_object(
            Bucket=bucket, CopySource={"Bucket": bucket, "Key": key}, Key=validated_key
        )
        # Esborrar original
        s3.delete_object(Bucket=bucket, Key=key)
    except Exception as e:
        print(f"Error movent el fitxer: {e}")
        return {"status": "error"}

    # S'imprimeix un missatge amb la ubicació del fitxer mogut per facilitar el
    # seguiment i la depuració.
    print(f"Fitxer mogut a: s3://{bucket}/{validated_key}")

    # Es retorna un objecte JSON amb l'estat de la validació i la ubicació del
    # fitxer validat o amb error.
    return {"status": "ok", "validated_file": validated_key}
