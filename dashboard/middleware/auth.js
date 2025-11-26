const { extractUserFromToken } = require('../utils/jwt');
const User = require('../models/User');

// JWT 토큰 인증 미들웨어
const authenticateToken = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({ 
        success: false, 
        message: '액세스 토큰이 필요합니다.' 
      });
    }

    // 토큰에서 사용자 정보 추출
    const userInfo = extractUserFromToken(token);
    
    if (!userInfo) {
      return res.status(403).json({ 
        success: false, 
        message: '유효하지 않은 토큰입니다.' 
      });
    }

    // DB에서 사용자 존재 여부 확인 (선택사항)
    const user = await User.findById(userInfo.userId);
    if (!user) {
      return res.status(403).json({ 
        success: false, 
        message: '사용자를 찾을 수 없습니다.' 
      });
    }

    // 요청 객체에 사용자 정보 추가
    req.user = {
      ...userInfo,
      email: user.email,
      full_name: user.full_name
    };

    next();
  } catch (error) {
    console.error('인증 미들웨어 오류:', error);
    return res.status(500).json({ 
      success: false, 
      message: '서버 오류가 발생했습니다.' 
    });
  }
};

// 역할 기반 접근 제어 미들웨어
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({ 
        success: false, 
        message: '인증이 필요합니다.' 
      });
    }

    const userRole = req.user.role;
    const allowedRoles = Array.isArray(roles) ? roles : [roles];

    if (!allowedRoles.includes(userRole)) {
      return res.status(403).json({ 
        success: false, 
        message: '권한이 부족합니다.' 
      });
    }

    next();
  };
};

// 선택적 인증 미들웨어 (토큰이 있으면 검증, 없어도 통과)
const optionalAuth = async (req, res, next) => {
  try {
    const authHeader = req.headers.authorization;
    const token = authHeader && authHeader.split(' ')[1];

    if (token) {
      const userInfo = extractUserFromToken(token);
      if (userInfo) {
        const user = await User.findById(userInfo.userId);
        if (user) {
          req.user = {
            ...userInfo,
            email: user.email,
            full_name: user.full_name
          };
        }
      }
    }

    next();
  } catch (error) {
    // 선택적 인증에서는 오류가 발생해도 계속 진행
    next();
  }
};

module.exports = {
  authenticateToken,
  requireRole,
  optionalAuth
};
