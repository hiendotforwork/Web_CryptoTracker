/**
 * Crypto Tracker - API Service
 * 
 * Axios instance duy nhất cho all API calls.
 * - Request interceptor: tự gắn Authorization header
 * - Response interceptor: xử lý 401 → redirect to /auth
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
    // Lấy token từ localStorage
    const token = localStorage.getItem('token')
    
    // Nếu có token, gắn vào Authorization header
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// =====================================================
// RESPONSE INTERCEPTOR
// =====================================================
/**
 * Response interceptor - Xử lý lỗi authentication
 */
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Xử lý lỗi 401 - Unauthorized
    if (error.response?.status === 401) {
      // Xóa token khỏi localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Redirect về trang /auth
      window.location.href = '/auth'
    }
    
    return Promise.reject(error)
  }
)

// =====================================================
// EXPORT
// =====================================================
export { api }