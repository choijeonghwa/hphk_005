from flask import Flask, request
import requests
import json
import time
import os
from bs4 import BeautifulSoup as bs

app = Flask(__name__)



### TELEGRAM_TOKEN을 문자열로 할 경우 다른사람이 쉽게 들어올 수 있고 변조될 가능성 높아짐
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#우회서버 이용할거야
TELEGRAM_URL = 'https://api.hphk.io/telegram'

cafe_keys = {
    '전체' : -1,
    '부천점' : 15,
    '안양점' : 13,
    '대구동성로2호점' : 14,
    '대구동성로점' : 9,
    '궁동직영점' : 1,
    '은행직영점' : 2,
    '부산서면점' : 19,
    '홍대상수점' : 20,
    '강남점' : 16,
    '건대점' : 10,
    '홍대점' : 11,
    '신촌점' : 6,
    '잠실점' : 21,
    '부평점' : 17,
    '익산점' : 12,
    '전주고사점' : 8,
    '천안신부점' : 18,
    '천안점' : 3,
    '천안두정점' : 7,
    '청주점' : 4
    }
    
cafe_code = {
        '강남1호점':3,
        '홍대1호점':1,
        '부산 서면점':5,
        '인천 부평점':4,
        '강남2호점':11,
        '홍대2호점':10
    }

def get_total_info():
    url = "http://www.seoul-escape.com/reservation/change_date/"
    params = {
        'current_date': '2018/12/21'
    }
    response = requests.get(url, params = params).text
    
    document = json.loads(response)
    

    total={}
    game_room_list = document["gameRoomList"]
    # 기본 틀 잡기
    for cafe in cafe_code:
        total[cafe]=[]
        for room in game_room_list:
            if(cafe_code[cafe]==room["branch_id"]):
                total[cafe].append({"title":room["room_name"], "info":[]})
        
    # 앞에서 만든 틀에 데이터 집어넣기
    book_list = document['bookList']    
    for cafe in total:
        for book in book_list:
            if(cafe==book["branch"]):
                for theme in total[cafe]:
                    if(theme["title"] == book['room']):
                        if(book["booked"]):
                            booked = "예약완료"
                        else:
                            booked = "예약가능"
                        theme['info'].append("{} - {}".format(book["hour"], booked))
                
    return total
    
def seoul_escape_list():
    total = get_total_info()
    return total.keys()
    
def seoul_escape_info(cd):
    total = get_total_info()
    cafe = total[cd]
    tmp = []
    for theme in cafe:
        tmp.append("{}\n{}".format(theme["title"],'\n'.join(theme["info"])))
    return tmp
    
    
def master_key_info(cd):
    url = "http://www.master-key.co.kr/booking/booking_list_new"
    params = {
        'data' : time.strftime("%Y-%m-%d"),
        'store' : cd,
        'room' : ''
    }
    
    response = requests.post(url, params).text
    document = bs(response, 'html.parser')
    ul = document.select(".reserve .escape_view")
    
    theme_list = []
    for li in ul:
        title = li.select('p')[0].text
        info=''
        print(title)
        for col in li.select('.col'):
            info = info + '{} , {}\n' .format(col.select_one('.time').text, col.select_one('.state').text)
        theme={
            'title' : title,
            'info' : info
        }
        theme_list.append(theme)
        
    return theme_list


def master_key_list():
    url = "http://www.master-key.co.kr/home/office"
    
    response = requests.get(url).text
    
    document = bs(response, 'html.parser')
    
    lis = document.select(".escape_list .escape_view")
    
    
    ### a python how to eliminate string from string?
    cafe_list = []
    for li in lis:
        title = li.select_one(' p ').text
        if(title.endswith('NEW')):
            # 맨 뒤에 세 글자 잘라라!
            title = title[:-3]
        address = li.select_one('dd').text
        tel = li.select('dd')[1].text
        link = "http://www.master-key.co.kr" + li.select_one('a')["href"]
        
        cafe = {
            "title" : title,
            "address" : address,
            "tel" : tel,
            "link" : link
        }
        cafe_list.append(cafe)
    return cafe_list
    
    
@app.route('/{}'.format(TELEGRAM_TOKEN), methods=['POST'])
def telegram():
    # 텔레그램으로부터 요청이 들어올 경우, 해당 요청을 처리하는 코드
    req = request.get_json()
    chat_id = req["message"]["from"]["id"]
    msg = req["message"]["text"]
    
    # 마스터키 전체
    # 마스터키 ****점
    if (msg.startswith('마스터키')):
        cafe_name = msg.split(' ')[-1]
        cd = cafe_keys[cafe_name]
        
        if(cd > 0):
            data = master_key_info(cd)
        else:
            data = master_key_list()
        msg = []
        for d in data:
            msg.append('\n'.join(d.values()))
        msg = '\n'.join(msg)
        
    elif(msg.startswith('서이룸')):
        cafe_name = msg.split(' ')[-1]
        
        if(len(cafe_name) == 3):
            cafe_name = msg.split(' ')[-2] + ' ' + msg.split(' ')[-1]
        
        
        data = ""
        if(cafe_name == "전체"):
            data = seoul_escape_list()
        else:
            data = seoul_escape_info(cafe_name)
        msg = []
        for d in data:
            msg.append(d.strip())
        msg = '\n'.join(msg)
        # if(len(cafe_name) > 2):
        #     cafe_name = ' '.join(cafe_name[1:3])
        #     print(cafe_name)
        # else:
        #     cafe_name = cafe_name[-1]
        #     if(cafe_name == "전체"):
        #         data = seoul_escape_list()
        #     else:
        #         data = seoul_escape_info(cafe_name)
        # msg = []
        # for d in data:
        #     msg.append('\n'.join(d.values()))
        # msg = '\n'.join(msg)
    else:
        msg = '등록되지 않은 지점입니다.'
    
    
    
    
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