# 크롤링시 필요한 라이브러리 불러오기
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import mysql.connector
import json

db_config = {
    "host": "wallst-database.ckbjgxfonehb.ap-northeast-2.rds.amazonaws.com",
    "user": "admin",
    "password": "wallstdb99",
    "database": "mydb",
}

json_file_path = "삼성전자_20231006_22hours41minutes18seconds.json"

try:
    # MySQL 연결
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # JSON 파일 열기
    with open(json_file_path, "r", encoding="UTF8") as json_file:
        json_data = json.load(json_file)

    # JSON 데이터를 MySQL 테이블에 분배하여 삽입
    for item in json_data:
        id = item.get("id", None)  
        date = item.get("date", None) 
        title = item.get("title", None)
        link = item.get("link", None)
        content = item.get("content", None)
        press = item.get("press", None)
        thumbnail_link = item.get("thumbnail_link", None)
        keyword = item.get("keyword", None)
        score = item.get("score", None)
        

        # INSERT INTO 문을 사용하여 데이터 삽입
        insert_query = "INSERT INTO test_samsung (id, date, title, link, content, press, thumbnail_link, keyword, score) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(insert_query, (id, date, title, link, content, press, thumbnail_link, keyword, score))

    connection.commit()
    print("JSON 데이터가 MySQL에 삽입되었습니다.")

except mysql.connector.Error as error:
    print("MySQL 오류:", error)

finally:
    # 연결 종료
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL 연결이 닫혔습니다.")
