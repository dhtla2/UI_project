#!/usr/bin/env python3
"""
Dashboard API 서버

MQTT로 수집된 데이터를 dashboard에서 조회할 수 있도록 API를 제공합니다.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import pymysql
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # CORS 활성화

@app.route('/api/dashboard/recent-inspections', methods=['GET'])
def get_recent_inspections():
    """최근 검사 결과 조회"""
    try:
        limit = request.args.get('limit', 10, type=int)
        # 임시 데이터 반환
        data = {
            "recent_inspections": [
                {"id": 1, "status": "completed", "timestamp": "2025-08-26T10:00:00Z"},
                {"id": 2, "status": "in_progress", "timestamp": "2025-08-26T09:30:00Z"}
            ]
        }
        return jsonify(data)
    except Exception as e:
        logger.error(f"최근 검사 결과 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/quality-metrics', methods=['GET'])
def get_quality_metrics():
    """품질 메트릭 요약 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        data = dashboard_service.get_quality_metrics_summary(days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"품질 메트릭 요약 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/data-source-stats', methods=['GET'])
def get_data_source_stats():
    """데이터 소스별 통계 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        data = dashboard_service.get_data_source_stats(days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"데이터 소스별 통계 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/performance-trends', methods=['GET'])
def get_performance_trends():
    """성능 트렌드 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        data = dashboard_service.get_performance_trends(days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"성능 트렌드 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/delay-metrics', methods=['GET'])
def get_delay_metrics():
    """지연시간 메트릭 요약 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        data = dashboard_service.get_delay_metrics_summary(days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"지연시간 메트릭 요약 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/error-summary', methods=['GET'])
def get_error_summary():
    """오류 요약 조회"""
    try:
        days = request.args.get('days', 7, type=int)
        data = dashboard_service.get_error_summary(days)
        return jsonify(data)
    except Exception as e:
        logger.error(f"오류 요약 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/ais-summary', methods=['GET'])
def get_ais_summary():
    """AIS 데이터 요약 조회"""
    try:
        # MySQL 연결
        connection = pymysql.connect(
            host='localhost',
            port=3307,
            user='root',
            password='Keti1234!',
            database='port_database',
            charset='utf8mb4'
        )
        
        with connection.cursor() as cursor:
            # 1. 총 선박 수
            cursor.execute("SELECT COUNT(*) FROM ais_info")
            total_ships = cursor.fetchone()[0]
            
            # 2. 고유 선박 타입 수
            cursor.execute("SELECT COUNT(DISTINCT vsslTp) FROM ais_info WHERE vsslTp IS NOT NULL")
            unique_ship_types = cursor.fetchone()[0]
            
            # 3. 고유 국적 수
            cursor.execute("SELECT COUNT(DISTINCT flag) FROM ais_info WHERE flag IS NOT NULL")
            unique_flags = cursor.fetchone()[0]
            
            # 4. 평균 속도
            cursor.execute("SELECT AVG(sog) FROM ais_info WHERE sog > 0")
            avg_speed = cursor.fetchone()[0]
            avg_speed = round(float(avg_speed), 1) if avg_speed else 0
            
            # 5. 최대 속도
            cursor.execute("SELECT MAX(sog) FROM ais_info WHERE sog > 0")
            max_speed = cursor.fetchone()[0]
            max_speed = round(float(max_speed), 1) if max_speed else 0
            
            # 6. 선박 타입별 분포 (상위 5개)
            cursor.execute("""
                SELECT vsslTp, COUNT(*) as count 
                FROM ais_info 
                WHERE vsslTp IS NOT NULL 
                GROUP BY vsslTp 
                ORDER BY count DESC 
                LIMIT 5
            """)
            ship_type_distribution = [{"type": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # 7. 국적별 분포 (상위 5개)
            cursor.execute("""
                SELECT flag, COUNT(*) as count 
                FROM ais_info 
                WHERE flag IS NOT NULL 
                GROUP BY flag 
                ORDER BY count DESC 
                LIMIT 5
            """)
            flag_distribution = [{"flag": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            # 8. 속도 구간별 분포
            cursor.execute("""
                SELECT 
                    CASE 
                        WHEN sog <= 5 THEN '0-5 노트'
                        WHEN sog <= 10 THEN '6-10 노트'
                        WHEN sog <= 15 THEN '11-15 노트'
                        WHEN sog <= 20 THEN '16-20 노트'
                        ELSE '20+ 노트'
                    END as speed_range,
                    COUNT(*) as count
                FROM ais_info 
                WHERE sog > 0 
                GROUP BY speed_range
                ORDER BY 
                    CASE speed_range
                        WHEN '0-5 노트' THEN 1
                        WHEN '6-10 노트' THEN 2
                        WHEN '11-15 노트' THEN 3
                        WHEN '16-20 노트' THEN 4
                        ELSE 5
                    END
            """)
            speed_distribution = [{"range": row[0], "count": row[1]} for row in cursor.fetchall()]
        
        connection.close()
        
        summary_data = {
            "total_ships": total_ships,
            "unique_ship_types": unique_ship_types,
            "unique_flags": unique_flags,
            "avg_speed": avg_speed,
            "max_speed": max_speed,
            "ship_type_distribution": ship_type_distribution,
            "flag_distribution": flag_distribution,
            "speed_distribution": speed_distribution
        }
        
        return jsonify(summary_data)
        
    except Exception as e:
        logger.error(f"AIS 데이터 요약 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/inspection-details/<inspection_id>', methods=['GET'])
def get_inspection_details(inspection_id):
    """특정 검사 상세 정보 조회"""
    try:
        data = dashboard_service.get_inspection_details(inspection_id)
        if not data:
            return jsonify({'error': '검사 정보를 찾을 수 없습니다'}), 404
        return jsonify(data)
    except Exception as e:
        logger.error(f"검사 상세 정보 조회 실패: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard/health', methods=['GET'])
def health_check():
    """헬스 체크"""
    return jsonify({'status': 'healthy', 'service': 'dashboard-api'})

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'API 엔드포인트를 찾을 수 없습니다'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': '내부 서버 오류가 발생했습니다'}), 500

if __name__ == '__main__':
    logger.info("Dashboard API 서버를 시작합니다...")
    logger.info("서버 주소: http://localhost:3000")
    logger.info("API 문서: http://localhost:3000/api/dashboard/health")
    
    try:
        app.run(
            host='0.0.0.0',
            port=3000,
            debug=True,
            threaded=True
        )
    except Exception as e:
        logger.error(f"서버 시작 실패: {e}")
