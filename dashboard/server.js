const express = require('express');
const path = require('path');
const cors = require('cors');
const { createProxyMiddleware } = require('http-proxy-middleware');
require('dotenv').config();

// 인증 관련 모듈 import
const authRoutes = require('./routes/auth');
const { testConnection } = require('./db/connection');

const app = express();
const PORT = process.env.PORT || 8000;
const BACKEND_URL = 'http://localhost:3000';

// CORS 설정
app.use(cors({
  origin: ['http://localhost:3000', 'http://localhost:8000'],
  credentials: true
}));

// JSON 파싱 미들웨어
app.use(express.json());

// 인증 라우트 설정 (프록시보다 먼저 설정)
app.use('/api/auth', authRoutes);

// API 프록시 설정 - 3000포트 Backend로 프록시
app.use('/api', async (req, res) => {
  console.log(`[DEBUG] API Request: ${req.method} ${req.url}`);
  
  try {
    const targetUrl = `${BACKEND_URL}/api${req.url}`;
    console.log(`[PROXY] ${req.method} ${req.url} → ${targetUrl}`);
    
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });
    
    const data = await response.json();
    console.log(`[PROXY] Response: ${response.status} for ${req.url}`);
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ 
      error: 'Proxy Error',
      message: error.message 
    });
  }
});

// UI 프록시 설정 - 3000포트 Backend로 프록시
app.use('/ui', async (req, res) => {
  console.log(`[DEBUG] UI Request: ${req.method} ${req.url}`);
  
  try {
    const targetUrl = `${BACKEND_URL}/ui${req.url}`;
    console.log(`[PROXY] ${req.method} ${req.url} → ${targetUrl}`);
    
    const response = await fetch(targetUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
        ...req.headers
      },
      body: req.method !== 'GET' ? JSON.stringify(req.body) : undefined
    });
    
    const data = await response.json();
    console.log(`[PROXY] Response: ${response.status} for ${req.url}`);
    
    res.status(response.status).json(data);
  } catch (error) {
    console.error('Proxy Error:', error);
    res.status(500).json({ 
      error: 'Proxy Error',
      message: error.message 
    });
  }
});

// 헬스 체크 엔드포인트
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    message: 'Express server is running',
    backend: BACKEND_URL,
    timestamp: new Date().toISOString()
  });
});

// React 빌드 파일 서빙
app.use(express.static(path.join(__dirname, 'build')));

// React 라우팅 - API가 아닌 모든 요청을 index.html로 리다이렉트
app.use((req, res) => {
  // API 요청이 아닌 경우에만 React 앱을 서빙
  if (!req.path.startsWith('/api') && !req.path.startsWith('/health')) {
    res.sendFile(path.join(__dirname, 'build', 'index.html'));
  } else {
    res.status(404).json({ error: 'Not Found' });
  }
});

// 서버 시작
async function startServer() {
  // 데이터베이스 연결 테스트
  const dbConnected = await testConnection();
  if (!dbConnected) {
    console.error('❌ 데이터베이스 연결 실패. 서버를 시작할 수 없습니다.');
    process.exit(1);
  }

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Express server running on http://0.0.0.0:${PORT}`);
    console.log(`📡 Proxying API calls to: ${BACKEND_URL}`);
    console.log(`🔗 Health check: http://0.0.0.0:${PORT}/health`);
    console.log(`🔐 Auth API: http://0.0.0.0:${PORT}/api/auth`);
    console.log(`📁 Serving React app from: ${path.join(__dirname, 'build')}`);
  });
}

startServer().catch(console.error);
