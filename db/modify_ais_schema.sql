-- AIS 정보 테이블 스키마 수정
-- lon, lat 컬럼을 더 넓은 범위로 확장하여 위치 데이터 범위 초과 문제 해결

USE port_database;

-- 현재 테이블 구조 확인
DESCRIBE ais_info;

-- lon 컬럼을 DECIMAL(12,8)로 수정 (경도: -180 ~ +180)
-- 소수점 8자리까지 정밀도 보장
ALTER TABLE ais_info MODIFY COLUMN lon DECIMAL(12,8);

-- lat 컬럼을 DECIMAL(12,8)로 수정 (위도: -90 ~ +90)
-- 소수점 8자리까지 정밀도 보장
ALTER TABLE ais_info MODIFY COLUMN lat DECIMAL(12,8);

-- 수정된 테이블 구조 확인
DESCRIBE ais_info;

-- 테이블 정보 확인
SELECT COUNT(*) as '레코드 수' FROM ais_info;

-- 샘플 데이터 확인 (lon, lat 값이 정상적으로 저장되는지)
SELECT id, mmsiNo, callLetter, lon, lat, created_at 
FROM ais_info 
LIMIT 5;

