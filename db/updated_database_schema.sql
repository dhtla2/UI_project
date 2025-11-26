-- API 응답 결과 기반 업데이트된 DB 스키마
-- 2025-08-25 API 구조 체크 결과 반영

USE port_database;

-- =====================================================
-- 1. TC 작업 정보 (188,880건)
-- =====================================================
CREATE TABLE IF NOT EXISTS tc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(10),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    tcNo VARCHAR(10),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(200),
    wkId VARCHAR(50),
    jobNo VARCHAR(50),
    szTp VARCHAR(10),
    ytNo VARCHAR(10),
    rtNo VARCHAR(10),
    block VARCHAR(10),
    bay VARCHAR(10),
    roww VARCHAR(10),
    ordTime VARCHAR(20),
    wkTime VARCHAR(20),
    jobState VARCHAR(50),
    evntTime VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_wkTime (wkTime),
    INDEX idx_tcNo (tcNo)
);

-- =====================================================
-- 2. QC 작업 정보 (90,793건)
-- =====================================================
CREATE TABLE IF NOT EXISTS qc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(10),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    qcNo VARCHAR(10),
    cntrNo VARCHAR(20),
    ytNo VARCHAR(10),
    shpNm VARCHAR(200),
    tmnlNm VARCHAR(100),
    fmId VARCHAR(10),
    wkId VARCHAR(50),
    disBay VARCHAR(10),
    disRow VARCHAR(10),
    disTier VARCHAR(10),
    disHd VARCHAR(10),
    lodBay VARCHAR(10),
    lodRow VARCHAR(10),
    lodTier VARCHAR(10),
    lodHd VARCHAR(10),
    szTp VARCHAR(10),
    ordTime VARCHAR(20),
    wkTime VARCHAR(20),
    jobState VARCHAR(50),
    evntTime VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_wkTime (wkTime),
    INDEX idx_qcNo (qcNo)
);

-- =====================================================
-- 3. YT 작업 정보 (85,872건)
-- =====================================================
CREATE TABLE IF NOT EXISTS yt_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(10),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    ytNo VARCHAR(10),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(200),
    wkId VARCHAR(50),
    jobNo VARCHAR(50),
    frPos VARCHAR(10),
    toPos VARCHAR(10),
    szTp VARCHAR(10),
    ordTime VARCHAR(20),
    wkTime VARCHAR(20),
    jobState VARCHAR(50),
    evntTime VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_wkTime (wkTime),
    INDEX idx_ytNo (ytNo)
);

-- =====================================================
-- 4. 선석 계획 (0건 - 데이터 없음)
-- =====================================================
-- berth_schedule 테이블 (JSON 응답 컬럼에 맞춰 업데이트)
DROP TABLE IF EXISTS berth_schedule;
CREATE TABLE berth_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50),
    yr VARCHAR(10),
    no VARCHAR(20),
    spCall VARCHAR(50),
    tmnlId VARCHAR(20),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    callNo VARCHAR(10),
    shpNm VARCHAR(100),
    tmnlNm VARCHAR(100),
    operCd VARCHAR(20),
    berthNo VARCHAR(20),
    psId VARCHAR(10),
    bitFr VARCHAR(50),
    bitTo VARCHAR(50),
    disCnt DECIMAL(10,2),
    lodCnt DECIMAL(10,2),
    jobDt VARCHAR(20),
    eta VARCHAR(20),
    etb VARCHAR(20),
    etw VARCHAR(20),
    etc VARCHAR(20),
    etd VARCHAR(20),
    ata VARCHAR(20),
    atb VARCHAR(20),
    atw VARCHAR(20),
    atc VARCHAR(20),
    atd VARCHAR(20),
    cct VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_callYr (callYr),
    INDEX idx_timeFrom (eta),
    INDEX idx_timeTo (etd)
) COMMENT='예상 레코드 수: 1개';

