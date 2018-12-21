from bs4 import BeautifulSoup as bs
import requests

## 여기서는 requests.post로!! Network 탭의 Request Method 방식
## get 방식은 url에 파라미터 정보가 있지만
## post 방식은 숨어있음. 맨 밑에 Form Data라는 곳에 정보 있음
## params 변수에 위의 데이터 정보 넘겨주기

def master_key_info(cd):
    url = "http://www.master-key.co.kr/booking/booking_list_new"
    params = {
        'data' : '2018-12-22',
        'store' : cd
    }
    response = requests.post(url, params).text
    document = bs(response, 'html.parser')
    ul = document.select(".reserve .escape_view")
    
    for li in ul:
        title = li.select('p')[0].text
        info=''
        print(title)
        for col in li.select('.col'):
            info = info + '{} , {}\n' .format(col.select_one('.time').text, col.select_one('.state').text)
        print(info)
        


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
        address = "http://www.master-key.co.kr" + li.select_one('dd').text
        tel = li.select('dd')[1].text
        link = li.select_one('a')["href"]
        
        cafe = {
            "title" : title,
            "address" : address,
            "tel" : tel,
            "link" : link
        }
        cafe_list.append(cafe)
    return cafe_list
    
# 사용자로부터 '마스터키 ****점'이라는 메시지를 받으면

# msg.split(' ')[1] <= 지점명 냐????????

# 해당 지점에 대한 오늘의 정보를 요청하고(크롤링)

# 메시지(예약정보)를 보내준다
    
for cafe in master_key_list():
    print('{} : {}'.format(cafe["title"], cafe["link"].split('=')[0]))
(master_key_info(7))