import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import schedule
import configparser
import os
import logging
from datetime import datetime;
from Classes.Query import Query
from Classes.DataReceiver import DataReceiver
from Classes.LogWriter import LogWriter
from Classes.DatabaseElements import *
from Routines import *

class TcpService (win32serviceutil.ServiceFramework):
    _svc_name_ = "TCPServer"
    _svc_display_name_ = "TCP Server"
    
    def __init__(self,args):

        #   Path definition for log and config file
        #   NOTE: when running a service, expanduser return "C:\Windows\System32\config\systemprofile"
        path = os.path.expanduser(os.path.join("~","AppData","Local","TcpServer"))

        #   Logs define
        self.infoLog = logging.getLogger("InfoLog")
        infoHandler = logging.FileHandler(filename= path+r"\Logs\ServiceInfoLog.log")
        infoFormatter = logging.Formatter("%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)", datefmt="%d-%m-%Y %H:%M:%S")
        infoHandler.setFormatter(infoFormatter)
        self.infoLog.addHandler(infoHandler)
        self.infoLog.setLevel(logging.INFO)
        self.warningLog = logging.getLogger("warningLog")
        warningHandler = logging.FileHandler(filename= path+r"\Logs\ServiceWarningLog.log")
        warningFormatter = logging.Formatter("%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)", datefmt="%d-%m-%Y %H:%M:%S")
        warningHandler.setFormatter(warningFormatter)
        self.warningLog.addHandler(warningHandler)
        self.warningLog.setLevel(logging.WARNING)
        self.errorLog = logging.getLogger("errorLog")
        errorHandler = logging.FileHandler(filename= path+r"\Logs\ServiceErrorLog.log")
        errorFormatter = logging.Formatter("%(asctime)s - %(module)s - %(name)s - %(levelname)s - %(message)", datefmt="%d-%m-%Y %H:%M:%S")
        errorHandler.setFormatter(errorFormatter )
        self.errorLog.addHandler(errorHandler)
        self.errorLog.setLevel(logging.ERROR)

        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        socket.setdefaulttimeout(60)
        self.stop_requested = False

        #   Define of ConfigParser object to read .cfg files
        config = configparser.ConfigParser()
        configpath = os.path.expanduser(os.path.join("~","AppData","Local","TcpServer"))
        configfile = configpath+"/config.cfg"
        #   If file does not exist, I define it to not run in error
        if not os.path.exist(configfile):
            self.infoLog.info(f"File {configfile} does not exist... Creating file...")
            try:
                config['NetAccess'] = {
                    'host': 'localhost',
                    'port': '3306'
                    }
                config['Credentials'] = {
                    'username': 'myuser',
                    'password': 'mypassword'
                    }
                config['Database'] = {
                    'name': 'mydb'
                    }
                self.infoLog.info("File creato")
            except Exception as e:
                self.errorLog.error(e)
        config.read(configfile)

        #   Get credentials loaded by config file
        self.__DBMSuser = config.get('Credentials', 'username')
        self.__DBMSpsw = config.get('Credentials', 'password')
        del config  #   Not necessary, but made for safety
                
    #   Service stop sequence
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.infoLog.info("Stopping service...")
        self.stop_requested = True

    #   Service starting sequence
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        try:
            self.main()
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {e}")
            os._exit(-1)

    def main(self):

        #   Routine to delete data older than 1 year
        Routines.setRoutine(host=self.__DBMSuser, psw=self.__DBMSpsw)

        writer = LogWriter()
        #   System variable setting
        count = 0 # Cycles executed
        
        config = configparser.ConfigParser()
        configpath = os.path.expanduser(os.path.join("~","AppData","Local","TcpServer"))
        configfile = configpath+"/config.cfg"
        if not os.path.exist(configfile):
            try:
                self.infoLog.info(f"Il file {configfile} does not exist...")
            except:
                print("Can't write log")
        config.read(configfile)
        
        #   Settings for DBMS (MariaDB) connection
        DBMShost = config.get('NetAccess', 'host')
        DBMSport = config.get('NetAccess', 'port')
        #   Define of Query object to connect to DBMS and execute queries
        myQuery = Query()

        myQuery.SetServer(newHost=DBMShost,newPort=DBMSport)

        dataReceiver = DataReceiver()

        #   Database creation
        database = config.get('Database', 'name')
        myQuery.QueryExecute(instr='CREATE',db=database)
        
        del config  #   Not necessary, but made for safety

        #   Tables creation
        #   Those are tables exemple. myDatabaseTable take variable number of arguments, but actually tables are defined in DatabaseElements.py.
        #   To change tables, change them there too.
        #   Actually, program work only with this structure
        Events = myDatabaseTable(
            database,
            'Events',
            'id',
            id= "INT NOT NULL AUTO_INCREMENT",
            data= "DATETIME NOT NULL",
            event= "VARCHAR(120) NULL",
            value= "VARCHAR(25) NULL",
            signalType= "ENUM('EVN','ALM','BLK','ERR') NOT NULL",
            FULLTEXT= "INDEX idx_evnt (event)",
            INDEX= "idx_data (data) USING BTREE"
            )
        Values = myDatabaseTable(
            database,
            'Values',
            'id',
            id= "INT NOT NULL AUTO_INCREMENT",
            data= "DATETIME NOT NULL",
            event= "VARCHAR(120) NULL",
            value= "DECIMAL(10, 2) NULL",
            unit= "VARCHAR(10) NULL",
            signalType= "ENUM('VLE') NOT NULL",
            FULLTEXT= "INDEX idx_evnt (event)",
            INDEX= "idx_data (data) USING BTREE"
            )
        Settings = myDatabaseTable(
            database,
            'Settings',
            'id',
            id= "INT NOT NULL AUTO_INCREMENT",
            data= "DATETIME NOT NULL",
            station= "VARCHAR(50) NULL",
            operator= "VARCHAR(50) NULL",
            event= "VARCHAR(120) NULL",
            value= "DECIMAL(10, 2) NULL",
            signalType= "ENUM('STG') NOT NULL",
            FULLTEXT= "INDEX idx_evnt (event)",
            INDEX= "idx_data (data) USING BTREE"
            )

        tables = [
            Events,
            Values,
            Settings
            ]

        for table in tables:
            myQuery.QueryExecute(instr='CREATE',db=database,tb=table)
            
        schedule.every().day.at('00:00').do(Routines.DeleteOldRecords,database,tables)
    
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y - %H:%M:%S")
        print ("---------- " +date_time + " The server is ready to receive ----------")
        try:
            writer.writeLog("---------- "+date_time+" The server is ready to receive ----------", writer.path + "Log_"+writer.filecode+".Log")
        except Exception as e:
            print(f"Error writing in log: {e}")
        ka = False

        while True:

            if self.stop_requested == True:
                break

            #Connection to sender
            try:
                print("Connecting to sender...")
                dataReceiver.ConnectionAccept()
                print("...connected!")

            except Exception as e:
                message = f"Sender connection error: {e}"
                print(message)
                try:
                    writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                except Exception as e:
                    print(f"Error writing in log: {e}")

            else:
                while True:
                    try:
                        schedule.run_pending()
                    except Exception as e:
                        message = f"Errore nell'eliminazione dei dati vecchi {e}"
                        print(message)
                        try:
                            writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                        except Exception as e:
                            print(f"Error writing in log: {e}")

                    if ka == False:
                        count += 1
                        print(f"Data reception attempt n. {count}...")

                    ka = False
            
                    finalBuffer = dataReceiver.ManageBuffer() #   Return list with buffer's data, 'ka' or False
                    
                    if finalBuffer == False: #   Return False if connection interrupt and need to reconnect
                        #   Communication interrupted, get back to connection phase
                        break

                    if finalBuffer == 'ka':
                        ka = True
                        continue

                    for response in finalBuffer:

                        if response == None:
                            continue

                        else:
                            try:
                                if type(response) == Value:
                                    myQuery.QueryExecute(
                                        instr='INSERT',
                                        db=database,
                                        tb=Values,
                                        data=response.data,
                                        event=response.event,
                                        value=response.value,
                                        unit=response.unit,
                                        signalType=response.signalType
                                        )
                                elif type(response) == Settings:
                                    myQuery.QueryExecute(
                                        instr='INSERT',
                                        db=database,
                                        tb=Settings,
                                        data=response.data,
                                        station=response.station,
                                        operator=response.operator,
                                        event=response.event,
                                        value=response.value,
                                        signalType=response.signalType)
                                else:
                                    myQuery.QueryExecute(
                                        instr='INSERT',
                                        db=database,
                                        tb=Events,
                                        data=response.data,
                                        event=response.event,
                                        value=response.value,
                                        signalType=response.signalType)
                            except Exception as e:
                                print(f"Error executing query: {e}")
                                try:
                                    writer.writeLog(f"Error executing query: {e}",writer.path + "ErrorLog_" + writer.filecode + ".Log")
                                except Exception as e:
                                    print(f"Error writing in log: {e}")

if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(TcpService)
