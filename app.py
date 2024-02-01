import os
from dotenv import load_dotenv
import streamlit as st
import requests
import snowflake.connector
from snowflake.connector.errors import DatabaseError, ProgrammingError
import pandas as pd

user = os.environ.get('SNOWFLAKE_USER')
password = os.environ.get('SNOWFLAKE_PASSWORD')
account = os.environ.get('SNOWFLAKE_ACCOUNT')
database = 'MZC_APP'
schema = 'PUBLIC'
table = 'DART_DATA'
api_key = os.environ.get('API_KEY')

def page1():
    st.title('DART 공시 정보 검색')
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
                st.error("8자리 코드를 맞춰주세요 혹은 정확한 공시코드가 아닙니다")
            else:
            # Create the DataFrame
                df = pd.DataFrame(list(zip(fixed_values, dynamic_values)), columns=['공시 정보', '값'])

            # Optionally, remove the first and second rows as per your previous requirement
                df = df.iloc[2:]
                st.table(df)

        else:
            st.write("에러가 발생했습니다")
    return corp_code_search if corp_code_search else None

def send_request(corp_code):
    bsns_year='2023'
    reprt_code='11013' #1분기보고서: 11013 반기보고서: 11012 3분기보고서: 11014 사업보고서: 11011
    url = f"https://opendart.fss.or.kr/api/fnlttSinglAcnt.json?crtfc_key={api_key}&corp_code={corp_code}&bsns_year={bsns_year}&reprt_code={reprt_code}"
    response = requests.get(url)
    if response.status_code == 200:
        json_data = response.json()
        if json_data['status'] in ['013', '014']:
            return f"에러: {json_data['message']}"
        return json_data
    else:
        return "에러: 데이터를 볼러올 수 없습니다."

def page2(corp_code):
    st.title("재무제표 정보")
    data_list = send_request(corp_code)
    print(data_list)
    if isinstance(data_list, str) and data_list.startswith("에러"):
        st.write("재무제표 혹은 파일이 검색되지 않습니다")
    elif data_list:
        json_data = data_list['list']
        if json_data:
            df = pd.DataFrame(json_data)
            df = df.iloc[14:,2:]
            st.dataframe(df)
        else:
            st.write("No data available")
    else:
        st.error("Failed to retrieve or parse data")

# Initialize the page number in the session state
if 'page_number' not in st.session_state:
    st.session_state.page_number = 1

corp_code = None
# Render the current page
if st.session_state.page_number == 1:
    corp_code = page1()
    if st.button("재무제표 검색"):
        if corp_code is None:
            st.write("공시번호를 검색해 주세요")
        else:
            st.session_state.page_number = 2

if st.session_state.page_number == 2 and corp_code:
    json_data = send_request(corp_code)
    page2(corp_code)



