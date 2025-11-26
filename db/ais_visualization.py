#!/usr/bin/env python3
"""
AIS 데이터 시각화 스크립트

MySQL DB의 ais_info 테이블에서 데이터를 가져와서
기본적인 차트들을 생성합니다.

시각화 내용:
1. 선박 타입별 분포 (원형 차트)
2. 국적별 선박 분포 (막대 차트)
3. 선박 속도 분포 (히스토그램)
"""

import pymysql
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
import logging
from datetime import datetime
import os

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AISVisualizer:
    """AIS 데이터 시각화 클래스"""
    
    def __init__(self, db_config=None):
        """초기화"""
        self.db_config = db_config or {
            'host': 'localhost',
            'port': 3307,
            'user': 'root',
            'password': 'Keti1234!',
            'database': 'port_database',
            'charset': 'utf8mb4'
        }
        self.connection = None
        self.ais_data = None
        
    def connect_db(self):
        """데이터베이스 연결"""
        try:
            self.connection = pymysql.connect(**self.db_config)
            logger.info(f"데이터베이스 '{self.db_config['database']}'에 연결되었습니다.")
            return True
        except Exception as e:
            logger.error(f"데이터베이스 연결 실패: {e}")
            return False
    
    def disconnect_db(self):
        """데이터베이스 연결 해제"""
        if self.connection:
            self.connection.close()
            logger.info("데이터베이스 연결이 종료되었습니다.")
    
    def fetch_ais_data(self):
        """AIS 데이터 조회"""
        try:
            query = """
            SELECT 
                vsslTp,            -- 선박 타입
                flag,              -- 국적
                sog,               -- 속도 (Speed Over Ground)
                vsslNm,            -- 선박명
                callLetter,        -- 호출부호
                lon,               -- 경도
                lat,               -- 위도
                vsslLen,           -- 선박 길이
                vsslWidth,         -- 선박 폭
                cog,               -- 방향 (Course Over Ground)
                created_at         -- 생성 시간
            FROM ais_info 
            WHERE vsslTp IS NOT NULL 
            AND flag IS NOT NULL 
            AND sog IS NOT NULL
            LIMIT 1000
            """
            
            df = pd.read_sql(query, self.connection)
            self.ais_data = df
            logger.info(f"AIS 데이터 {len(df)}건을 조회했습니다.")
            return df
            
        except Exception as e:
            logger.error(f"AIS 데이터 조회 실패: {e}")
            return None
    
    def create_ship_type_chart(self):
        """선박 타입별 분포 원형 차트"""
        if self.ais_data is None or self.ais_data.empty:
            logger.warning("시각화할 데이터가 없습니다.")
            return None
        
        # 선박 타입별 개수 계산
        ship_type_counts = self.ais_data['vsslTp'].value_counts()
        
        # 상위 10개만 표시하고 나머지는 '기타'로 그룹화
        if len(ship_type_counts) > 10:
            top_10 = ship_type_counts.head(10)
            others_count = ship_type_counts.iloc[10:].sum()
            ship_type_counts = pd.concat([top_10, pd.Series([others_count], index=['기타'])])
        
        # 원형 차트 생성
        fig = px.pie(
            values=ship_type_counts.values,
            names=ship_type_counts.index,
            title="선박 타입별 분포",
            hole=0.3  # 도넛 차트
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(
            title_x=0.5,
            title_font_size=20,
            showlegend=True
        )
        
        return fig
    
    def create_flag_chart(self):
        """국적별 선박 분포 막대 차트"""
        if self.ais_data is None or self.ais_data.empty:
            logger.warning("시각화할 데이터가 없습니다.")
            return None
        
        # 국적별 개수 계산
        flag_counts = self.ais_data['flag'].value_counts()
        
        # 상위 15개만 표시
        top_flags = flag_counts.head(15)
        
        # 막대 차트 생성
        fig = px.bar(
            x=top_flags.values,
            y=top_flags.index,
            orientation='h',  # 가로 막대 차트
            title="국적별 선박 분포 (상위 15개)",
            labels={'x': '선박 수', 'y': '국적'}
        )
        
        fig.update_layout(
            title_x=0.5,
            title_font_size=20,
            xaxis_title="선박 수",
            yaxis_title="국적",
            height=600
        )
        
        return fig
    
    def create_speed_chart(self):
        """선박 속도 분포 히스토그램"""
        if self.ais_data is None or self.ais_data.empty:
            logger.warning("시각화할 데이터가 없습니다.")
            return None
        
        # 속도 데이터 정리 (0보다 큰 값만)
        speed_data = self.ais_data[self.ais_data['sog'] > 0]['sog']
        
        if speed_data.empty:
            logger.warning("속도 데이터가 없습니다.")
            return None
        
        # 히스토그램 생성
        fig = px.histogram(
            x=speed_data,
            nbins=30,
            title="선박 속도 분포",
            labels={'x': '속도 (노트)', 'y': '선박 수'},
            opacity=0.7
        )
        
        fig.update_layout(
            title_x=0.5,
            title_font_size=20,
            xaxis_title="속도 (노트)",
            yaxis_title="선박 수",
            bargap=0.1
        )
        
        # 평균 속도 표시
        mean_speed = speed_data.mean()
        fig.add_vline(
            x=mean_speed, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"평균: {mean_speed:.1f} 노트"
        )
        
        return fig
    
    def create_summary_dashboard(self):
        """요약 대시보드 생성"""
        if self.ais_data is None or self.ais_data.empty:
            logger.warning("시각화할 데이터가 없습니다.")
            return None
        
        # 서브플롯 생성 (2x2 그리드)
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('선박 타입별 분포', '국적별 선박 분포', '선박 속도 분포', '데이터 요약'),
            specs=[[{"type": "pie"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "table"}]]
        )
        
        # 1. 선박 타입별 분포 (원형 차트)
        ship_type_counts = self.ais_data['vsslTp'].value_counts().head(8)
        fig.add_trace(
            go.Pie(labels=ship_type_counts.index, values=ship_type_counts.values, name="선박 타입"),
            row=1, col=1
        )
        
        # 2. 국적별 분포 (막대 차트)
        flag_counts = self.ais_data['flag'].value_counts().head(10)
        fig.add_trace(
            go.Bar(x=flag_counts.index, y=flag_counts.values, name="국적별"),
            row=1, col=2
        )
        
        # 3. 속도 분포 (히스토그램)
        speed_data = self.ais_data[self.ais_data['sog'] > 0]['sog']
        if not speed_data.empty:
            fig.add_trace(
                go.Histogram(x=speed_data, name="속도"),
                row=2, col=1
            )
        
        # 4. 데이터 요약 테이블
        summary_data = [
            ['총 선박 수', len(self.ais_data)],
            ['고유 선박 타입', self.ais_data['vsslTp'].nunique()],
            ['고유 국적', self.ais_data['flag'].nunique()],
            ['평균 속도', f"{speed_data.mean():.1f} 노트" if not speed_data.empty else "N/A"],
            ['최대 속도', f"{speed_data.max():.1f} 노트" if not speed_data.empty else "N/A"]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['항목', '값']),
                cells=dict(values=[[row[0] for row in summary_data], [row[1] for row in summary_data]])
            ),
            row=2, col=2
        )
        
        # 레이아웃 업데이트
        fig.update_layout(
            title_text="AIS 데이터 요약 대시보드",
            title_x=0.5,
            title_font_size=24,
            height=800,
            showlegend=False
        )
        
        return fig
    
    def save_charts(self, output_dir="ais_charts"):
        """차트들을 HTML 파일로 저장"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logger.info(f"출력 디렉토리 '{output_dir}'를 생성했습니다.")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # 1. 선박 타입별 분포
            ship_type_fig = self.create_ship_type_chart()
            if ship_type_fig:
                ship_type_fig.write_html(f"{output_dir}/ship_type_distribution_{timestamp}.html")
                logger.info("선박 타입별 분포 차트를 저장했습니다.")
            
            # 2. 국적별 분포
            flag_fig = self.create_flag_chart()
            if flag_fig:
                flag_fig.write_html(f"{output_dir}/flag_distribution_{timestamp}.html")
                logger.info("국적별 분포 차트를 저장했습니다.")
            
            # 3. 속도 분포
            speed_fig = self.create_speed_chart()
            if speed_fig:
                speed_fig.write_html(f"{output_dir}/speed_distribution_{timestamp}.html")
                logger.info("속도 분포 차트를 저장했습니다.")
            
            # 4. 요약 대시보드
            dashboard_fig = self.create_summary_dashboard()
            if dashboard_fig:
                dashboard_fig.write_html(f"{output_dir}/ais_dashboard_{timestamp}.html")
                logger.info("요약 대시보드를 저장했습니다.")
            
            logger.info(f"모든 차트가 '{output_dir}' 디렉토리에 저장되었습니다.")
            
        except Exception as e:
            logger.error(f"차트 저장 실패: {e}")
    
    def show_charts(self):
        """차트들을 브라우저에서 표시"""
        try:
            # 1. 선박 타입별 분포
            ship_type_fig = self.create_ship_type_chart()
            if ship_type_fig:
                ship_type_fig.show()
            
            # 2. 국적별 분포
            flag_fig = self.create_flag_chart()
            if flag_fig:
                flag_fig.show()
            
            # 3. 속도 분포
            speed_fig = self.create_speed_chart()
            if speed_fig:
                speed_fig.show()
            
            # 4. 요약 대시보드
            dashboard_fig = self.create_summary_dashboard()
            if dashboard_fig:
                dashboard_fig.show()
                
        except Exception as e:
            logger.error(f"차트 표시 실패: {e}")

def main():
    """메인 실행 함수"""
    logger.info("🚢 AIS 데이터 시각화를 시작합니다...")
    
    # 시각화 객체 생성
    visualizer = AISVisualizer()
    
    try:
        # 1. 데이터베이스 연결
        if not visualizer.connect_db():
            logger.error("데이터베이스 연결에 실패했습니다.")
            return
        
        # 2. AIS 데이터 조회
        ais_data = visualizer.fetch_ais_data()
        if ais_data is None:
            logger.error("AIS 데이터 조회에 실패했습니다.")
            return
        
        # 3. 데이터 기본 정보 출력
        logger.info(f"데이터 형태: {ais_data.shape}")
        logger.info(f"컬럼: {list(ais_data.columns)}")
        logger.info(f"선박 타입: {ais_data['vsslTp'].value_counts().head()}")
        logger.info(f"국적: {ais_data['flag'].value_counts().head()}")
        
        # 4. 차트 생성 및 저장
        visualizer.save_charts()
        
        # 5. 브라우저에서 차트 표시 (선택사항)
        show_in_browser = input("브라우저에서 차트를 표시하시겠습니까? (y/n): ").lower().strip()
        if show_in_browser == 'y':
            visualizer.show_charts()
        
        logger.info("✅ AIS 데이터 시각화가 완료되었습니다!")
        
    except Exception as e:
        logger.error(f"시각화 중 오류 발생: {e}")
    
    finally:
        # 6. 데이터베이스 연결 해제
        visualizer.disconnect_db()

if __name__ == "__main__":
    main()
