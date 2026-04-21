import threading
import time

class Message_Queue:
    Queue=[]
    Mutex=threading.Lock()
    size=0

    def __init__(self):
        self.sending = False
        self.updated = time.time()

    def Enqueue(self, header, message):
        msg = {"HEADER": header,
               "MESSAGE": message}
        with self.Mutex:
            self.Queue.append(msg)
            self.size += 1
            self.updated = time.time()
    
    def Dequeue(self):
        message = None
        with self.Mutex:
            if self.size > 0:
                message = self.Queue.pop(0)
                self.size -= 1
                self.updated = time.time()
        return message            
    
    def Size(self):
        size = -1
        with self.Mutex:
            size = self.size
        return size
    
    def start_sending(self):
        self.sending = True
    
    def done_sending(self):
        self.sending = False
    
    def sending_status(self):
        return self.sending