-- =====================================================
-- 5. AIS 정보 (898건) - 기존 테이블 업데이트
-- =====================================================
DROP TABLE IF EXISTS ais_info;
CREATE TABLE ais_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mmsiNo VARCHAR(20),
    imoNo VARCHAR(20),
    vsslNm VARCHAR(200),
    callLetter VARCHAR(20),
    vsslTp VARCHAR(100),
    vsslTpCd VARCHAR(10),
    vsslTpCrgo VARCHAR(100),
    vsslCls VARCHAR(10),
    vsslLen DECIMAL(10,2),
    vsslWidth DECIMAL(10,2),
    flag VARCHAR(100),
    flagCd VARCHAR(10),
    vsslDefBrd DECIMAL(10,2),
    lon DECIMAL(15,10),
    lat DECIMAL(15,10),
    sog DECIMAL(8,2),
    cog DECIMAL(8,2),
    rot DECIMAL(8,2),
    headSide VARCHAR(10),
    vsslNavi VARCHAR(100),
    vsslNaviCd VARCHAR(10),
    source VARCHAR(50),
    dt_pos_utc VARCHAR(20),
    dt_static_utc VARCHAR(20),
    vsslTpMain VARCHAR(100),
    vsslTpSub VARCHAR(100),
    dstNm VARCHAR(100),
    dstCd VARCHAR(20),
    eta VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mmsiNo (mmsiNo),
    INDEX idx_imoNo (imoNo),
    INDEX idx_callLetter (callLetter),
    INDEX idx_dt_pos_utc (dt_pos_utc)
);

-- =====================================================
-- 6. 컨테이너 양적하정보 (1,012건) - 기존 테이블 업데이트
-- =====================================================
DROP TABLE IF EXISTS cntr_load_unload_info;
CREATE TABLE cntr_load_unload_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(10),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    cntrNo VARCHAR(20),
    tmnlNm VARCHAR(100),
    ix VARCHAR(50),
    ixdt VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_ixdt (ixdt)
);

-- =====================================================
-- 7. 컨테이너 신고상세정보 (1건)
-- =====================================================
DROP TABLE IF EXISTS cntr_report_detail;
CREATE TABLE cntr_report_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mrnNo VARCHAR(100),
    blNo VARCHAR(100),
    msnNo VARCHAR(50),
    cntrNo VARCHAR(20),
    cntrStd VARCHAR(20),
    cntrSize VARCHAR(10),
    cntrSealNo1 VARCHAR(50),
    cntrSealNo2 VARCHAR(50),
    cntrSealNo3 VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_mrnNo (mrnNo),
    INDEX idx_blNo (blNo),
    INDEX idx_cntrNo (cntrNo)
);

-- =====================================================
-- 8. 선박 입항신고정보 (1건)
-- =====================================================
DROP TABLE IF EXISTS vssl_entr_report;
CREATE TABLE vssl_entr_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    docTp VARCHAR(10),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    offrNm VARCHAR(100),
    rptDt VARCHAR(20),
    perfDt VARCHAR(20),
    berthPlcCd1 VARCHAR(10),
    berthPlcCd2 VARCHAR(10),
    berthPlcNm VARCHAR(100),
    nxtPrt2Cd VARCHAR(10),
    nxtPrt2Nm VARCHAR(100),
    nxtPrt1Cd VARCHAR(10),
    nxtPrt1Nm VARCHAR(100),
    crgTn DECIMAL(12,2),
    dngrCrgTn DECIMAL(12,2),
    grsTn DECIMAL(12,2),
    sailTpCd VARCHAR(10),
    ocCtCd VARCHAR(10),
    flagCd VARCHAR(10),
    flagNm VARCHAR(100),
    vsslTpCd VARCHAR(10),
    vsslTpNm VARCHAR(100),
    vsslNm VARCHAR(200),
    subCallLetter1 VARCHAR(20),
    subCallLetter2 VARCHAR(20),
    arvlDt VARCHAR(20),
    tugYn VARCHAR(10),
    pltYn VARCHAR(10),
    arvlObjCd VARCHAR(10),
    arvlObjNm VARCHAR(100),
    depPrt1Cd VARCHAR(10),
    depPrt1Nm VARCHAR(100),
    depPrt2Cd VARCHAR(10),
    depPrt2Nm VARCHAR(100),
    etdDt VARCHAR(20),
    lastPrtDepDt VARCHAR(20),
    lastPrt1Cd VARCHAR(10),
    lastPrt1Nm VARCHAR(100),
    lastPrt2Cd VARCHAR(10),
    lastPrt2Nm VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_arvlDt (arvlDt)
);

