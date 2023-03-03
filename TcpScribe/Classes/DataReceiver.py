#   Socket required to connect to sender
from socket import *
from .LogWriter import LogWriter
from .DatabaseElements import Event, Value, Settings

class DataReceiver(object):
    
    def __init__(self, port=9100):
        #   TCP socket creation, bind execution and set to passive mode
        self.serverPort=port
        self.serverSocket = socket(AF_INET,SOCK_STREAM)
        self.serverSocket.bind(('',self.serverPort))
        self.serverSocket.listen(1)
        #   Reception variables and buffer's data interpretation
        self.dataReady = False  #   Required to verify reliability of data
        self.receivedBytes = 0 # Received bytes count
        self.connSocket = socket
    
    def RecvBuffer(self):
        lenghtBuffer = 3900 #   Buffer max lenght
        bufferData = ''
        while len(bufferData) < lenghtBuffer:
            partData = self.connSocket.recv(lenghtBuffer-len(bufferData))
            if partData == '' :
                writer = LogWriter()
                writer.writeLog("Connection interrupted. Received " + str(len(bufferData))+" of " + str(lenghtBuffer),writer.path + "ErrorLog_" + writer.filecode + ".Log") 
            bufferData = bufferData + partData.decode("latin1")
        return bufferData

    #   Buffer structure:   NNNN[NEW]BUFFERDATA[NEW]BUFFERDATA
    def GetNByte(self, buffer):
        
        startData = buffer.find("[NEW]")    #   find first [NEW]
        byteNumStr = buffer[:startData] #   Extract bytes number
    
        #   String integrity check
        if len(byteNumStr) > 0 :
            #   Check of chars until tag
            allCharIsNumeric = True
            for Char in byteNumStr:
                if not Char.isnumeric() :
                    allCharIsNumeric = False
                    break
                
            if allCharIsNumeric :
                return int(byteNumStr)
            else:
                return 0

        else :
            return 0

    def ConnectionAccept(self):
        self.connSocket, self.addr = self.serverSocket.accept()

    #   ManageBuffer() - Elabora ed interpreta il buffer
    #   Return classi Evento, Valore, Settaggio
    #   In caso di errori, Return:
    #       False - Connessione con l'host non presente
    #       None - Errore con i dati
    #       'ka' - Ricevuto Keep Alive
    #   Struttura Buffer:   NNNN[NEW]DATIBUFFER[NEW]DATIBUFFER
    #   Struttura dati: DATA ORA - EVENTO[TIPO]
    #   I tipi di dati possono essere
    #       [ALV] - Keep Alive
    #       [EVN]/[ALM]/[BLK] - Eventi, allarmi ed allarmi bloccati
    #           Struttura: DATA ORA - EVENTO - VALORE[EVN/ALM/BLK]
    #       [VLE] - Valori
    #           Struttura: DATA ORA - EVENTO - VALORE - UNITA'[VLE]
    #           I valori sono solo numeri
    #       [STG] - Settaqggi
    #           Struttura: DATA ORA - STAZIONE - OPERATORE - EVENTO - VALORE[STG]
    #           I valori non sono solo numeri
    def ManageBuffer(self):
        
        writer = LogWriter()
        finalBuffer = []
        messaggio = ''

        #   Tentativo di ricezione del buffer
        try:
            bufferRecevedStr = self.RecvBuffer()

        except Exception as e:
            print(f"Errore nella connessione all'host: {e}'")
            return False

        else:
            #   Gestione del Keep Alive
            if bufferRecevedStr.find('[ALV]') != -1:
                self.dataReady = False
                return 'ka'

            bufferRecevedStr = bufferRecevedStr.replace('@','')

            self.receivedBytes = self.GetNByte(bufferRecevedStr)

            #   Controllo che il buffer sia arrivato integro
            if self.receivedBytes > 0:
                self.dataReady = True
            
            print(f"Byte del blocco = {self.receivedBytes}")
            
            #   Azzerp byteRicevuti per evitare numeri in memoria non corretti
            self.receivedBytes = 0

            if self.dataReady:
                print("Elaboro i dati...")

                self.dataReady = False

                #   Trovo il primo [NEW] (escludendo il numero di byte) e prendo solo il buffer di dati
                bufferRecevedStr = bufferRecevedStr[bufferRecevedStr.find("[NEW]")+5:]

                #   Creo una lista listOfData contenente i vari dati
                listOfData = bufferRecevedStr.split("[NEW]")
                
                #   Interpreto i dati ad uno ad uno
                for dataRicevuto in listOfData:
                    
                    noTag = False
                    VLEdata = False
                    STGdata = False

                    #   Verifico il Tipo del dato
                    #   VLE - Valori / STG - Settaggi / EVN - Eventi / ALM - Allarmi / BLK - Blocchi / ERR - Dati senza tipo
                    if dataRicevuto.find("[VLE]") != -1:
                        VLEdata = True
                        Type = 'VLE' #  Dato per database
                    elif dataRicevuto.find("[STG]") != -1 :
                        STGdata = True
                        Type = 'STG' #  Dato per database
                    elif dataRicevuto.find("[EVN]") != -1 :
                        Type = 'EVN' #  Dato per database
                    elif dataRicevuto.find("[ALM]") != -1 :
                        Type = 'ALM' #  Dato per database
                    elif dataRicevuto.find("[BLK]") != -1 :
                        Type = 'BLK' #  Dato per database
                    else :
                        noTag = True
                        try:
                            messaggio = "Nessun TAG rilevato. Lunghezza Stringa:"+str(len(dataRicevuto))+'\n'+dataRicevuto+'\n'
                        except Exception as e:
                            print(f"Errore nella scrittura su log: {e}")
                        print(messaggio)
                        writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                        Type = 'ERR' #  Dato per database
                        
                    #   Rimuovo il tag
                    if not noTag :
                            dataRicevuto = dataRicevuto.replace(f"[{Type}]","")
                            
                    #   Separo data e messaggio
                    spazi = 0 # Contatore di spazi
                    iPos = 0 #  Indicatore della posizione di divisione
                    for carattere in dataRicevuto:
                        if spazi < 3 :
                            if carattere==" ":
                                spazi += 1
                            iPos +=1
                        else :
                            break

                    #   Scrivo su due variabili separate la data e il messaggio
                    strDate = dataRicevuto[:iPos-1]
                    strMsg = dataRicevuto[iPos:]

                    #   Divisione e riformattazione data e ora
                    dataTempo = strDate.split(' - ')
                    data = dataTempo[0].split('-')
                    anno = data[2]
                    mese = data[1]
                    giorno = data[0]
                    ora = dataTempo[1]
                    dataTempo = f"{anno}-{mese}-{giorno} {ora}"

                    event = strMsg #    Dato per database - Lo registro adesso e poi lo modifico in caso di valore

                    if VLEdata:

                        print(strMsg)

                        fields = strMsg.split(' - ')
                        try:
                            writer.writeLog(messaggio, writer.path+"Log_"+writer.filecode+".Log")
                        except Exception as e:
                            print(f"Errore nella scrittura su log: {e}")

                        if len(fields) == 2:
                            ValUnit = fields[1].split(" ")
                        elif len(fields) == 3 :
                            ValUnit = fields[1].split(" ")
                        elif len(fields) == 4 : 
                            ValUnit = fields[1]
                        else:
                            messaggio = "*****ATTENZIONE !!! Errore Decode Campi*****,"+strMsg+"-- Numero campi trovati: "+str(len(fields))+"\n"+dataRicevuto+'\n'
                            print(messaggio)
                            try:
                                writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Errore nella scrittura su log: {e}")
                            finalBuffer.append(None)
                        try:
                            recordData = Value(
                                data= dataTempo,
                                event= fields[0],
                                value= ValUnit[0],
                                unit= ValUnit[1]
                                )
                            finalBuffer.append(recordData)
                        except Exception as e:
                            messaggio = f"Errore nella scrittura del valore: {e}\n"+dataRicevuto+'\n'
                            print(messaggio)
                            try:
                                writer.writeLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Errore nella scrittura su log: {e}")
                            finalBuffer.append(None)

                    elif STGdata:

                        print(strMsg)

                        fields = strMsg.split(' - ')

                        if len(fields) < 4:
                            messaggio = "*****ATTENZIONE !!! Errore Decode Campi*****,"+strMsg+"-- Numero campi trovati: "+str(len(fields))+dataRicevuto+'\n'
                            print(messaggio)
                            try:
                                writer.WriteLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Errore nella scrittura su log: {e}")
                        else:
                            tempMsg = fields[2:] #  Scrivo i vari pezzi del messaggio e il valore in TempMsg. Il valore finisce sull'ultimo valore.
                            tempValue = tempMsg[len(tempMsg)-1] #   Estrapolo il valore dall'ultimo set di TempMsg (Formattato cos�: 'SET TO VALORE')
                            value = tempValue[7:]
                            #   Ricompatto il messaggio
                            event = ' - '.join(tempMsg[:len(tempMsg)-1])
                            try:
                                recordData = Settings(
                                    data= dataTempo,
                                    station= fields[0],
                                    operator= fields[1],
                                    event= event,
                                    value= value,
                                    )
                                finalBuffer.append(recordData)
                            except:
                                messaggio = "*****ATTENZIONE !!! Errore Decode Campi*****,"+strMsg +"-- Numero campi trovati: "+str(len(fields))+dataRicevuto+'\n'
                                print(messaggio)
                                try:
                                    writer.WriteLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                                except Exception as e:
                                    print(f"Errore nella scrittura su log: {e}")
                                finalBuffer.append(None)
                    
                    else:
                        fields = event.split(' - ')
                        event= ' - '.join(fields[:len(fields)-1])
                        value = fields[len(fields)-1]
                        if len(value)>25:
                            value = value[:25]
                    
                        recordData = Event(
                            data= dataTempo,
                            event= event,
                            value= value,
                            signalType= Type
                            )
                        finalBuffer.append(recordData)
            else:
                messaggio = "Dati incoerenti possibile perdita di informazioni"
                print(messaggio)
                try:
                    writer.WriteLog(messaggio, writer.path+"ErrorLog_"+writer.filecode+".Log")
                except Exception as e:
                    print(f"Errore nella scrittura su log: {e}")
                finalBuffer.append(None)

            return finalBuffer