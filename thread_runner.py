import logging
import time
import threading
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ThreadRunner():

    DEFAULT_SLEEP_TIME = 5

    def __init__(self, func, default_loop_delay_seconds, default_loop_variation_percentage):
        self.thread_running = False
        self.once = False
        self.args = {}
        self.loop_args = {"loop_delay_seconds": default_loop_delay_seconds,
                          "loop_variation_percentage": default_loop_variation_percentage}
        self.output = {}
        self.func = func
        self.th = threading.Thread(target=self.runLoopedFunction, daemon=True)
        self.th.start()
        logger.info("Thread started")

    def waitFor(self):
        loop_variation = int(self.loop_args["loop_delay_seconds"] * (self.loop_args["loop_variation_percentage"] / 100))
        time_delay = self.loop_args["loop_delay_seconds"] + random.randint(-loop_variation, loop_variation)
        return time_delay

    def runLoopedFunction(self):
        while True:
            if self.thread_running:
                self.output = self.func(**self.args)
                if self.once:
                    self.thread_running = False
                else:
                    time_to_sleep = self.waitFor()
                    time_next_cycle = (datetime.now() +
                                       timedelta(seconds=time_to_sleep) +
                                       timedelta(seconds=self.DEFAULT_SLEEP_TIME)).strftime("%Y/%m/%d, %H:%M:%S")
                    logger.info(f"Loop waiting for {time_to_sleep} seconds, next scrape will happen at {time_next_cycle}")
                    time.sleep(time_to_sleep)
            time.sleep(self.DEFAULT_SLEEP_TIME)

    def startFunction(self, once=False):
        self.once = once
        logger.info(f"Thread function started {'in single mode' if once else 'in loop mode'} ")
        self.thread_running = True

    def stopFunction(self):
        self.thread_running = False
        logger.info("Thread function stopped")

    def updateDelay(self, **kwargs):
        self.loop_args = kwargs
        logger.info(f"Updated delay: {kwargs}")
        return self

    def updateFuncArg(self, **kwargs):
        self.args = kwargs
        logger.info(f"Updated function params: {kwargs}")
        return self

    def getOutput(self):
        return self.output

    def getStatus(self):
        if self.thread_running:
            return f"RUNNING - Loop mode: {not self.once}  - Media scraping mode: {self.args['media_mode']} - Ids source: {self.args['ids_source']}"
        else:
            return "STOPPED"