-- =====================================================
-- 9. 선박 출항신고정보 (1건)
-- =====================================================
DROP TABLE IF EXISTS vssl_dprt_report;
CREATE TABLE vssl_dprt_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    docTp VARCHAR(10),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    offrNm VARCHAR(100),
    rptDt VARCHAR(20),
    perfDt VARCHAR(20),
    berthPlcCd1 VARCHAR(10),
    berthPlcCd2 VARCHAR(10),
    berthPlcNm VARCHAR(100),
    nxtPrt2Cd VARCHAR(10),
    nxtPrt2Nm VARCHAR(100),
    nxtPrt1Cd VARCHAR(10),
    nxtPrt1Nm VARCHAR(100),
    crgTn DECIMAL(12,2),
    dngrCrgTn DECIMAL(12,2),
    grsTn DECIMAL(12,2),
    sailTpCd VARCHAR(10),
    sailTpNm VARCHAR(100),
    occtCd VARCHAR(10),
    occtNm VARCHAR(100),
    flagCd VARCHAR(10),
    flagNm VARCHAR(100),
    vsslTpCd VARCHAR(10),
    vsslTpNm VARCHAR(100),
    vsslNm VARCHAR(200),
    subCallLetter1 VARCHAR(20),
    subCallLetter2 VARCHAR(20),
    depDt VARCHAR(20),
    tugYn VARCHAR(10),
    pltYn VARCHAR(10),
    dstPrt2Cd VARCHAR(10),
    dstPrt2Nm VARCHAR(100),
    dstPrt1Cd VARCHAR(10),
    dstPrt1Nm VARCHAR(100),
    dstArvlDt VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_depDt (depDt)
);

-- =====================================================
-- 10. 관제정보 (VTCHistory) (2건)
-- =====================================================
DROP TABLE IF EXISTS vssl_history;
CREATE TABLE vssl_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    comCnt VARCHAR(10),
    typeCd VARCHAR(10),
    typeNm VARCHAR(100),
    comDt VARCHAR(20),
    comPlc1 VARCHAR(10),
    comPlc2 VARCHAR(10),
    comPlcNm VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_comDt (comDt)
);

-- =====================================================
-- 11. 외항통과선박신청정보 (1건)
-- =====================================================
DROP TABLE IF EXISTS vssl_pass_report;
CREATE TABLE vssl_pass_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    vsslNm VARCHAR(200),
    arvlObjCd VARCHAR(10),
    stayHr VARCHAR(10),
    anchorPlace VARCHAR(50),
    stayFr VARCHAR(20),
    stayTo VARCHAR(20),
    docTp VARCHAR(10),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    agentPic VARCHAR(100),
    appvlCd VARCHAR(10),
    rejectDt VARCHAR(20),
    rejectRsn TEXT,
    applyDt VARCHAR(20),
    processDt VARCHAR(20),
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_applyDt (applyDt)
);

-- =====================================================
-- 12. 화물반출입신고정보 (0건 - 데이터 없음)
-- =====================================================
-- cargo_imp_exp_report 테이블 (JSON 응답 컬럼에 맞춰 업데이트)
DROP TABLE IF EXISTS cargo_imp_exp_report;
CREATE TABLE cargo_imp_exp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    mrnNo VARCHAR(50),
    blNo VARCHAR(50),
    msnNo VARCHAR(20),
    vsslKey VARCHAR(50),
    prtAtNm VARCHAR(100),
    agentCd VARCHAR(20),
    agentNm VARCHAR(100),
    ioTpCd VARCHAR(10),
    ioTpNm VARCHAR(50),
    cargoTp VARCHAR(10),
    cargoTpNm VARCHAR(50),
    mailNm VARCHAR(200),
    kipNm VARCHAR(200),
    crgNm TEXT,
    itemCd VARCHAR(20),
    itemNm TEXT,
    dngrUnCd VARCHAR(20),
    trPackTpCd VARCHAR(10),
    stvMtdCd VARCHAR(10),
    stvMtdNm VARCHAR(100),
    msrTnTp VARCHAR(10),
    msrTnTpNm VARCHAR(100),
    msrTn DECIMAL(10,2),
    wgtTn DECIMAL(10,2),
    msrCm DECIMAL(10,2),
    wgtKg DECIMAL(12,2),
    bulkMsrCm DECIMAL(10,2),
    bulkWgtKg DECIMAL(12,2),
    conQty INT,
    ldPrtCd VARCHAR(20),
    ldPrtNm VARCHAR(100),
    unldPrtCd VARCHAR(20),
    unldPrtNm VARCHAR(100),
    ioDt VARCHAR(20),
    flagCd VARCHAR(10),
    flagNm VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_callYr (callYr),
    INDEX idx_mrnNo (mrnNo),
    INDEX idx_blNo (blNo),
    INDEX idx_vsslKey (vsslKey)
) COMMENT='예상 레코드 수: 5,504개';

