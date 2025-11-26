#!/usr/bin/env python3
"""
DB 동기화 관리 서비스

API 응답 데이터를 port_database의 해당 테이블에 저장하고 관리합니다.
업데이트된 DB 구조 (25개 테이블)에 맞게 최적화되었습니다.
"""

import logging
import pymysql
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class DBSyncManager:
    """DB 동기화 관리"""
    
    def __init__(self, host: str = "localhost", port: int = 3307, 
                 user: str = "root", password: str = "", database: str = "port_database",
                 charset: str = "utf8mb4", autocommit: bool = True):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.autocommit = autocommit
        self.connection = None
        
        # 업데이트된 테이블 목록 (28개)
        self.all_tables = [
            "tc_work_info", "qc_work_info", "yt_work_info", "berth_schedule",
            "ais_info", "cntr_load_unload_info", "cntr_report_detail",
            "vssl_entr_report", "vssl_dprt_report", "vssl_history",
            "vssl_pass_report", "vssl_spec_info", "cargo_imp_exp_report", "cargo_item_code",
            "dg_imp_report", "dg_manifest", "fac_use_statement",
            "fac_use_stmt_bill", "vssl_sec_isps_info", "vssl_sec_port_info",
            "load_unload_from_to_info", "vssl_sanction_info", "country_code",
            "vssl_entr_intn_code", "pa_code", "port_code",
            "vssl_Tos_VsslNo", "vssl_Port_VsslNo"
        ]
        
    def connect(self) -> bool:
        """DB 연결"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                autocommit=self.autocommit
            )
            logger.info(f"✅ DB 연결 성공: {self.host}:{self.port}/{self.database}")
            return True
        except Exception as e:
            logger.error(f"❌ DB 연결 실패: {e}")
            return False
    
    def disconnect(self):
        """DB 연결 해제"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 DB 연결 해제")
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[Dict[str, Any]]]:
        """쿼리 실행"""
        try:
            if not self.connection or not self.connection.open:
                if not self.connect():
                    return None
            
            with self.connection.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return [{"affected_rows": cursor.rowcount}]
                    
        except Exception as e:
            logger.error(f"❌ 쿼리 실행 실패: {e}")
            logger.error(f"쿼리: {query}")
            if params:
                logger.error(f"파라미터: {params}")
            return None
    
    def _get_duplicate_update_clause(self, table_name: str, columns: List[str]) -> str:
        """테이블별 중복 처리 UPDATE 절 생성"""
        if table_name == "tc_work_info":
            # TC 작업정보: tmnlId + shpCd + callYr + serNo + tcNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    cntrNo = VALUES(cntrNo),
                    tmnlNm = VALUES(tmnlNm),
                    shpNm = VALUES(shpNm),
                    wkId = VALUES(wkId),
                    jobNo = VALUES(jobNo),
                    szTp = VALUES(szTp),
                    ytNo = VALUES(ytNo),
                    rtNo = VALUES(rtNo),
                    block = VALUES(block),
                    bay = VALUES(bay),
                    roww = VALUES(roww),
                    ordTime = VALUES(ordTime),
                    wkTime = VALUES(wkTime),
                    jobState = VALUES(jobState),
                    evntTime = VALUES(evntTime),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "qc_work_info":
            # QC 작업정보: tmnlId + shpCd + callYr + serNo + qcNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    cntrNo = VALUES(cntrNo),
                    ytNo = VALUES(ytNo),
                    shpNm = VALUES(shpNm),
                    tmnlNm = VALUES(tmnlNm),
                    fmId = VALUES(fmId),
                    wkId = VALUES(wkId),
                    disBay = VALUES(disBay),
                    disRow = VALUES(disRow),
                    disTier = VALUES(disTier),
                    disHd = VALUES(disHd),
                    lodBay = VALUES(lodBay),
                    lodRow = VALUES(lodRow),
                    lodTier = VALUES(lodTier),
                    lodHd = VALUES(lodHd),
                    szTp = VALUES(szTp),
                    ordTime = VALUES(ordTime),
                    wkTime = VALUES(wkTime),
                    jobState = VALUES(jobState),
                    evntTime = VALUES(evntTime),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "yt_work_info":
            # YT 작업정보: tmnlId + shpCd + callYr + serNo + ytNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    cntrNo = VALUES(cntrNo),
                    tmnlNm = VALUES(tmnlNm),
                    shpNm = VALUES(shpNm),
                    wkId = VALUES(wkId),
                    jobNo = VALUES(jobNo),
                    frPos = VALUES(frPos),
                    toPos = VALUES(toPos),
                    szTp = VALUES(szTp),
                    ordTime = VALUES(ordTime),
                    wkTime = VALUES(wkTime),
                    jobState = VALUES(jobState),
                    evntTime = VALUES(evntTime),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "ais_info":
            # AIS 정보: mmsiNo + imoNo + callLetter로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslNm = VALUES(vsslNm),
                    vsslTp = VALUES(vsslTp),
                    vsslTpCd = VALUES(vsslTpCd),
                    vsslTpCrgo = VALUES(vsslTpCrgo),
                    vsslCls = VALUES(vsslCls),
                    vsslLen = VALUES(vsslLen),
                    vsslWidth = VALUES(vsslWidth),
                    flag = VALUES(flag),
                    flagCd = VALUES(flagCd),
                    vsslDefBrd = VALUES(vsslDefBrd),
                    lon = VALUES(lon),
                    lat = VALUES(lat),
                    sog = VALUES(sog),
                    cog = VALUES(cog),
                    rot = VALUES(rot),
                    headSide = VALUES(headSide),
                    vsslNavi = VALUES(vsslNavi),
                    vsslNaviCd = VALUES(vsslNaviCd),
                    source = VALUES(source),
                    dt_pos_utc = VALUES(dt_pos_utc),
                    dt_static_utc = VALUES(dt_static_utc),
                    vsslTpMain = VALUES(vsslTpMain),
                    vsslTpSub = VALUES(vsslTpSub),
                    dstNm = VALUES(dstNm),
                    dstCd = VALUES(dstCd),
                    eta = VALUES(eta),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "cntr_load_unload_info":
            # 컨테이너 양적하정보: tmnlId + shpCd + callYr + serNo + cntrNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    tmnlNm = VALUES(tmnlNm),
                    ix = VALUES(ix),
                    ixdt = VALUES(ixdt),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "cntr_report_detail":
            # 컨테이너 신고상세정보: mrnNo + msnNo + blNo + cntrNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    cntrStd = VALUES(cntrStd),
                    cntrSize = VALUES(cntrSize),
                    cntrSealNo1 = VALUES(cntrSealNo1),
                    cntrSealNo2 = VALUES(cntrSealNo2),
                    cntrSealNo3 = VALUES(cntrSealNo3),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_entr_report":
            # 선박 입항신고정보: prtAtCd + callLetter + callYr + serNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    docTp = VALUES(docTp),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    offrNm = VALUES(offrNm),
                    rptDt = VALUES(rptDt),
                    perfDt = VALUES(perfDt),
                    berthPlcCd1 = VALUES(berthPlcCd1),
                    berthPlcCd2 = VALUES(berthPlcCd2),
                    berthPlcNm = VALUES(berthPlcNm),
                    nxtPrt2Cd = VALUES(nxtPrt2Cd),
                    nxtPrt2Nm = VALUES(nxtPrt2Nm),
                    nxtPrt1Cd = VALUES(nxtPrt1Cd),
                    nxtPrt1Nm = VALUES(nxtPrt1Nm),
                    crgTn = VALUES(crgTn),
                    dngrCrgTn = VALUES(dngrCrgTn),
                    grsTn = VALUES(grsTn),
                    sailTpCd = VALUES(sailTpCd),
                    ocCtCd = VALUES(ocCtCd),
                    flagCd = VALUES(flagCd),
                    flagNm = VALUES(flagNm),
                    vsslTpCd = VALUES(vsslTpCd),
                    vsslTpNm = VALUES(vsslTpNm),
                    vsslNm = VALUES(vsslNm),
                    subCallLetter1 = VALUES(subCallLetter1),
                    subCallLetter2 = VALUES(subCallLetter2),
                    arvlDt = VALUES(arvlDt),
                    tugYn = VALUES(tugYn),
                    pltYn = VALUES(pltYn),
                    arvlObjCd = VALUES(arvlObjCd),
                    arvlObjNm = VALUES(arvlObjNm),
                    depPrt1Cd = VALUES(depPrt1Cd),
                    depPrt1Nm = VALUES(depPrt1Nm),
                    depPrt2Cd = VALUES(depPrt2Cd),
                    depPrt2Nm = VALUES(depPrt2Nm),
                    etdDt = VALUES(etdDt),
                    lastPrtDepDt = VALUES(lastPrtDepDt),
                    lastPrt1Cd = VALUES(lastPrt1Cd),
                    lastPrt1Nm = VALUES(lastPrt1Nm),
                    lastPrt2Cd = VALUES(lastPrt2Cd),
                    lastPrt2Nm = VALUES(lastPrt2Nm),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_dprt_report":
            # 선박 출항신고정보: prtAtCd + callLetter + callYr + serNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    docTp = VALUES(docTp),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    offrNm = VALUES(offrNm),
                    rptDt = VALUES(rptDt),
                    perfDt = VALUES(perfDt),
                    berthPlcCd1 = VALUES(berthPlcCd1),
                    berthPlcCd2 = VALUES(berthPlcCd2),
                    berthPlcNm = VALUES(berthPlcNm),
                    nxtPrt2Cd = VALUES(nxtPrt2Cd),
                    nxtPrt2Nm = VALUES(nxtPrt2Nm),
                    nxtPrt1Cd = VALUES(nxtPrt1Cd),
                    nxtPrt1Nm = VALUES(nxtPrt1Nm),
                    crgTn = VALUES(crgTn),
                    dngrCrgTn = VALUES(dngrCrgTn),
                    grsTn = VALUES(grsTn),
                    sailTpCd = VALUES(sailTpCd),
                    sailTpNm = VALUES(sailTpNm),
                    occtCd = VALUES(occtCd),
                    occtNm = VALUES(occtNm),
                    flagCd = VALUES(flagCd),
                    flagNm = VALUES(flagNm),
                    vsslTpCd = VALUES(vsslTpCd),
                    vsslTpNm = VALUES(vsslTpNm),
                    vsslNm = VALUES(vsslNm),
                    subCallLetter1 = VALUES(subCallLetter1),
                    subCallLetter2 = VALUES(subCallLetter2),
                    depDt = VALUES(depDt),
                    tugYn = VALUES(tugYn),
                    pltYn = VALUES(pltYn),
                    dstPrt2Cd = VALUES(dstPrt2Cd),
                    dstPrt2Nm = VALUES(dstPrt2Nm),
                    dstPrt1Cd = VALUES(dstPrt1Cd),
                    dstPrt1Nm = VALUES(dstPrt1Nm),
                    dstArvlDt = VALUES(dstArvlDt),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_history":
            # 관제정보: prtAtCd + callLetter + callYr + serNo + comCnt로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    typeCd = VALUES(typeCd),
                    typeNm = VALUES(typeNm),
                    comDt = VALUES(comDt),
                    comPlc1 = VALUES(comPlc1),
                    comPlc2 = VALUES(comPlc2),
                    comPlcNm = VALUES(comPlcNm),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_pass_report":
            # 외항통과선박신청정보: prtAtCd + callLetter + callYr + serNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    vsslNm = VALUES(vsslNm),
                    arvlObjCd = VALUES(arvlObjCd),
                    stayHr = VALUES(stayHr),
                    anchorPlace = VALUES(anchorPlace),
                    stayFr = VALUES(stayFr),
                    stayTo = VALUES(stayTo),
                    docTp = VALUES(docTp),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    agentPic = VALUES(agentPic),
                    appvlCd = VALUES(appvlCd),
                    rejectDt = VALUES(rejectDt),
                    rejectRsn = VALUES(rejectRsn),
                    applyDt = VALUES(applyDt),
                    processDt = VALUES(processDt),
                    remark = VALUES(remark),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_spec_info":
            # 선박 제원 정보: callLetter + mmsiNo + imoNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    regNo = VALUES(regNo),
                    vsslNm = VALUES(vsslNm),
                    vsslEngNm = VALUES(vsslEngNm),
                    vsslTp = VALUES(vsslTp),
                    vsslTpCd = VALUES(vsslTpCd),
                    vsslLth = VALUES(vsslLth),
                    vsslWdth = VALUES(vsslWdth),
                    vsslDpth = VALUES(vsslDpth),
                    vsslDraft = VALUES(vsslDraft),
                    grtg = VALUES(grtg),
                    nrtg = VALUES(nrtg),
                    deadWgt = VALUES(deadWgt),
                    dwt = VALUES(dwt),
                    buildYr = VALUES(buildYr),
                    buildCntry = VALUES(buildCntry),
                    buildPlace = VALUES(buildPlace),
                    regCntry = VALUES(regCntry),
                    regPort = VALUES(regPort),
                    regYr = VALUES(regYr),
                    owner = VALUES(owner),
                    operator = VALUES(operator),
                    engine = VALUES(engine),
                    enginePower = VALUES(enginePower),
                    speed = VALUES(speed),
                    crew = VALUES(crew),
                    passenger = VALUES(passenger),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "cargo_item_code":
            # 화물품목코드: crgItemCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    crgItemCdNmShort = VALUES(crgItemCdNmShort),
                    crgItemCdNmEShort = VALUES(crgItemCdNmEShort),
                    crgItemNm = VALUES(crgItemNm),
                    crgItemNmE = VALUES(crgItemNmE),
                    cgItemCd = VALUES(cgItemCd),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "dg_imp_report":
            # 위험물반입신고서: prtAtCd + callLetter + callYr + serNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    vsslNm = VALUES(vsslNm),
                    inTp = VALUES(inTp),
                    wrkNo = VALUES(wrkNo),
                    agentCd = VALUES(agentCd),
                    rptDt = VALUES(rptDt),
                    bfRpt1Cd = VALUES(bfRpt1Cd),
                    bfRpt1Nm = VALUES(bfRpt1Nm),
                    bfRpt2Cd = VALUES(bfRpt2Cd),
                    bfRpt2Nm = VALUES(bfRpt2Nm),
                    conQty = VALUES(conQty),
                    crgNm = VALUES(crgNm),
                    crgTpCd1 = VALUES(crgTpCd1),
                    crgTpCd2 = VALUES(crgTpCd2),
                    crgTpNm1 = VALUES(crgTpNm1),
                    crgTpNm2 = VALUES(crgTpNm2),
                    msrTnTp = VALUES(msrTnTp),
                    msrUnit = VALUES(msrUnit),
                    qty = VALUES(qty),
                    useTrgt1 = VALUES(useTrgt1),
                    useTrgt2 = VALUES(useTrgt2),
                    dgObjYn = VALUES(dgObjYn),
                    rptNth = VALUES(rptNth),
                    perfDt = VALUES(perfDt),
                    stvCoCd = VALUES(stvCoCd),
                    stvCoNm = VALUES(stvCoNm),
                    useObj1 = VALUES(useObj1),
                    useObj2 = VALUES(useObj2),
                    wrkDtFr = VALUES(wrkDtFr),
                    wrkDtTo = VALUES(wrkDtTo),
                    wrkPlc1 = VALUES(wrkPlc1),
                    wrkPlc2 = VALUES(wrkPlc2),
                    useObj1Nm = VALUES(useObj1Nm),
                    useObj2Nm = VALUES(useObj2Nm),
                    ocCtCd = VALUES(ocCtCd),
                    returnDt = VALUES(returnDt),
                    returnRsn = VALUES(returnRsn),
                    crgDblYn = VALUES(crgDblYn),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "fac_use_statement":
            # 항만시설사용 신청/결과정보: prtAtCd + callLetter + callYr + serNo + useNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    prtAtNm = VALUES(prtAtNm),
                    vsslNm = VALUES(vsslNm),
                    reqFacCd = VALUES(reqFacCd),
                    reqFacSubCd = VALUES(reqFacSubCd),
                    reqFacNm = VALUES(reqFacNm),
                    allotFacCd = VALUES(allotFacCd),
                    allotFacSubCd = VALUES(allotFacSubCd),
                    allotFacNm = VALUES(allotFacNm),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    ocCtCd = VALUES(ocCtCd),
                    useObjCd = VALUES(useObjCd),
                    useObjNm = VALUES(useObjNm),
                    useScrDtFr = VALUES(useScrDtFr),
                    useScrDtTo = VALUES(useScrDtTo),
                    allotDtFr = VALUES(allotDtFr),
                    allotDtTo = VALUES(allotDtTo),
                    useDtFr = VALUES(useDtFr),
                    useDtTo = VALUES(useDtTo),
                    vsslTpCd = VALUES(vsslTpCd),
                    vsslTpNm = VALUES(vsslTpNm),
                    apprvlRsn = VALUES(apprvlRsn),
                    apprvlCd = VALUES(apprvlCd),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "fac_use_stmt_bill":
            # 항만시설사용신고정보-화물료: prtAtCd + callLetter + callYr + serNo + billNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    useTp = VALUES(useTp),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    facCd = VALUES(facCd),
                    facSubCd = VALUES(facSubCd),
                    facNm = VALUES(facNm),
                    ioDt = VALUES(ioDt),
                    notifyDt = VALUES(notifyDt),
                    fiscalYr = VALUES(fiscalYr),
                    feeTp = VALUES(feeTp),
                    feeTpNm = VALUES(feeTpNm),
                    dueDt = VALUES(dueDt),
                    totalFee = VALUES(totalFee),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_sec_isps_info":
            # 선박보안인증서 통보: prtAtCd + callLetter + callYr + serNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    prtAtNm = VALUES(prtAtNm),
                    vsslKey = VALUES(vsslKey),
                    vsslNm = VALUES(vsslNm),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    imoNo = VALUES(imoNo),
                    rptDt = VALUES(rptDt),
                    vsslSecLevel = VALUES(vsslSecLevel),
                    ispsNo = VALUES(ispsNo),
                    ispsOff = VALUES(ispsOff),
                    ispsIssueFlag = VALUES(ispsIssueFlag),
                    ispsIssueFlagNm = VALUES(ispsIssueFlagNm),
                    ispsValidFromDt = VALUES(ispsValidFromDt),
                    ispsValidToDt = VALUES(ispsValidToDt),
                    resultYn = VALUES(resultYn),
                    perfDt = VALUES(perfDt),
                    resultTx = VALUES(resultTx),
                    returnDt = VALUES(returnDt),
                    returnRsn = VALUES(returnRsn),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_sec_port_info":
            # 선박보안인증서 통보 경유지 정보: prtAtCd + callLetter + callYr + serNo + seqNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    prtAtNm = VALUES(prtAtNm),
                    vsslKey = VALUES(vsslKey),
                    vsslNm = VALUES(vsslNm),
                    bfPrt1Cd = VALUES(bfPrt1Cd),
                    bfPrt1Nm = VALUES(bfPrt1Nm),
                    bfPrt2Cd = VALUES(bfPrt2Cd),
                    bfPrt2Nm = VALUES(bfPrt2Nm),
                    arvlDt = VALUES(arvlDt),
                    depDt = VALUES(depDt),
                    vsslSecLevel = VALUES(vsslSecLevel),
                    vsslSecLevelNm = VALUES(vsslSecLevelNm),
                    portSecLevel = VALUES(portSecLevel),
                    portSecLevelNm = VALUES(portSecLevelNm),
                    remark = VALUES(remark),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "load_unload_from_to_info":
            # 선박양적하 시작종료정보: tmnlId + shpCd + callYr + callNo로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    tmnlNm = VALUES(tmnlNm),
                    shpNm = VALUES(shpNm),
                    wkId = VALUES(wkId),
                    disBeginDt = VALUES(disBeginDt),
                    disEndDt = VALUES(disEndDt),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_sanction_info":
            # 제재대상선박 정보: prtAtCd + callLetter + penaltyCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslKey = VALUES(vsslKey),
                    callYr = VALUES(callYr),
                    serNo = VALUES(serNo),
                    vsslKorNm = VALUES(vsslKorNm),
                    penaltyNm = VALUES(penaltyNm),
                    imoNo = VALUES(imoNo),
                    flag = VALUES(flag),
                    flagNm = VALUES(flagNm),
                    agentCd = VALUES(agentCd),
                    agentNm = VALUES(agentNm),
                    shpOwnerNm = VALUES(shpOwnerNm),
                    grsTn = VALUES(grsTn),
                    vsslLen = VALUES(vsslLen),
                    vsslNo = VALUES(vsslNo),
                    perfDt = VALUES(perfDt),
                    adminDetail = VALUES(adminDetail),
                    penaltyRqrPlc = VALUES(penaltyRqrPlc),
                    penaltyRqrPlcDetail = VALUES(penaltyRqrPlcDetail),
                    rglt = VALUES(rglt),
                    penaltyFr = VALUES(penaltyFr),
                    penaltyTo = VALUES(penaltyTo),
                    remark = VALUES(remark),
                    icdtNum = VALUES(icdtNum),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "country_code":
            # 국가코드: cntryCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    cntryEngNm = VALUES(cntryEngNm),
                    cntryKorNm = VALUES(cntryKorNm),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_entr_intn_code":
            # 입항목적코드: vsslEntrIntnCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    vsslEntrIntnNm = VALUES(vsslEntrIntnNm),
                    vsslEntrIntnNmng = VALUES(vsslEntrIntnNmng),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "pa_code":
            # 항구청코드: paCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    paCdEng = VALUES(paCdEng),
                    paNm = VALUES(paNm),
                    paNmEng = VALUES(paNmEng),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "port_code":
            # 항구코드: natCd + portCd로 중복 체크
            return """
                ON DUPLICATE KEY UPDATE
                    natNm = VALUES(natNm),
                    natPortCd = VALUES(natPortCd),
                    portNm = VALUES(portNm),
                    portNmE = VALUES(portNmE),
                    loctCd = VALUES(loctCd),
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_Tos_VsslNo":
            # TOS 선박번호 매칭: 전체 매칭 조합으로 중복 체크
            # (prtAtCd + callYrPmis + callSignPmis + callSeqPmis + tmnlCd + callYrTos + vsslCdTos + callSeqTos)
            # 전체 조합이 UNIQUE이므로 중복 시 updated_at만 갱신
            return """
                ON DUPLICATE KEY UPDATE
                    updated_at = CURRENT_TIMESTAMP
            """
        elif table_name == "vssl_Port_VsslNo":
            # 항만 선박번호 매칭: 전체 매칭 조합으로 중복 체크
            # (prtAtCd + callYrPmis + callSignPmis + callSeqPmis + tmnlCd + callYrTos + vsslCdTos + callSeqTos)
            # 전체 조합이 UNIQUE이므로 중복 시 updated_at만 갱신
            return """
                ON DUPLICATE KEY UPDATE
                    updated_at = CURRENT_TIMESTAMP
            """
        else:
            # 기타 테이블: 기본 중복 처리 (updated_at만 업데이트)
            return """
                ON DUPLICATE KEY UPDATE
                    updated_at = CURRENT_TIMESTAMP
            """
    
    def insert_data(self, table_name: str, data: List[Dict[str, Any]]) -> bool:
        """
        데이터를 테이블에 삽입 (중복 데이터 처리 포함)
        
        Args:
            table_name: 테이블명
            data: 삽입할 데이터 리스트
            
        Returns:
            성공 여부
        """
        if not data:
            logger.warning(f"삽입할 데이터가 없습니다: {table_name}")
            return True
        
        try:
            # 컬럼명 추출
            columns = list(data[0].keys())
            placeholders = ', '.join(['%s'] * len(columns))
            column_names = ', '.join(columns)
            
            # 중복 처리 로직 가져오기
            duplicate_update = self._get_duplicate_update_clause(table_name, columns)
            
            # INSERT 쿼리 생성 (중복 처리 포함)
            query = f"""
                INSERT INTO {table_name} ({column_names})
                VALUES ({placeholders})
                {duplicate_update}
            """
            
            # 데이터 준비
            values = []
            for item in data:
                row_values = []
                for col in columns:
                    value = item.get(col)
                    if isinstance(value, dict):
                        value = json.dumps(value, ensure_ascii=False)
                    elif isinstance(value, list):
                        value = json.dumps(value, ensure_ascii=False)
                    row_values.append(value)
                values.append(tuple(row_values))
            
            # 배치 삽입
            with self.connection.cursor() as cursor:
                cursor.executemany(query, values)
                self.connection.commit()
                
            logger.info(f"✅ {table_name} 테이블에 {len(data)}개 행 삽입/업데이트 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 데이터 삽입 실패 ({table_name}): {e}")
            return False
    
    def update_data(self, table_name: str, data: Dict[str, Any], 
                   where_conditions: Dict[str, Any]) -> bool:
        """
        데이터 업데이트
        
        Args:
            table_name: 테이블명
            data: 업데이트할 데이터
            where_conditions: WHERE 조건
            
        Returns:
            성공 여부
        """
        try:
            # SET 절 생성
            set_clause = ', '.join([f"{k} = %s" for k in data.keys()])
            
            # WHERE 절 생성
            where_clause = ' AND '.join([f"{k} = %s" for k in where_conditions.keys()])
            
            query = f"""
                UPDATE {table_name}
                SET {set_clause}
                WHERE {where_clause}
            """
            
            # 파라미터 준비
            params = tuple(list(data.values()) + list(where_conditions.values()))
            
            result = self.execute_query(query, params)
            if result:
                logger.info(f"✅ {table_name} 테이블 업데이트 완료")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 데이터 업데이트 실패 ({table_name}): {e}")
            return False
    
    def delete_data(self, table_name: str, where_conditions: Dict[str, Any]) -> bool:
        """
        데이터 삭제
        
        Args:
            table_name: 테이블명
            where_conditions: WHERE 조건
            
        Returns:
            성공 여부
        """
        try:
            where_clause = ' AND '.join([f"{k} = %s" for k in where_conditions.keys()])
            query = f"DELETE FROM {table_name} WHERE {where_clause}"
            
            params = tuple(where_conditions.values())
            result = self.execute_query(query, params)
            
            if result:
                logger.info(f"✅ {table_name} 테이블에서 데이터 삭제 완료")
                return True
            return False
            
        except Exception as e:
            logger.error(f"❌ 데이터 삭제 실패 ({table_name}): {e}")
            return False
    
    def get_table_info(self, table_name: str) -> Optional[Dict[str, Any]]:
        """테이블 정보 조회"""
        try:
            query = "DESCRIBE " + table_name
            result = self.execute_query(query)
            
            if result:
                columns = []
                for row in result:
                    columns.append({
                        "field": row["Field"],
                        "type": row["Type"],
                        "null": row["Null"],
                        "key": row["Key"],
                        "default": row["Default"],
                        "extra": row["Extra"]
                    })
                
                return {
                    "table_name": table_name,
                    "columns": columns,
                    "column_count": len(columns)
                }
            return None
            
        except Exception as e:
            logger.error(f"❌ 테이블 정보 조회 실패 ({table_name}): {e}")
            return None
    
    def get_table_count(self, table_name: str) -> int:
        """테이블의 행 수 조회"""
        try:
            query = f"SELECT COUNT(*) as count FROM {table_name}"
            result = self.execute_query(query)
            
            if result and len(result) > 0:
                return result[0]["count"]
            return 0
            
        except Exception as e:
            logger.error(f"❌ 테이블 행 수 조회 실패 ({table_name}): {e}")
            return 0
    
    def check_table_exists(self, table_name: str) -> bool:
        """테이블 존재 여부 확인"""
        try:
            query = """
                SELECT COUNT(*) as count 
                FROM information_schema.tables 
                WHERE table_schema = %s AND table_name = %s
            """
            result = self.execute_query(query, (self.database, table_name))
            
            if result and len(result) > 0:
                return result[0]["count"] > 0
            return False
            
        except Exception as e:
            logger.error(f"❌ 테이블 존재 여부 확인 실패 ({table_name}): {e}")
            return False
    
    def get_sync_status(self, sync_id: str) -> Dict[str, Any]:
        """동기화 상태 조회"""
        try:
            # 업데이트된 테이블 목록 사용
            tables = self.all_tables
            
            sync_status = {
                "sync_id": sync_id,
                "total_tables": len(tables),
                "synced_tables": 0,
                "table_details": {},
                "total_records": 0,
                "sync_timestamp": None
            }
            
            for table in tables:
                if self.check_table_exists(table):
                    count = self.get_table_count(table)
                    sync_status["table_details"][table] = {
                        "exists": True,
                        "record_count": count
                    }
                    sync_status["total_records"] += count
                    
                    # sync_id로 필터링된 레코드 수 조회
                    if self.connection and self.connection.open:
                        try:
                            with self.connection.cursor() as cursor:
                                cursor.execute(f"SELECT COUNT(*) as count FROM {table} WHERE sync_id = %s", (sync_id,))
                                result = cursor.fetchone()
                                if result:
                                    sync_status["table_details"][table]["sync_records"] = result[0]
                                    if result[0] > 0:
                                        sync_status["synced_tables"] += 1
                        except:
                            sync_status["table_details"][table]["sync_records"] = 0
                else:
                    sync_status["table_details"][table] = {
                        "exists": False,
                        "record_count": 0,
                        "sync_records": 0
                    }
            
            return sync_status
            
        except Exception as e:
            logger.error(f"❌ 동기화 상태 조회 실패: {e}")
            return {}
    
    def cleanup_old_sync_data(self, days: int = 30) -> bool:
        """오래된 동기화 데이터 정리"""
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            # 업데이트된 테이블 목록 사용
            tables = self.all_tables
            
            total_deleted = 0
            for table in tables:
                if self.check_table_exists(table):
                    query = f"""
                        DELETE FROM {table} 
                        WHERE sync_timestamp < %s
                    """
                    result = self.execute_query(query, (cutoff_date.isoformat(),))
                    if result and len(result) > 0:
                        deleted_count = result[0]["affected_rows"]
                        total_deleted += deleted_count
                        if deleted_count > 0:
                            logger.info(f"🧹 {table} 테이블에서 {deleted_count}개 오래된 레코드 삭제")
            
            logger.info(f"🧹 총 {total_deleted}개 오래된 레코드 정리 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 오래된 데이터 정리 실패: {e}")
            return False
    
    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.disconnect()
