import os
from dotenv import load_dotenv
import streamlit as st
import requests
import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError
import pandas as pd

st.title('DART 공시 정보 검색')

# User input for database credentials
user = os.environ.get('SNOWFLAKE_USER')
password = os.environ.get('SNOWFLAKE_PASSWORD')
account = os.environ.get('SNOWFLAKE_ACCOUNT')
database = 'MZC_APP'
schema = 'PUBLIC'
table = 'DART_DATA'
api_key = os.environ.get('API_KEY')

# Connect to Snowflake
@st.cache_resource
def create_snowflake_connection():
    try:
        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            database=database,
            schema=schema
        )
        return conn
    except DatabaseError as e:
        st.error(f"Database Connection Failed: {e}")
        return None

# Create a search bar for company name
company_name_search = st.text_input("회사명을 입력하세요:")

if company_name_search:
    conn = create_snowflake_connection()
    if conn:
        try:
            # Construct the SQL query for company name
            company_name_query = f"""
            SELECT * 
            FROM {database}.{schema}.{table}
            WHERE CORP_NAME LIKE '%{company_name_search}%'
            """

            # Execute the query
            cur = conn.cursor()
            cur.execute(company_name_query)
            results = cur.fetchall()

            # Display the results
            if results:
                st.table(results)
            else:
                st.write("회사 검색 불가")

        except ProgrammingError as e:
            st.error(f"쿼리 에러: {e}")
    else:
        st.error("DB 연결 실패")

# Create a search bar for CORP_CODE
corp_code_search = st.text_input("CORP_CODE를 입력하세요:")

if corp_code_search:
    # Construct the URL with the searched CORP_CODE
    url = f"https://opendart.fss.or.kr/api/company.json?crtfc_key={api_key}&corp_code={corp_code_search}"

    # Make a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Display the response or part of it in the Streamlit app
        dataset = response.json()
        df = pd.DataFrame(list(dataset.items()), columns=['공시 정보', '값'])
        st.table(df)
    else:
        st.write("에러가 발생했습니다")