-- =====================================================
-- 13. 화물품목코드 (1건)
-- =====================================================
DROP TABLE IF EXISTS cargo_item_code;
CREATE TABLE cargo_item_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crgItemCd VARCHAR(20),
    crgItemCdNmShort VARCHAR(200),
    crgItemCdNmEShort VARCHAR(200),
    crgItemNm VARCHAR(200),
    crgItemNmE VARCHAR(200),
    cgItemCd VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_crgItemCd (crgItemCd)
);

-- =====================================================
-- 14. 위험물반입신고서 (1건)
-- =====================================================
DROP TABLE IF EXISTS dg_imp_report;
CREATE TABLE dg_imp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    vsslNm VARCHAR(200),
    inTp VARCHAR(10),
    wrkNo VARCHAR(50),
    agentCd VARCHAR(20),
    rptDt VARCHAR(20),
    bfRpt1Cd VARCHAR(10),
    bfRpt1Nm VARCHAR(100),
    bfRpt2Cd VARCHAR(10),
    bfRpt2Nm VARCHAR(100),
    conQty INT,
    crgNm VARCHAR(200),
    crgTpCd1 VARCHAR(10),
    crgTpCd2 VARCHAR(10),
    crgTpNm1 VARCHAR(100),
    crgTpNm2 VARCHAR(100),
    msrTnTp VARCHAR(10),
    msrUnit VARCHAR(10),
    qty DECIMAL(12,3),
    useTrgt1 VARCHAR(100),
    useTrgt2 VARCHAR(100),
    dgObjYn VARCHAR(10),
    rptNth VARCHAR(10),
    perfDt VARCHAR(20),
    stvCoCd VARCHAR(20),
    stvCoNm VARCHAR(200),
    useObj1 VARCHAR(10),
    useObj2 VARCHAR(10),
    wrkDtFr VARCHAR(20),
    wrkDtTo VARCHAR(20),
    wrkPlc1 VARCHAR(10),
    wrkPlc2 VARCHAR(10),
    useObj1Nm VARCHAR(100),
    useObj2Nm VARCHAR(100),
    ocCtCd VARCHAR(10),
    returnDt VARCHAR(20),
    returnRsn TEXT,
    crgDblYn VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_rptDt (rptDt)
);

-- =====================================================
-- 15. 위험물 적하알림표 (0건 - 데이터 없음)
-- =====================================================
-- dg_manifest 테이블 (JSON 응답 컬럼에 맞춰 업데이트)
DROP TABLE IF EXISTS dg_manifest;
CREATE TABLE dg_manifest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    cntrNo VARCHAR(20),
    vsslKey VARCHAR(50),
    prtAtNm VARCHAR(100),
    vsslNm VARCHAR(100),
    inTp VARCHAR(10),
    wrkNo VARCHAR(50),
    repNo VARCHAR(100),
    docSeq VARCHAR(20),
    agentCd VARCHAR(20),
    agentNm VARCHAR(100),
    rptDt VARCHAR(20),
    dngrUnCd VARCHAR(20),
    wrkTp VARCHAR(10),
    blNo VARCHAR(100),
    classCd VARCHAR(20),
    crgTp TEXT,
    kipNm VARCHAR(200),
    mailNm VARCHAR(200),
    msrTnTp VARCHAR(10),
    msrUnit VARCHAR(20),
    qty VARCHAR(50),
    wrkPlc1 VARCHAR(50),
    wrkPlc2 VARCHAR(50),
    dngrInDt VARCHAR(20),
    dngrWrkTpNm VARCHAR(100),
    consTp VARCHAR(10),
    cargoTp VARCHAR(10),
    dngrYn VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_callYr (callYr),
    INDEX idx_cntrNo (cntrNo),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_repNo (repNo)
) COMMENT='예상 레코드 수: 40개';

