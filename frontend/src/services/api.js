/**
 * API Service
 *
 * Axios instance duy nhất cho all API calls.
 * - Request interceptor: tự gắn Authorization header
 * - Response interceptor: xử lý 401 → redirect /auth
 *
 * Để bỏ qua auto-redirect 401 (ví dụ watchlist), thêm
 * { _skipAuthRedirect: true } vào config của request.
 */

// =====================================================
// IMPORTS
// =====================================================
import axios from 'axios'

// =====================================================
// AXIOS INSTANCE
// =====================================================
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// =====================================================
// REQUEST INTERCEPTOR
// =====================================================
/**
 * Request interceptor - Tự động gắn JWT token vào header
 */
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// =====================================================
// RESPONSE INTERCEPTOR
// =====================================================
/**
 * Response interceptor - Xử lý lỗi 401 tự động
 *
 * WHY: Chỉ redirect khi:
 * 1. Không phải request auth (login/register)
 * 2. Không đang ở trang /auth (tránh loop)
 * 3. Request không có cờ _skipAuthRedirect = true
 */
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const requestUrl = error.config?.url || ''
      const isAuthRequest =
        requestUrl.includes('/auth/login') ||
        requestUrl.includes('/auth/register')

      // Cờ cho phép caller tự xử lý 401 mà không bị redirect
      const skipRedirect = error.config?._skipAuthRedirect === true

      if (!isAuthRequest && !skipRedirect && window.location.pathname !== '/auth') {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        window.location.href = '/auth'
      }
    }

    return Promise.reject(error)
  }
)

// =====================================================
// EXPORT
// =====================================================
export { api }