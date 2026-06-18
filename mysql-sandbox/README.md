# Entorn de proves de Mysql

## Connexió al contenidor d'aplicació

El fitxer `docker-compose.yml` defineix dos contenidors, un amb MySQL i un altre
amb les eines de client de MySQL i Python. El contenidor de MySQL exposa el port
3306, que és el port per defecte de MySQL. El contenidor d'aplicació es connecta
al contenidor de MySQL mitjançant el nom del servei `mysql` definit al fitxer
`docker-compose.yml`. Això permet que el contenidor d'aplicació accedeixi a la
base de dades MySQL sense necessitat de conèixer l'adreça IP del contenidor de
MySQL. Per iniciar els contenidors alhora, podem executar la comanda:

```bash
docker-compose up
```

El nom del contenidor amb les eines de client és `mysql-sandbox-python-app-1` i
el nom del contenidor de MySQL és `mysql-sandbox-mysql-1`. Per veure els
contenidors en execució, podem executar la comanda:

```bash
docker ps -a
```

```text
CONTAINER ID   IMAGE                                                                     COMMAND                  CREATED         STATUS                     PORTS                                         NAMES
608d51034525   mysql-sandbox-python-app                                                           "bash -lc 'while tru…"   49 seconds ago   Up 48 seconds                                                            mysql-sandbox-python-app-1
2afd45486380   mysql:8.0                                                                          "docker-entrypoint.s…"   10 minutes ago   Up 49 seconds              0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql-sandbox-mysql-1
```

Amb aquestes dades ja podem connectar amb el contenidor mysql-sandbox-python-app-1:

```bash
docker exec -it mysql-sandbox-python-app-1 bash
```

### Crear la base de dades, les taules i l'usuari

Quan s'inicia el contenidor s'executa el fitxer init.sql que crea la base de
dades `botigues` i l'usuari `uoc` amb els permisos necessaris. També crea dues
taules `productes` i `vendes`. Els passos també es poden executar manualment:

Primer ens connectarem a la base de dades de MySQL com a root, per a permetre a
l'usuari `uoc` que es connecti des de qualsevol adreça IP:

```bash
mysql -h mysql -u root -prootpass --skip-ssl botigues
```

```sql
DROP USER IF EXISTS 'uoc'@'%';
CREATE USER 'uoc'@'%' IDENTIFIED BY 'examplepass';
GRANT ALL PRIVILEGES ON botigues.* TO 'uoc'@'%';
FLUSH PRIVILEGES;
```

Una vega establertes les credencials i els permisos de l'usuari `uoc`, ens podem
connectar a la base de dades amb la següent comanda:

```bash
mysql -h mysql -u uoc -pexamplepass --skip-ssl --local-infile=1 botigues
```

El següent pas serà inserir els productes a la base de dades:

```sql
CREATE TABLE productes (
    id_producte VARCHAR(20) PRIMARY KEY,
    departament VARCHAR(255) NOT NULL,
    descripcio VARCHAR(255) NOT NULL,
    preu DECIMAL(10, 2) NOT NULL
);
CREATE TABLE vendes (
    id_venda INT AUTO_INCREMENT PRIMARY KEY,
    id_botiga VARCHAR(20) NOT NULL,
    id_producte VARCHAR(20) NOT NULL,
    quantitat INT NOT NULL,
    data DATE NOT NULL,
    hora TIME NOT NULL,
    CONSTRAINT fk_vendes_productes
        FOREIGN KEY (id_producte)
        REFERENCES productes(id_producte)
);
```

### Carregar les dades del fitxer productes.csv a la taula productes

Per connectar-se a la base de dades amb l'usuari `uoc`:

```bash
mysql -h mysql -u uoc -pexamplepass --skip-ssl --local-infile=1 botigues
```

Per carregar les dades del fitxer productes.csv a la taula productes:

