-- API_PARAMS.endpoint_defaults 기반 누락된 DB 테이블 생성 스크립트
-- port_database에 추가할 테이블들

USE port_database;

-- 1. 컨테이너 양적하정보
CREATE TABLE IF NOT EXISTS cntr_load_unload_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    tmnlId VARCHAR(50),
    shpCd VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    timeFrom VARCHAR(20),
    timeTo VARCHAR(20),
    cntrNo VARCHAR(50),
    blNo VARCHAR(100),
    cntrSize VARCHAR(20),
    cntrType VARCHAR(20),
    loadPort VARCHAR(50),
    dischargePort VARCHAR(50),
    loadDate VARCHAR(20),
    dischargeDate VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_cntrNo (cntrNo)
);

-- 2. 컨테이너 신고상세정보
CREATE TABLE IF NOT EXISTS cntr_report_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    mrnNo VARCHAR(100),
    msnNo VARCHAR(50),
    blNo VARCHAR(100),
    cntrNo VARCHAR(50),
    cntrSize VARCHAR(20),
    cntrType VARCHAR(20),
    cargoDesc TEXT,
    weight DECIMAL(10,2),
    volume DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_mrnNo (mrnNo),
    INDEX idx_cntrNo (cntrNo)
);

-- 3. 선박양적하 시작종료정보
CREATE TABLE IF NOT EXISTS load_unload_from_to_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    tmnlId VARCHAR(50),
    shpCd VARCHAR(50),
    callYr VARCHAR(10),
    callNo VARCHAR(10),
    startTime VARCHAR(20),
    endTime VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_tmnlId (tmnlId)
);

-- 4. 관제정보 (VTCHistory)
CREATE TABLE IF NOT EXISTS vssl_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    vsslName VARCHAR(100),
    vsslType VARCHAR(50),
    vsslFlag VARCHAR(20),
    vsslLength DECIMAL(8,2),
    vsslWidth DECIMAL(8,2),
    vsslDraft DECIMAL(6,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 5. 선박 입항신고정보
CREATE TABLE IF NOT EXISTS vssl_entr_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    vsslName VARCHAR(100),
    vsslType VARCHAR(50),
    vsslFlag VARCHAR(20),
    entrDate VARCHAR(20),
    entrPurpose VARCHAR(100),
    crewCount INT,
    passengerCount INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 6. 선박 출항신고정보
CREATE TABLE IF NOT EXISTS vssl_dprt_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    vsslName VARCHAR(100),
    vsslType VARCHAR(50),
    vsslFlag VARCHAR(20),
    dprtDate VARCHAR(20),
    dprtPurpose VARCHAR(100),
    nextPort VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 7. 화물반출입신고정보
CREATE TABLE IF NOT EXISTS cargo_imp_exp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    cargoType VARCHAR(50),
    cargoDesc TEXT,
    weight DECIMAL(10,2),
    volume DECIMAL(10,2),
    impExpType VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 8. 항만시설사용 신청/결과정보
CREATE TABLE IF NOT EXISTS fac_use_statement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    facilityType VARCHAR(50),
    facilityCode VARCHAR(50),
    useStartTime VARCHAR(20),
    useEndTime VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 9. 항만시설사용신고정보-화물료
CREATE TABLE IF NOT EXISTS fac_use_stmt_bill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    facilityType VARCHAR(50),
    facilityCode VARCHAR(50),
    useStartTime VARCHAR(20),
    useEndTime VARCHAR(20),
    billAmount DECIMAL(12,2),
    billStatus VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 10. 선박보안인증서 통보
CREATE TABLE IF NOT EXISTS vssl_sec_isps_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    ispsCertNo VARCHAR(100),
    ispsCertType VARCHAR(50),
    issueDate VARCHAR(20),
    expiryDate VARCHAR(20),
    certStatus VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 11. 선박보안인증서 통보 경유지 정보
CREATE TABLE IF NOT EXISTS vssl_sec_port_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    portCode VARCHAR(50),
    portName VARCHAR(100),
    callDate VARCHAR(20),
    securityLevel VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 12. 외항통과선박신청정보
CREATE TABLE IF NOT EXISTS vssl_pass_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    vsslName VARCHAR(100),
    vsslType VARCHAR(50),
    vsslFlag VARCHAR(20),
    passDate VARCHAR(20),
    passPurpose VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 13. 위험물반입신고서
CREATE TABLE IF NOT EXISTS dg_imp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    dgClass VARCHAR(20),
    dgDesc TEXT,
    weight DECIMAL(10,2),
    packageType VARCHAR(50),
    unNo VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 14. 위험물 적하알림표
CREATE TABLE IF NOT EXISTS dg_manifest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    callYr VARCHAR(10),
    serNo VARCHAR(10),
    cntrNo VARCHAR(50),
    repNo VARCHAR(100),
    dgClass VARCHAR(20),
    dgDesc TEXT,
    weight DECIMAL(10,2),
    packageType VARCHAR(50),
    unNo VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter),
    INDEX idx_cntrNo (cntrNo)
);

-- 15. 화물품목코드
CREATE TABLE IF NOT EXISTS cargo_item_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    crgItemCd VARCHAR(20),
    crgItemName VARCHAR(200),
    crgItemDesc TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_crgItemCd (crgItemCd)
);

-- 16. 제재대상선박 정보
CREATE TABLE IF NOT EXISTS vssl_sanction_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(50),
    vsslName VARCHAR(100),
    sanctionType VARCHAR(50),
    sanctionReason TEXT,
    sanctionDate VARCHAR(20),
    expiryDate VARCHAR(20),
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_callLetter (callLetter)
);

-- 17. 국가코드
CREATE TABLE IF NOT EXISTS country_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    cntryCd VARCHAR(10),
    cntryName VARCHAR(100),
    cntryNameEn VARCHAR(100),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_cntryCd (cntryCd)
);

-- 18. 입항목적코드
CREATE TABLE IF NOT EXISTS vssl_entr_intn_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    vsslEntrIntnCd VARCHAR(10),
    vsslEntrIntnName VARCHAR(100),
    vsslEntrIntnDesc TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_vsslEntrIntnCd (vsslEntrIntnCd)
);

-- 19. 항구청코드
CREATE TABLE IF NOT EXISTS pa_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    paCd VARCHAR(10),
    paName VARCHAR(100),
    paNameEn VARCHAR(100),
    region VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_paCd (paCd)
);

-- 20. 항구코드
CREATE TABLE IF NOT EXISTS port_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    inspection_id VARCHAR(100),
    natCd VARCHAR(10),
    portCd VARCHAR(20),
    portName VARCHAR(100),
    portNameEn VARCHAR(100),
    country VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_inspection_id (inspection_id),
    INDEX idx_portCd (portCd)
);

-- 테이블 생성 완료 확인
SELECT 
    table_name,
    table_rows,
    data_length,
    index_length
FROM information_schema.tables 
WHERE table_schema = 'port_database'
ORDER BY table_name;
