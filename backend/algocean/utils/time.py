import datetime

def isoformat2datetime(isoformat:str):
    dt, _, us = isoformat.partition(".")
    dt = datetime.datetime.strptime(dt, "%Y-%m-%dT%H:%M:%S")
    us = int(us.rstrip("Z"), 10)
    dt = dt + datetime.timedelta(microseconds=us)
    assert isinstance(dt, datetime.datetime)
    return dt

def isoformat2timestamp(isoformat:str, return_type='int'):
    supported_types = ['int', 'float']
    assert return_type in supported_types, f'return type should in {supported_types} but you put {return_type}'
    dt = isoformat2datetime(isoformat)
    timestamp = eval(return_type)(dt.timestamp())
    assert isinstance(timestamp, int)
    return timestamp


def timedeltatimestamp( **kwargs):
    assert len(kwargs) == 1
    supported_modes = ['hours', 'seconds', 'minutes', 'days']
    mode = list(kwargs.keys())[0]
    assert mode in supported_modes, f'return type should in {supported_modes} but you put {mode}'
    
    current_timestamp = datetime.datetime.utcnow()
    timetamp_delta  =  current_timestamp.timestamp() -  ( current_timestamp- datetime.timedelta(**kwargs)).timestamp()
    return timetamp_delta


class Timer:
    supported_modes = ['second', 'timestamp']


    def __init__(self, start=False):
        self.start_time = None
        self.end_time = None
        if start:
            self.start()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.stop()
    
    def start(self):
        assert self.start_time == None, f'You already started the timer at {self.start_time}'
        
        self.start_time = self.current_time


    @staticmethod
    def get_current_time():
        return datetime.datetime.utcnow()

    @property
    def current_time(self):
        return self.get_current_time()

    def elapsed_time(self, return_type='seconds'):
        div_factor = 1
        if return_type in ['microseconds', 'ms', 'micro', 'microsecond']:
            div_factor = 1
        elif return_type in ['seconds', 's' , 'second', 'sec']:
            div_factor = 1000
        
        elif return_type in ['minutes', 'm', 'min' , 'minutes']: 
            div_factor = 1000*60
        
        else:
            raise NotImplementedError
        
        timestamp_period =  (self.current_time -self.start_time).microseconds/div_factor
        return timestamp_period

    def stop(self):
        self.end_time = None
        self.start_time = None