```SQL
LOAD DATA LOCAL INFILE './productes.csv'
INTO TABLE productes
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(id_producte, departament, descripcio, preu);
```

Nota: les sentències sql s'han d'executar des de la carpeta data, hi ha d'haver
un fitxer `productes.csv`.

Nombre de registres a la taula productes:

```SQL
SELECT COUNT(*) AS total_productes FROM productes;
```

L'script `process.py` s'ha d'executar des de la carpeta source i els fitxers de
les vendes han d'estar a la carpeta `validat` dins de la carpeta `data`.

Per validar la inserció de les dades:

```bash
mysql -h mysql -u uoc -pexamplepass --skip-ssl --local-infile=1 botigues
```

Nombre de registres a la taula vendes:

```sql
SELECT COUNT(*) AS total_vendes FROM vendes;
```

Nombre total de productes venuts i recaptació per botiga.

```sql
SELECT 
    v.id_botiga,
    SUM(v.quantitat) AS total_unitats,
    SUM(v.quantitat * p.preu) AS total_import
FROM vendes v
JOIN productes p ON v.id_producte = p.id_producte
GROUP BY v.id_botiga
ORDER BY v.id_botiga;
```

Nombre total de productes venuts i recaptació per botiga, ordenació per
recaptació total:

```sql
SELECT 
    v.id_botiga,
    SUM(v.quantitat) AS total_unitats,
    SUM(v.quantitat * p.preu) AS total_import
FROM vendes v
JOIN productes p ON v.id_producte = p.id_producte
GROUP BY v.id_botiga
ORDER BY total_import DESC;
```

Nombre total de productes venuts i recaptació per dia:

```sql
SELECT 
    v.data,
    SUM(v.quantitat) AS total_unitats,
    SUM(v.quantitat * p.preu) AS total_import
FROM vendes v
JOIN productes p ON v.id_producte = p.id_producte
GROUP BY v.data
ORDER BY v.data;
```

### Mysql Workbench

Es pot utilitzar Mysql Workbench per fer proves i consultes a la base de
dades `botigues`. Per crear una nova connexió Afegim els paràmetres de la
connexió:

<img src="./img/wb001.avif" alt="paràmetres connexió" width="674px" style="max-width: 674px; display: block; margin: 0 auto;">

Establim la contrasenya:

<img src="./img/wb002.avif" alt="contrasenya" width="349px" style="max-width: 349px; display: block; margin: 0 auto;">

Provem la connexió:

<img src="./img/wb003.avif" alt="prova" width="186px" style="max-width: 186px; display: block; margin: 0 auto;">

Un cop desada, la connexió apareixerà a la finestra principal.

<img src="./img/wb004.avif" alt="principal" width="800px" style="max-width: 800px; display: block; margin: 0 auto;">

## Fitxers

- **Dockerfile** Fitxer amb les instruccions per crear la imatge del contenidor python-app
- **mysql/** Carpeta amb els fitxers del contenidor mysql
  - **init** Carpeta amb els fitxers d'inicialització del contenidor mysql
    - **init.sql** Fitxer amb les sentències necessàries per crear la base de dades, les taules i l'usuari.
- **python-app/** Carpeta amb els fitxers del contenidor python-app
  - **data/** Carpeta amb els fitxers csv
    - **entrada/** Carpeta d'entrada dels fitxers csv de les vendes que seran validats per l'script `validate.py`
    - **error/** Carpeta que conté els fitxers csv amb errors després de validar-los.
    - **processat/** Carpeta que conté els fitxers csv processats de les vendes, els fitxers d'entrada estan a la carpeta `validat/`
    - **validat/** Carpeta que conté els fitxers csv validats de les vendes després de validar-los.
    - **productes.csv** Fitxer csv amb els productes
- **requirements.txt** Fitxer amb les dependències de Python per a l'script `process.py`
- **source** Carpeta que conté els scripts per validar els fitxers csv de vendes i per afegir el contingut en una base de dades mysql
