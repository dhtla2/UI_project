export interface AISInfo {
  id?: number;
  mmsi_no?: string;
  imo_no?: string;
  vssl_nm?: string;
  call_letter?: string;
  vssl_tp?: string;
  vssl_tp_cd?: string;
  vssl_tp_crgo?: string;
  vssl_cls?: string;
  vssl_len?: number;
  vssl_width?: number;
  flag?: string;
  flag_cd?: string;
  vssl_def_brd?: number;
  lon?: number;
  lat?: number;
  sog?: number; // Speed Over Ground
  cog?: number; // Course Over Ground
  rot?: number; // Rate of Turn
  head_side?: number; // Heading
  vssl_navi?: string;
  vssl_navi_cd?: string;
  source?: string;
  dt_pos_utc?: string;
  dt_static_utc?: string;
  vssl_tp_main?: string;
  vssl_tp_sub?: string;
  dst_nm?: string;
  dst_cd?: string;
  eta?: string;
  created_at?: string;
}

export interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

export interface ShipTypeStats {
  shipType: string;
  count: number;
}

export interface FlagStats {
  flag: string;
  count: number;
}

export interface NavigationStatusStats {
  status: string;
  count: number;
} 