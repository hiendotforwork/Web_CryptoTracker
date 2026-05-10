<template>
  <div class="app">
    <!-- Animated Background -->
    <div class="bg-gradient"></div>
    <div class="bg-grid"></div>
    
    <!-- Navbar -->
    <nav class="navbar">
      <div class="navbar-glow"></div>
      <div class="container navbar-container">
        <!-- Logo -->
        <router-link to="/" class="navbar-brand">
          <div class="brand-icon-wrapper">
            <svg class="brand-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v12M6 12h12"/>
              <circle cx="12" cy="12" r="4"/>
            </svg>
            <div class="brand-icon-glow"></div>
          </div>
          <span class="brand-text">
            <span class="brand-text-main">Crypto</span>
            <span class="brand-text-accent">Tracker</span>
          </span>
        </router-link>
        
        <!-- Desktop Navigation -->
        <div class="navbar-nav">
          <router-link 
            v-for="link in navLinks" 
            :key="link.path"
            :to="link.path" 
            class="nav-link"
            :class="{ 'nav-link-active': link.path === '/' && $route.path === '/' }"
          >
            <component :is="link.icon" class="nav-icon" />
            <span>{{ link.label }}</span>
          </router-link>
          
          <div class="nav-divider"></div>
          
          <template v-if="isAuthenticated">
            <router-link to="/watchlist" class="nav-link nav-link-watchlist">
              <StarIcon class="nav-icon" />
              <span>Watchlist</span>
            </router-link>
            <div class="nav-user-wrapper">
              <div class="nav-user-avatar">
                {{ user?.username?.charAt(0)?.toUpperCase() || 'U' }}
              </div>
              <span class="nav-user">{{ user?.username }}</span>
            </div>
            <button class="btn-logout" @click="handleLogout">
              <LogOutIcon class="btn-icon" />
              <span>Đăng xuất</span>
            </button>
          </template>
          <router-link v-else to="/auth" class="nav-link btn-login">
            <LogInIcon class="nav-icon" />
            <span>Đăng nhập</span>
          </router-link>
        </div>
        
        <!-- Mobile Hamburger -->
        <button 
          class="navbar-toggler" 
          @click="isMenuOpen = !isMenuOpen"
          :aria-expanded="isMenuOpen"
          aria-label="Toggle navigation"
        >
          <span class="toggler-icon" :class="{ open: isMenuOpen }">
            <span></span>
            <span></span>
            <span></span>
          </span>
        </button>
      </div>
      
      <!-- Mobile Menu -->
      <Transition name="slide-down">
        <div class="navbar-menu" :class="{ open: isMenuOpen }" v-show="isMenuOpen">
          <div class="mobile-menu-inner">
            <router-link 
              v-for="link in navLinks" 
              :key="link.path"
              :to="link.path" 
              class="mobile-link"
              @click="isMenuOpen = false"
            >
              <component :is="link.icon" class="mobile-icon" />
              <span>{{ link.label }}</span>
            </router-link>
            
            <div class="mobile-divider"></div>
            
            <template v-if="isAuthenticated">
              <router-link 
                to="/watchlist" 
                class="mobile-link mobile-link-watchlist"
                @click="isMenuOpen = false"
              >
                <StarIcon class="mobile-icon" />
                <span>Watchlist</span>
              </router-link>
              <div class="mobile-user-info">
                <div class="mobile-user-avatar">
                  {{ user?.username?.charAt(0)?.toUpperCase() || 'U' }}
                </div>
                <span class="mobile-user">{{ user?.username }}</span>
              </div>
              <button class="mobile-link btn-logout" @click="handleLogout">
                <LogOutIcon class="mobile-icon" />
                <span>Đăng xuất</span>
              </button>
            </template>
            <router-link v-else to="/auth" class="mobile-link btn-login" @click="isMenuOpen = false">
              <LogInIcon class="mobile-icon" />
              <span>Đăng nhập</span>
            </router-link>
          </div>
        </div>
      </Transition>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <Transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </Transition>
      </router-view>
    </main>
    
    <!-- Toast Notifications -->
    <TransitionGroup name="toast" tag="div" class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        <div class="toast-icon">
          <CheckIcon v-if="toast.type === 'success'" />
          <AlertIcon v-else-if="toast.type === 'error'" />
          <InfoIcon v-else />
        </div>
        <span class="toast-message">{{ toast.message }}</span>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup>