-- =====================================================
-- 16. 항만시설사용 신청/결과정보 (1건)
-- =====================================================
DROP TABLE IF EXISTS fac_use_statement;
CREATE TABLE fac_use_statement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    useNo VARCHAR(10),
    vsslKey VARCHAR(20),
    prtAtNm VARCHAR(100),
    vsslNm VARCHAR(200),
    reqFacCd VARCHAR(10),
    reqFacSubCd VARCHAR(10),
    reqFacNm VARCHAR(100),
    allotFacCd VARCHAR(10),
    allotFacSubCd VARCHAR(10),
    allotFacNm VARCHAR(100),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    ocCtCd VARCHAR(10),
    useObjCd VARCHAR(10),
    useObjNm VARCHAR(100),
    useScrDtFr VARCHAR(20),
    useScrDtTo VARCHAR(20),
    allotDtFr VARCHAR(20),
    allotDtTo VARCHAR(20),
    useDtFr VARCHAR(20),
    useDtTo VARCHAR(20),
    vsslTpCd VARCHAR(10),
    vsslTpNm VARCHAR(100),
    apprvlRsn TEXT,
    apprvlCd VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_useDtFr (useDtFr)
);

-- =====================================================
-- 17. 항만시설사용신고정보-화물료 (1건)
-- =====================================================
DROP TABLE IF EXISTS fac_use_stmt_bill;
CREATE TABLE fac_use_stmt_bill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKey VARCHAR(20),
    useTp VARCHAR(10),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    facCd VARCHAR(10),
    facSubCd VARCHAR(10),
    facNm VARCHAR(100),
    ioDt VARCHAR(20),
    notifyDt VARCHAR(20),
    fiscalYr VARCHAR(4),
    billNo VARCHAR(20),
    feeTp VARCHAR(10),
    feeTpNm VARCHAR(100),
    dueDt VARCHAR(20),
    totalFee VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_billNo (billNo)
);

-- =====================================================
-- 18. 선박보안인증서 통보 (1건)
-- =====================================================
DROP TABLE IF EXISTS vssl_sec_isps_info;
CREATE TABLE vssl_sec_isps_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    prtAtNm VARCHAR(100),
    vsslKey VARCHAR(20),
    vsslNm VARCHAR(200),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    imoNo VARCHAR(20),
    rptDt VARCHAR(20),
    vsslSecLevel VARCHAR(10),
    ispsNo VARCHAR(100),
    ispsOff VARCHAR(100),
    ispsIssueFlag VARCHAR(10),
    ispsIssueFlagNm VARCHAR(100),
    ispsValidFromDt VARCHAR(20),
    ispsValidToDt VARCHAR(20),
    resultYn VARCHAR(10),
    perfDt VARCHAR(20),
    resultTx TEXT,
    returnDt VARCHAR(20),
    returnRsn TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_ispsNo (ispsNo)
);

-- =====================================================
-- 19. 선박보안인증서 통보 경유지 정보 (10건)
-- =====================================================
DROP TABLE IF EXISTS vssl_sec_port_info;
CREATE TABLE vssl_sec_port_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    prtAtNm VARCHAR(100),
    seqNo VARCHAR(10),
    vsslKey VARCHAR(20),
    vsslNm VARCHAR(200),
    bfPrt1Cd VARCHAR(10),
    bfPrt1Nm VARCHAR(100),
    bfPrt2Cd VARCHAR(10),
    bfPrt2Nm VARCHAR(100),
    arvlDt VARCHAR(20),
    depDt VARCHAR(20),
    vsslSecLevel VARCHAR(10),
    vsslSecLevelNm VARCHAR(100),
    portSecLevel VARCHAR(10),
    portSecLevelNm VARCHAR(100),
    remark TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_seqNo (seqNo)
);

-- =====================================================
-- 20. 선박양적하 시작종료정보 (2건)
-- =====================================================
DROP TABLE IF EXISTS load_unload_from_to_info;
CREATE TABLE load_unload_from_to_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(10),
    shpCd VARCHAR(10),
    callYr VARCHAR(4),
    callNo VARCHAR(10),
    wkId VARCHAR(50),
    tmnlNm VARCHAR(100),
    shpNm VARCHAR(200),
    disBeginDt VARCHAR(20),
    disEndDt VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_tmnlId (tmnlId),
    INDEX idx_shpCd (shpCd),
    INDEX idx_disBeginDt (disBeginDt)
);

