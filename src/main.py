from data.crawl_thread import CrawlThreadGroup

if __name__ == '__main__':
    CRAWL_DATA = True

    if CRAWL_DATA:
        PAGE_SIZE = 10
        NUM_THREAD = 50
        crawl_thread_group = CrawlThreadGroup(NUM_THREAD, PAGE_SIZE)
        crawl_thread_group.run()
