# thats the code that need to be improved
from bs4 import BeautifulSoup
import requests
import urllib
import pandas as pd
from openpyxl import load_workbook
import numpy
import random
from random import choice
import time
import datetime
import investpy as inp
import csv
import os

CWD = os.getcwd()

bot_key = "bot_key"
TOKEN = ""
URL2 = "https://api.telegram.org/bot{}/".format(bot_key)  # bot key
USERNAME_BOT = ""

chat_id = "chat_id"  # your chat id


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def echo_all(updates):  # to handle bot requests it is needed to be here
    for update in updates["result"]:
        if update.get("message") != None:
            if update.get("message", {}).get("text") != None:
                text = update["message"]["text"]
                chat = update["message"]["chat"]["id"]
                print(text)

                if text == "/test" or text == "/test@" + USERNAME_BOT:  # send message by recieving
                    text = "test response"
                    send_message(text, chat)
                elif text == "/start" or text == "/start@" + USERNAME_BOT:
                    send_message("/test for test the bot", chat)


def send_message(text, chat_id):  # that function is for sending messages
    tot = urllib.parse.quote_plus(text)
    url = URL2 + "sendMessage?text={}&chat_id={}".format(tot, chat_id)
    get_url(url)


def coins_df():
    first50 = inp.get_cryptos_overview()[0:49][["name", "symbol", "price"]]  # load top 50 coins

    crypto_df = pd.read_csv(CWD + "/cryptos.csv", usecols=["name",
                                                           "id"])  # load coins id for scrapping  from here: \venv\Lib\site-packages\investpy\resources

    Merged = pd.merge(first50,
                      crypto_df,
                      on=["name"],
                      how='left')  # merge these 2 guys together

    Merged = Merged.dropna().reset_index(drop=True)

    Merged["id"] = Merged["id"].astype(numpy.int64)
    return Merged


def user_ags_and_proxies():
    with open(CWD + '/User agents.txt') as file:
        USER_AGENTS = [line.rstrip() for line in file]

    PROXYTXT = open(CWD + '/proxies_approved.txt', 'r')
    proxies = PROXYTXT.read().split('\n')
    return USER_AGENTS, proxies


def get_html(idd_coin, url_add, time_stamp):  # website parcing
    url = f"https://www.investing.com/crypto/{url_add}-usd-technical"

    xx = random.randrange(0, len(USER_AGENTS))

    data_values = {
        'pairID': idd_coin,
        'period': time_stamp,
        'viewType': 'normal'
    }

    headers = {
        "User-Agent": USER_AGENTS[xx],
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "text/html",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
    }

    proxy = {"http": "http://" + choice(proxies)}

    req = requests.post(url, data=data_values, headers=headers, proxies=proxy)

    return req.text


def get_page_data(html):  # getting values form tables
    soup = BeautifulSoup(html, 'lxml')
    try:

        maBuy = int(soup.find("div", id="techStudiesInnerWrap").find("i", id="maBuy").text[1:-1])

        maSell = int(soup.find("div", id="techStudiesInnerWrap").find("i", id="maSell").text[1:-1])

        tiBuy = int(soup.find("div", id="techStudiesInnerWrap").find("i", id="tiBuy").text[1:-1])
        tiSell = int(soup.find("div", id="techStudiesInnerWrap").find("i", id="tiSell").text[1:-1])

        dictionar_buy = {"maBuy": maBuy, "tiBuy ": tiBuy}
        dictionar_sell = {"maSell ": maSell, "tiSell": tiSell}
    except AttributeError:
        dictionar_buy = {"maBuy": 6, "tiBuy ": 6}
        dictionar_sell = {"maSell ": 6, "tiSell": 6}

    return dictionar_buy, dictionar_sell


def write_csv(data):
    with open(CWD + "/monetoss.csv", "a") as f:
        writer = csv.writer(f)
        writer.writerow((data["name"], data["price"], data["decission"], data["time"]))


time_stamp = [5 * 60, 15 * 60, 30 * 60, 60 * 60, 5 * 60 * 60, 24 * 60 * 60]  # , 60 * 60 * 24
new_buy = {}
new_sell = {}
data = {}  # thats a big  file monetos
data2 = []  # small file, it will rewrite itself always


def main():
    text = "started"
    send_message(text, chat_id)

    for coins in range(len(Merged["id"])):
        idd_coin = Merged["id"][coins]
        url_add = (Merged["name"][coins] + "/" + Merged["symbol"][coins]).lower()

        son = random.uniform(2.5, 7.5)
        time.sleep(son)
        NAME = str(Merged["name"][coins])
        Symbol = str(Merged["symbol"][coins])

        price = Merged["price"][coins]

        for i in range(len(time_stamp)):
            dictionar_buy, dictionar_sell = get_page_data(get_html(idd_coin, url_add, time_stamp[i]))  # get_page_data
            new_buy[i] = dictionar_buy
            new_sell[i] = dictionar_sell

        if (sum(new_buy[0].values()) + sum(new_buy[1].values()) + sum(new_buy[2].values())) <= 4:  # was 4

            text = "sell " + NAME + " " + str(price)
            send_message(text, chat_id)

            data = {"name": NAME,
                    "symbol": Symbol,
                    "price": price,
                    "decission": "sell",
                    "time": datetime.datetime.now()}
            data2.append(data)
            write_csv(data)
        else:
            pass
        if (sum(new_sell[0].values()) + sum(new_sell[1].values()) + sum(new_sell[2].values())) <= 4:  # was 4

            text = "buy " + NAME + " " + str(price)
            send_message(text, chat_id)
            data = {"name": NAME,
                    "symbol": Symbol,
                    "price": price,
                    "decission": "buy",
                    "time": datetime.datetime.now()}
            data2.append(data)
            write_csv(data)
        else:
            pass

    df = pd.DataFrame(data2)
    writer = pd.ExcelWriter(CWD + '/_btrx.xlsx', engine='openpyxl')
    df.to_excel(writer, index=False, header=False)
    writer.save()
    writer.close()
    text = "file written"
    send_message(text, chat_id)


if __name__ == '__main__':
    USER_AGENTS, proxies = user_ags_and_proxies()
    Merged = coins_df()
    main()
