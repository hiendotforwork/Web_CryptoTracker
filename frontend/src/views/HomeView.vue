<template>
  <div class="home-view">
    <div class="container">
      <!-- Header -->
      <header class="page-header">
        <h1 class="page-title">Crypto Tracker</h1>
        <p class="page-subtitle">Theo dõi giá cryptocurrency hàng đầu</p>
      </header>
      
      <!-- Loading State -->
      <div class="loading" v-if="isLoading">
        <div class="skeleton-table">
          <div class="skeleton-row" v-for="i in 5" :key="i"></div>
        </div>
      </div>
      
      <!-- Error State -->
      <div class="error-state" v-else-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="handleRetry">Thử lại</button>
      </div>
      
      <!-- Content -->
      <div class="content" v-else>
        <!-- Search Bar -->
        <div class="search-bar">
          <div class="search-wrapper">
            <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              type="text" 
              v-model="searchQuery" 
              placeholder="Tìm kiếm coin..."
              class="search-input"
              @input="handleSearch"
              aria-label="Tìm kiếm coin"
            />
            <button 
              v-if="searchQuery" 
              class="search-clear" 
              @click="clearSearch"
              aria-label="Xóa tìm kiếm"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Coin Table -->
        <CoinTable 
          :coins="filteredCoins"
          :mode="'default'"
          :page="currentPage"
          :per-page="25"
          :added-coins="watchlistCoinIds"
          @add-to-watchlist="addToWatchlist"
        />
        
        <!-- Pagination (hidden when searching) -->
        <div class="pagination" v-if="!searchQuery">
          <button 
            class="btn-page" 
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
            aria-label="Trang trước"
          >
            Trước
          </button>
          <span class="page-info">Trang {{ currentPage }} / {{ totalPages }}</span>
          <button 
            class="btn-page" 
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
            aria-label="Trang sau"
          >
            Sau
          </button>
        </div>
      </div>
    </div>
    
    <!-- Toast Container -->
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
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCoinStore } from '@/stores/coinStore'
import { useWatchlistStore } from '@/stores/watchlistStore'
import { useAuthStore } from '@/stores/auth'
import CoinTable from '@/components/CoinTable.vue'

// =====================================================
// STORES
// =====================================================
const coinStore = useCoinStore()
const watchlistStore = useWatchlistStore()
const authStore = useAuthStore()

// Store refs (reactive)
const { 
  coins, 
  totalPages, 
  isLoading, 
  error, 
  currentPage 
} = storeToRefs(coinStore)

const { isAuthenticated } = storeToRefs(authStore)
const { coins: watchlistCoins } = storeToRefs(watchlistStore)

// =====================================================
// STATE
// =====================================================
const searchQuery = ref('')
const searchTimer = ref(null)

// Toast state
const toast = ref({
  show: false,
  message: '',
  type: 'info'
})

// =====================================================
// COMPUTED
// =====================================================

/**
 * Filter coins theo search query
 * Search không dùng pagination - lọc local từ coins đã load
 */
const filteredCoins = computed(() => {
  if (!searchQuery.value) {
    return coins.value
  }
  const query = searchQuery.value.toLowerCase().trim()
  return coins.value.filter(coin => 
    coin.name?.toLowerCase().includes(query) ||
    coin.symbol?.toLowerCase().includes(query)
  )
})

/**
 * Lấy danh sách ID coins đã thêm vào watchlist
 */
const watchlistCoinIds = computed(() => {
  return watchlistCoins.value.map(c => c.coin_id)
})

// =====================================================
// METHODS
// =====================================================

/**
 * Xử lý search với debounce 300ms
 */
function handleSearch() {
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }
  searchTimer.value = setTimeout(() => {
    // Search không reset page - giữ nguyên trang
    // Filter diễn ra local nên không cần gọi API
  }, 300)
}

/**
 * Xóa search và quay lại danh sách đầy đủ
 */
function clearSearch() {
  searchQuery.value = ''
}

/**
 * Thay đổi trang
 */
function changePage(page) {
  coinStore.fetchCoins(page)
}

/**
 * Retry khi có lỗi
 */
function handleRetry() {
  coinStore.fetchCoins(currentPage.value)
}

/**
 * Thêm coin vào watchlist
 */
async function addToWatchlist(coinId) {
  if (!isAuthenticated.value) {
    showToast('Vui lòng đăng nhập để thêm vào watchlist', 'error')
    return
  }
  
  try {
    await watchlistStore.addCoin(coinId)
    const coin = coins.value.find(c => c.id === coinId)
    showToast(`Đã thêm ${coin?.name || coinId} vào watchlist`, 'success')
  } catch (err) {
    showToast('Không thể thêm vào watchlist', 'error')
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
// WATCH
// =====================================================

/**
 * Watch search query - xóa timer khi unmount
 */

// =====================================================
// LIFECYCLE
// =====================================================
onMounted(() => {
  coinStore.fetchCoins(1)
})

onUnmounted(() => {
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }
})
</script>

<style scoped>
.home-view {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
}

/* =====================================================
   HEADER
   ===================================================== */
.page-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

/* =====================================================
   SEARCH BAR
   ===================================================== */
.search-bar {
  margin-bottom: var(--spacing-xl);
}

.search-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 450px;
  margin: 0 auto;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  width: 20px;
  height: 20px;
  color: var(--color-text-secondary);
  pointer-events: none;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md) var(--spacing-xl);
  padding-left: 48px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary-light);
  box-shadow: 0 0 0 3px rgba(160, 180, 200, 0.2);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-clear {
  position: absolute;
  right: var(--spacing-md);
  padding: var(--spacing-xs);
  color: var(--color-text-secondary);
  background: transparent;
  border: none;
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  cursor: pointer;
}

.search-clear svg {
  width: 18px;
  height: 18px;
}

.search-clear:hover {
  color: var(--color-text-primary);
  background: rgba(160, 180, 200, 0.1);
}

/* =====================================================
   PAGINATION
   ===================================================== */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-xl);
}

.btn-page {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 500;
  transition: all var(--transition-fast);
  cursor: pointer;
}

.btn-page:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
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
   ERROR STATE
   ===================================================== */
.error-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-base);
}

.btn-retry {
  padding: var(--spacing-sm) var(--spacing-xl);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-retry:hover {
  background: var(--color-primary-light);
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
  .toast-wrapper {
    left: var(--spacing-md);
    right: var(--spacing-md);
    bottom: var(--spacing-md);
  }
}
</style>