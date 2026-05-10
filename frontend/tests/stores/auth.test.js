/**
 * tests/stores/auth.test.js
 *
 * What: Unit tests cho Pinia auth store
 * Why: Đảm bảo login/logout/isAuthenticated hoạt động đúng
 * How: Dùng vitest + createPinia(), mock axios qua vi.mock
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// =====================================================
// MOCK axios (api service)
// =====================================================
vi.mock('@/services/api', () => ({
  api: {
    post: vi.fn()
  }
}))

// Import sau khi đã mock để lấy tham chiếu mock
import { api } from '@/services/api'

describe('auth store', () => {
  beforeEach(() => {
    // Tạo Pinia mới và kích hoạt trước mỗi test — đảm bảo isolation
    setActivePinia(createPinia())

    // Reset localStorage sạch hoàn toàn
    localStorage.clear()

    // Reset tất cả mock calls
    vi.clearAllMocks()
  })

  // -------------------------------------------------------------------
  // Test #1: isAuthenticated trả false khi chưa có token
  // -------------------------------------------------------------------
  it('isAuthenticated returns false when no token', () => {
    const store = useAuthStore()
    expect(store.isAuthenticated).toBe(false)
  })

  // -------------------------------------------------------------------
  // Test #2: login action lưu token và user vào store + localStorage
  // -------------------------------------------------------------------
  it('login action sets token and user', async () => {
    // Giả lập API server trả về dữ liệu hợp lệ
    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-jwt-token',
        user: { id: 1, username: 'alice' }
      }
    })

    const store = useAuthStore()
    await store.login('alice', 'pass123')

    // Kiểm tra state trong store
    expect(store.token).toBe('mock-jwt-token')
    expect(store.user).toEqual({ id: 1, username: 'alice' })

    // Kiểm tra đã persist vào localStorage
    expect(localStorage.getItem('token')).toBe('mock-jwt-token')
    expect(JSON.parse(localStorage.getItem('user'))).toEqual({ id: 1, username: 'alice' })
  })

  // -------------------------------------------------------------------
  // Test #3: logout xóa token và user khỏi store + localStorage
  // -------------------------------------------------------------------
  it('logout clears token and user from localStorage', async () => {
    // Chuẩn bị: set sẵn dữ liệu
    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-jwt-token',
        user: { id: 1, username: 'alice' }
      }
    })
    const store = useAuthStore()
    await store.login('alice', 'pass123')

    // Hành động: logout
    store.logout()

    // Kiểm tra store đã bị reset
    expect(store.token).toBe('')
    expect(store.user).toBeNull()

    // Kiểm tra localStorage đã bị xóa
    expect(localStorage.getItem('token')).toBeNull()
    expect(localStorage.getItem('user')).toBeNull()
  })

  // -------------------------------------------------------------------
  // Test #4: isAuthenticated trả true sau khi login thành công
  // -------------------------------------------------------------------
  it('isAuthenticated returns true after login', async () => {
    api.post.mockResolvedValueOnce({
      data: {
        access_token: 'mock-jwt-token',
        user: { id: 1, username: 'alice' }
      }
    })

    const store = useAuthStore()
    await store.login('alice', 'pass123')

    expect(store.isAuthenticated).toBe(true)
  })
})
