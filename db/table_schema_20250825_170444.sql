-- tc_work_info 테이블 생성
CREATE TABLE IF NOT EXISTS tc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    tcNo VARCHAR(255),
    cntrNo VARCHAR(255),
    tmnlNm VARCHAR(255),
    shpNm VARCHAR(255),
    wkId VARCHAR(255),
    jobNo VARCHAR(255),
    szTp VARCHAR(255),
    ytNo VARCHAR(255),
    rtNo VARCHAR(255),
    block VARCHAR(255),
    bay VARCHAR(255),
    roww VARCHAR(255),
    ordTime VARCHAR(255),
    wkTime VARCHAR(255),
    jobState VARCHAR(255),
    evntTime VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- qc_work_info 테이블 생성
CREATE TABLE IF NOT EXISTS qc_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    qcNo VARCHAR(255),
    cntrNo VARCHAR(255),
    ytNo VARCHAR(255),
    shpNm VARCHAR(255),
    tmnlNm VARCHAR(255),
    fmId VARCHAR(255),
    wkId VARCHAR(255),
    disBay VARCHAR(255),
    disRow VARCHAR(255),
    disTier VARCHAR(255),
    disHd VARCHAR(255),
    lodBay VARCHAR(255),
    lodRow VARCHAR(255),
    lodTier VARCHAR(255),
    lodHd VARCHAR(255),
    szTp VARCHAR(255),
    ordTime VARCHAR(255),
    wkTime VARCHAR(255),
    jobState VARCHAR(255),
    evntTime VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- yt_work_info 테이블 생성
CREATE TABLE IF NOT EXISTS yt_work_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    ytNo VARCHAR(255),
    cntrNo VARCHAR(255),
    tmnlNm VARCHAR(255),
    shpNm VARCHAR(255),
    wkId VARCHAR(255),
    jobNo VARCHAR(255),
    frPos VARCHAR(255),
    toPos VARCHAR(255),
    szTp VARCHAR(255),
    ordTime VARCHAR(255),
    wkTime VARCHAR(255),
    jobState VARCHAR(255),
    evntTime VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- berth_schedule 테이블 생성
