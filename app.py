from flask import Flask, request
import requests
import json
import time
import os
from bs4 import BeautifulSoup as bs

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#우회서버 이용할거야
TELEGRAM_URL = 'https://api.hphk.io/telegram'

@app.route('/{}'.format(TELEGRAM_TOKEN), methods=['POST'])
def telegram():
    # 텔레그램으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
    msg = req["message"]["text"]
   # msg = []
    ex_url = 'http://m.exchange.daum.net/mobile/exchange/exchangeMain.daum'
    ex_response = requests.get(ex_url).text
    soup = bs(ex_response, 'html.parser')
    
    li = soup.select('.name')
    
    lists = []
    count = 0
    for i in li:
        list = {
            "country" : i.select_one('a').text,
            
            "exch" : soup.select('.idx')[count].text
        }
        lists.append(list)
        count+=1
    
    if(msg == "환율"):
        msg = ""
        for i in lists:
            msg += '\n' + i["country"]+'\t\t'+i["exch"]
    print(msg)
    url = 'https://api.hphk.io/telegram/bot{}/sendMessage'.format(TELEGRAM_TOKEN)
    requests.get(url, params = {"chat_id": chat_id, "text": msg})
    return '', 200

# webhook을 등록해야함!
# webhook : alert 주는 것!
# 업데이트 되었는지 계속해서 확인하는 것이 아니라 webhook을 통해서 자동으로 업데이트 확인

@app.route('/set_webhook')
def set_webhook():
    url = TELEGRAM_URL + '/bot' + TELEGRAM_TOKEN + '/setWebhook'
    params = {
        # url은 우리가 만든 홈페이지에서 ':8080' 빼고 나머지 / http뒤에 s 붙여야함
        'url' : 'https://ssafy-week2-jeonghwa1017.c9users.io/{}'.format(TELEGRAM_TOKEN)
    }
    
    response = requests.get(url, params = params)
    return response
    

