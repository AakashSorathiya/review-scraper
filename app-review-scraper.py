import pandas as pd
import numpy as np
from google_play_scraper import app, Sort, reviews

result, continuation_token = reviews(
    'com.ubercab',
    lang='en', # defaults to 'en'
    country='us', # defaults to 'us'
    sort=Sort.NEWEST, # defaults to Sort.NEWEST
    count=50, # defaults to 100
)

df_reviews = pd.DataFrame(np.array(result),columns=['review'])
df_reviews = df_reviews.join(pd.DataFrame(df_reviews.pop('review').tolist()))

print(df_reviews.head())

df_reviews.to_csv("reviews.csv")
