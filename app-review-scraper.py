import json
from typing import Union, Optional
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from time import sleep
from datetime import datetime
import re
import pandas as pd

PLAY_STORE_BASE_URL = "https://play.google.com"
REVIEWS = re.compile("\)]}'\n\n([\s\S]+)")

class Reviews:
    URL_FORMAT = (
        "{}/_/PlayStoreUi/data/batchexecute?rpcids=oCPfdb&source-path=/store/apps/details&f.sid=1030595262832404848&bl=boq_playuiserver_20231010.04_p1&hl={{lang}}&authuser=0&soc-app=121&soc-platform=1&soc-device=1&_reqid=745241&rt=c".format(
            PLAY_STORE_BASE_URL
        )
    )

    def build(self, lang: str, country: str) -> str:
        return self.URL_FORMAT.format(lang=lang, country=country)

##    f.req=[[["UsvDTd","[null,null,[2,{sort},[{count},null,null],null,[]],[\"{app_id}\",7]]",null,"generic"]]]
    PAYLOAD_FORMAT_FOR_FIRST_PAGE = "f.req=%5B%5B%5B%22UsvDTd%22%2C%22%5Bnull%2Cnull%2C%5B2%2C{sort}%2C%5B{count}%2Cnull%2Cnull%5D%2Cnull%2C%5B%5D%5D%2C%5B%5C%22{app_id}%5C%22%2C7%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D"

##    f.req=[[["UsvDTd","[null,null,[2,{sort},[{count},null,\"{pagination_token}\"],null,[]],[\"{app_id}\",7]]",null,"generic"]]]
    PAYLOAD_FORMAT_FOR_PAGINATED_PAGE = "f.req=%5B%5B%5B%22UsvDTd%22%2C%22%5Bnull%2Cnull%2C%5B2%2C{sort}%2C%5B{count}%2Cnull%2C%5C%22{pagination_token}%5C%22%5D%2Cnull%2C%5B%5D%5D%2C%5B%5C%22{app_id}%5C%22%2C7%5D%5D%22%2Cnull%2C%22generic%22%5D%5D%5D"

    def build_body(
        self,
        app_id: str,
        sort: int,
        count: int,
        filter_score_with: int,
        pagination_token: str,
    ) -> bytes:
        if pagination_token is not None:
            result = self.PAYLOAD_FORMAT_FOR_PAGINATED_PAGE.format(
                app_id=app_id,
                sort=sort,
                count=count,
                score=filter_score_with,
                pagination_token=pagination_token,
            )
        else:
            result = self.PAYLOAD_FORMAT_FOR_FIRST_PAGE.format(
                app_id=app_id, sort=sort, score=filter_score_with, count=count
            )

        return result.encode()

    def build_review(self, *args):
        raw_review=args[0]
        review={}
        review["content"] = raw_review[4]
        review["rating"] = raw_review[2]
        review["likes"] = raw_review[6]
        review["date"] = str(datetime.fromtimestamp(raw_review[5][0]))
##        review["replyContent"] = None if raw_review[7][1]==None else raw_review[7][1]
##        review["replyDate"] = None if raw_review[7][2][0]==None else datetime.fromtimestamp(raw_review[7][2][0])
        
        return review


def post(url: str, data: Union[str, bytes], headers: dict) -> str:
    request = Request(url, data=data, headers=headers)
    try:
        resp = urlopen(request)
    except HTTPError as e:
        raise Exception(
            "Status code {} returned.".format(e.code)
        )

    return resp.read().decode("UTF-8")

def _fetch_review_items(
    url: str,
    app_id: str,
    sort: int,
    count: int,
    filter_score_with: Optional[int],
    pagination_token: Optional[str],
):
    dom = post(
        url,
        Reviews.build_body(
            app_id,
            sort,
            count,
            "null" if filter_score_with is None else filter_score_with,
            pagination_token,
        ),
        {"content-type": "application/x-www-form-urlencoded"},
    )

##    print(dom)
    result=[]
    result+=REVIEWS.findall(dom)[0].splitlines()
##    print(result)
    match = json.loads(result[1])

    return json.loads(match[0][2])[0], json.loads(match[0][2])[-1][-1]


Reviews = Reviews()
url = Reviews.build(lang="en", country="us")
all_reviews=[]
p_token=None

while True:
    result=[]
    
    try:
        review_items, token = _fetch_review_items(
                        url, "com.ubercab", 2, 1000, None, p_token
                    )

        for review_i in review_items:
            result.append(Reviews.build_review(review_i))

    except (TypeError, IndexError):
        print("error", p_token)
        token=None

    all_reviews+=result
    print("fetched 1000")
    
    if token is None:
        break
    else:
        p_token=token


##print(review_items[0])
##print(all_reviews)
##print(token)

df_reviews = pd.DataFrame(all_reviews)
df_reviews.to_csv("reviews.csv")
