# MySQL 데이터베이스 설정 가이드

## 1. MySQL 설치 및 설정

### Windows에서 MySQL 설치
1. MySQL Community Server 다운로드: https://dev.mysql.com/downloads/mysql/
2. MySQL Installer 실행 및 설치
3. MySQL 서비스 시작

### macOS에서 MySQL 설치
```bash
# Homebrew 사용
brew install mysql
brew services start mysql

# 또는 MySQL 공식 설치 프로그램 사용
```

### Linux에서 MySQL 설치
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql

# CentOS/RHEL
sudo yum install mysql-server
sudo systemctl start mysqld
sudo systemctl enable mysqld
```

## 2. MySQL 초기 설정

### MySQL 보안 설정
```bash
# MySQL에 root로 접속
mysql -u root -p

# 새 사용자 생성 (선택사항)
CREATE USER 'ais_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON port_database.* TO 'ais_user'@'localhost';
FLUSH PRIVILEGES;
```

## 3. 데이터베이스 초기화

### 1단계: 설정 파일 수정
`db/database_config.py` 파일에서 MySQL 연결 정보를 수정하세요:

```python
MYSQL_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',  # 또는 생성한 사용자명
    'password': 'your_password',  # MySQL 비밀번호
    'database': 'port_database',
    'charset': 'utf8mb4'
}
```

### 2단계: 데이터베이스 초기화 실행
```bash
cd db
python init_mysql_database.py
```

이 스크립트는 다음을 수행합니다:
- `port_database` 데이터베이스 생성
- `ais_info` 테이블 생성
- CSV 데이터 임포트 (선택사항)

## 4. 백엔드 서버 실행

### 의존성 설치
```bash
cd backend
pip install -r requirements.txt
```

### 서버 실행
```bash
python main.py
```

서버는 http://localhost:8000 에서 실행됩니다.

## 5. 프론트엔드 실행

```bash
cd dashboard
npm install
npm start
```

React 앱은 http://localhost:3000 에서 실행됩니다.

## 6. 데이터베이스 연결 확인

### MySQL에서 직접 확인
```bash
mysql -u root -p
USE port_database;
SHOW TABLES;
SELECT COUNT(*) FROM ais_info;
```

### API를 통한 확인
```bash
curl http://localhost:8000/ais/statistics
```

## 7. 문제 해결

### 연결 오류
- MySQL 서비스가 실행 중인지 확인
- 사용자명과 비밀번호가 올바른지 확인
- 포트 3306이 사용 가능한지 확인

### 권한 오류
- 사용자에게 적절한 권한이 부여되었는지 확인
- 데이터베이스가 존재하는지 확인

### 데이터 임포트 오류
- CSV 파일 경로가 올바른지 확인
- CSV 파일 형식이 예상과 일치하는지 확인

## 8. 성능 최적화

### 인덱스 생성
```sql
-- 자주 조회되는 컬럼에 인덱스 생성
CREATE INDEX idx_mmsi_no ON ais_info(mmsi_no);
CREATE INDEX idx_vssl_nm ON ais_info(vssl_nm);
CREATE INDEX idx_flag ON ais_info(flag);
CREATE INDEX idx_dt_pos_utc ON ais_info(dt_pos_utc);
```

### 설정 최적화
MySQL 설정 파일에서 다음 설정을 조정할 수 있습니다:
- `max_connections`: 동시 연결 수
- `innodb_buffer_pool_size`: InnoDB 버퍼 풀 크기
- `query_cache_size`: 쿼리 캐시 크기 