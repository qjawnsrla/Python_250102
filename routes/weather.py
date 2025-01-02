import json     # JSON 직렬화 / 역직렬화
import requests # http 통신
from bs4 import BeautifulSoup
from flask import request, Flask, jsonify, Response
import datetime
def get_sample_weather():
    url="http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108"
    # HTTP GET 요청
    response = requests.get(url)
    # HTMP Parsing
    soup = BeautifulSoup(response.text, 'html.parser')
    html_output = ""
    for loc in soup.findAll( "location"):
        html_output += f"<h2>{loc.select_one('city').string}</h2>"
        html_output += f"<h4>날씨 : {loc.select_one('wf').string}</h4>"
        html_output += f"<h4>최저 / 최고 기온 : {loc.select_one('tmn').string}/{loc.select_one('tmx')}</h4>"
        html_output += "</hr>"
    return html_output

# 위치 정보를 받아서 해당 위치의 현재 온도, 습도, 강수량이 표시되도록 수정
def get_short_term_weather():
    # API_KEY = "Jv3ERKeyevP4pcoZRu7M5%2F5sTKRej5I%2BjLwnTKFubmiSpnrgfNIlUwD2qS2dQfsLhRzNexprVNJTLrajHQ5zMw%3D%3D"
    # API_KEY_DECODE = requests.utils.unquote_unreserved(API_KEY)
    nx_val = request.args.get('x', default=None, type=int)
    ny_val = request.args.get('y', default=None, type=int)
    if nx_val is None or ny_val is None:
        return json.dumps({"error": "nx와 ny 값을 제공해야 합니다."}, ensure_ascii=False), 400
    API_KEY_DECODE = "Jv3ERKeyevP4pcoZRu7M5/5sTKRej5I+jLwnTKFubmiSpnrgfNIlUwD2qS2dQfsLhRzNexprVNJTLrajHQ5zMw=="

    # 현재 시간 가져오기
    now = datetime.datetime.now()
    # 서식에 맞게 날짜 정보 변경
    date = now.strftime('%Y%m%d')
    # 서식에 맞게 시간 정보 변경
    # time = now.strftime('%H%M')
    # 현재 분이 30분 이전이면 30분 전 시간으로 설정
    if now.minute < 30:
        now = now - datetime.timedelta(minutes=30)
        time = now.strftime('%H%M')
    else:
        time = now.strftime('%H%M')

    # 요청주소
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    # 요청 일자 지정
    baseDate = date
    baseTime = time
    # 예보 지점 (서울시 강남구 역삼동)
    # nx_val = 62
    # ny_val = 126
    # 한 페이지에 포함된 결과 수
    num_of_rows = 6
    # 페이지 번호
    page_no = 1
    # 응답 데이터 형식 지정
    data_type = 'JSON'

    # params ={'serviceKey' : '서비스키', 'pageNo' : '1', 'numOfRows' : '1000', 'dataType' : 'XML', 'base_date' : '20210628', 'base_time' : '0600', 'nx' : '55', 'ny' : '127' }
    req_parameter = {'serviceKey' : API_KEY_DECODE,
                     'nx' : nx_val, 'ny' : ny_val,
                     'base_date' : baseDate, 'base_time' : baseTime,
                     'pageNo' : page_no, 'numOfRows' : num_of_rows,
                     'dataType' : data_type
                     }
    # 요청과 응답
    try:
        response = requests.get(url, params=req_parameter)
        print(response.status_code)  # 상태 코드 출력
    except requests.exceptions.RequestException as e:
        print(f"날씨 정보 요청 실패 : {e}")
        return json.dumps({"에러": str(e)}, ensure_ascii=False)

    # JSON 형태로 응답받은 데이터를 딕셔너리로 변환
    dict_data = response.json()
    # print(dict_data)

    # 출력을 이쁘게 하기 위해 json.dumps()를 사용하여 들여쓰기(indent) 옵션을 지정
    print(json.dumps(dict_data, indent=2))

    # 딕셔너리 데이터를 분석하여 원하는 데이터를 추출
    weather_items = dict_data['response']['body']['items']['item']

    print(f"[ 발표 날짜 : {weather_items[0]['baseDate']} ]")
    print(f"[ 발표 시간 : {weather_items[0]['baseTime']} ]")

    weather_data = {}

    for k in range(len(weather_items)):
        weather_item = weather_items[k]
        obsrValue = weather_item['obsrValue']
        if weather_item['category'] == 'T1H':
            weather_data['tmp'] = f"{obsrValue}℃"
        elif weather_item['category'] == 'REH':
            weather_data['hum'] = f"{obsrValue}%"
        elif weather_item['category'] == 'RN1':
            weather_data['pre'] = f"{obsrValue}mm"

    # 딕셔너리를 JSON 형태로 변환
    json_weather = json.dumps(weather_data, ensure_ascii=False, indent=4)
    return json_weather


