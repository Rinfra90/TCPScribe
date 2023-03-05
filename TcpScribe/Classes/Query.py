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
        self.connDb = connDb    #   Used to verify if db connection is needed to execut a query

    @classmethod
    def SetServer(cls,newHost,newPort):
        cls.__host = newHost
        cls.__port = newPort

    @classmethod
    def GetServer(cls):
        print(f"Host: {cls.__host}")
        print(f"Port: {cls.__port}")
        
    @classmethod
    def SetCredential(cls,newUser,newPassword,oldPassword=''):
        cls.__user = newUser
        if oldPassword == cls.__psw:
            cls.__psw = newPassword
        else:
            print("Password not changed. Old password inconsistent")

    @classmethod
    def GetCredential(cls):
        print(f"User: {cls.__user}")
        if cls.__psw != '':
           print("Password set")
        else:
            print("Password not set")

    @staticmethod
    def Info():
        print("""---------------------------------------------------
Instructions
---------------------------------------------------
Class Query:
Variables:  __host
            __port
            __user
            __psw
Settable and gettable using those methods:
SetCredential(newUser,newPassword,oldPassword),
GetCredential(),
SetServer(newHost,newPort),
GetServer()
---------------------------------------------------
Info():
Info about class and how to use it
---------------------------------------------------
QueryExecute(instr,where,db,tb,col,engine,doubleCheck,pers,**val)
---------------------------------------------------
instr - Allowed instructions 'SELECT','DROP','CREATE', 'INSERT' and 'DELETE'
--------------------------
pers - Used to send personalized query. Insert full text into 'instr'
doubleCheck - Used to check if 'IF NOT EXISTS' is needed in table and database creation
--------------------------
SELECT:
db - Identify the database to connect to
col - Column to search for
tb - Identify the tables to query
where - Insert where conditions here
--------------------------
DROP:
tb - If empty, database get delete
db - Database to be deleted or table's database to be deleted
--------------------------
CREATE:
tb - If empty, create database
db - Database to be created or table's database to be created
**val - Additional arguments to define table structure
        Format VARNAME = 'PROPERTY'
        example:
        id = "NOT NULL AUTO_INCREMENT"
        Result:
        id NOT NULL AUTO_INCREMENT
engine - 'InnoDb' by default
--------------------------
INSERT:
db - Database to insert data in
tb - Table to insert data in
**val - Additional arguments to define fields and values to insert
        Field format = 'VALUE'
        example:
        Values='2'
        Insert new element into table tb with value '2' in 'Values' field
---------------------------------------------------""") 
        
    #   Method to analyze data integrity. Return full query or False if incorrect data
    def __CheckQuery(self, **args):

        check = False   #   Uesd to verify query integrity

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

        #   Check if personalized query then execute it
        if pers:
            if self.instr[-1] != ';':
                self.instr = self.instr + ';'
            return self.instr

        else:
            if self.db != '':
                #   Identify presetted instruction
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
                            sendQuery = "CREATE TABLE " + doubleCheck + f"{self.tb.name}\n(\n"
                            
                            if self.tb.fields.values():

                                checkKey = False
                            
                                for key, value in self.tb.fields.items():
                                    sendQuery = sendQuery + f"{key} {value}" + ",\n"
                                    if self.tb.priKey == key:
                                        checkKey = True

                                if self.tb.priKey != '':
                                    if checkKey:
                                        sendQuery = sendQuery + f"PRIMARY KEY ({self.tb.priKey})\n)\n"
                                        sendQuery = sendQuery + f"ENGINE = {self.tb.engine};"
                                        check = True
                                    else:
                                        print(f"Error executing query {self.instr.upper()}: Key does not match any value")
                                        return False
                                else:
                                    print(f"Error executing query {self.instr.upper()}: Specify primary key of the table")
                                    return False
            
                else:
                    if self.instr.upper() == 'DROP':
                        if self.tb == '*':
                            sendQuery = f"DROP DATABASE {self.db};"
                            check = True
                            self.connDb = False
                        else:
                            sendQuery = f"DROP TABLE {self.tb.name};"
                            check = True

                    else:
                        tbNames = ''

                        if type(self.tb) == tuple or type(self.tb) == list:
                            for table in self.tb:
                                if type(table) == myDatabaseTable:
                                    if tbNames == '':
                                        tbNames = table.name
                                    else:
                                        tbNames += ', ' + table.name
                                elif type(table) == str:
                                    if tbNames == '':
                                        tbNames = table
                                    else:
                                        tbNames += ', ' + table
                        elif type(self.tb) == myDatabaseTable:
                            tbNames = self.tb.name
                        else:
                            tbNames = self.tb

                        if type(self.col) == tuple or type(self.col) == list:
                            self.col = ", ".join(self.col)
                        if not type(self.col) == str:
                            print('Error columns format')
                            return False

                        if self.instr.upper() == 'SELECT':
                            sendQuery = "SELECT {} FROM {}".format(self.col,tbNames)
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
                                sendQuery = "INSERT INTO {} ({})\nVALUES ('{}');".format(tbNames,keys,vals)
                                check = True
                            else:
                                print(f"Error executing query {self.instr.upper()}: Values da inserire non specificati")
                                return False

                        elif self.instr.upper() == 'DELETE':
                            sendQuery = f"DELETE FROM {tbNames}"
                            if self.where != '':
                                sendQuery = sendQuery + f"\nWHERE {self.where}"
                            sendQuery = sendQuery + ';'
                            check = True
            else:
                print(f"Error executing query {self.instr.upper()}: database required")
                return False
                
            if check:
                return sendQuery
            else:
                print(f"Query {sendQuery} not executed")
                return False

    #   Method to reformat query's result string to print it clearely
    def __FormatTable(self, header, tb):

        lengths = []
        table = []
        if type(header) == tuple:
            newCol = []
            for el in header:
                newCol.append(el)
            header = newCol
        elif type(header) == str:
            header = header.split(',')

        table.append(header)
        nCol = 0
        for el in header:
            lengths.append(len(el))
            nCol += 1
        
        for row in tb:
            c = 0
            while c < nCol:
                if len(row[c]) > lengths[c]:
                    lengths[c] = len(row[c])
                c += 1
            table.append(row)

        formatHeader = '+'

        c = 0
        for el in header:
            i = 0
            while i <= lengths[c]:
                formatHeader += "-"
                i += 1
            formatHeader += "-+"
            c += 1

        outTable = []
        outTable.append(formatHeader)

        r=0
        for row in table:
            c = 0
            for el in row:
                while len(table[r][c]) < lengths[c]:
                    table[r][c] += ' '
                c += 1
            r += 1
            row = '| ' + ' | '.join(row) + ' |'
            outTable.append(row)
            if r == 1:
                outTable.append(formatHeader)
        
        outTable.append(formatHeader)
        return outTable

    #   Method to call to execute query
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
                print(f"Error connecting to MariaDB: '{e}'")
            else:
                try:
                    cursor = dbms.cursor()
                    cursor.execute(qy)
                    dbms.commit()
                    try:
                        for row in cursor:
                            extract = []
                            for el in row:
                                extract.append(str(el))
                            output.append(extract)

                        print("Data acquired...")
                        print("...Formatting visualization...")
                        
                        if col == '*':
                            if type(self.tb) == tuple or type(self.tb) == list:
                                for table in self.tb:
                                    if type(table) == myDatabaseTable:
                                        tbNames += "', '" + table.name
                                    elif type(table) == str:
                                        tbNames += "', '" + table
                            elif type(self.tb) == myDatabaseTable:
                                tbNames = self.tb.name
                            else:
                                tbNames = self.tb
                            qy = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='{tbNames}'"
                            cursor.execute(qy)
                            dbms.commit()
                            col=[]
                            for row in cursor:
                                col.append(row[0])

                        #   Method to format table to print it
                        #   To get result instead of print it, take output variable
                        formattedTable = self.__FormatTable(col,output)

                        for row in formattedTable:
                            print(row)

                    except:
                        try:
                            if not output == []:
                                print(output)
                            else:
                                pass
                        except Exception as e:
                            print(f"Output error: {e}")
                except mariadb.Error as e:
                    print(f"Error executing query: {e}\n{qy}")
                finally:
                    dbms.close()

        self.connDb = True

        if output == []:
            return
        else:
            return output