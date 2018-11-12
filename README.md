# search-engine
Search engine for CSC326.

# Server Information (for Lab 2)
Public IP Address: 54.166.117.231

To access the search engine, go to:
- http://54.166.117.231:8080, or alternatively,
- http://ec2-54-166-117-231.compute-1.amazonaws.com:8080

# Server Information (for Lab 3)
Public IP Address: 23.22.70.105

To access the search engine, go to:
- http://23.22.70.105:8080, or alternatively,
- http://ec2-23-22-70-105.compute-1.amazonaws.com:8080

To start a new instance on AWS, run:
- python start_instance.py

To terminate an instance, run:
- python stop_instance.py

# Benchmarking (for Lab 2)

To monitoring application performance, run:
- ab -n 1000 -c 35 http://54.166.117.231:8080/?keywords=google

To monitoring resource utilization, run:
- dstat -c -m -d -r -n
- ab -n 1000 -c 35 http://54.166.117.231:8080/?keywords=google

# Benchmarking (for Lab 3)

To monitoring application performance, run:
- ab -n 1000 -c 35 http://23.22.70.105:8080/?keywords=google

To monitoring resource utilization, run:
- dstat -c -m -d -r -n
- ab -n 1000 -c 35 http://23.22.70.105:8080/?keywords=google

See RESULT.txt for benchmark result

# Running the Backend

To run the crawler and the PageRank algorithm, run: 
- python run_backend_test.py

This script crawls the URLs in urls.txt, generates a PageRank score for each URL, and stores information such as lexicon, inverted index, PageRank scores, and document index in a SQLite data file named 'dbFile.db'. To get the search results for a keyword, run the following commands in python (make sure that crawler.py, pagerank.py, and dbFile.db are in your current directory): 
- from crawler import *
- search_results = get_results_db(search_word)

That's it! Note that get_results_db() returns a list of tuples, each containing (URL, page title, page description). 

# Testing
To test crawler.py (modified for Lab 1), run:
- python test_crawler.py
