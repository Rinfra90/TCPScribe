from datetime import datetime
import os

class LogWriter(object):

    def __init__(self,path= os.path.expanduser(os.path.join('~','AppData','Local','TCPScribe'))):
        try:
            os.makedirs(path,exist_ok=True)
        finally:
            pass
        self.path = path #  Path di salvataggio dei Log
        now = datetime.now()
        self.filecode = now.strftime("%Y%m%d") # Identificativo giornaliero per i file di Log

    def writeLog(self,Message,FileLog):
        now = datetime.now()
        date_time = now.strftime("%d/%m/%Y - %H:%M:%S")
        f = open(FileLog, "a", encoding='Windows-1252') #codifica per excel
        f.write("Data\hour " + date_time + "\n")
        f.write(Message)
        f.write("\n")
        f.close()