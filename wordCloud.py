import requests
from bs4 import BeautifulSoup
import json
import mysql.connector

db_config = {
    "host": "database-1.csupg5qofpr5.us-east-1.rds.amazonaws.com",
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

alter_queries = [
    "ALTER TABLE company_info MODIFY stock_today VARCHAR(255)",
    "ALTER TABLE company_info MODIFY market_cap VARCHAR(255)",
    "ALTER TABLE company_info MODIFY trading_vol VARCHAR(255)",
    "ALTER TABLE company_info MODIFY diff VARCHAR(255)"
]

for query in alter_queries:
    cursor.execute(query)

print("테이블 유형 변경")

# JSON 데이터를 MySQL 테이블에 분배하여 삽입 또는 업데이트
for item in json_data:
    name = item.get("종목명", None)
    stock_today = item.get("현재가", None)
    market_cap = item.get("시가총액", None)
    trading_vol = item.get("거래량", None)
    ratio = item.get("등락률", None)
    diff = item.get("전일비", None)

    # UPDATE 문을 사용하여 데이터 업데이트
    update_query = (
        "UPDATE company_info "
        "SET stock_today = %s, market_cap = %s, trading_vol = %s, ratio = %s, diff = %s "
        "WHERE name = %s"
    )
    cursor.execute(update_query, (stock_today, market_cap, trading_vol, ratio, diff, name))

alter_queries2 = [
    "UPDATE company_info SET stock_today = REPLACE(stock_today, ',', '')",
    "UPDATE company_info SET market_cap = REPLACE(market_cap, ',', '')",
    "UPDATE company_info SET trading_vol = REPLACE(trading_vol, ',', '')",
    "UPDATE company_info SET diff = REPLACE(diff, ',', '')",
    "ALTER TABLE company_info MODIFY stock_today INT",
    "ALTER TABLE company_info MODIFY market_cap INT",
    "ALTER TABLE company_info MODIFY trading_vol INT",
    "ALTER TABLE company_info MODIFY diff INT"
]

for query in alter_queries2:
    cursor.execute(query)
    print("Query Executed")

connection.commit()
print("JSON 데이터가 MySQL에 삽입되었습니다.")

# 연결 종료
if connection.is_connected():
    cursor.close()
    connection.close()
    print("MySQL 연결이 닫혔습니다.")
