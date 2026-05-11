<template>
  <div class="watchlist-view">
    <div class="container">
      <!-- Header -->
      <header class="page-header">
        <div class="header-content">
          <h1 class="page-title">
            <svg class="title-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
            Watchlist
          </h1>
          <p class="page-subtitle">Danh sách các coin bạn đang theo dõi</p>
        </div>
        <button 
          class="btn-refresh" 
          @click="refreshWatchlist"
          :disabled="isLoading"
          aria-label="Làm mới"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 4 23 10 17 10"/>
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
          </svg>
        </button>
      </header>
      
      <!-- Loading -->
      <div class="loading" v-if="isLoading">
        <div class="skeleton-table">
          <div class="skeleton-row" v-for="i in 5" :key="i"></div>
        </div>
      </div>
      
      <!-- Error State -->
      <div class="error-state" v-else-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="refreshWatchlist">Thử lại</button>
      </div>
      
      <!-- Empty State -->
      <div class="empty-state" v-else-if="coins.length === 0">
        <div class="empty-illustration">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
          </svg>
        </div>
        <p class="empty-message">Bạn chưa theo dõi coin nào</p>
        <p class="empty-hint">Khám phá và thêm các coin yêu thích vào danh sách</p>
        <button class="btn-explore" @click="$router.push('/')">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"/>
            <path d="m21 21-4.35-4.35"/>
          </svg>
          Khám phá ngay
        </button>
      </div>
      
      <!-- Watchlist Table -->
      <CoinTable 
        v-else
        :coins="coins"
        mode="watchlist"
        @remove-from-watchlist="handleRemove"
      />
    </div>
    
    <!-- Toast -->
    <Teleport to="body">
      <div class="toast-wrapper" v-if="toast.show">
        <div class="toast" :class="toast.type">
          <span class="toast-message">{{ toast.message }}</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useWatchlistStore } from '@/stores/watchlistStore'
import CoinTable from '@/components/CoinTable.vue'

// =====================================================
// STORE
// =====================================================
const watchlistStore = useWatchlistStore()
const { coins, isLoading, error } = storeToRefs(watchlistStore)

// =====================================================
// STATE
// =====================================================
const toast = ref({
  show: false,
  message: '',
  type: 'info'
})

// =====================================================
// METHODS
// =====================================================

/**
 * Refresh watchlist
 */
async function refreshWatchlist() {
  await watchlistStore.fetchWatchlist()
}

/**
 * Xóa coin khỏi watchlist
 */
async function handleRemove(coinId) {
  try {
    await watchlistStore.removeCoin(coinId)
    showToast('Đã xóa khỏi watchlist', 'success')
  } catch (err) {
    showToast('Không thể xóa khỏi watchlist', 'error')
  }
}

/**
 * Hiện toast notification
 */
function showToast(message, type = 'info') {
  toast.value = { show: true, message, type }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// =====================================================
// LIFECYCLE
// =====================================================
onMounted(() => {
  watchlistStore.fetchWatchlist()
})
</script>

<style scoped>
.watchlist-view {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
}

/* =====================================================
   HEADER
   ===================================================== */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-2xl);
}

.header-content {
  text-align: left;
}

.page-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.title-icon {
  width: 32px;
  height: 32px;
  color: var(--color-warning);
  fill: var(--color-warning);
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

.btn-refresh {
  padding: var(--spacing-sm);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.btn-refresh:hover:not(:disabled) {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-refresh:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-refresh svg {
  width: 20px;
  height: 20px;
}

/* =====================================================
   EMPTY STATE
   ===================================================== */
.empty-state {
  text-align: center;
  padding: var(--spacing-3xl);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
}

.empty-illustration {
  width: 80px;
  height: 80px;
  margin: 0 auto var(--spacing-xl);
  color: var(--color-text-secondary);
  opacity: 0.5;
}

.empty-illustration svg {
  width: 100%;
  height: 100%;
}

.empty-message {
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.empty-hint {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
  margin-bottom: var(--spacing-xl);
}

.btn-explore {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.btn-explore:hover {
  background: var(--color-primary-light);
  transform: translateY(-2px);
}

.btn-explore svg {
  width: 18px;
  height: 18px;
}

/* =====================================================
   ERROR STATE
   ===================================================== */
.error-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-md);
}

.btn-retry {
  padding: var(--spacing-sm) var(--spacing-xl);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
}

.btn-retry:hover {
  background: var(--color-primary-light);
}

/* =====================================================
   SKELETON LOADING
   ===================================================== */
.skeleton-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.skeleton-row {
  height: 60px;
  margin-bottom: var(--spacing-sm);
  border-radius: var(--radius-md);
  background: linear-gradient(90deg, 
    var(--color-bg-primary) 25%, 
    var(--color-bg-secondary) 50%, 
    var(--color-bg-primary) 75%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite;
}

.skeleton-row:last-child {
  margin-bottom: 0;
}

@keyframes skeleton-shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* =====================================================
   TOAST
   ===================================================== */
.toast-wrapper {
  position: fixed;
  bottom: var(--spacing-xl);
  right: var(--spacing-xl);
  z-index: 1000;
}

.toast {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
  animation: toast-in 0.3s ease;
}

.toast.success {
  border-color: rgba(16, 185, 129, 0.5);
}

.toast.error {
  border-color: rgba(204, 41, 54, 0.5);
}

.toast-message {
  color: var(--color-text-primary);
  font-weight: 500;
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

/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--spacing-md);
  }
  
  .toast-wrapper {
    left: var(--spacing-md);
    right: var(--spacing-md);
    bottom: var(--spacing-md);
  }
}
</style>