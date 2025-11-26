#!/bin/bash
# 백엔드 재시작 스크립트

echo "🔄 백엔드 재시작 중..."

# 기존 프로세스 종료
PID=$(ps aux | grep "python.*main_new.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$PID" ]; then
    echo "⏹️  기존 백엔드 종료 (PID: $PID)"
    kill $PID
    sleep 2
fi

# 새 프로세스 시작
cd /home/cotlab/UI_project_new/backend
nohup /home/cotlab/UI_project_new/.venv/bin/python3 main_new.py > ../backend.log 2>&1 &

sleep 3

# 프로세스 확인
NEW_PID=$(ps aux | grep "python.*main_new.py" | grep -v grep | awk '{print $2}')

if [ ! -z "$NEW_PID" ]; then
    echo "✅ 백엔드 재시작 완료 (PID: $NEW_PID)"
    echo "📋 로그: tail -f /home/cotlab/UI_project_new/backend.log"
else
    echo "❌ 백엔드 시작 실패"
    echo "로그 확인: cat /home/cotlab/UI_project_new/backend.log"
fi

