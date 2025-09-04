from preprocess import parsing
from summarize import company_summary
import os
import json
import psycopg2

# data = parsing.preprocessing_personal_info('./example_datas/talent_ex1.json')

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": os.getenv("POSTGRES_USER", "searchright"),
    "password": os.getenv("POSTGRES_PASSWORD", "searchright"),
    "database": os.getenv("POSTGRES_DB", "searchright"),
}

conn = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
        )

# # 커서 생성
# cursor = conn.cursor()

# # 회사 이름만 조회
# cursor.execute("SELECT name FROM company")

# # 결과 출력
# company_names = cursor.fetchall()
# for name in company_names:
#     print(name[0])

# # 종료
# cursor.close()
# conn.close()

#company_period = parsing.extract_company_period(data["positions"])


# companies_info = []
# for com in company_period:
#     company_data = parsing.get_company_data(conn, com['company'])
#     if company_data != None:
#         company_info = parsing.get_company_info(company_data, com['start_date'], com['end_date'])
#         companies_info.append({'company': com['company'],
#                                'company_info': company_info})
#     else:
#         companies_info = None

# mau_data = companies_info[0]['company_info']['mau']
# values = [d["value"] for d in mau_data if "value" in d and d["value"] is not None]

with open("./example_datas/company_ex1_비바리퍼블리카.json", "r") as f:
        company_data = json.load(f)
start_date = (2021, 1)
end_date = (2023, 8)


data = parsing.get_company_info(company_data, start_date, end_date)
# print(data['finance'])


statements = company_summary.company_info_summary(data)
print(f"\n{statements}")


# for i in range(0, len(companies_info)):
#     print(companies_info[i])

# print(type(companies_info[0]['company_info']['mau']))


# company_name = "네이버"
# start_date = (2024, 1)
# end_date = (2025, 6)

# result = parsing.get_company_data(conn, company=company_name)

# from pprint import pprint
# pprint(result)