CREATE TABLE IF NOT EXISTS berth_schedule (
    id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(255),
    yr VARCHAR(255),
    no VARCHAR(255),
    spCall VARCHAR(255),
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    callNo VARCHAR(255),
    shpNm VARCHAR(255),
    tmnlNm VARCHAR(255),
    operCd VARCHAR(255),
    berthNo VARCHAR(255),
    psId VARCHAR(255),
    bitFr VARCHAR(255),
    bitTo VARCHAR(255),
    disCnt DECIMAL(15,6),
    lodCnt DECIMAL(15,6),
    jobDt VARCHAR(255),
    eta VARCHAR(255),
    etb VARCHAR(255),
    etw VARCHAR(255),
    etc VARCHAR(255),
    etd VARCHAR(255),
    ata VARCHAR(255),
    atb VARCHAR(255),
    atw VARCHAR(255),
    atc VARCHAR(255),
    atd VARCHAR(255),
    cct VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ais_info 테이블 생성
CREATE TABLE IF NOT EXISTS ais_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mmsiNo VARCHAR(255),
    imoNo VARCHAR(255),
    vsslNm VARCHAR(255),
    callLetter VARCHAR(255),
    vsslTp VARCHAR(255),
    vsslTpCd VARCHAR(255),
    vsslTpCrgo VARCHAR(255),
    vsslCls VARCHAR(255),
    vsslLen DECIMAL(15,6),
    vsslWidth DECIMAL(15,6),
    flag VARCHAR(255),
    flagCd VARCHAR(255),
    vsslDefBrd VARCHAR(255),
    lon VARCHAR(255),
    lat VARCHAR(255),
    sog VARCHAR(255),
    cog VARCHAR(255),
    rot VARCHAR(255),
    headSide VARCHAR(255),
    vsslNavi VARCHAR(255),
    vsslNaviCd VARCHAR(255),
    source VARCHAR(255),
    dt_pos_utc VARCHAR(255),
    dt_static_utc VARCHAR(255),
    vsslTpMain VARCHAR(255),
    vsslTpSub VARCHAR(255),
    dstNm VARCHAR(255),
    dstCd VARCHAR(255),
    eta VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- cntr_load_unload_info 테이블 생성
CREATE TABLE IF NOT EXISTS cntr_load_unload_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    cntrNo VARCHAR(255),
    tmnlNm VARCHAR(255),
    ix VARCHAR(255),
    ixdt VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- cntr_report_detail 테이블 생성
CREATE TABLE IF NOT EXISTS cntr_report_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mrnNo VARCHAR(255),
    blNo VARCHAR(255),
    msnNo VARCHAR(255),
    cntrNo VARCHAR(255),
    cntrStd VARCHAR(255),
    cntrSize VARCHAR(255),
    cntrSealNo1 VARCHAR(255),
    cntrSealNo2 VARCHAR(255),
    cntrSealNo3 VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_entr_report 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_entr_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    docTp VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    offrNm VARCHAR(255),
    rptDt VARCHAR(255),
    perfDt VARCHAR(255),
    berthPlcCd1 VARCHAR(255),
    berthPlcCd2 VARCHAR(255),
    berthPlcNm VARCHAR(255),
    nxtPrt2Cd VARCHAR(255),
    nxtPrt2Nm VARCHAR(255),
    nxtPrt1Cd VARCHAR(255),
    nxtPrt1Nm VARCHAR(255),
    crgTn DECIMAL(15,6),
    dngrCrgTn DECIMAL(15,6),
    grsTn DECIMAL(15,6),
    sailTpCd VARCHAR(255),
    ocCtCd VARCHAR(255),
    flagCd VARCHAR(255),
    flagNm VARCHAR(255),
    vsslTpCd VARCHAR(255),
    vsslTpNm VARCHAR(255),
    vsslNm VARCHAR(255),
    subCallLetter1 VARCHAR(255),
    subCallLetter2 VARCHAR(255),
    arvlDt VARCHAR(255),
    tugYn VARCHAR(255),
    pltYn VARCHAR(255),
    arvlObjCd VARCHAR(255),
    arvlObjNm VARCHAR(255),
    depPrt1Cd VARCHAR(255),
    depPrt1Nm VARCHAR(255),
    depPrt2Cd VARCHAR(255),
    depPrt2Nm VARCHAR(255),
    etdDt VARCHAR(255),
    lastPrtDepDt VARCHAR(255),
    lastPrt1Cd VARCHAR(255),
    lastPrt1Nm VARCHAR(255),
    lastPrt2Cd VARCHAR(255),
    lastPrt2Nm VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_dprt_report 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_dprt_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    docTp VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    offrNm VARCHAR(255),
    rptDt VARCHAR(255),
    perfDt VARCHAR(255),
    berthPlcCd1 VARCHAR(255),
    berthPlcCd2 VARCHAR(255),
    berthPlcNm VARCHAR(255),
    nxtPrt2Cd VARCHAR(255),
    nxtPrt2Nm VARCHAR(255),
    nxtPrt1Cd VARCHAR(255),
    nxtPrt1Nm VARCHAR(255),
    crgTn DECIMAL(15,6),
    dngrCrgTn DECIMAL(15,6),
    grsTn DECIMAL(15,6),
    sailTpCd VARCHAR(255),
    sailTpNm VARCHAR(255),
    occtCd VARCHAR(255),
    occtNm VARCHAR(255),
    flagCd VARCHAR(255),
    flagNm VARCHAR(255),
    vsslTpCd VARCHAR(255),
    vsslTpNm VARCHAR(255),
    vsslNm VARCHAR(255),
    subCallLetter1 VARCHAR(255),
    subCallLetter2 VARCHAR(255),
    depDt VARCHAR(255),
    tugYn VARCHAR(255),
    pltYn VARCHAR(255),
    dstPrt2Cd VARCHAR(255),
    dstPrt2Nm VARCHAR(255),
    dstPrt1Cd VARCHAR(255),
    dstPrt1Nm VARCHAR(255),
    dstArvlDt VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_history 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    comCnt VARCHAR(255),
    typeCd VARCHAR(255),
    typeNm VARCHAR(255),
    comDt VARCHAR(255),
    comPlc1 VARCHAR(255),
    comPlc2 VARCHAR(255),
    comPlcNm VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_pass_report 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_pass_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    vsslNm VARCHAR(255),
    arvlObjCd VARCHAR(255),
    stayHr VARCHAR(255),
    anchorPlace VARCHAR(255),
    stayFr VARCHAR(255),
    stayTo VARCHAR(255),
    docTp VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    agentPic VARCHAR(255),
    appvlCd VARCHAR(255),
    rejectDt VARCHAR(255),
    rejectRsn VARCHAR(255),
    applyDt VARCHAR(255),
    processDt VARCHAR(255),
    remark VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- cargo_imp_exp_report 테이블 생성
CREATE TABLE IF NOT EXISTS cargo_imp_exp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    mrnNo VARCHAR(255),
    blNo VARCHAR(255),
    msnNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    ioTpCd VARCHAR(255),
    ioTpNm VARCHAR(255),
    cargoTp VARCHAR(255),
    cargoTpNm VARCHAR(255),
    mailNm VARCHAR(255),
    kipNm VARCHAR(255),
    crgNm VARCHAR(255),
    itemCd VARCHAR(255),
    itemNm VARCHAR(255),
    dngrUnCd VARCHAR(255),
    trPackTpCd VARCHAR(255),
    stvMtdCd VARCHAR(255),
    stvMtdNm VARCHAR(255),
    msrTnTp VARCHAR(255),
    msrTnTpNm VARCHAR(255),
    msrTn DECIMAL(15,6),
    wgtTn DECIMAL(15,6),
    msrCm DECIMAL(15,6),
    wgtKg DECIMAL(15,6),
    bulkMsrCm DECIMAL(15,6),
    bulkWgtKg DECIMAL(15,6),
    conQty INT,
    ldPrtCd VARCHAR(255),
    ldPrtNm VARCHAR(255),
    unldPrtCd VARCHAR(255),
    unldPrtNm VARCHAR(255),
    ioDt VARCHAR(255),
    flagCd VARCHAR(255),
    flagNm VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- cargo_item_code 테이블 생성
CREATE TABLE IF NOT EXISTS cargo_item_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    crgItemCd VARCHAR(255),
    crgItemCdNmShort VARCHAR(255),
    crgItemCdNmEShort VARCHAR(255),
    crgItemNm VARCHAR(255),
    crgItemNmE VARCHAR(255),
    cgItemCd VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- dg_imp_report 테이블 생성
CREATE TABLE IF NOT EXISTS dg_imp_report (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    vsslNm VARCHAR(255),
    inTp VARCHAR(255),
    wrkNo VARCHAR(255),
    agentCd VARCHAR(255),
    rptDt VARCHAR(255),
    bfRpt1Cd VARCHAR(255),
    bfRpt1Nm VARCHAR(255),
    bfRpt2Cd VARCHAR(255),
    bfRpt2Nm VARCHAR(255),
    conQty INT,
    crgNm VARCHAR(255),
    crgTpCd1 VARCHAR(255),
    crgTpCd2 VARCHAR(255),
    crgTpNm1 VARCHAR(255),
    crgTpNm2 VARCHAR(255),
    msrTnTp VARCHAR(255),
    msrUnit VARCHAR(255),
    qty DECIMAL(15,6),
    useTrgt1 VARCHAR(255),
    useTrgt2 VARCHAR(255),
    dgObjYn VARCHAR(255),
    rptNth VARCHAR(255),
    perfDt VARCHAR(255),
    stvCoCd VARCHAR(255),
    stvCoNm VARCHAR(255),
    useObj1 VARCHAR(255),
    useObj2 VARCHAR(255),
    wrkDtFr VARCHAR(255),
    wrkDtTo VARCHAR(255),
    wrkPlc1 VARCHAR(255),
    wrkPlc2 VARCHAR(255),
    useObj1Nm VARCHAR(255),
    useObj2Nm VARCHAR(255),
    ocCtCd VARCHAR(255),
    returnDt VARCHAR(255),
    returnRsn VARCHAR(255),
    crgDblYn VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- dg_manifest 테이블 생성
CREATE TABLE IF NOT EXISTS dg_manifest (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    cntrNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    vsslNm VARCHAR(255),
    inTp VARCHAR(255),
    wrkNo VARCHAR(255),
    repNo VARCHAR(255),
    docSeq VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    rptDt VARCHAR(255),
    dngrUnCd VARCHAR(255),
    wrkTp VARCHAR(255),
    blNo VARCHAR(255),
    classCd VARCHAR(255),
    crgTp VARCHAR(255),
    kipNm VARCHAR(255),
    mailNm VARCHAR(255),
    msrTnTp VARCHAR(255),
    msrUnit VARCHAR(255),
    qty VARCHAR(255),
    wrkPlc1 VARCHAR(255),
    wrkPlc2 VARCHAR(255),
    dngrInDt VARCHAR(255),
    dngrWrkTpNm VARCHAR(255),
    consTp VARCHAR(255),
    cargoTp VARCHAR(255),
    dngrYn VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- fac_use_statement 테이블 생성
CREATE TABLE IF NOT EXISTS fac_use_statement (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    useNo VARCHAR(255),
    vsslKey VARCHAR(255),
    prtAtNm VARCHAR(255),
    vsslNm VARCHAR(255),
    reqFacCd VARCHAR(255),
    reqFacSubCd VARCHAR(255),
    reqFacNm VARCHAR(255),
    allotFacCd VARCHAR(255),
    allotFacSubCd VARCHAR(255),
    allotFacNm VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    ocCtCd VARCHAR(255),
    useObjCd VARCHAR(255),
    useObjNm VARCHAR(255),
    useScrDtFr VARCHAR(255),
    useScrDtTo VARCHAR(255),
    allotDtFr VARCHAR(255),
    allotDtTo VARCHAR(255),
    useDtFr VARCHAR(255),
    useDtTo VARCHAR(255),
    vsslTpCd VARCHAR(255),
    vsslTpNm VARCHAR(255),
    apprvlRsn VARCHAR(255),
    apprvlCd VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- fac_use_stmt_bill 테이블 생성
CREATE TABLE IF NOT EXISTS fac_use_stmt_bill (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKey VARCHAR(255),
    useTp VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    facCd VARCHAR(255),
    facSubCd VARCHAR(255),
    facNm VARCHAR(255),
    ioDt VARCHAR(255),
    notifyDt VARCHAR(255),
    fiscalYr VARCHAR(255),
    billNo VARCHAR(255),
    feeTp VARCHAR(255),
    feeTpNm VARCHAR(255),
    dueDt VARCHAR(255),
    totalFee VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_sec_isps_info 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_sec_isps_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    prtAtNm VARCHAR(255),
    vsslKey VARCHAR(255),
    vsslNm VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    imoNo VARCHAR(255),
    rptDt VARCHAR(255),
    vsslSecLevel VARCHAR(255),
    ispsNo VARCHAR(255),
    ispsOff VARCHAR(255),
    ispsIssueFlag VARCHAR(255),
    ispsIssueFlagNm VARCHAR(255),
    ispsValidFromDt VARCHAR(255),
    ispsValidToDt VARCHAR(255),
    resultYn VARCHAR(255),
    perfDt VARCHAR(255),
    resultTx VARCHAR(255),
    returnDt VARCHAR(255),
    returnRsn VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_sec_port_info 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_sec_port_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    prtAtNm VARCHAR(255),
    seqNo VARCHAR(255),
    vsslKey VARCHAR(255),
    vsslNm VARCHAR(255),
    bfPrt1Cd VARCHAR(255),
    bfPrt1Nm VARCHAR(255),
    bfPrt2Cd VARCHAR(255),
    bfPrt2Nm VARCHAR(255),
    arvlDt VARCHAR(255),
    depDt VARCHAR(255),
    vsslSecLevel VARCHAR(255),
    vsslSecLevelNm VARCHAR(255),
    portSecLevel VARCHAR(255),
    portSecLevelNm VARCHAR(255),
    remark VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- load_unload_from_to_info 테이블 생성
CREATE TABLE IF NOT EXISTS load_unload_from_to_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tmnlId VARCHAR(255),
    shpCd VARCHAR(255),
    callYr VARCHAR(255),
    callNo VARCHAR(255),
    wkId VARCHAR(255),
    tmnlNm VARCHAR(255),
    shpNm VARCHAR(255),
    disBeginDt VARCHAR(255),
    disEndDt VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_sanction_info 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_sanction_info (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prtAtCd VARCHAR(255),
    callLetter VARCHAR(255),
    vsslKey VARCHAR(255),
    penaltyCd VARCHAR(255),
    callYr VARCHAR(255),
    serNo VARCHAR(255),
    vsslKorNm VARCHAR(255),
    penaltyNm VARCHAR(255),
    imoNo VARCHAR(255),
    flag VARCHAR(255),
    flagNm VARCHAR(255),
    agentCd VARCHAR(255),
    agentNm VARCHAR(255),
    shpOwnerNm VARCHAR(255),
    grsTn DECIMAL(15,6),
    vsslLen DECIMAL(15,6),
    vsslNo VARCHAR(255),
    perfDt VARCHAR(255),
    adminDetail VARCHAR(255),
    penaltyRqrPlc VARCHAR(255),
    penaltyRqrPlcDetail VARCHAR(255),
    rglt VARCHAR(255),
    penaltyFr VARCHAR(255),
    penaltyTo VARCHAR(255),
    remark VARCHAR(255),
    icdtNum VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- country_code 테이블 생성
CREATE TABLE IF NOT EXISTS country_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cntryCd VARCHAR(255),
    cntryEngNm VARCHAR(255),
    cntryKorNm VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- vssl_entr_intn_code 테이블 생성
CREATE TABLE IF NOT EXISTS vssl_entr_intn_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vsslEntrIntnCd VARCHAR(255),
    vsslEntrIntnNm VARCHAR(255),
    vsslEntrIntnNmng VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- pa_code 테이블 생성
CREATE TABLE IF NOT EXISTS pa_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    paCd VARCHAR(255),
    paCdEng VARCHAR(255),
    paNm VARCHAR(255),
    paNmEng VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- port_code 테이블 생성
CREATE TABLE IF NOT EXISTS port_code (
    id INT AUTO_INCREMENT PRIMARY KEY,
    natCd VARCHAR(255),
    portCd VARCHAR(255),
    natNm VARCHAR(255),
    natPortCd VARCHAR(255),
    portNm VARCHAR(255),
    portNmE VARCHAR(255),
    loctCd VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

