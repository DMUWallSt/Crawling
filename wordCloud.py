import requests
from bs4 import BeautifulSoup
import json

res = requests.get('https://finance.naver.com/sise/sise_market_sum.naver')
soup = BeautifulSoup(res.content, 'html.parser')

section = soup.find('tbody')
items = section.find_all('tr', onmouseover="mouseOver(this)")

# 종목 정보를 담을 리스트
stock_list = []

for item in items:
    basic_info = item.get_text()
    sinfo = basic_info.split("\n")

    # 종목 정보를 딕셔너리로 저장
    stock_info = {
        '종목명': sinfo[2].strip(),
        '현재가': sinfo[3].strip(),
        #'전일비': sinfo[6].strip(), # [ +,- 구분이 안되서 제외 ]
        '등락률': sinfo[11].strip(),
        '액면가': sinfo[14].strip(),
        '시가총액': sinfo[15].strip(),
        '상장주식수': sinfo[16].strip(),
        '외국인비율': sinfo[17].strip(),
        '거래량': sinfo[18].strip()
    }
    stock_list.append(stock_info)

# 크롤링한 데이터를 JSON 파일로 저장
with open('stock_data.json', 'w', encoding='utf-8') as json_file:
    json.dump(stock_list, json_file, ensure_ascii=False, indent=2)

print('크롤링이 완료되었습니다.')
