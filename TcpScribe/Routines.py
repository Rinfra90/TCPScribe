import os
from Classi.DatabaseElements import myDatabaseTable
from Classi.LogWriter import LogWriter
from Classi.Query import Query
from datetime import datetime

class Routines(object):

    __miaQuery = Query()
    __now = datetime.now

    @classmethod
    def setRoutine(cls, host='localhost', port=3306, user='root', psw='', oldpsw=''):
        cls.__miaQuery.SetServer(host,port)
        cls.__miaQuery.SetCredenziali(user,psw,oldpsw)
    
    @classmethod
    def DeleteOldRecords(cls, database, tb):

        cls.__now = datetime.now()
        lastYear = str((cls.__now.year-1)) + cls.__now.strftime("/%m/%d")

        writer = LogWriter()
        
        tbNome = ''
        
        if type(tb) == tuple or type(tb) == list:
            for tabella in tb:
                if type(tabella) == myDatabaseTable:
                    tbNome = tabella.nome
                elif type(tabella) == str:
                    tbNome = tabella
                cls.Deleter(lastYear, database, tbNome, writer)

        elif type(tb) == myDatabaseTable:
            tbNome = tb.nome
            cls.Deleter(lastYear, database, tbNome, writer)

        else:
            tbNome = tb
            cls.Deleter(lastYear, database, tbNome, writer)


    @classmethod
    def Deleter(cls,lastYear, database, tbNome, writer):
        try:
            cls.__miaQuery.QueryExecute(
                instr= 'DELETE',
                where= f"Data < '{lastYear}'",
                db= database,
                tb= tbNome
                )
            print("Dati vecchi cancellati")
        except Exception as e:
            messaggio = f"Errore nell'eliminazione dei vecchi dati: {e}"
            print(messaggio)
            try:
                writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Errore nella scrittura del file log: {e}")
    
    @classmethod
    def DeleteNotSoOldRecords(cls, database, tb):

        cls.__now = datetime.now()
        lastDay = '2022/09/29'

        writer = LogWriter()

        try:
            cls.__miaQuery.QueryExecute(
                instr= 'DELETE',
                where= f"Data < '{lastDay}'",
                db= database,
                tb= tb
                )
        except Exception as e:
            messaggio = f"Errore nell'eliminazione dei vecchi dati: {e}"
            print(messaggio)
            try:
                writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Errore nella scrittura del file log: {e}")

    @classmethod
    def fileExcel(cls, database, tb, col, where='', path='/', outfile='dbRecord', ext='.xls'):

        writer = LogWriter()

        os.makedirs(path, exist_ok=True)
        counter = ''

        exit = False
        if os.path.exists(path+outfile+ext):
            c = 1
            while not exit:
                if not os.path.exists(path+outfile+'_'+str(c)+ext):
                    counter = f'_{c}'
                    exit = True
                else:
                    c += 1
       
        try:
            print("Eseguo Query")
            cls.__miaQuery.QueryExecute(
                instr= 'SELECT',
                where= where,
                db= database,
                tb= tb,
                col= col,
                outfile= path+outfile+counter+ext
                )
            print("Query eseguita")
        except Exception as e:
            messaggio = f"Errore nella creazione del file Excel: {e}"
            print(messaggio)
            try:
                writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Errore nella scrittura del file log: {e}")