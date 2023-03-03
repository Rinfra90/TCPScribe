# TCP Scribe

Qualora si fosse interessati solamente alle procedure necessarie per l'installazione del servizio, iniziare da [PC](#pc) e continuare con la sezione [Procedura di installazione](#procedura-di-installazione)

### Legenda

- [Informazioni generali](#informazioni-generali)
- [PC](#pc)
- [Procedura di installazione](#procedura-di-installazione)

# Informazioni generali
## Legenda
- [Info](#info)
- [File di configurazione](#file-di-configurazione)
- [Log](#log)

## Info
TCP Scribe è un servizio di Windows pensato per girare silentemente in background. Il suo scopo è quello di ricevere dati tramite comunicazione TCP e di scriverli su un database. _TCP Scribe_ è pensato per utilizzare una struttura di dati standard, ottimizzati per l'analisi di una nave. I tipi di dati che _TCP Scribe_ interpreta sono Eventi, Allarmi, Settaggi e Valori.
Nel caso il database non esista, il servizio provvederà autonomamente a crearne uno con il nome _Analizer_ ed a definirne tutte le proprietà necessarie per il corretto funzionamento.
Consultare la sezione [Struttura Database](#struttura-database) per ulteriori informazioni

Le credenziali di accesso al database sono immagazzinate in un file di configurazione insieme alle coordinate di accesso al server. Il file di configurazione ha il solo scopo di agevolare la modifica delle proprietà da parte del distributore. Consultare la sezione [File di configurazione](#file-di-configurazione) per maggiori informazioni.

Tutte le informazioni relative ad errori o azioni di processo, vengono invece immagazzinate all'interno di diversi file Log. Anche l'utilizzo di questi file, ha lo scopo di aiutare la manutenzione e il supporto in caso di eventuali problematiche da parte del distributore. Consultare la sezione [Log](#log) per maggiori informazioni.

*Copyright © 2022 - [Cienne Solutions](https://www.ciennesolutions.it/) -  È vietata la redistribuzione e la pubblicazione dei contenuti e immagini non autorizzata espressamente dall´autore.*

## Struttura Database

Il database è pensato per le esigenze di una nave ed è suddiviso in tre tabelle.
- [Eventi ed allarmi](#eventi-ed-allarmi)
- [Settaggi](#settaggi)
- [Valori](#valori)

### Eventi ed allarmi

Questa tabella raccoglie la maggior parte degli stati presenti sulla nave.
| id | Data | Evento | Valore | Tipo |
| ------ | ------ | ------ | ------ | ------ |
|    Numero univoco identificativo    |    Data di registrazione dell'evento da parte del controllore    | Nome dell'evento registrato | Variabile in base alla tipologia di evento | Sigla che identifica se Evento o allarme |
|    Numero intero    |    Formato `yyyy-mm-dd hh:mm:ss`    |    Descrizione testuale    |    Descrizione testuale    |    EVN/ALM    |

### Settaggi

Questa tabella raccoglie le interazioni degli utenti e i cambiamenti di settaggi
  | id | Data | Stazione | Operatore | Evento | Valore | Tipo |
| ------ | ------ | ------ | ------ | ------ | ------ | ------ |
|    Numero univoco identificativo    | Data di registrazione dell'evento da parte del controllore | Stazione dalla quale è stata eseguita l'operazione | Chi ha eseguito l'operazione nella stazione |     Nome dell'evento registrato | Variabile in base alla tipologia di evento | Sigla identificativa del settaggio |
|    Numero intero    |    Formato `yyyy-mm-dd hh:mm:ss`    |    Descrizione testuale    | Descrizione testuale    | Descrizione testuale    |    Descrizione testuale    |    STG    |

### Valori

In questa tabella, vengono registrati tutti i valori relativi alla nave.

## File di configurazione

### Folder
Il file di configurazione deve essere inserito all'interno della cartella dell'utente di sistema: `C:\Windows\System32\config\systemprofile\AppData\Local\TCPScribe`
### Contenuto
All'interno del file sono immagazzinate le coordinate del server e le credenziali di accesso al database.
Le credenziali vengono inserite durante la procedura di installazione

## Log
### Folder
La cartella con i log vuoti deve essere inserita all'interno della cartella dell'utente di sistema: `C:\Windows\System32\config\systemprofile\AppData\Local\TCPScribe`
### Tipologia
Il servizio scriverà all'interno dei 3 log:
- ServiceErrorLog
- ServiceInfoLog
- ServiceWarningLog
Ogni log conterrà messaggi di un diverso livello (Errore, Warning e Informazione)

+++

# PC
## Legenda
- [Disinstallare Antivirus](#disinstallare-antivirus)
- [Disattivare UAC](#disattivare-uac)
- [Disattivare Firewall](#disattivare-firewall)

## Legenda

- [Disinstallare Antivirus](#disinstallare-antivirus)
- [Disattivare UAC](#disattivare-uac)
- [Disattivare Firewall](#disattivare-firewall)

## Disinstallare Antivirus

IMPORTANTE: Disinstallare subito qualsiasi antivirus in quanto potrebbe riconoscere Python o PIP (installatore dei pacchetti Python) come minaccia

## Disattivare UAC

- Premere Win
- Scrivere UAC
- Aprire "Modifica le impostazioni di controllo dell'account utente"
- Spostare in basso la barra fino a selezionare "Non notificare mai all'utente"
- Premere OK
- Premere Sì alla richiesta di conferma

## Disattivare Firewall

- Premere Win
- Scrivere "Firewall"
- Aprire "Protezione firewall e della rete"
- Selezionare "Rete di dominio"
- Disattivare
- Ripetere passaggio per "Rete privata" e "Rete pubblica"

+++

# Procedura di installazione
Procedura per installare i vari programmi necessari e il servizio

## Legenda
- [Creare cartella programma](#creare-cartella-programma)
- [Python](#python)
- [MariaDB](#maria-db)
- [Installazione servizio](#installazione-servizio)

## Creare cartella programma

Questa guida è stata pensata per usare sempre i soliti percorsi.
Se non si seguono esattamente i soliti passaggi, vanno regolati i path di conseguenza.
- Copiare la cartella "TCPScribe" sul desktop
- Seguire il passaggio [Preparare file di configurazione](#preparare-file-di-configurazione) per quanto riguarda la cartella Windows

---

## Python

All'interno della cartella TCPScribe è presente la versione 3.11.2 64bit.
Se si vuol scaricare la versione più recente, passare dalla sezione Download, altrimenti andare direttamente alla sezione Installazione usando il file `TCPScribe\Python\python-3.11.2-amd64.exe`

### Download

Andare su https://www.python.org/downloads/ e scaricare l'ultima versione
### Installazione
- Lanciare il file python-X.XX.X-amd64
- Spuntare 'Use admin privileges when installing py.exe' e 'Add python.exe to PATH'
- Lanciare 'Install Now'
- Selezionare 'Disable path lenght limit'
### Aggiornare pip
- Premere Win
- Scrivere prompt dei comandi
- Premere con il tasto destro su prompt dei comandi
- Selezionare "Esegui come amministratore"
- Lanciare il comando `python.exe -m pip install --upgrade pip`
### Installare pacchetti
- Aprire la cartella TCPScribe sul Desktop
- Premere con il tasto destro su "Requirements.txt"
- Selezionare "Copia come percorso"
- Premere Win
- Scrivere prompt dei comandi
- Premere con il tasto destro su prompt dei comandi
- Selezionare "Esegui come amministratore"
- Scrivere il seguente comando: `pip install -r <PATH>` sostituendo <PATH> con il percorso del file requirements
	- Per copiare il percorso del file requirements, premere con il tasto destro sul terminale.
	- Il risultato dovrebbe essere `pip install -r "C:\Users\Cienne\Desktop\TCPScribe\requirements.txt"`
### Variabile di sistema

Questa procedura è molto importante, perché senza di questa il servizio non partirà e darà Errore 1053
- Cercare la directory di installazione di Python, solitamente `C:\Users\Cienne\AppData\Local\Programs\Python\PythonXXX`, dove al posto delle X ci saranno i numeri della versione
- Copiare il percorso della cartella
- Premere Win
- Scrivere "Variabili di ambiente"
- Aprire "Modifica le variabili di ambiente relative al sistema"
- Nella finestra delle proprietà del sistema, fare clic sulla scheda "Avanzate"
- Cliccare su "Variabili d'ambiente"
- Trovare la variabile d'ambiente PATH nella sezione "Variabili di sistema"
- Selezionare PATH e fare clic su "Modifica"
- Premere "Nuovo"
- Incollare il percorso copiato precedentemente
- Premere "Nuovo"
- Incollare il percorso copiato precedentemente seguito da `\Scripts`, ad esempio `C:\Users\Cienne\AppData\Local\Programs\Python\Python311\Scripts`

---

## MariaDB

### Installazione programma
- Aprire la cartella MariaDB dentro la cartella TCPScribe sul Desktop
- Lanciare il file "mariadb-10.9.3-winx64.msi"
- Premere "Next"
- Accettare i termini e premere "Next"
- Lasciare invariato il Custom Setup e premere "Next"
- Lasciare la spunta su "Modify password for database user 'root'"
- Immettere 'cnscns' come password
- Spuntare "Enable access from remote machines for 'root' user"
- Premere "Next"
- Lasciare invariate le "Default instance properties"
### Settare Variabile d'ambiente
Questa procedura abilita l'utilizzo da terminale del comando `mysql`
- Cercare la directory di installazione di MariaDB, solitamente `C:\Program Files\MariaDB 10.9\bin`
- Copiare il percorso della cartella
- Premere Win
- Scrivere "Variabili di ambiente"
- Aprire "Modifica le variabili di ambiente relative al sistema"
- Nella finestra delle proprietà del sistema, fare clic sulla scheda "Avanzate"
- Cliccare su "Variabili d'ambiente"
- Trovare la variabile d'ambiente PATH nella sezione "Variabili di sistema"
- Selezionare PATH e fare clic su "Modifica"
- Premere "Nuovo"
- Incollare il percorso copiato precedentemente

---

## Installazione servizio

### Preparare file di configurazione
- Ottenere le credenziali. Per ottenere le credenziali necessarie alla scrittura, basterà aprire le cartelle e dare il consenso.
	- Andare in `C:\Windows\System32\config\systemprofile\AppData\Local\`
	- Quando verrà detto che non si dispone delle autorizzazioni necessarie, premere continua per ottenerle.
	- Chiudere la cartella
- Spostare la cartella "Windows" in `C:\`
- E' consigliato anche copiare un collegamento della cartella "TCPScribe" appena copiata e inserirlo sul desktop
### Procedura di installazione
- Aprire la cartella TCPScribe sul Desktop
- Premere con il tasto destro su "TCPScribe.py"
- Selezionare "Copia come percorso"
- Premere Win
- Scrivere prompt dei comandi
- Premere con il tasto destro su prompt dei comandi
- Selezionare "Esegui come amministratore"
- Scrivere il seguente comando: `python <PATH> install` dove al posto di PATH va inserito il percorso copiato in precedenza di TCPScribe.py
	- Un esempio del risultato potrebbe essere questo: `python "C:\Users\Cienne\Desktop\TCPScribe\TCPScribe.py" install`
### Settare il servizio
- Premere Win
- Scrivere "Servizi"
- Aprire "Servizi"
- Trovare "TCP Scribe"
- Premere due volte per aprire le proprietà
- Su "Tipo di avvio" modificare da "Manuale" ad "Automatico"
- Premere il pulsante sottostante "Avvia"