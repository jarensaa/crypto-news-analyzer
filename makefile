export PYTHONPATH := .

media-aggregator:
	python3 ./cryptoApp/social-media-aggregator/aggregator.py

media-scraper:
	python3 ./cryptoApp/social-media-scraper/scraper.py

media:
	python3 ./cryptoApp/social-media-runner.py

media+plot:
	python3 ./cryptoApp/social-media-runner.py --plot

plot:
	python3 ./cryptoApp/timelinePlotter/plotter.py --plot

