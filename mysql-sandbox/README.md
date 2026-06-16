# Entorn de proves de Mysql

## Connexió al contenidor d'aplicació

El contenidor de l'aplicació i del client de MySQL no té cap procés que
s'executi en primer pla, per la qual cosa no es manté en execució. Per iniciar
el contenidor, primer haurem de determinar la xarxa del contenidor de MySQL i
quin nom té el nom del contenidor de l'aplicació:

La xarxa és `mysql-sandbox_default`:

```bash
docker network ls
```

```text
NETWORK ID     NAME                    DRIVER    SCOPE
c1008688b77c   bridge                  bridge    local
9c8ec509a463   host                    host      local
5aa93fd3999b   mysql-sandbox_default   bridge    local
b5421b1c96e3   none                    null      local
```

El nom del contenidor és `mysql-sandbox-python-app`:

```bash
docker ps -a
```

```text
CONTAINER ID   IMAGE                                                                     COMMAND                  CREATED         STATUS                     PORTS                                         NAMES
d8c54fbcab4b   mysql-sandbox-python-app                                                  "python3"                3 minutes ago   Exited (0) 3 minutes ago                                                 mysql-sandbox-python-app-1
5b57330a793f   mysql:8.0                                                                 "docker-entrypoint.s…"   3 minutes ago   Up 3 minutes               0.0.0.0:3306->3306/tcp, [::]:3306->3306/tcp   mysql-sandbox-mysql-1
```

Amb aquestes dades ja podem iniciar el contenidor:

```bash
docker run -it \
  --network mysql-sandbox_default \
  -v $(pwd)/python-app/data:/app/data \
  -v $(pwd)/python-app/source:/app/source \
  mysql-sandbox-python-app bash
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
