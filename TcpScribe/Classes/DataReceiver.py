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
        
    #   In case off errors Return:
    #       False - Host connection not present
    #       None - Data error
    #       'ka' - Keep Alive received
    #   Buffer structure:   NNNN[NEW]BUFFERDATA[NEW]BUFFERDATA
    #   Data structure: DATE TIME - EVENT[TYPE]
    #   Type of datas can be
    #       [ALV] - Keep Alive
    #       [EVN]/[ALM]/[BLK] - Events, alarms and blocked alarms
    #           Structure: DATE TIME - EVENT - VALUE[EVN/ALM/BLK]
    #       [VLE] - Values
    #           Structure: DATE TIME - EVENT - VALUE - UNIT[VLE]
    #           Values are only numbers
    #       [STG] - Settings
    #           Structure: DATE TIME - STATION - OPERATOR - EVENT - VALUE[STG]
    #           Values are not only numbers
    def ManageBuffer(self):
        
        writer = LogWriter()
        finalBuffer = []
        message = ''

        #   Buffer reception attempt
        try:
            bufferRecevedStr = self.RecvBuffer()

        except Exception as e:
            print(f"Host connection error: {e}'")
            return False

        else:
            #   Keep Alive management
            if bufferRecevedStr.find('[ALV]') != -1:
                self.dataReady = False
                return 'ka'

            bufferRecevedStr = bufferRecevedStr.replace('@','')

            self.receivedBytes = self.GetNByte(bufferRecevedStr)

            #   Buffer integrity check
            if self.receivedBytes > 0:
                self.dataReady = True
            
            print(f"Block bytes = {self.receivedBytes}")
            
            #   receivedBytes reset to not sthourge incorrect data
            self.receivedBytes = 0

            if self.dataReady:
                print("Processing data...")

                self.dataReady = False

                #   Find first [NEW] and get first data buffer
                bufferRecevedStr = bufferRecevedStr[bufferRecevedStr.find("[NEW]")+5:]

                #   Define listOfData containing data
                listOfData = bufferRecevedStr.split("[NEW]")
                
                #   Data interpretation one by one
                for receivedData in listOfData:
                    
                    noTag = False
                    VLEdata = False
                    STGdata = False

                    #   Data Type Check
                    #   VLE - Values / STG - Settings / EVN - Events / ALM - alarms / BLK - Blocked alarms / ERR - no type data
                    if receivedData.find("[VLE]") != -1:
                        VLEdata = True
                        Type = 'VLE' #  Database element
                    elif receivedData.find("[STG]") != -1 :
                        STGdata = True
                        Type = 'STG' #  Database element
                    elif receivedData.find("[EVN]") != -1 :
                        Type = 'EVN' #  Database element
                    elif receivedData.find("[ALM]") != -1 :
                        Type = 'ALM' #  Database element
                    elif receivedData.find("[BLK]") != -1 :
                        Type = 'BLK' #  Database element
                    else :
                        noTag = True
                        try:
                            message = "Nessun TAG rilevato. Lunghezza Stringa:"+str(len(receivedData))+'\n'+receivedData+'\n'
                        except Exception as e:
                            print(f"Log writing error: {e}")
                        print(message)
                        writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                        Type = 'ERR' #  Database element
                        
                    #   Tag remove
                    if not noTag :
                            receivedData = receivedData.replace(f"[{Type}]","")
                            
                    #   Date and message split
                    spaces = 0 # Spaces counter
                    iPos = 0 #  Split position indicator
                    for char in receivedData:
                        if spaces < 3 :
                            if char==" ":
                                spaces += 1
                            iPos +=1
                        else :
                            break

                    #   Store date and message in two different variables
                    strDate = receivedData[:iPos-1]
                    strMsg = receivedData[iPos:]

                    #   Date time split and formatting
                    dateTime = strDate.split(' - ')
                    date = dateTime[0].split('-')
                    year = date[2]
                    month = date[1]
                    day = date[0]
                    hour = dateTime[1]
                    dateTime = f"{year}-{month}-{day} {hour}"

                    event = strMsg #    Database element - assign it and modify it if value

                    if VLEdata:

                        print(strMsg)

                        fields = strMsg.split(' - ')
                        try:
                            writer.writeLog(message, writer.path+"Log_"+writer.filecode+".Log")
                        except Exception as e:
                            print(f"Log writing error: {e}")

                        if len(fields) == 2:
                            ValUnit = fields[1].split(" ")
                        elif len(fields) == 3 :
                            ValUnit = fields[1].split(" ")
                        elif len(fields) == 4 : 
                            ValUnit = fields[1]
                        else:
                            message = "*****ATTENTION !!! Field decode error*****,"+strMsg+"-- Fields number found: "+str(len(fields))+"\n"+receivedData+'\n'
                            print(message)
                            try:
                                writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Log writing error: {e}")
                            finalBuffer.append(None)
                        try:
                            recordData = Value(
                                date= dateTime,
                                event= fields[0],
                                value= ValUnit[0],
                                unit= ValUnit[1]
                                )
                            finalBuffer.append(recordData)
                        except Exception as e:
                            message = f"Error writing value: {e}\n"+receivedData+'\n'
                            print(message)
                            try:
                                writer.writeLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Log writing error: {e}")
                            finalBuffer.append(None)

                    elif STGdata:

                        print(strMsg)

                        fields = strMsg.split(' - ')

                        if len(fields) < 4:
                            message = "*****ATTENTION !!! Field decode error*****,"+strMsg+"-- Fields number found: "+str(len(fields))+receivedData+'\n'
                            print(message)
                            try:
                                writer.WriteLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                            except Exception as e:
                                print(f"Log writing error: {e}")
                        else:
                            tempMsg = fields[2:] #  Write message and value in TempMsg. Value is stored as last one.
                            tempValue = tempMsg[len(tempMsg)-1] #   Extract Value (Format: 'SET TO VALUE')
                            value = tempValue[7:]
                            #   Rejoin message
                            event = ' - '.join(tempMsg[:len(tempMsg)-1])
                            try:
                                recordData = Settings(
                                    date= dateTime,
                                    station= fields[0],
                                    operator= fields[1],
                                    event= event,
                                    value= value,
                                    )
                                finalBuffer.append(recordData)
                            except:
                                message = "*****ATTENTION !!! Field decode error*****,"+strMsg +"-- Fields number found: "+str(len(fields))+receivedData+'\n'
                                print(message)
                                try:
                                    writer.WriteLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                                except Exception as e:
                                    print(f"Log writing error: {e}")
                                finalBuffer.append(None)
                    
                    else:
                        fields = event.split(' - ')
                        event= ' - '.join(fields[:len(fields)-1])
                        value = fields[len(fields)-1]
                        if len(value)>25:
                            value = value[:25]
                    
                        recordData = Event(
                            date= dateTime,
                            event= event,
                            value= value,
                            signalType= Type
                            )
                        finalBuffer.append(recordData)
            else:
                message = "Inconsistent data possible loss of information"
                print(message)
                try:
                    writer.WriteLog(message, writer.path+"ErrorLog_"+writer.filecode+".Log")
                except Exception as e:
                    print(f"Log writing error: {e}")
                finalBuffer.append(None)

            return finalBuffer