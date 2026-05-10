/**
 * Crypto Tracker - Vue Router Configuration
 * 
 * Định nghĩa 5 routes với lazy import và navigation guard kiểm tra auth.
 */

// =====================================================
// IMPORTS
// =====================================================
import { createRouter, createWebHistory } from 'vue-router'

// =====================================================
// ROUTES
// =====================================================
const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Crypto Tracker' }
  },
  {
    path: '/auth',
    name: 'Auth',
    component: () => import('@/views/AuthView.vue'),
    meta: { title: 'Đăng nhập - Crypto Tracker' }
  },
  {
    path: '/coin/:id',
    name: 'CoinDetail',
    component: () => import('@/views/CoinDetailView.vue'),
    meta: { title: 'Chi tiết coin - Crypto Tracker' }
  },
  {
    path: '/news',
    name: 'News',
    component: () => import('@/views/NewsView.vue'),
    meta: { title: 'Tin tức - Crypto Tracker' }
  },
  {
    path: '/compare',
    name: 'Compare',
    component: () => import('@/views/CompareView.vue'),
    meta: { title: 'So sánh - Crypto Tracker' }
  },
  {
    path: '/watchlist',
    name: 'Watchlist',
    component: () => import('@/views/WatchlistView.vue'),
    meta: { 
      title: 'Watchlist - Crypto Tracker',
      requiresAuth: true 
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404 - Không tìm thấy' }
  }
]

// =====================================================
// ROUTER INSTANCE
// =====================================================
const router = createRouter({
  history: createWebHistory(),
  routes
})

// =====================================================
// NAVIGATION GUARD
// =====================================================
/**
 * Navigation Guard - Kiểm tra auth trước khi vào route cần auth
 * 
 * Logic:
 * - Nếu route có meta.requiresAuth = true
 * - Và chưa có token trong localStorage
 * - Thì redirect về /auth
 */
router.beforeEach((to, from, next) => {
  // Cập nhật document.title theo route meta
  if (to.meta.title) {
    document.title = to.meta.title
  }
  
  // Kiểm tra route có yêu cầu auth không
  if (to.meta.requiresAuth) {
    const token = localStorage.getItem('token')
    
    if (!token) {
      // Chưa login, redirect về /auth
      next({ name: 'Auth', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // Cho phép tiếp tục
  next()
})

export default router