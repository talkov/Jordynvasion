import time
class Timer():
    def __init__(self,howMuchTime):
        self.for_sec = howMuchTime
        self.start_time = 0

    def start_timer(self):
        self.start_time = time.time()

    def timer(self):
        if int(time.time() - self.start_time) == self.for_sec:
            return False
        else:
            return True

    def activate(self,on_or_off,buff_still_on):
        #if the input is 1 activate timer
        if on_or_off:
            self.start_timer()
            while self.timer():
                buff_still_on = True
                return True
            buff_still_on = False
            return False
        else:
            self.for_sec = 0