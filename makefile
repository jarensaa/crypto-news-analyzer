export PYTHONPATH := .

media-aggregator:
	python3 ./cryptoApp/social-media-aggregator/aggregator.py

media-scraper:
	python3 ./cryptoApp/social-media-scraper/scraper.py

media:
	python3 ./cryptoApp/social-media-runner.py

media+plot:
	python3 ./cryptoApp/social-media-runner.py --plot

media-noscrape:
	python3 ./cryptoApp/social-media-runner.py --noscrape

media-noscrape-plot:
	python3 ./cryptoApp/social-media-runner.py --noscrape --plot

corr:
	python3 ./cryptoApp/correlation-explorer.py

plot:
	python3 ./cryptoApp/timelinePlotter/plotter.py --plot

plot+build:
	python3 ./cryptoApp/correlation-explorer.py --plot

mathie1:
	python3 ./cryptoApp/utilityRunners/bitcoin1.py

mathie1-scrape:
	python3 ./cryptoApp/utilityRunners/bitcoin1.py --scrape

delete:
	python3 ./cryptoApp/deleter.py
