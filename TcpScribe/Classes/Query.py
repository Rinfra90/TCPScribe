from .DatabaseElements import myDatabaseTable
import mariadb

class Query:

    __host = 'localhost'
    __port = 3306
    __user = 'root'
    __psw = ''

    def __init__(self, connDb=True):
        self.instr = ''
        self.where = ''
        self.db = ''
        self.tb = '*'
        self.col = '*'
        self.outfile = ''
        self.connDb = connDb #Variabile utilizzata per verificare se � necessario connettersi a un db per eseguire la query

    @classmethod
    def SetServer(cls,newHost,newPort):
        cls.__host = newHost
        cls.__port = newPort

    @classmethod
    def GetServer(cls):
        print(f"Host: {cls.__host}")
        print(f"Port: {cls.__port}")
        
    @classmethod
    def SetCredenziali(cls,newUser,newPassword,oldPassword=''):
        cls.__user = newUser
        if oldPassword == cls.__psw:
            cls.__psw = newPassword
        else:
            print("Password non cambiata. Vecchia password incoerente")

    @classmethod
    def GetCredenziali(cls):
        print(f"User: {cls.__user}")
        if cls.__psw != '':
           print("Password settata")
        else:
            print("Password non settata")

    @staticmethod
    def Info():
        print("""---------------------------------------------------
Istruzioni
---------------------------------------------------
Class Query:
Variabili:  __host
            __port
            __user
            __psw
Settabili e visualizzabili tramite i seguenti metodi:
SetCredenziali(newUser,newPassword,oldPassword),
GetCredenziali(),
SetServer(newHost,newPort),
GetServer()
---------------------------------------------------
Info():
Informazioni sulla classe e su come utilizzare i metodi della classe
---------------------------------------------------
EseguiQuery(instr,where,db,tb,col,engine,doubleCheck,pers,**val)
---------------------------------------------------
instr - Ammette 'SELECT','DROP','CREATE' e 'INSERT'
--------------------------
pers - viene utilizzato per inviare query personalizzate. Inserire il testo completo all'interno di 'instr'
doubleCheck - utilizzata per scegliere se aggiungere 'IF NOT EXISTS' in fase di creazione tabelle e database
--------------------------
SELECT:
db - Identifica il database a cui connettersi
col - Le colonne da ricercare vengono passate qui
tb - Identifica le tabelle su cui eseguire le query
where - Inserire qui tutte le varie condizioni che si vogliono aggiungere
--------------------------
DROP:
tb - Se non viene inserito niente, viene eliminato il database
db - Indica il database da eliminare o da cui eliminare la tabella
--------------------------
CREATE:
tb - Se non viene inserito niente, viene creato il database
db - Indica il database da creare o su cui creare la tabella
**val - Aggiungere argomenti aggiuntivi per indicare la Structure di una tabella.
        Formato NOMEVAR = 'PROPRIETA'
        es:
        id = "NOT NULL AUTO_INCREMENT"
        Risulta nella seguente query:
        id NOT NULL AUTO_INCREMENT
engine - Di default e' 'InnoDb'
--------------------------
INSERT:
db - Identifica il database sui cui verryear inseriti i dati
tb - Identifica le tabelle in cui verryear inseriti i dati
**val - Aggiungere argomenti aggiuntivi per definire i campi dove inserirli e i Values da inserire.
        Formato campo = 'VALUE'
        es:
        Values='2'
        Inserisce un nuovo elemento nella/e tabella/e tb con VALUE '2' nel campo 'Values'
---------------------------------------------------""") 
        
    #Metodo per analizzare l'integrit� dei dati e che restituisce la query completa o False in caso i dati non siano corretti
    def __CheckQuery(self, **args):

        check = False #Variabile utilizzata per verificare l'integrit� della query

        val = False

        for key, value in args.items():
            if key == 'doubleCheck':
                doubleCheck = value
            elif key == 'pers':
                pers = value
            else:
                val = value
                keys = ', '.join(value.keys())
                vals = ', '.join(value.values())

        #Guardo se � una query personalizzata e nel caso la eseguo
        if pers:
            if self.instr[-1] != ';':
                self.instr = self.instr + ';'
            return self.instr

        else:
            if self.db != '':
                #Identifico le istruzioni preimpostate
                if self.instr.upper() == 'CREATE':
                        if doubleCheck == True:
                            doubleCheck = "IF NOT EXISTS "
                        else:
                            doubleCheck = ''
                        if self.tb == '*':
                            sendQuery = "CREATE DATABASE " + doubleCheck + f"{self.db};"
                            check = True
                            self.connDb = False
                        else:
                            sendQuery = "CREATE TABLE " + doubleCheck + f"{self.tb.nome}\n(\n"
                            
                            if self.tb.campi.values():

                                checkKey = False
                            
                                for chiave, VALUE in self.tb.campi.items():
                                    sendQuery = sendQuery + f"{chiave} {VALUE}" + ",\n"
                                    if self.tb.priKey == chiave:
                                        checkKey = True

                                if self.tb.priKey != '':
                                    if checkKey:
                                        sendQuery = sendQuery + f"PRIMARY KEY ({self.tb.priKey})\n)\n"
                                        sendQuery = sendQuery + f"ENGINE = {self.tb.engine};"
                                        check = True
                                    else:
                                        print(f"Errore nell'esecuzione della Query {self.instr.upper()}: La chiave non corrisponde a nessun VALUE")
                                        return False
                                else:
                                    print(f"Errore nell'esecuzione della Query {self.instr.upper()}: Specificare la chiave primaria della tabella")
                                    return False
            
                else:
                    if self.instr.upper() == 'DROP':
                        if self.tb == '*':
                            sendQuery = f"DROP DATABASE {self.db};"
                            check = True
                            self.connDb = False
                        else:
                            sendQuery = f"DROP TABLE {self.tb.nome};"
                            check = True

                    else:
                        tbNomi = ''

                        if type(self.tb) == tuple or type(self.tb) == list:
                            for tabella in self.tb:
                                if type(tabella) == myDatabaseTable:
                                    if tbNomi == '':
                                        tbNomi = tabella.nome
                                    else:
                                        tbNomi += ', ' + tabella.nome
                                elif type(tabella) == str:
                                    if tbNomi == '':
                                        tbNomi = tabella
                                    else:
                                        tbNomi += ', ' + tabella
                        elif type(self.tb) == myDatabaseTable:
                            tbNomi = self.tb.nome
                        else:
                            tbNomi = self.tb

                        if type(self.col) == tuple or type(self.col) == list:
                            self.col = ", ".join(self.col)
                        if not type(self.col) == str:
                            print('Errore nel passaggio delle colonne')
                            return False

                        if self.instr.upper() == 'SELECT':
                            sendQuery = "SELECT {} FROM {}".format(self.col,tbNomi)
                            if self.outfile != '':
                                sendQuery += f" INTO OUTFILE '{self.outfile}'"
                            if self.where != '':
                                sendQuery = sendQuery + f"\nWHERE {self.where}"
                            sendQuery = sendQuery + ";"
                            check = True

                        elif self.instr.upper() == 'INSERT':
                            if val:
                                keys = ', '.join(val.keys())
                                vals = "', '".join(val.values())
                                sendQuery = "INSERT INTO {} ({})\nVALUES ('{}');".format(tbNomi,keys,vals)
                                check = True
                            else:
                                print(f"Errore nell'esecuzione della Query {self.instr.upper()}: Values da inserire non specificati")
                                return False

                        elif self.instr.upper() == 'DELETE':
                            sendQuery = f"DELETE FROM {tbNomi}"
                            if self.where != '':
                                sendQuery = sendQuery + f"\nWHERE {self.where}"
                            sendQuery = sendQuery + ';'
                            check = True
            else:
                print(f"Errore nell'esecuzione della Query {self.instr.upper()}: E' necessario specificare un database")
                return False
                
            if check:
                return sendQuery
            else:
                print(f"Query {sendQuery} non eseguita")
                return False

    #Metodo che riformatta la tabella delle stringhe risultanti dalla query in maniera da stamparla a video in maniera pi� chiara
    def __FormattaTabella(self, header, tb):

        lunghezze = []
        tabella = []
        if type(header) == tuple:
            newcol = []
            for el in header:
                newcol.append(el)
            header = newcol
        elif type(header) == str:
            header = header.split(',')

        tabella.append(header)
        ncol = 0
        for el in header:
            lunghezze.append(len(el))
            ncol += 1
        
        for row in tb:
            c = 0
            while c < ncol:
                if len(row[c]) > lunghezze[c]:
                    lunghezze[c] = len(row[c])
                c += 1
            tabella.append(row)

        formatHeader = '+'

        c = 0
        for el in header:
            i = 0
            while i <= lunghezze[c]:
                formatHeader += "-"
                i += 1
            formatHeader += "-+"
            c += 1

        outTabella = []
        outTabella.append(formatHeader)

        r=0
        for row in tabella:
            c = 0
            for el in row:
                while len(tabella[r][c]) < lunghezze[c]:
                    tabella[r][c] += ' '
                c += 1
            r += 1
            row = '| ' + ' | '.join(row) + ' |'
            outTabella.append(row)
            if r == 1:
                outTabella.append(formatHeader)
        
        outTabella.append(formatHeader)
        return outTabella

    #Metodo da richiamare per far eseguire la query.
    #Dettagli inseriti all'interno del metodo Info.
    def QueryExecute(self, instr, where='', db='', tb='*', col='*', doubleCheck=True, pers=False, outfile='', **val):
                        
        output = []
        self.instr = instr
        self.where = where
        self.db = db
        self.tb = tb
        self.col = col
        self.outfile = outfile

        qy = self.__CheckQuery(doubleCheck=doubleCheck, pers=pers, val=val)

        if qy:
            try:
                if self.connDb:
                    dbms = mariadb.connect(host=self.__host,port=int(self.__port),user=self.__user,password=self.__psw,database=self.db)
                else:
                    dbms = mariadb.connect(host=self.__host,port=int(self.__port),user=self.__user,password=self.__psw)
            except mariadb.Error as e:
                print(f"Errore nella connessione a MariaDB: '{e}'")
            else:
                try:
                    cursore = dbms.cursor()
                    cursore.execute(qy)
                    dbms.commit()
                    try:
                        for row in cursore:
                            extract = []
                            for el in row:
                                extract.append(str(el))
                            output.append(extract)

                        print("Dati acquisiti...")
                        print("...Formatto la visualizzazione...")
                        
                        if col == '*':
                            if type(self.tb) == tuple or type(self.tb) == list:
                                for tabella in self.tb:
                                    if type(tabella) == myDatabaseTable:
                                        tbNomi += "', '" + tabella.nome
                                    elif type(tabella) == str:
                                        tbNomi += "', '" + tabella
                            elif type(self.tb) == myDatabaseTable:
                                tbNomi = self.tb.nome
                            else:
                                tbNomi = self.tb
                            qy = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tbNomi}'"
                            cursore.execute(qy)
                            dbms.commit()
                            col=[]
                            for row in cursore:
                                col.append(row[0])

                        #   Con questa funzione si formatta la tabella per stamparla a video
                        #   Se si vuole il risultato invece di stamparlo, bisogna prendere la variabile output
                        tabellaFormattata = self.__FormattaTabella(col,output)

                        for row in tabellaFormattata:
                            print(row)

                    except:
                        try:
                            if not output == []:
                                print(output)
                            else:
                                #print("Query Eseguita. 0 righe da visualizzare.")
                                pass
                        except:
                            pass
                except mariadb.Error as e:
                    print(f"Errore nell'esecuzione della Query: {e}\n{qy}")
                finally:
                    dbms.close()

        self.connDb = True

        if output == []:
            return
        else:
            return output