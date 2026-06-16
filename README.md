# PAC3

## SSH sense contrasenya

### 1. Crear les claus SSH

Per utilitzar SSH sense contrasenya, primer cal generar un parell de claus (privada i pública):

```shell
ssh-keygen -t ed25519 -f ~/.ssh/id_ed25519-uoc -C "USUARI@uoc.edu"
```

> [!NOTE]
> Substituir USUARI amb el nom d'usuari del teu compte a la UOC (sense @uoc.edu)

Això crearà:

- `~/.ssh/id_ed25519-uoc` (clau privada)
- `~/.ssh/id_ed25519-uoc.pub` (clau pública)

### 2. Copiar la clau pública al servidor

Envia la clau pública al servidor mitjançant `ssh-copy-id`:

```shell
ssh-copy-id -i ~/.ssh/id_ed25519-uoc.pub -p 55000 USUARI@eimtcld3.uoclabs.uoc.es
```

Això afegirà la clau pública al fitxer `~/.ssh/authorized_keys` del servidor.

### 3. Configurar ~/.ssh/config

Crea o edita el fitxer `~/.ssh/config` amb la següent configuració:

```text
Host uoc
    Hostname eimtcld3.uoclabs.uoc.es
    User USUARI
    Port 55000
    IdentityFile ~/.ssh/id_ed25519-uoc
    IdentitiesOnly yes
```

### 4. Usar SSH sense contrasenya

Amb aquesta configuració, ara pots connectar-te sense contrasenya executant:

```shell
ssh uoc
```

## Clonar el dipòsit amb Fine-grained Personal Access Token

Per clonar el dipòsit de GitHub sense usar SSH, també es pot fer amb un `Fine-grained personal access token` amb permisos només de lectura sobre el contingut del repositori.

### 1. Crear el token

A GitHub, cal accedir a `Settings` > `Developer settings` > `Personal access tokens` > `Fine-grained tokens`. Des d'aquesta pàgina es pot crear un nou token i assignar-li només els permisos mínims necessaris per llegir el contingut del repositori. En general, n'hi ha prou amb concedir accés de lectura al repositori i al seu contingut (`Contents: Read-only`).

### 2. Clonar el repositori

Quan Git demani autenticació, cal fer servir el token com a contrasenya. Per exemple:

```shell
git clone https://github.com/USUARI/REPOSITORI.git
```

Quan aparegui la sol·licitud d'usuari i contrasenya:

- Usuari: el nom d'usuari de GitHub
- Contrasenya: el `Fine-grained personal access token`

> [!NOTE]
> El token es pot desar en un magatzem i es poden configurar els paràmetres predeterminats

```shell
git config --global user.name "rbuj"
git config --global user.email "robert.buj@gmail.com"
git config --global credential.helper store
git clone https://github.com/rbuj/M2.958-PAC2.git PAC2
git config --global --list
```

> [!WARNING]
> El Fine-grained Personal Access Token es desa al fitxer ~/.git-credentials, per eliminar les credencials de forma segura, executa la comanda de sota

```shell
git credential-store --file ~/.git-credentials erase
```

## Desenvolupament amb contenidors o entorns virtuals

L'avantatge d'utilitzar un contenidor o un entorn virtual és que permet aïllar
les dependències del projecte del sistema operatiu, evitant conflictes entre
diferents projectes i versions de biblioteques.

### OPCIÓ 1: Desenvolupament amb Dev Containers

#### Requisits

