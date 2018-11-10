
# CSC326 Lab 3

# Python script for running the crawler and the PageRank algorithm,
# and pretty prints PageRank scores in greatest-to-least PageRank sorted order

# Note: This script assumes that:
# urls.txt (containing a list of urls to be crawled) and pagerank.py is in the current directory

# See crawler.py for function implementations
from crawler import *
import pprint

if __name__ == "__main__":
    bot = crawler(None, "urls.txt")
    bot.crawl(depth=1)

    pprint.pprint(bot.get_sorted_pagerank())
    pprint.pprint(bot.get_sorted_pagerank_url())