/**
 * Crypto Tracker - App Layout Component
 * 
 * Component cha chính chứa:
 * - Navbar responsive với hamburger menu
 * - Background effects (gradient + grid)
 * - Toast notification system
 * - Page transitions
 * 
 * WHY: Tách riêng layout giúp các view con tập trung vào logic nghiệp vụ
 * HOW: Dùng Composition API, provide/inject cho toast system
 */
import { ref, computed, onMounted, onUnmounted, h } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// =====================================================
// ICONS (Inline SVG components)
// =====================================================

/**
 * Icon component cho Home
 */
const HomeIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('path', { d: 'M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z' }),
    h('polyline', { points: '9 22 9 12 15 12 15 22' })
  ])
}

/**
 * Icon component cho News
 */
const NewsIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('path', { d: 'M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2' })
  ])
}

/**
 * Icon component cho Star (Watchlist)
 */
const StarIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('polygon', { points: '12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2' })
  ])
}

/**
 * Icon component cho Login
 */
const LogInIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('path', { d: 'M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4' }),
    h('polyline', { points: '10 17 15 12 10 7' }),
    h('line', { x1: '15', y1: '12', x2: '3', y2: '12' })
  ])
}

/**
 * Icon component cho Logout
 */
const LogOutIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('path', { d: 'M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4' }),
    h('polyline', { points: '16 17 21 12 16 7' }),
    h('line', { x1: '21', y1: '12', x2: '9', y2: '12' })
  ])
}

/**
 * Icon component cho Check (Toast)
 */
const CheckIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('polyline', { points: '20 6 9 17 4 12' })
  ])
}

/**
 * Icon component cho Alert
 */
const AlertIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('line', { x1: '12', y1: '8', x2: '12', y2: '12' }),
    h('line', { x1: '12', y1: '16', x2: '12.01', y2: '16' })
  ])
}

/**
 * Icon component cho Info
 */
const InfoIcon = {
  render: () => h('svg', { 
    viewBox: '0 0 24 24', 
    fill: 'none', 
    stroke: 'currentColor', 
    'stroke-width': '2',
    'stroke-linecap': 'round',
    'stroke-linejoin': 'round'
  }, [
    h('circle', { cx: '12', cy: '12', r: '10' }),
    h('line', { x1: '12', y1: '16', x2: '12', y2: '12' }),
    h('line', { x1: '12', y1: '8', x2: '12.01', y2: '8' })
  ])
}

// =====================================================
// NAVIGATION LINKS
// =====================================================
const navLinks = [
  { path: '/', label: 'Trang chủ', icon: HomeIcon },
  { path: '/news', label: 'Tin tức', icon: NewsIcon },
]

// =====================================================
// STATE & STORE
// =====================================================
const router = useRouter()
const authStore = useAuthStore()

// Local state
const isMenuOpen = ref(false)
const toasts = ref([])
const windowWidth = ref(window.innerWidth)

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// =====================================================
// METHODS
// =====================================================

/**
 * Xử lý đăng xuất
 * - Gọi store logout
 * - Đóng menu mobile
 * - Redirect về trang chủ
 */
function handleLogout() {
  authStore.logout()
  isMenuOpen.value = false
  router.push('/')
}

/**
 * Hiển thị toast notification
 * @param {string} message - Nội dung thông báo
 * @param {string} type - Loại: success, error, info
 */