-- =====================================================
-- 21. 제재대상선박 정보 (2건)
-- =====================================================
DROP TABLE IF EXISTS vssl_sanction_info;
CREATE TABLE vssl_sanction_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(10),
    callLetter VARCHAR(20),
    vsslKey VARCHAR(20),
    penaltyCd VARCHAR(10),
    callYr VARCHAR(4),
    serNo VARCHAR(10),
    vsslKorNm VARCHAR(200),
    penaltyNm TEXT,
    imoNo VARCHAR(20),
    flag VARCHAR(10),
    flagNm VARCHAR(100),
    agentCd VARCHAR(20),
    agentNm VARCHAR(200),
    shpOwnerNm VARCHAR(200),
    grsTn DECIMAL(12,2),
    vsslLen DECIMAL(10,2),
    vsslNo VARCHAR(20),
    perfDt VARCHAR(20),
    adminDetail TEXT,
    penaltyRqrPlc VARCHAR(10),
    penaltyRqrPlcDetail VARCHAR(200),
    rglt TEXT,
    penaltyFr VARCHAR(20),
    penaltyTo VARCHAR(20),
    remark TEXT,
    icdtNum VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_prtAtCd (prtAtCd),
    INDEX idx_callLetter (callLetter),
    INDEX idx_vsslKey (vsslKey),
    INDEX idx_penaltyCd (penaltyCd)
);

-- =====================================================
-- 22. 국가코드 (1건)
-- =====================================================
DROP TABLE IF EXISTS country_code;
CREATE TABLE country_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cntryCd VARCHAR(10),
    cntryEngNm VARCHAR(200),
    cntryKorNm VARCHAR(200),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cntryCd (cntryCd)
);

-- =====================================================
-- 23. 입항목적코드 (1건)
-- =====================================================
DROP TABLE IF EXISTS vssl_entr_intn_code;
CREATE TABLE vssl_entr_intn_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vsslEntrIntnCd VARCHAR(10),
    vsslEntrIntnNm VARCHAR(100),
    vsslEntrIntnNmng VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_vsslEntrIntnCd (vsslEntrIntnCd)
);

-- =====================================================
-- 24. 항구청코드 (1건)
-- =====================================================
DROP TABLE IF EXISTS pa_code;
CREATE TABLE pa_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paCd VARCHAR(10),
    paCdEng VARCHAR(10),
    paNm VARCHAR(100),
    paNmEng VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_paCd (paCd)
);

-- =====================================================
-- 25. 항구코드 (1건)
-- =====================================================
DROP TABLE IF EXISTS port_code;
CREATE TABLE port_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    natCd VARCHAR(10),
    portCd VARCHAR(20),
    natNm VARCHAR(100),
    natPortCd VARCHAR(20),
    portNm VARCHAR(200),
    portNmE VARCHAR(200),
    loctCd VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_natCd (natCd),
    INDEX idx_portCd (portCd)
);

-- =====================================================
-- 테이블 생성 완료 확인
-- =====================================================
SELECT 
    table_name,
    table_rows,
    data_length,
    index_length
FROM information_schema.tables 
WHERE table_schema = 'port_database'
ORDER BY table_name;

-- =====================================================
-- 주요 테이블별 레코드 수 예상
-- =====================================================
/*
tc_work_info: 188,880건 (TC 작업 정보)
qc_work_info: 90,793건 (QC 작업 정보)  
yt_work_info: 85,872건 (YT 작업 정보)
ais_info: 898건 (AIS 정보)
cntr_load_unload_info: 1,012건 (컨테이너 양적하정보)
cntr_report_detail: 1건 (컨테이너 신고상세정보)
vssl_entr_report: 1건 (선박 입항신고정보)
vssl_dprt_report: 1건 (선박 출항신고정보)
vssl_history: 2건 (관제정보)
vssl_pass_report: 1건 (외항통과선박신청정보)
cargo_imp_exp_report: 5,504건 (화물반출입신고정보)
cargo_item_code: 1건 (화물품목코드)
dg_imp_report: 1건 (위험물반입신고서)
dg_manifest: 40건 (위험물 적하알림표)
fac_use_statement: 1건 (항만시설사용 신청/결과정보)
fac_use_stmt_bill: 1건 (항만시설사용신고정보-화물료)
vssl_sec_isps_info: 1건 (선박보안인증서 통보)
vssl_sec_port_info: 10건 (선박보안인증서 통보 경유지 정보)
load_unload_from_to_info: 2건 (선박양적하 시작종료정보)
vssl_sanction_info: 2건 (제재대상선박 정보)
country_code: 1건 (국가코드)
vssl_entr_intn_code: 1건 (입항목적코드)
pa_code: 1건 (항구청코드)
port_code: 1건 (항구코드)
berth_schedule: 1건 (선석 계획)
*/
