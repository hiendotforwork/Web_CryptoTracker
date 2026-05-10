<template>
  <div class="home-view">
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">Crypto Tracker</h1>
        <p class="page-subtitle">Theo dõi giá cryptocurrency hàng đầu</p>
      </header>
      
      <div class="loading" v-if="isLoading">
        <div class="skeleton-table">
          <div class="skeleton-row" v-for="i in 5" :key="i"></div>
        </div>
      </div>
      
      <div class="error-state" v-else-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="fetchCoins()">Thử lại</button>
      </div>
      
      <div class="content" v-else>
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
            />
            <button v-if="searchQuery" class="search-clear" @click="clearSearch">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
        </div>
        
        <div class="coin-table">
          <div class="table-header">
            <span class="col-rank">#</span>
            <span class="col-name">Tên</span>
            <span class="col-price">Giá</span>
            <span class="col-change">24h %</span>
            <span class="col-action"></span>
          </div>
          
          <div 
            class="table-row" 
            v-for="(coin, index) in filteredCoins" 
            :key="coin.id"
            @click="goToCoinDetail(coin.id)"
          >
            <span class="col-rank">{{ index + 1 }}</span>
            <span class="col-name">
              <img :src="coin.image" :alt="coin.name" class="coin-icon" />
              <span class="coin-name">{{ coin.name }}</span>
              <span class="coin-symbol">{{ coin.symbol.toUpperCase() }}</span>
            </span>
            <span class="col-price">${{ formatPrice(coin.current_price) }}</span>
            <span 
              class="col-change"
              :class="{ 'positive': coin.price_change_percentage_24h > 0, 'negative': coin.price_change_percentage_24h < 0 }"
            >
              {{ coin.price_change_percentage_24h > 0 ? '▲' : '▼' }}
              {{ Math.abs(coin.price_change_percentage_24h).toFixed(2) }}%
            </span>
            <span class="col-action">
              <button 
                v-if="isAuthenticated && !hasCoin(coin.id)"
                class="btn-add"
                @click.stop="addToWatchlist(coin.id)"
              >
                +
              </button>
              <span v-else-if="hasCoin(coin.id)" class="added-badge">✓</span>
            </span>
          </div>
        </div>
        
        <div class="pagination">
          <button 
            class="btn-page" 
            :disabled="currentPage <= 1"
            @click="changePage(currentPage - 1)"
          >
            Trước
          </button>
          <span class="page-info">Trang {{ currentPage }} / {{ totalPages }}</span>
          <button 
            class="btn-page" 
            :disabled="currentPage >= totalPages"
            @click="changePage(currentPage + 1)"
          >
            Sau
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

// State
const coins = ref([])
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const searchTimer = ref(null)

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

/**
 * Chỉ hiện coins sau khi search (không phân trang khi search)
 * Search không dùng pagination - lọc local
 */
const filteredCoins = computed(() => {
  if (!searchQuery.value) {
    return coins.value
  }
  const query = searchQuery.value.toLowerCase()
  return coins.value.filter(coin => 
    coin.name.toLowerCase().includes(query) ||
    coin.symbol.toLowerCase().includes(query)
  )
})

// Methods
function formatPrice(price) {
  if (!price) return '0.00'
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function goToCoinDetail(coinId) {
  router.push(`/coin/${coinId}`)
}

function handleSearch() {
  // Debounce 300ms - xóa timer cũ và tạo timer mới
  if (searchTimer.value) {
    clearTimeout(searchTimer.value)
  }
  searchTimer.value = setTimeout(() => {
    currentPage.value = 1
  }, 300)
}

function clearSearch() {
  searchQuery.value = ''
  currentPage.value = 1
  fetchCoins(currentPage.value)
}

function changePage(page) {
  currentPage.value = page
  fetchCoins(page)
}

async function fetchCoins(page = 1) {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await api.get(`/coins?page=${page}&per_page=25`)
    coins.value = response.data.coins || []
    totalPages.value = response.data.total_pages || 1
    currentPage.value = page
  } catch (err) {
    error.value = 'Không thể tải dữ liệu. Vui lòng thử lại.'
    console.error('Error fetching coins:', err)
  } finally {
    isLoading.value = false
  }
}

function hasCoin(coinId) {
  return false // Will be implemented with watchlist store
}

function addToWatchlist(coinId) {
  // Will be implemented later
}

// Lifecycle
onMounted(() => {
  fetchCoins()
})

// Cleanup timer when component unmounts
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

.search-bar {
  margin-bottom: var(--spacing-xl);
}

.search-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
  width: 100%;
  max-width: 450px;
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
  box-shadow: 0 0 0 3px rgba(138, 180, 196, 0.2);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-clear {
  position: absolute;
  right: var(--spacing-md);
  padding: var(--spacing-xs);
  color: var(--color-text-secondary);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
}

.search-clear svg {
  width: 18px;
  height: 18px;
}

.search-clear:hover {
  color: var(--color-text-primary);
  background: rgba(138, 180, 196, 0.1);
}

.coin-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.table-header {
  display: grid;
  grid-template-columns: 60px 1fr 150px 120px 80px;
  padding: var(--spacing-md);
  background: var(--color-bg-primary);
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-row {
  display: grid;
  grid-template-columns: 60px 1fr 150px 120px 80px;
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--color-border);
  cursor: pointer;
  transition: background-color var(--transition-fast);
  align-items: center;
}

.table-row:hover {
  background: var(--color-bg-primary);
}

.table-row:last-child {
  border-bottom: none;
}

.col-rank {
  color: var(--color-text-secondary);
  font-weight: 500;
}

.col-name {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.coin-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
}

.coin-name {
  font-weight: 500;
  color: var(--color-text-primary);
}

.coin-symbol {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.col-price {
  font-weight: 600;
  color: var(--color-text-primary);
}

.col-change {
  font-weight: 500;
}

.col-change.positive {
  color: var(--color-success);
}

.col-change.negative {
  color: var(--color-danger);
}

.btn-add {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.btn-add:hover {
  background: var(--color-primary-light);
}

.added-badge {
  color: var(--color-success);
  font-weight: 600;
}

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
  transition: all var(--transition-fast);
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
}

/* Skeleton */
.skeleton-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-md);
}

.skeleton-row {
  height: 60px;
  margin-bottom: var(--spacing-sm);
  border-radius: var(--radius-md);
}

/* Error */
.error-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-md);
}

.btn-retry {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .table-header {
    display: none;
  }
  
  .table-row {
    grid-template-columns: 1fr;
    gap: var(--spacing-sm);
  }
  
  .col-rank {
    display: none;
  }
  
  .col-name {
    flex-wrap: wrap;
  }
  
  .col-price,
  .col-change {
    font-size: var(--font-size-sm);
  }
}
</style>