function showToast(message, type = 'info') {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  
  // Auto remove sau 3s
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

// Expose showToast để các component con có thể dùng
defineExpose({ showToast })

// =====================================================
// LIFECYCLE & EVENTS
// =====================================================

/**
 * Xử lý resize window - đóng menu trên mobile
 */
function handleResize() {
  windowWidth.value = window.innerWidth
  if (window.innerWidth > 768) {
    isMenuOpen.value = false
  }
}

/**
 * Xử lý route change - đóng menu mobile
 */
function handleRouteChange() {
  isMenuOpen.value = false
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
  router.afterEach(handleRouteChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
/* =====================================================
   APP CONTAINER
   ===================================================== */
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* =====================================================
   BACKGROUND EFFECTS
   ===================================================== */

/**
 * Animated gradient background
 * WHY: Tạo hiệu ứng atmospheric, tạo chiều sâu cho UI
 */
.bg-gradient {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -2;
  background: 
    radial-gradient(ellipse 80% 50% at 20% 40%, rgba(61, 107, 138, 0.15) 0%, transparent 50%),
    radial-gradient(ellipse 60% 40% at 80% 60%, rgba(26, 58, 92, 0.2) 0%, transparent 50%),
    linear-gradient(180deg, var(--color-bg-primary) 0%, #0a1420 100%);
  pointer-events: none;
}

/**
 * Grid pattern overlay
 * WHY: Tạo cảm giác techy, professional cho dashboard
 */
.bg-grid {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  background-image: 
    linear-gradient(rgba(61, 107, 138, 0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(61, 107, 138, 0.03) 1px, transparent 1px);
  background-size: 50px 50px;
  pointer-events: none;
}

/* =====================================================
   NAVBAR
   ===================================================== */
.navbar {
  background: linear-gradient(180deg, rgba(26, 58, 92, 0.95) 0%, rgba(26, 58, 92, 0.8) 100%);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(138, 180, 196, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

/**
 * Glow effect behind navbar
 * WHY: Tạo hiệu ứng "neon" nhẹ, tăng tính futuristic
 */
.navbar-glow {
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 60%;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--color-primary-light), transparent);
  opacity: 0.5;
}

.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 72px;
  padding: 0 var(--spacing-lg);
}

/* =====================================================
   BRAND / LOGO
   ===================================================== */
.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  text-decoration: none;
  transition: transform var(--transition-fast);
}

.navbar-brand:hover {
  transform: scale(1.02);
}

.brand-icon-wrapper {
  position: relative;
  width: 40px;
  height: 40px;
}

.brand-icon {
  width: 40px;
  height: 40px;
  color: var(--color-primary-light);
  position: relative;
  z-index: 1;
}

.brand-icon-glow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60px;
  height: 60px;
  background: radial-gradient(circle, rgba(138, 180, 196, 0.3) 0%, transparent 70%);
  border-radius: 50%;
  filter: blur(10px);
  animation: pulse-glow 3s ease-in-out infinite;
}

@keyframes pulse-glow {
  0%, 100% { opacity: 0.3; transform: translate(-50%, -50%) scale(1); }
  50% { opacity: 0.6; transform: translate(-50%, -50%) scale(1.1); }
}

.brand-text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand-text-main {
  font-size: var(--font-size-lg);
  font-weight: 700;
  color: var(--color-text-primary);
  letter-spacing: 0.5px;
}

.brand-text-accent {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-primary-light);
  letter-spacing: 2px;
  text-transform: uppercase;
}

/* =====================================================
   NAVIGATION LINKS
   ===================================================== */
.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.nav-divider {
  width: 1px;
  height: 24px;
  background: rgba(138, 180, 196, 0.2);
  margin: 0 var(--spacing-sm);
}

.nav-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  position: relative;
}

.nav-link::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%) scaleX(0);
  width: 80%;
  height: 2px;
  background: var(--color-primary-light);
  border-radius: 2px;
  transition: transform var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: rgba(138, 180, 196, 0.1);
}

.nav-link:hover::after {
  transform: translateX(-50%) scaleX(1);
}

.nav-link.router-link-active {
  color: var(--color-text-primary);
}

.nav-link.router-link-active::after {
  transform: translateX(-50%) scaleX(1);
}

.nav-icon {
  width: 18px;
  height: 18px;
}

.nav-link-watchlist {
  color: var(--color-warning);
}

.nav-link-watchlist .nav-icon {
  fill: var(--color-warning);
}

/* =====================================================
   USER INFO
   ===================================================== */
.nav-user-wrapper {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md);
  background: rgba(138, 180, 196, 0.1);
  border-radius: var(--radius-full);
}

.nav-user-avatar {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: 50%;
  font-size: var(--font-size-sm);
  font-weight: 700;
  color: var(--color-bg-primary);
}

.nav-user {
  color: var(--color-primary-light);
  font-weight: 500;
  font-size: var(--font-size-sm);
}

/* =====================================================
   LOGIN BUTTON
   ===================================================== */
