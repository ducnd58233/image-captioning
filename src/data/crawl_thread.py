import logging

from threading import Thread, Lock
from data.crawl_data import CrawlData
from config.log_custom import LogCustomFormatter

class CrawlThreadGroup:
    def __init__(self, num_thread, page_size):
        self.num_thread = num_thread
        self.page_size = page_size

    def run(self):
        page_start = 1
        page_end = page_start + self.page_size
        running_threads = []
        for i in range(self.num_thread):
            try:
                thread = CrawlThread(f'thread {i}', page_start, page_end)
                thread.start()
                running_threads.append(thread)
                page_start = page_end
                page_end = page_start + self.page_size
            except Exception as e:
                print(e)

        for running_thread in running_threads:
            running_thread.join()

class CrawlThread(Thread):
    def __init__(self, name, page_start, page_end):
        super(CrawlThread, self).__init__()
        self.logger = logging.getLogger(name)

        # create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        ch.setFormatter(LogCustomFormatter())

        self.logger.addHandler(ch)
        self.logger.setLevel(logging.INFO)
        self.name = name
        self.page_start = page_start
        self.page_end = page_end
        self.lock = Lock()

    def run(self):
        self.logger.info(self.name + " is starting...")
        process = CrawlData(self.name, self.logger, self.page_start, self.page_end, self.lock)
        process.run()
        self.logger.info(self.name + " DONE!")

