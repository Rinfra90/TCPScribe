import os
from Classes.DatabaseElements import myDatabaseTable
from Classes.LogWriter import LogWriter
from Classes.Query import Query
from datetime import datetime

class Routines(object):

    __myQuery = Query()
    __now = datetime.now

    @classmethod
    def setRoutine(cls, host='localhost', port=3306, user='root', psw='', oldpsw=''):
        cls.__myQuery.SetServer(host,port)
        cls.__myQuery.SetCredenziali(user,psw,oldpsw)
    
    @classmethod
    def DeleteOldRecords(cls, database, tb):

        cls.__now = datetime.now()
        lastYear = str((cls.__now.year-1)) + cls.__now.strftime("/%m/%d")

        writer = LogWriter()
        
        tbName = ''
        
        if type(tb) == tuple or type(tb) == list:
            for table in tb:
                if type(table) == myDatabaseTable:
                    tbName = table.name
                elif type(table) == str:
                    tbName = table
                cls.Deleter(lastYear, database, tbName, writer)

        elif type(tb) == myDatabaseTable:
            tbName = tb.name
            cls.Deleter(lastYear, database, tbName, writer)

        else:
            tbName = tb
            cls.Deleter(lastYear, database, tbName, writer)


    @classmethod
    def Deleter(cls,lastYear, database, tbNome, writer):
        try:
            cls.__myQuery.QueryExecute(
                instr= 'DELETE',
                where= f"Date < '{lastYear}'",
                db= database,
                tb= tbNome
                )
            print("Old data deleted")
        except Exception as e:
            message = f"Error deleting old datas: {e}"
            print(message)
            try:
                writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Error writing log file: {e}")
    
    @classmethod
    def DeleteNotSoOldRecords(cls, database, tb):

        cls.__now = datetime.now()
        lastDay = '2022/09/29'

        writer = LogWriter()

        try:
            cls.__myQuery.QueryExecute(
                instr= 'DELETE',
                where= f"Date < '{lastDay}'",
                db= database,
                tb= tb
                )
        except Exception as e:
            message = f"Error deleting old datas: {e}"
            print(message)
            try:
                writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Error writing log file: {e}")

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
            print("Executing query")
            cls.__myQuery.QueryExecute(
                instr= 'SELECT',
                where= where,
                db= database,
                tb= tb,
                col= col,
                outfile= path+outfile+counter+ext
                )
            print("Query executed")
        except Exception as e:
            message = f"Error creating Excel file: {e}"
            print(message)
            try:
                writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
            except Exception as e:
                print(f"Error writing log file: {e}")