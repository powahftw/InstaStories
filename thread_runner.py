import logging
import time
import threading
import random
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class ThreadRunner():

    DEFAULT_SLEEP_TIME = 5
    DEFAULT_ATTEMPTS = 3

    def __init__(self, func, default_loop_delay_seconds, default_loop_variation_percentage):
        self.thread_running = False
        self.shutting_down = False  # Variable used to mark that after this iteration the Thread will be stopped.
        self.args = {}
        self.loop_args = {"loop_delay_seconds": default_loop_delay_seconds,
                          "loop_variation_percentage": default_loop_variation_percentage}
        self.output = {}
        self.func = func
        self.th = threading.Thread(target=self.runLoopedFunction, daemon=True)
        self.th.start()
        logger.info("Thread started")

    def waitFor(self):
        temp_loop_delay_seconds = int(self.loop_args["loop_delay_seconds"])
        loop_variation = temp_loop_delay_seconds * (int(self.loop_args["loop_variation_percentage"]) // 100)
        time_delay = temp_loop_delay_seconds + random.randint(-loop_variation, loop_variation)
        return time_delay

    def runLoopedFunction(self):
        while True:
            if self.thread_running:
                tries_left = self.DEFAULT_ATTEMPTS
                last_request_completed = False
                while tries_left > 0 and not last_request_completed:
                    try:
                        for output in self.func(**self.args):
                            self.output = output
                        last_request_completed = True
                    except Exception as err:
                        sleep_time = self.DEFAULT_SLEEP_TIME * (10 ** (self.DEFAULT_ATTEMPTS - tries_left))
                        logger.warning(f"Error occurred while trying to scrape, retrying after {sleep_time} secs. \
                                        \n Error: {err}")
                        time.sleep(sleep_time)
                        tries_left -= 1
                if not last_request_completed:
                    logger.warning("Thread stopped, error in trying to scrape users, please restart it")
                    self.shutting_down = True

                if self.shutting_down:
                    self.thread_running = False
                else:
                    time_to_sleep = self.waitFor()
                    time_next_cycle = (datetime.now() +
                                       timedelta(seconds=time_to_sleep) +
                                       timedelta(seconds=self.DEFAULT_SLEEP_TIME)).strftime("%Y/%m/%d, %H:%M:%S")
                    logger.info(f"Loop waiting for {time_to_sleep} seconds, next scrape will happen at {time_next_cycle}")
                    time.sleep(time_to_sleep)
            time.sleep(self.DEFAULT_SLEEP_TIME)

    def startFunction(self, keep_running=False):
        self.shutting_down = not keep_running
        logger.info(f"Thread function started {'in loop mode' if keep_running else 'in single mode'} ")
        self.thread_running = True

    def stopFunction(self):
        self.shutting_down = True
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
        # See the Instastories.py's "start_scrape" func for more details
        return self.output

    def getStatus(self):
        # Statuses: running, shutdown, stopped
        if self.thread_running:
            return "shutdown" if self.shutting_down else "running"
        else:
            return "stopped"
