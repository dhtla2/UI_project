const mysql = require('mysql2/promise');
const bcrypt = require('bcryptjs');
require('dotenv').config();

async function setupDatabase() {
  let connection;
  
  try {
    // MySQL 연결
    connection = await mysql.createConnection({
      host: process.env.DB_HOST || 'localhost',
      port: process.env.DB_PORT || 3307,
      user: process.env.DB_USER || 'root',
      password: process.env.DB_PASSWORD || 'Keti1234!',
      database: process.env.DB_NAME || 'port_database'
    });

    console.log('✅ MySQL 연결 성공');

    // 사용자 테이블 생성
    const createTableQuery = `
      CREATE TABLE IF NOT EXISTS users (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100),
        full_name VARCHAR(100),
        role ENUM('admin', 'user', 'viewer') DEFAULT 'user',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        last_login TIMESTAMP NULL
      )
    `;

    await connection.execute(createTableQuery);
    console.log('✅ users 테이블 생성 완료');

    // 기본 사용자 계정 생성
    const adminPasswordHash = await bcrypt.hash('admin123', 10);
    const userPasswordHash = await bcrypt.hash('user123', 10);

    const insertUsersQuery = `
      INSERT IGNORE INTO users (username, password_hash, email, full_name, role) VALUES 
      (?, ?, ?, ?, ?),
      (?, ?, ?, ?, ?)
    `;

    await connection.execute(insertUsersQuery, [
      'admin', adminPasswordHash, 'admin@example.com', '관리자', 'admin',
      'user', userPasswordHash, 'user@example.com', '일반사용자', 'user'
    ]);

    console.log('✅ 기본 사용자 계정 생성 완료');
    console.log('📋 생성된 계정:');
    console.log('   - admin / admin123 (관리자)');
    console.log('   - user / user123 (일반사용자)');

    // 생성된 사용자 확인
    const [users] = await connection.execute('SELECT id, username, email, full_name, role, created_at FROM users');
    console.log('📊 현재 사용자 목록:');
    console.table(users);

  } catch (error) {
    console.error('❌ 데이터베이스 설정 실패:', error.message);
    process.exit(1);
  } finally {
    if (connection) {
      await connection.end();
      console.log('✅ MySQL 연결 종료');
    }
  }
}

// 스크립트 실행
if (require.main === module) {
  setupDatabase();
}

module.exports = { setupDatabase };
