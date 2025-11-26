// 품질 검사 설정 데이터
export interface APIParams {
  [key: string]: string | number;
}

export interface QualityCheckRule {
  [key: string]: any;
}

export interface DataTypeConfig {
  id: string;
  name: string;
  description: string;
  category: string;
  defaultParams: APIParams;
  defaultMeta: QualityCheckRule;
}

// 25가지 데이터 타입 설정
export const DATA_TYPES: DataTypeConfig[] = [
  // 작업 정보 관련
  {
    id: "tc_work_info",
    name: "TC 작업정보",
    description: "터미널 크레인 작업 정보",
    category: "작업정보",
    defaultParams: {
      regNo: "KETI",
      tmnlId: "BPTS",
      shpCd: "HASM",
      callYr: "2021",
      serNo: "012",
      timeFrom: "20220110000000",
      timeTo: "20220130235959"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 },
          callYr: { rtype: "I", ctype: "I", val1: 2000, val2: 2100 }
        },
        DATE: {
          S: {
            wkTime: { val1: "1900-01-01" }
          }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            tmnlId: ["tmnlId"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["tmnlId", "wkTime", "serNo", "callYr"]
        }
      }
    }
  },
  {
    id: "qc_work_info",
    name: "QC 작업정보",
    description: "쿼크 크레인 작업 정보",
    category: "작업정보",
    defaultParams: {
      regNo: "KETI",
      tmnlId: "BPTS",
      shpCd: "STMY",
      callYr: "2022",
      serNo: "001",
      timeFrom: "20220110000000",
      timeTo: "20220130235959"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 },
          callYr: { rtype: "I", ctype: "I", val1: 2000, val2: 2100 }
        },
        DATE: {
          S: {
            wkTime: { val1: "1900-01-01" }
          }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            tmnlId: ["tmnlId"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["tmnlId", "wkTime", "serNo", "callYr"]
        }
      }
    }
  },
  {
    id: "yt_work_info",
    name: "YT 작업정보",
    description: "야드 트랙터 작업 정보",
    category: "작업정보",
    defaultParams: {
      regNo: "KETI",
      tmnlId: "BPTS",
      shpCd: "HHDT",
      callYr: "2022",
      serNo: "001",
      timeFrom: "20220110000000",
      timeTo: "20220130000000"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 },
          callYr: { rtype: "I", ctype: "I", val1: 2000, val2: 2100 }
        },
        DATE: {
          S: {
            wkTime: { val1: "1900-01-01" }
          }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            tmnlId: ["tmnlId"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["tmnlId", "wkTime", "serNo", "callYr"]
        }
      }
    }
  },
  // 선석 계획 관련
  {
    id: "berth_schedule",
    name: "선석계획",
    description: "선석 스케줄 계획 정보",
    category: "선석관리",
    defaultParams: {
      regNo: "KETI",
      callYr: "2022",
      shpCd: "KSCM",
      timeTp: "A",
      timeFrom: "20220110000000"
    },
    defaultMeta: {
      DV: {
        DATE: {
          D: {
            row1: {
              columns: ["atd", "ata"],
              val1: "D",
              val2: 3
            }
          }
        }
      }
    }
  },
  // AIS 정보 관련
  {
    id: "ais_info",
    name: "AIS 정보",
    description: "자동식별시스템 정보",
    category: "선박관리",
    defaultParams: {
      regNo: "KETI",
      mmsiNo: "312773000",
      callLetter: "V3JW",
      imoNo: "8356869"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          lat: { rtype: "F", ctype: "I", val1: -90, val2: 90 },
          lon: { rtype: "F", ctype: "I", val1: -180, val2: 180 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            mmsiNo: ["mmsiNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["mmsiNo", "callLetter", "lat", "lon", "sog", "cog"]
        }
      }
    }
  },
  // 컨테이너 관련
  {
    id: "cntr_load_unload_info",
    name: "컨테이너 양적하정보",
    description: "컨테이너 적재/양하 정보",
    category: "컨테이너관리",
    defaultParams: {
      regNo: "KETI",
      tmnlId: "BPTS",
      shpCd: "STMY",
      callYr: "2022",
      serNo: "001",
      timeFrom: "20220101000000",
      timeTo: "20220131235959"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            cntrNo: ["cntrNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["cntrNo", "tmnlId", "wkTime", "cntrSize"]
        }
      }
    }
  },
  {
    id: "cntr_report_detail",
    name: "컨테이너신고상세정보",
    description: "컨테이너 신고 상세 정보",
    category: "컨테이너관리",
    defaultParams: {
      regNo: "KETI",
      mrnNo: "22ANLU0015I",
      msnNo: "2012",
      blNo: "AEL1288023",
      cntrNo: "CMAU8845903"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            cntrNo: ["cntrNo"],
            blNo: ["blNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["cntrNo", "blNo", "mrnNo", "msnNo"]
        }
      }
    }
  },
  // 선박 관련
  {
    id: "vssl_entr_report",
    name: "선박 입항신고정보",
    description: "선박 입항 신고 정보",
    category: "선박관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "060333",
      callYr: "2022",
      serNo: "105"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "vssl_dprt_report",
    name: "선박 출항신고정보",
    description: "선박 출항 신고 정보",
    category: "선박관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "D5QP8",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "vssl_history",
    name: "관제정보",
    description: "선박 관제 이력 정보",
    category: "선박관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "000347",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "vssl_pass_report",
    name: "외항통과선박신청정보",
    description: "외항 통과 선박 신청 정보",
    category: "선박관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "SVCD4",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  // 화물 관련
  {
    id: "cargo_imp_exp_report",
    name: "화물반출입신고정보",
    description: "화물 반출입 신고 정보",
    category: "화물관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "9HA5500",
      callYr: "2022"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "cargo_item_code",
    name: "화물품목코드",
    description: "화물 품목 코드 정보",
    category: "화물관리",
    defaultParams: {
      regNo: "KETI",
      crgItemCd: "291636"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            crgItemCd: ["crgItemCd"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["crgItemCd", "crgItemNm"]
        }
      }
    }
  },
  // 위험물 관련
  {
    id: "dg_imp_report",
    name: "위험물반입신고서",
    description: "위험물 반입 신고서",
    category: "위험물관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "V7A5515",
      callYr: "2023",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "dg_manifest",
    name: "위험물 적하알림표",
    description: "위험물 적하 알림표",
    category: "위험물관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "DSRB8",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  // 항만시설 관련
  {
    id: "fac_use_statement",
    name: "항만시설사용 신청/결과정보",
    description: "항만시설 사용 신청/결과 정보",
    category: "항만시설관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "DSGZ",
      callYr: "2023",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "fac_use_stmt_bill",
    name: "항만시설사용신고정보-화물료",
    description: "항만시설 사용 신고 정보 (화물료)",
    category: "항만시설관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "130037",
      callYr: "2023",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  // 보안 관련
  {
    id: "vssl_sec_isps_info",
    name: "선박보안인증서 통보",
    description: "선박 보안 인증서 통보 정보",
    category: "보안관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "V7PX2",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "vssl_sec_port_info",
    name: "선박보안인증서 통보 경유지 정보",
    description: "선박 보안 인증서 통보 경유지 정보",
    category: "보안관리",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "3FUZ5",
      callYr: "2022",
      serNo: "001"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          serNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"],
            serNo: ["serNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "callYr", "serNo", "prtAtCd"]
        }
      }
    }
  },
  // 기타 정보
  {
    id: "load_unload_from_to_info",
    name: "선박양적하 시작종료정보",
    description: "선박 양적하 시작/종료 정보",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI",
      tmnlId: "BPTS",
      shpCd: "ACVG",
      callYr: "2022",
      callNo: "7"
    },
    defaultMeta: {
      DV: {
        RANGE: {
          callNo: { rtype: "I", ctype: "I", val1: 0, val2: 999 }
        }
      },
      DC: {
        DUPLICATE: {
          U: {
            callNo: ["callNo"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callNo", "tmnlId", "shpCd", "callYr"]
        }
      }
    }
  },
  {
    id: "vssl_sanction_info",
    name: "제재대상선박 정보",
    description: "제재 대상 선박 정보",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "9LU2620"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "vssl_entr_intn_code",
    name: "선박입항신고정보-국제통신번호",
    description: "선박 입항 신고 정보 (국제통신번호)",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI",
      prtAtCd: "020",
      callLetter: "V7A5515"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            callLetter: ["callLetter"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["callLetter", "prtAtCd"]
        }
      }
    }
  },
  {
    id: "country_code",
    name: "국가코드",
    description: "국가 코드 정보",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            cntryCd: ["cntryCd"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["cntryCd", "cntryNm"]
        }
      }
    }
  },
  {
    id: "pa_code",
    name: "항만청코드",
    description: "항만청 코드 정보",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            paCd: ["paCd"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["paCd", "paNm"]
        }
      }
    }
  },
  {
    id: "port_code",
    name: "항만코드",
    description: "항만 코드 정보",
    category: "기타정보",
    defaultParams: {
      regNo: "KETI"
    },
    defaultMeta: {
      DC: {
        DUPLICATE: {
          U: {
            prtCd: ["prtCd"]
          }
        }
      },
      DU: {
        USAGE: {
          columns: ["prtCd", "prtNm"]
        }
      }
    }
  }
];

// 카테고리별 그룹화
export const DATA_TYPES_BY_CATEGORY = DATA_TYPES.reduce((acc, dataType) => {
  if (!acc[dataType.category]) {
    acc[dataType.category] = [];
  }
  acc[dataType.category].push(dataType);
  return acc;
}, {} as Record<string, DataTypeConfig[]>);

// 검사 타입 정의
export const CHECK_TYPES = {
  COMPLETENESS: "완전성",
  VALIDITY: "유효성", 
  CONSISTENCY: "일관성",
  USAGE: "사용성",
  TIMELINESS: "적시성"
} as const;

export type CheckType = keyof typeof CHECK_TYPES;
