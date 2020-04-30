import time
import threading
import random

class ThreadRunner():

    def __init__(self, func, default_loop_delay, default_loop_variation):
        self.thread_running = False
        self.once = False
        self.args = {}
        self.loop_args = {"loop_delay": default_loop_delay, "loop_variation": default_loop_variation}
        self.output = {}
        self.func = func
        self.th = threading.Thread(target=self.runLoopedFunction, daemon=True)
        self.th.start()

    def runLoopedFunction(self):
        while True:
            loop_variation = int(self.loop_args["loop_delay"] * (self.loop_args["loop_variation"] / 100))
            time_delay = self.loop_args["loop_delay"] + random.randint(-loop_variation, loop_variation)
            time.sleep(time_delay)
            if self.thread_running:
                self.output = self.func(**self.args)
                if self.once:
                    self.thread_running = False

    def startFunction(self, once=False):
        self.once = once
        self.thread_running = True

    def stopFunction(self):
        self.thread_running = False

    def updateDelay(self, **kwargs):
        self.loop_args = kwargs
        return self

    def updateFuncArg(self, **kwargs):
        self.args = kwargs
        return self

    def getOutput(self):
        return self.output
