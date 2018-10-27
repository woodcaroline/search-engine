# search-engine
Search engine for CSC326.

# Server Information
Public IP Address: 54.166.117.231

To access the search engine, go to:
- http://54.166.117.231:8080, or alternatively,
- http://ec2-54-166-117-231.compute-1.amazonaws.com:8080

To start a new instance on AWS, run:
- python start_instance.py

To terminate an instance, run:
- python stop_instance.py

# Benchmarking

To monitoring application performance, run:
- ab -n 1000 -c 35 http://54.166.117.231:8080/?keywords=google

To monitoring resource utilization, run:
- dstat -c -m -d -r -n
- ab -n 1000 -c 35 http://54.166.117.231:8080/?keywords=google

See RESULT.txt for benchmark result

# Testing
To test crawler.py (modified for Lab 1), run:
- python test_crawler.py
