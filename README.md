# review-scraper
Scraping User Reviews

### app-review-scraper.py

This file contains the code to scrap user reviews on any app in google play store.
Currently it is using `reviews` module of the library which allows to scrap limited user reviews. The library also provides `reviews_all` module which can be used to scrap all the user reviews.
Also we can provide different country and languages as parameters.

Packages required to run this file:
```
google-play-scraper==1.2.4
numpy==1.26.0
pandas==2.1.1
python-dateutil==2.8.2
pytz==2023.3.post1
six==1.16.0
tzdata==2023.3
```

Sample of CSV file that will get created:
<img width="949" alt="image" src="https://github.com/AakashSorathiya/review-scraper/assets/39656130/36033a86-547f-41bc-a5b8-7b13fe0de213">
