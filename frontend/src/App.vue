<template>
  <div class="app">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="container navbar-container">
        <!-- Logo -->
        <router-link to="/" class="navbar-brand">
          <span class="brand-icon">🪙</span>
          <span class="brand-text">Crypto Tracker</span>
        </router-link>
        
        <!-- Desktop Navigation -->
        <div class="navbar-nav">
          <router-link to="/" class="nav-link">Trang chủ</router-link>
          <router-link to="/news" class="nav-link">Tin tức</router-link>
          <router-link 
            v-if="isAuthenticated" 
            to="/watchlist" 
            class="nav-link"
          >
            Watchlist
          </router-link>
          <template v-if="isAuthenticated">
            <span class="nav-user">{{ user?.username }}</span>
            <button class="nav-link btn-logout" @click="handleLogout">
              Đăng xuất
            </button>
          </template>
          <router-link v-else to="/auth" class="nav-link btn-login">
            Đăng nhập
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
      <div class="navbar-menu" :class="{ open: isMenuOpen }">
        <router-link to="/" class="mobile-link" @click="isMenuOpen = false">
          Trang chủ
        </router-link>
        <router-link to="/news" class="mobile-link" @click="isMenuOpen = false">
          Tin tức
        </router-link>
        <router-link 
          v-if="isAuthenticated" 
          to="/watchlist" 
          class="mobile-link"
          @click="isMenuOpen = false"
        >
          Watchlist
        </router-link>
        <hr class="mobile-divider" />
        <template v-if="isAuthenticated">
          <span class="mobile-user">{{ user?.username }}</span>
          <button class="mobile-link btn-logout" @click="handleLogout">
            Đăng xuất
          </button>
        </template>
        <router-link v-else to="/auth" class="mobile-link" @click="isMenuOpen = false">
          Đăng nhập
        </router-link>
      </div>
    </nav>
    
    <!-- Main Content -->
    <main class="main-content">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <!-- Toast Notifications -->
    <div class="toast-container">
      <div 
        v-for="toast in toasts" 
        :key="toast.id"
        class="toast"
        :class="toast.type"
      >
        {{ toast.message }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// State
const isMenuOpen = ref(false)
const toasts = ref([])

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)
const user = computed(() => authStore.user)

// Methods
function handleLogout() {
  authStore.logout()
  isMenuOpen.value = false
  router.push('/')
}

function showToast(message, type = 'info') {
  const id = Date.now()
  toasts.value.push({ id, message, type })
  setTimeout(() => {
    toasts.value = toasts.value.filter(t => t.id !== id)
  }, 3000)
}

// Close menu when route changes
function handleRouteChange() {
  isMenuOpen.value = false
}

// Handle window resize
function handleResize() {
  if (window.innerWidth > 768) {
    isMenuOpen.value = false
  }
}

// Lifecycle
onMounted(() => {
  window.addEventListener('resize', handleResize)
  router.afterEach(handleRouteChange)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Navbar */
.navbar {
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 64px;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 700;
  font-size: var(--font-size-lg);
  color: var(--color-text-primary);
  text-decoration: none;
}

.brand-icon {
  font-size: var(--font-size-xl);
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
}

.nav-link {
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color var(--transition-fast);
}

.nav-link:hover,
.nav-link.router-link-active {
  color: var(--color-text-primary);
}

.nav-user {
  color: var(--color-primary-light);
  font-weight: 500;
}

.btn-login {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary) !important;
}

.btn-login:hover {
  background: var(--color-primary-light);
}

.btn-logout {
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
}

/* Hamburger */
.navbar-toggler {
  display: none;
  padding: var(--spacing-sm);
  background: none;
  border: none;
}

.toggler-icon {
  display: flex;
  flex-direction: column;
  gap: 5px;
  width: 24px;
}

.toggler-icon span {
  display: block;
  height: 2px;
  background: var(--color-text-primary);
  transition: all var(--transition-fast);
}

.toggler-icon.open span:nth-child(1) {
  transform: translateY(7px) rotate(45deg);
}

.toggler-icon.open span:nth-child(2) {
  opacity: 0;
}

.toggler-icon.open span:nth-child(3) {
  transform: translateY(-7px) rotate(-45deg);
}

/* Mobile Menu */
.navbar-menu {
  display: none;
  flex-direction: column;
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
}

.navbar-menu.open {
  display: flex;
}

.mobile-link {
  padding: var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-weight: 500;
  text-align: left;
  transition: color var(--transition-fast);
}

.mobile-link:hover {
  color: var(--color-text-primary);
}

.mobile-divider {
  border: none;
  border-top: 1px solid var(--color-border);
  margin: var(--spacing-sm) 0;
}

.mobile-user {
  padding: var(--spacing-md);
  color: var(--color-primary-light);
  font-weight: 500;
}

/* Main Content */
.main-content {
  flex: 1;
}

/* Toast */
.toast-container {
  position: fixed;
  bottom: var(--spacing-lg);
  right: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  z-index: 1000;
}

.toast {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  box-shadow: var(--shadow-lg);
  animation: slideIn 0.3s ease;
}

.toast.success {
  border-left: 4px solid var(--color-success);
}

.toast.error {
  border-left: 4px solid var(--color-danger);
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Page Transition */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .navbar-nav {
    display: none;
  }
  
  .navbar-toggler {
    display: block;
  }
}
</style>