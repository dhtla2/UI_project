const { pool } = require('../db/connection');
const bcrypt = require('bcryptjs');

class User {
  // 사용자명으로 사용자 찾기
  static async findByUsername(username) {
    try {
      const [rows] = await pool.execute(
        'SELECT * FROM users WHERE username = ? AND is_active = TRUE',
        [username]
      );
      return rows[0] || null;
    } catch (error) {
      console.error('사용자 조회 실패:', error);
      throw error;
    }
  }

  // ID로 사용자 찾기
  static async findById(id) {
    try {
      const [rows] = await pool.execute(
        'SELECT id, username, email, full_name, role, created_at FROM users WHERE id = ? AND is_active = TRUE',
        [id]
      );
      return rows[0] || null;
    } catch (error) {
      console.error('사용자 ID 조회 실패:', error);
      throw error;
    }
  }

  // 비밀번호 검증
  static async validatePassword(plainPassword, hashedPassword) {
    try {
      return await bcrypt.compare(plainPassword, hashedPassword);
    } catch (error) {
      console.error('비밀번호 검증 실패:', error);
      return false;
    }
  }

  // 마지막 로그인 시간 업데이트
  static async updateLastLogin(userId) {
    try {
      await pool.execute(
        'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?',
        [userId]
      );
    } catch (error) {
      console.error('마지막 로그인 시간 업데이트 실패:', error);
    }
  }

  // 새 사용자 생성 (선택사항)
  static async create(userData) {
    try {
      const { username, password, email, full_name, role = 'user' } = userData;
      const hashedPassword = await bcrypt.hash(password, 10);
      
      const [result] = await pool.execute(
        'INSERT INTO users (username, password_hash, email, full_name, role) VALUES (?, ?, ?, ?, ?)',
        [username, hashedPassword, email, full_name, role]
      );
      
      return result.insertId;
    } catch (error) {
      console.error('사용자 생성 실패:', error);
      throw error;
    }
  }

  // 모든 사용자 조회 (관리자용)
  static async findAll() {
    try {
      const [rows] = await pool.execute(
        'SELECT id, username, email, full_name, role, is_active, created_at, last_login FROM users ORDER BY created_at DESC'
      );
      return rows;
    } catch (error) {
      console.error('사용자 목록 조회 실패:', error);
      throw error;
    }
  }
}

module.exports = User;
