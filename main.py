import os
import streamlit as st
import requests
import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError
import pandas as pd

st.title('MZC DART 공시 정보 검색 서비스')

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

rows_per_page = 20
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

def fetch_data(page_number, rows_per_page):
    offset = (page_number - 1) * rows_per_page
    paginated_query = f"""
    SELECT *
    FROM {database}.{schema}.{table}
    WHERE CORP_NAME LIKE '%{company_name_search}%'
    LIMIT {rows_per_page} OFFSET {offset}
    """
    cur = conn.cursor()
    cur.execute(paginated_query)
    return cur.fetchall()

# Create a search bar for company name
company_name_search = st.text_input("회사명을 입력하세요:")

if company_name_search:
    conn = create_snowflake_connection()
    if conn:
        try:
            results = fetch_data(st.session_state.page_number, rows_per_page)

            # Display the results
            if results:
                df = pd.DataFrame(results, columns = ['공시번호', '기업명', '종목코드', '최종수정일자'])
                st.table(df)
                col1, col2 = st.columns([1, 1])

                with col1:
                    if st.button('이전 페이지'):
                        if st.session_state.page_number > 1:
                            st.session_state.page_number -= 1

                with col2:
                    if st.button('다음 페이지'):
                        st.session_state.page_number += 1

            else:
                st.write("회사 검색 불가")

        except ProgrammingError as e:
            st.error(f"쿼리 에러: {e}")
    else:
        st.error("DB 연결 실패")

st.markdown("####")

# Create a search bar for CORP_CODE
corp_code_search = st.text_input("공시번호를 입력하세요:")

if corp_code_search:
    # Construct the URL with the searched CORP_CODE
    url = f"https://opendart.fss.or.kr/api/company.json?crtfc_key={api_key}&corp_code={corp_code_search}"

    # Make a GET request to the URL
    response = requests.get(url)

    # Check if the request was successful
    if response.status_code == 200:
        # Display the response or part of it in the Streamlit app
        dataset = response.json()
        dynamic_values = [item[1] for item in dataset.items()]  # Extracting second element from each item

        # Fixed values for the first column
        fixed_values = ['status','message','공시번호','정식명칭','영문명칭','종목명','종목코드','대표자명','법인구분','법인등록번호','사업자등록번호','주소','홈페이지','IR홈페이지','전화번호','팩스번호','업종코드','설립일','결산월']  # Your fixed values here

        # Ensure that the length of fixed_values matches the length of dynamic_values
        if len(fixed_values) != len(dynamic_values):
            st.error("Mismatch in the number of fixed and dynamic values")
        else:
        # Create the DataFrame
            df = pd.DataFrame(list(zip(fixed_values, dynamic_values)), columns=['공시 정보', '값'])

        # Optionally, remove the first and second rows as per your previous requirement
            df = df.iloc[2:]
            st.table(df)

    else:
        st.write("에러가 발생했습니다")


st.markdown("####")
st.write("Created By: mzcsaas@mz.co.kr")