.btn-login {
  padding: var(--spacing-sm) var(--spacing-lg) !important;
  background: linear-gradient(135deg, var(--color-primary) 0%, #4a7a9d 100%);
  border-radius: var(--radius-full) !important;
  color: var(--color-text-primary) !important;
  font-weight: 600;
  box-shadow: 0 4px 15px rgba(61, 107, 138, 0.3);
}

.btn-login:hover {
  background: linear-gradient(135deg, var(--color-primary-light) 0%, var(--color-primary) 100%);
  box-shadow: 0 6px 20px rgba(61, 107, 138, 0.4);
  transform: translateY(-2px);
}

.btn-login::after {
  display: none;
}

/* =====================================================
   LOGOUT BUTTON
   ===================================================== */
.btn-logout {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  background: transparent;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.btn-logout:hover {
  color: var(--color-danger);
  background: rgba(239, 68, 68, 0.1);
}

.btn-icon {
  width: 18px;
  height: 18px;
}

/* =====================================================
   MOBILE TOGGLER (HAMBURGER)
   ===================================================== */
.navbar-toggler {
  display: none;
  padding: var(--spacing-sm);
  background: none;
  border: none;
  z-index: 110;
}

.toggler-icon {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 24px;
  padding: var(--spacing-xs);
}

.toggler-icon span {
  display: block;
  height: 2px;
  background: var(--color-text-primary);
  border-radius: 2px;
  transition: all var(--transition-fast);
}

.toggler-icon.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.toggler-icon.open span:nth-child(2) {
  opacity: 0;
  transform: scaleX(0);
}

.toggler-icon.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* =====================================================
   MOBILE MENU
   ===================================================== */
.navbar-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(26, 58, 92, 0.98);
  backdrop-filter: blur(20px);
  border-bottom: 1px solid rgba(138, 180, 196, 0.1);
}

.mobile-menu-inner {
  display: flex;
  flex-direction: column;
  padding: var(--spacing-md);
}

.mobile-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.mobile-link:hover {
  color: var(--color-text-primary);
  background: rgba(138, 180, 196, 0.1);
}

.mobile-icon {
  width: 20px;
  height: 20px;
}

.mobile-divider {
  height: 1px;
  background: rgba(138, 180, 196, 0.1);
  margin: var(--spacing-md) 0;
}

.mobile-link-watchlist .mobile-icon {
  fill: var(--color-warning);
}

.mobile-user-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
}

.mobile-user-avatar {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
  border-radius: 50%;
  font-size: var(--font-size-base);
  font-weight: 700;
  color: var(--color-bg-primary);
}

.mobile-user {
  color: var(--color-primary-light);
  font-weight: 500;
}

/* =====================================================
   MAIN CONTENT
   ===================================================== */
.main-content {
  flex: 1;
  padding: var(--spacing-xl) 0;
}

/* =====================================================
   TOAST NOTIFICATIONS
   ===================================================== */
.toast-container {
  position: fixed;
  bottom: var(--spacing-xl);
  right: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  z-index: 1000;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) var(--spacing-lg);
  background: rgba(26, 58, 92, 0.95);
  backdrop-filter: blur(20px);
  border-radius: var(--radius-lg);
  border: 1px solid rgba(138, 180, 196, 0.2);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  pointer-events: auto;
  min-width: 280px;
}

.toast.success {
  border-color: rgba(16, 185, 129, 0.3);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(26, 58, 92, 0.95) 100%);
}

.toast.success .toast-icon {
  color: var(--color-success);
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(26, 58, 92, 0.95) 100%);
}

.toast.error .toast-icon {
  color: var(--color-danger);
}

.toast.info .toast-icon {
  color: var(--color-primary-light);
}

.toast-icon {
  width: 20px;
  height: 20px;
  flex-shrink: 0;
}

.toast-message {
  color: var(--color-text-primary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

/* Toast transitions */
.toast-enter-active {
  animation: toast-in 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.toast-leave-active {
  animation: toast-out 0.3s ease forwards;
}

@keyframes toast-in {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes toast-out {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

/* =====================================================
   PAGE TRANSITIONS
   ===================================================== */
.page-enter-active {
  animation: page-in 0.3s ease;
}

.page-leave-active {
  animation: page-out 0.2s ease;
}

@keyframes page-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes page-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* Mobile menu transition */
.slide-down-enter-active {
  animation: slide-down-in 0.3s ease;
}

.slide-down-leave-active {
  animation: slide-down-out 0.2s ease;
}

@keyframes slide-down-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slide-down-out {
  from {
    opacity: 1;
    transform: translateY(0);
  }
  to {
    opacity: 0;
    transform: translateY(-10px);
  }
}

/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 768px) {
  .navbar-container {
    height: 64px;
  }
  
  .navbar-nav {
    display: none;
  }
  
  .navbar-toggler {
    display: block;
  }
  
  .toast-container {
    left: var(--spacing-md);
    right: var(--spacing-md);
    bottom: var(--spacing-md);
  }
  
  .toast {
    min-width: auto;
  }
}
</style>
