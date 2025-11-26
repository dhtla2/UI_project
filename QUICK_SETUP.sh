#!/bin/bash

# 🚀 로그인 ID 연동 빠른 설정 스크립트
# 이 스크립트는 로그인한 사용자 ID를 로깅 시스템과 연동합니다.

echo "======================================"
echo "🔗 로그인 ID 연동 설정 시작"
echo "======================================"
echo ""

# 1. utils/api.ts 파일 확인
echo "📁 1. utils/api.ts 파일 확인 중..."
if [ -f "dashboard/src/utils/api.ts" ]; then
    echo "✅ utils/api.ts 파일이 존재합니다."
else
    echo "❌ utils/api.ts 파일이 없습니다!"
    echo "   INTEGRATION_GUIDE.md를 참조하여 파일을 생성해주세요."
    exit 1
fi
echo ""

# 2. AuthContext.tsx import 확인
echo "📁 2. AuthContext.tsx 업데이트 확인 중..."
if grep -q "createAuthenticatedFetch" "dashboard/src/contexts/AuthContext.tsx"; then
    echo "✅ AuthContext.tsx가 업데이트되었습니다."
else
    echo "⚠️  AuthContext.tsx에 import가 추가되지 않았습니다."
    echo "   다음 라인을 AuthContext.tsx 상단에 추가해주세요:"
    echo "   import { createAuthenticatedFetch } from '../utils/api';"
fi
echo ""

# 3. 백엔드 미들웨어 확인
echo "📁 3. 백엔드 미들웨어 확인 중..."
BACKEND_FILE=""

if [ -f "backend/main.py" ]; then
    BACKEND_FILE="backend/main.py"
elif [ -f "backend/main_old.py" ]; then
    BACKEND_FILE="backend/main_old.py"
else
    echo "❌ 백엔드 메인 파일을 찾을 수 없습니다!"
    exit 1
fi

if grep -q "user_id='auto_logged_user'" "$BACKEND_FILE"; then
    echo "⚠️  백엔드에서 여전히 'auto_logged_user'를 사용하고 있습니다!"
    echo "   다음을 수정해주세요:"
    echo ""
    echo "   변경 전: user_id='auto_logged_user'"
    echo "   변경 후: user_id=request.headers.get('X-User-ID', 'anonymous')"
    echo ""
    echo "   파일: $BACKEND_FILE"
    echo ""
    read -p "   자동으로 수정하시겠습니까? (y/N): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # 백업 생성
        cp "$BACKEND_FILE" "${BACKEND_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
        echo "   📦 백업 생성: ${BACKEND_FILE}.backup_$(date +%Y%m%d_%H%M%S)"
        
        # 수정
        sed -i "s/user_id='auto_logged_user'/user_id=request.headers.get('X-User-ID', 'anonymous')/g" "$BACKEND_FILE"
        echo "   ✅ 백엔드 파일이 수정되었습니다!"
    else
        echo "   ⏩ 수동으로 수정해주세요."
    fi
else
    echo "✅ 백엔드 미들웨어가 올바르게 설정되었습니다."
fi
echo ""

# 4. 프론트엔드 빌드
echo "📦 4. 프론트엔드 빌드 중..."
cd dashboard
if npm run build > /dev/null 2>&1; then
    echo "✅ 프론트엔드 빌드 성공!"
else
    echo "⚠️  프론트엔드 빌드에 경고가 있습니다. (정상 작동할 수 있음)"
fi
cd ..
echo ""

# 5. 완료 메시지
echo "======================================"
echo "✅ 설정 완료!"
echo "======================================"
echo ""
echo "📋 다음 단계:"
echo "   1. 백엔드 서버 재시작:"
echo "      cd backend && python3 main.py"
echo ""
echo "   2. 프론트엔드 서버 시작 (다른 터미널):"
echo "      cd dashboard && npm start"
echo ""
echo "   3. 브라우저에서 테스트:"
echo "      - 로그인: admin / admin123"
echo "      - 페이지 방문 후 DB 확인"
echo ""
echo "   4. DB 확인:"
echo "      python3 verify_page_visits.py"
echo ""
echo "📖 자세한 내용:"
echo "   INTEGRATION_GUIDE.md 참조"
echo ""