- Docker Desktop [instal·lar](https://www.docker.com/products/docker-desktop/)
- Visual Studio Code: [instal·lar](https://code.visualstudio.com/)
- Remote Development, extensió de Visual Studio Code: [instal·lar](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.vscode-remote-extensionpack)

#### Creació del contenidor

Una vegada oberta la carpeta del projecte a VS Code, clicarem a la icona
"Open a Remote Window" i seleccionarem "Reopen in Container".

<p align="center">
  <img src="./img/connect.avif" width="73px" style="border:solid 1px red;">
</p>

Aquesta ordre crearà un contenidor i instal·larà totes les dependències. Una
vegada s'ha completat el procés de creació del contenidor, cal instal·lar les
extensions recomanades per al projecte:

<p align="center">
  <img src="./img/extensions.avif" width="480px" style="border:solid 1px red;">
</p>

Un cop creat i activat l'entorn virtual, ja es pot executar el codi a VS Code.

> [!IMPORTANT]
> Abans d'iniciar o crear el contenidor cal que Docker Desktop estigui en execució.

Per tancar la connexió, clicarem a la icona "Dev Container: Miniconda" i
seleccionarem "Close Remote Connection". El contenidor es pot aturar des del
tauler de Docker Desktop.

<p align="center">
  <img src="./img/disconnect.avif" width="511px" style="border:solid 1px red;">
</p>

### Opció 2: Conda

#### Requisits de Conda

- miniconda
  - (macos) es recomana instal·lar-ho a través de [Homebrew](https://brew.sh/)
  - (windows) es recomana utilitzar l'[instal·lador](<<https://www.anaconda.com/docs/getting-started/miniconda/install/overview>)
- Visual Studio Code: [instal·lar](https://code.visualstudio.com/)

#### Creació de l'entorn virtual

Per crear un entorn virtual amb conda, executeu la següent ordre al directori
arrel del projecte:

```sh
conda env create --prefix=./.conda --file=environment.yml
```

Per tal d'assegurar que l'entorn virtual s'ha creat correctament, podeu
comprovar que el directori `.conda/` s'ha creat al directori arrel del projecte.

> [!TIP]
> Miniconda requereix menys espai i és més lleuger que Anaconda. Per a
> instal·lar Miniconda en sistemes macOS, podeu utilitzar Homebrew:

```sh
brew install --cask miniconda
conda init
conda config --set auto_activate_base False
source ~/.bash_profile
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main
conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r
```

>
> [!NOTE]
> Podeu utilitzar l'extensió de Visual Studio Code
> [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)
> per gestionar entorns virtuals i executar codi Python dins de l'editor.
> Per crear un entorn virtual amb conda, accediu a la paleta d'ordres
> (`Ctrl+Shift+P` o `Cmd+Shift+P` a macOS) i escriviu "Python: Create Environment".

> [!IMPORTANT]
> Si voleu canviar l'intèrpret de Python utilitzat per Visual Studio Code,
> podeu fer-ho des de la paleta d'ordres (`Ctrl+Shift+P` o `Cmd+Shift+P` a macOS)
> escrivint "Python: Select Interpreter" i seleccionant l'intèrpret de l'entorn
> virtual que heu creat. Cal tenir en compte que l'intèrpret se seleccionarà
> automàticament amb l'entorn virtual quant aquest s'hagi creat amb l'extensió
> comentada en la nota anterior.

#### Activació i desactivació de l'entorn virtual

Per activar l'entorn virtual, executeu la següent ordre:

```sh
conda activate ./.conda
```

Per a desactivar l'entorn virtual, executeu la següent ordre:

```sh
conda deactivate
```

> [!TIP]
> Per canviar el prompt de l'entorn virtual i que mostri el nom de l'entorn,
> un cop activat, podeu executar la següent ordre per escurçar-lo:

```sh
conda config --set env_prompt '({name}) '
```

## Fitxers

- **bin/**: carpeta amb diversos scripts d'utilitat
  - **clear.sh**: script que neteja el notebook eliminant les metadades
  - **deploy.sh**: script per desplegar el quadern a la plataforma de la UOC
  - **format_sh.sh**: script per donar format als fitxes shell
  - **png2avif.sh**: converteix els fitxers png a avif
  - **png2jpg.sh**: converteix els fitxers png a jpg a la carpeta actual i
    a les subcarpetes
- **data/**: carpeta amb les dades de vendes generades amb l'script `generador_dades_vendes.py`
  - **productes.csv**: fitxer CSV amb informació dels productes
  - **CODI_YYYY-MM-DD.csv**: fitxer CSV amb les vendes d'un dia concret (YYYY-MM-DD) per a la botiga amb el codi CODI
- **environment.yml**: fitxer de configuració per crear l'entorn virtual amb conda
- **img/**: carpeta amb imatges utilitzades
- **mysql-sandbox**: carpeta amb fitxers necessaris per a la creació d'un entorn MySQL per fer proves
- **source/**: carpeta amb el codi font del projecte
  - **validate/**: carpeta amb scripts per validar les dades de vendes
    - **lambda_function.py**: script amb la funció Lambda per validar les dades de vendes
  - **process/**: carpeta amb scripts per processar les dades de vendes
    - **lambda_function.py**: script amb la funció Lambda per carregar les dades de vendes a la base de dades (processar)
  - **generador_dades_vendes.py**: script per generar dades de vendes d'exemple
