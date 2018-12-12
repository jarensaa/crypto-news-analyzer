import copy

BITCOIN = "BTC"
ETHEREUM = "ETH"

COINS = [BITCOIN, ETHEREUM]

cryptocurrencies = dict()

cryptocurrencies[BITCOIN] = {
    "tag": "bitcoin",
    "fromTime": "",
    "toTime": "",
    "subreddits": [
        {
            "subreddit": "CryptoCurrency",
            "keywords": "bitcoin,BTC"
        },
        {
            "subreddit": "bitcoin",
            "keywords": ""
        }
    ]
}

cryptocurrencies[ETHEREUM] = {
    "tag": "ethereum",
    "fromTime": "",
    "toTime": "",
    "subreddits": [
        {
            "subreddit": "CryptoCurrency",
            "keywords": "Ethereum,ETH"
        },
        {
            "subreddit": "ethereum",
            "keywords": ""
        },
        {
            "subreddit": "ethtrader",
            "keywords": ""
        }
    ]
}


def generateCoinScrapingData(coin, fromTime, toTime):
    if(coin not in COINS):
        print("The coin {} is not supported.".format(coin))
        quit(1)

    scrapingData = copy.deepcopy(cryptocurrencies[coin])
    scrapingData["fromTime"] = fromTime
    scrapingData["toTime"] = toTime

    return scrapingData