def get_multiple_locations_weather():
    API_KEY_DECODE = "Jv3ERKeyevP4pcoZRu7M5/5sTKRej5I+jLwnTKFubmiSpnrgfNIlUwD2qS2dQfsLhRzNexprVNJTLrajHQ5zMw=="

    # 여러 지역의 좌표 (nx, ny) 값을 리스트로 저장
    locations = [
        {"name": "서울", "nx": 60, "ny": 127},
        {"name": "부산", "nx": 98, "ny": 76},
        {"name": "대구", "nx": 89, "ny": 89},
        {"name": "인천", "nx": 55, "ny": 125},
        # 다른 지역 추가 가능
    ]

    weather_data_all_locations = []

    # 각 지역에 대해 날씨 정보 요청
    for location in locations:
        # 지역 이름과 좌표
        location_name = location["name"]
        nx_val = location["nx"]
        ny_val = location["ny"]
        # 현재 시간 가져오기
        now = datetime.datetime.now()
        # 서식에 맞게 날짜 정보 변경
        date = now.strftime('%Y%m%d')
        # 서식에 맞게 시간 정보 변경
        # time = now.strftime('%H%M')
        # 현재 분이 30분 이전이면 30분 전 시간으로 설정
        if now.minute < 30:
            now = now - datetime.timedelta(minutes=30)
            time = now.strftime('%H%M')
        else:
            time = now.strftime('%H%M')

        # 기존 get_short_term_weather() 함수에서 사용하는 URL 및 요청 파라미터
        url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
        req_parameter = {
            'serviceKey': API_KEY_DECODE,
            'nx': nx_val,
            'ny': ny_val,
            'base_date': date,
            'base_time': time,
            'pageNo': 1,
            'numOfRows': 6,
            'dataType': 'JSON'
        }

        try:
            response = requests.get(url, params=req_parameter)
            response.raise_for_status()  # 응답 상태 코드 확인
        except requests.exceptions.RequestException as e:
            print(f"{location_name} 날씨 정보 요청 실패: {e}")
            continue

        dict_data = response.json()
        weather_items = dict_data['response']['body']['items']['item']

        # 지역별 날씨 데이터 추출
        location_weather = {
            "location": location_name,
            "tmp": None,
            "hum": None,
            "pre": None
        }

        for weather_item in weather_items:
            obsrValue = weather_item['obsrValue']
            if weather_item['category'] == 'T1H':
                location_weather["tmp"] = f"{obsrValue}℃"
            elif weather_item['category'] == 'REH':
                location_weather["hum"] = f"{obsrValue}%"
            elif weather_item['category'] == 'RN1':
                location_weather["pre"] = f"{obsrValue}mm"

        weather_data_all_locations.append(location_weather)

    # 모든 지역의 날씨 정보 출력
    return json.dumps(weather_data_all_locations, ensure_ascii=False, indent=4)

