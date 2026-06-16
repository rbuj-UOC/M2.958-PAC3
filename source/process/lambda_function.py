import boto3
import csv
import io
import json
import pymysql
import os
import socket

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


def _extract_s3_record(record) -> dict:
    """Aquesta funció s'encarrega d'extraure el registre de S3 d'un registre de SQS.

    Args:
        record (dict): Un registre de SQS que pot contenir informació de S3.

    Returns:
        dict: El registre de S3 extret del registre de SQS.

    Raises:
        KeyError: Si el registre de SQS no conté la informació necessària per extraure el registre de S3.

    Comprova si el registre conté informació de S3 i, si és així, retorna aquest
    registre. Si no, intenta extreure el cos del missatge i parsejar-lo com a
    JSON per obtenir el registre de S3. Si no es pot trobar la informació
    necessària, es llança una excepció.
    """
    # Comprovar si el registre conté informació de S3, en cas que no sigui així,
    # retorna el registre original per intentar extreure la informació de S3
    # del cos del missatge.
    if "s3" in record:
        return record

    # Si el registre no conté informació de S3, intenta extreure el cos del
    # missatge i parsejar-lo com a JSON per obtenir el registre de S3.
    # Si no es pot trobar la informació necessària, es llança una excepció.
    body = record.get("body")
    if not body:
        raise KeyError("body")

    # Parseja el cos del missatge com a JSON per obtenir el registre de S3.
    payload = json.loads(body) if isinstance(body, str) else body

    # Retorna el primer registre.
    return payload["Records"][0]


def lambda_handler(event, _context) -> dict:
    """Aquesta funció Lambda s'encarrega de processar els fitxers CSV que han estat validats i moguts a la carpeta "validat" del bucket de S3.

    Args:
        event (dict): Un event de SQS que conté informació sobre els fitxers CSV a processar.
        _context: Context de l'execució de la funció Lambda (no s'utilitza en aquesta funció).

    Returns:
        dict: Un objecte JSON amb l'estat de l'operació.

    La funció llegeix cada fitxer CSV, processa les dades i insereix els
    registres en una base de dades RDS. Un cop processat el fitxer, es mou a la
    carpeta "processat". Si hi ha algun error durant el procés, es registra
    l'error i es continua amb el següent fitxer.
    """
    # Crear un client de S3
    s3 = boto3.client("s3")

    # Llegir les variables d'entorn per a la connexió a RDS
    try:
        RDS_HOST = os.environ["RDS_HOST"]
        RDS_USER = os.environ["RDS_USER"]
        RDS_PASSWORD = os.environ["RDS_PASSWORD"]
        RDS_DB = os.environ["RDS_DB"]
        print("S'han llegit correctament les variables d'entorn per a RDS")
    except KeyError as e:
        print(f"Error: Variable d'entorn no definida: {e}")
        return {"status": "ok"}

    # Comprovar que Lambda resol correctament el DNS del RDS
    try:
        socket.gethostbyname(RDS_HOST)
        print(f"El DNS ha estat resolt correctament per RDS_HOST: {RDS_HOST}")
    except Exception as e:
        print(f"Error resolent DNS per RDS_HOST: {e}")
        return {"status": "ok"}

    # Connectar a la base de dades RDS
    print("Connectant a la base de dades RDS...")
    connection = pymysql.connect(
        host=RDS_HOST,
        user=RDS_USER,
        password=RDS_PASSWORD,
        database=RDS_DB,
    )

    # Comprovar que la connexió a RDS s'ha establert correctament
    if connection.open:
        print("S'ha establert correctament la connexió a RDS")
    else:
        print("Error en establir la connexió a RDS")
        return {"status": "ok"}

    # Processar cada registre de l'esdeveniment de SQS
    for record in event["Records"]:
        # Obtenir el missatge del registre SQS
        body = record["body"]
        print("Missatge rebut:", body)

        try:
            # Extraure la informació del registre S3
            s3_record = _extract_s3_record(record)

            # Obtenir informació del fitxer pujat
            bucket = s3_record["s3"]["bucket"]["name"]
            key = s3_record["s3"]["object"]["key"]
            print(f"Fitxer rebut: s3://{bucket}/{key}")

            response = s3.get_object(Bucket=bucket, Key=key)
            csv_content = response["Body"].read().decode("utf-8")
            csv_reader = csv.reader(io.StringIO(csv_content))
            next(csv_reader)  # Saltar la capçalera

            # Processar cada fila del CSV i inserir a RDS
            print("S'estan inserint dades a RDS...")
            with connection.cursor() as cursor:
                # Crear la consulta SQL per inserir les dades a la taula
                # "vendes". Aquesta consulta utilitza placeholders (%s) per
                # evitar vulnerabilitats d'injecció SQL i permet inserir les
                # dades de forma segura.
                for row in csv_reader:
                    values = dict(zip(EXPECTED_COLUMNS, row))
                    sql = "INSERT INTO vendes (id_botiga, id_producte, quantitat, data, hora) VALUES (%s, %s, %s, %s, %s)"
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
            # Imprimir un missatge indicant que les dades han estat inserides
            # correctament a RDS.
            print("Les dades han estat inserides correctament a RDS")

            # Si s'ha processat correctament, moure el fitxer de la carpeta
            # "validat" a la carpeta "processat"
            processed_key = key.replace("validat/", "processat/")
            print("El fitxer CSV ha estat processat correctament")
            s3.copy_object(
                Bucket=bucket,
                CopySource={"Bucket": bucket, "Key": key},
                Key=processed_key,
            )
            s3.delete_object(Bucket=bucket, Key=key)
            print("El fitxer CSV ha estat mogut correctament")

        except Exception as e:
            print(f"Error processant el fitxer CSV: {e}")

    # Tancar la connexió a RDS un cop s'han processat tots els fitxers. És
    # important tancar la connexió per alliberar recursos i evitar possibles
    # problemes de connexió en futures execucions de la funció Lambda.
    connection.close()

    # Es retorna un objecte JSON amb l'estat de l'operació. En aquest cas, es
    # retorna "ok" encara que hi hagi hagut errors en el processament del
    # fitxer.
    return {"status": "ok"}
