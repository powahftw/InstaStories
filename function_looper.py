import time
import threading

class ThreadRunner():

    def __init__(self, func):
        self.loop_running = True
        self.thread_running = False
        self.once = False
        self.args = {}
        self.output = {}
        self.func = func
        self.th = threading.Thread(target=self.runLoopedFunction, daemon=True)
        self.th.start()

    def runLoopedFunction(self):
        while self.loop_running:
            time.sleep(1)
            if self.thread_running:
                self.output = self.func(**self.args)
                if self.once:
                    self.thread_running = False

    def startFunction(self, once=False):
        self.once = once
        self.thread_running = True

    def stopFunction(self):
        self.thread_running = False

    def updateFuncArg(self, **kwargs):
        self.args = kwargs
        return self

    def getOutput(self):
        return self.output

    def stop(self):
        self.loop_running = False
