/**
 * Crypto Tracker - Auth Store (Pinia)
 * 
 * Quản lý trạng thái authentication với JWT token.
 * Sử dụng localStorage để persist sau reload.
 */

// =====================================================
// SETUP STORE VỚI PINIA COMPOSITION API
// =====================================================
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { api } from '@/services/api'

export const useAuthStore = defineStore('auth', () => {
  // =====================================================
  // STATE - Khởi tạo từ localStorage để persist sau reload
  // =====================================================
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  
  // =====================================================
  // GETTERS
  // =====================================================
  const isAuthenticated = computed(() => !!token.value)
  
  // =====================================================
  // ACTIONS
  // =====================================================
  
  /**
   * Đăng nhập
   * @param {string} username - Tên đăng nhập
   * @param {string} password - Mật khẩu
   */
  async function login(username, password) {
    const response = await api.post('/auth/login', {
      username,
      password
    })
    
    // Lưu token và user
    token.value = response.data.access_token
    user.value = response.data.user
    
    // Persist vào localStorage
    localStorage.setItem('token', token.value)
    localStorage.setItem('user', JSON.stringify(user.value))
    
    return response.data
  }
  
  /**
   * Đăng ký
   * @param {object} data - Object chứa username, email, password
   */
  async function register(data) {
    const response = await api.post('/auth/register', data)
    return response.data
  }
  
  /**
   * Đăng xuất - Xóa token và user khỏi localStorage
   */
  function logout() {
    token.value = ''
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    
    // Clear watchlist khi logout
    // Import dynamic để tránh circular dependency
    import('@/stores/watchlistStore').then(({ useWatchlistStore }) => {
      const watchlistStore = useWatchlistStore()
      watchlistStore.clear()
    })
  }
  
  /**
   * Đổi mật khẩu
   * @param {string} currentPassword - Mật khẩu hiện tại
   * @param {string} newPassword - Mật khẩu mới
   */
  async function changePassword(currentPassword, newPassword) {
    const response = await api.patch('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword
    })
    return response.data
  }

  /**
   * Đổi tên đăng nhập
   * @param {string} newUsername - Username mới
   * @param {string} currentPassword - Mật khẩu xác nhận
   */
  async function changeUsername(newUsername, currentPassword) {
    const response = await api.patch('/auth/change-username', {
      new_username: newUsername,
      current_password: currentPassword
    })

    // Cập nhật store và localStorage với username mới
    if (response.data.user) {
      user.value = { ...user.value, username: response.data.user.username }
      localStorage.setItem('user', JSON.stringify(user.value))
    }

    return response.data
  }

  /**
   * Xóa tài khoản — logout sau khi xóa thành công
   * @param {string} currentPassword - Mật khẩu xác nhận
   */
  async function deleteAccount(currentPassword) {
    const response = await api.delete('/auth/delete-account', {
      data: { current_password: currentPassword }
    })

    // Xóa hết state sau khi tài khoản bị xóa
    logout()

    return response.data
  }

  // =====================================================
  // RETURN
  // =====================================================
  return {
    // State
    token,
    user,
    
    // Getters
    isAuthenticated,
    
    // Actions
    login,
    register,
    logout,
    changePassword,
    changeUsername,
    deleteAccount
  }
})