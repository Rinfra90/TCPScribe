class myDatabaseTable(object):

    def __init__(self, database, name, priKey, engine='InnoDB', **args):
        self.database = database
        self.name = name
        self.priKey = priKey
        self.engine = engine
        self.fields = {}
        for k,v in args.items():
            self.fields[k] = v

class Event(object):

    lastid = 0

    def __init__(self, date, event, value, signalType=''):
        Event.lastid += 1
        self.id = Event.lastid
        self.date = date
        self.event = event
        self.value = value
        self.signalType = signalType
    
class Value(Event):

    def __init__(self, date, event, value, unit):
        super().__init__(date,event,value)
        self.unit = unit
        self.signalType = 'VLE'

class Settings(Event):

    def __init__(self, date, station, operator, event, value):
        super().__init__(date,event,value)
        self.station = station
        self.operator = operator
        self.signalType = 'STG'