import requests
from bs4 import BeautifulSoup
import json
import mysql.connector

db_config = {
    "host": "wallst-database.ckbjgxfonehb.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "wallstdb99",
    "database": "mydb",
}

json_file_path = f"stock_data.json"

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
        '전일비': sinfo[6].strip(), # 등락률 보고 올랐는지 내렸는지 구분 가능
        '등락률': sinfo[11].strip(),
        '액면가': sinfo[14].strip(),
        '시가총액': sinfo[15].strip(),
        '상장주식수': sinfo[16].strip(),
        '외국인비율': sinfo[17].strip(),
        '거래량': sinfo[18].strip()
    }
    stock_list.append(stock_info)

# 크롤링한 데이터를 JSON 파일로 저장
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(stock_list, json_file, ensure_ascii=False, indent=2)

print('크롤링이 완료되었습니다.')

# MySQL 연결
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

# JSON 파일 열기
with open(json_file_path, "r", encoding="UTF8") as json_file:
    json_data = json.load(json_file)

# JSON 데이터를 MySQL 테이블에 분배하여 삽입
for item in json_data:
    name = item.get("종목명", None)
    stock_today = item.get("현재가", None)
    market_cap = item.get("시가총액", None)
    trading_vol = item.get("거래량", None)
    ratio = item.get("등락률", None)
    diff = item.get("전일비", None)

    # # INSERT INTO 문을 사용하여 데이터 삽입
    insert_query = "INSERT INTO company_info (name, stock_today, market_cap, trading_vol, ratio, diff) VALUES (%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE name = %s, stock_today = %s, market_cap = %s, trading_vol = %s, ratio = %s, diff = %s"
    cursor.execute(insert_query, (name, stock_today, market_cap, trading_vol, ratio, diff, name, stock_today, market_cap, trading_vol, ratio, diff))
    


    connection.commit()
print("JSON 데이터가 MySQL에 삽입되었습니다.")

# 연결 종료
if connection.is_connected():
    cursor.close()
    connection.close()
    print("MySQL 연결이 닫혔습니다.")
