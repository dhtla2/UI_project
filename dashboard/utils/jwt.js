const jwt = require('jsonwebtoken');
require('dotenv').config();

const JWT_SECRET = process.env.JWT_SECRET || 'fallback-secret-key';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '24h';

// JWT 토큰 생성
function generateToken(payload) {
  try {
    return jwt.sign(payload, JWT_SECRET, { 
      expiresIn: JWT_EXPIRES_IN,
      issuer: 'dashboard-app'
    });
  } catch (error) {
    console.error('JWT 토큰 생성 실패:', error);
    throw error;
  }
}

// JWT 토큰 검증
function verifyToken(token) {
  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    console.error('JWT 토큰 검증 실패:', error);
    throw error;
  }
}

// JWT 토큰 디코딩 (검증 없이)
function decodeToken(token) {
  try {
    return jwt.decode(token);
  } catch (error) {
    console.error('JWT 토큰 디코딩 실패:', error);
    return null;
  }
}

// 토큰에서 사용자 정보 추출
function extractUserFromToken(token) {
  try {
    const decoded = verifyToken(token);
    return {
      userId: decoded.userId,
      username: decoded.username,
      role: decoded.role,
      iat: decoded.iat,
      exp: decoded.exp
    };
  } catch (error) {
    return null;
  }
}

module.exports = {
  generateToken,
  verifyToken,
  decodeToken,
  extractUserFromToken
};
