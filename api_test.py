import requests
import json
import pandas as pd
import os
import sqlite3

headerInfo = {
        'Content-Type': 'application/json; charset=utf-8',
        'accept': '*/*',
        'x-ncp-apigw-api-key': 'w4v69kgnlu'
        #'Authorization': 'Bearer {}'.format(qiita_access_token)
    }
baseURI = r'https://aipc-data.com/api'
qc_uri = baseURI + r'/QCWorkInfo/retrieveQCWorkInfoList'
transport_uri = baseURI + r'/Transport/retrieveAssignmentHistoryList'
uri = baseURI + r'/QCWorkInfo/retrieveQCWorkInfoList'
ais_uri = baseURI + r'/AISInfo/retrieveAISInfoList'

params = {
  "regNo": "KETI",
  "mmsiNo": "312773000",
  "callLetter": "V3JW",
  "imoNo": "8356869"
}
        
json_data = json.dumps(params)

result = requests.post(ais_uri, headers=headerInfo, data=json_data)
response_data = result.json()
print(response_data['resultList'][:5])

# JSON 데이터를 DataFrame으로 변환하여 CSV 파일로 저장
try:
    # JSON 응답이 리스트인 경우
    if isinstance(response_data, list):
        df = pd.DataFrame(response_data)
    # JSON 응답이 딕셔너리이고 데이터가 특정 키에 있는 경우
    elif isinstance(response_data, dict):
            df = pd.DataFrame(response_data['resultList'])
    else:
        df = pd.DataFrame(response_data['resultList'])
    
    # CSV 파일로 저장
    csv_filename = 'ais_data.csv'
    df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
    print(f"데이터가 {csv_filename} 파일로 저장되었습니다.")
    print(f"저장된 데이터 형태: {df.shape}")
    
except Exception as e:
    print(f"CSV 저장 중 오류 발생: {e}")
    print("응답 데이터 구조:")
    print(json.dumps(response_data, indent=2, ensure_ascii=False))