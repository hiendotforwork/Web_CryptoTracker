<template>
  <div class="watchlist-view">
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">Watchlist</h1>
        <p class="page-subtitle">Danh sách các coin bạn đang theo dõi</p>
      </header>
      
      <!-- Loading -->
      <div class="loading" v-if="isLoading">
        <div class="skeleton-table">
          <div class="skeleton-row" v-for="i in 5" :key="i"></div>
        </div>
      </div>
      
      <!-- Empty State -->
      <div class="empty-state" v-else-if="coins.length === 0">
        <p class="empty-message">Bạn chưa theo dõi coin nào</p>
        <button class="btn-explore" @click="$router.push('/')">Khám phá ngay</button>
      </div>
      
      <!-- Watchlist Table -->
      <div class="coin-table" v-else>
        <div class="table-header">
          <span class="col-rank">#</span>
          <span class="col-name">Tên</span>
          <span class="col-price">Giá</span>
          <span class="col-change">24h %</span>
          <span class="col-action"></span>
        </div>
        
        <div 
          class="table-row" 
          v-for="(item, index) in coins" 
          :key="item.coin_id"
          @click="goToCoinDetail(item.coin_id)"
        >
          <span class="col-rank">{{ index + 1 }}</span>
          <span class="col-name">
            <img :src="item.coin?.image" :alt="item.coin?.name" class="coin-icon" />
            <span class="coin-name">{{ item.coin?.name }}</span>
            <span class="coin-symbol">{{ item.coin?.symbol?.toUpperCase() }}</span>
          </span>
          <span class="col-price">${{ formatPrice(item.coin?.current_price) }}</span>
          <span 
            class="col-change"
            :class="{ 'positive': item.coin?.price_change_percentage_24h > 0, 'negative': item.coin?.price_change_percentage_24h < 0 }"
          >
            {{ item.coin?.price_change_percentage_24h > 0 ? '▲' : '▼' }}
            {{ Math.abs(item.coin?.price_change_percentage_24h).toFixed(2) }}%
          </span>
          <span class="col-action">
            <button 
              class="btn-delete"
              @click.stop="removeCoin(item.coin_id)"
            >
              🗑️
            </button>
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '@/services/api'

const router = useRouter()

// State
const coins = ref([])
const isLoading = ref(true)

// Methods
function formatPrice(price) {
  if (!price) return '0.00'
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function goToCoinDetail(coinId) {
  router.push(`/coin/${coinId}`)
}

async function fetchWatchlist() {
  isLoading.value = true
  
  try {
    const response = await api.get('/watchlist')
    coins.value = response.data.watchlist || []
  } catch (err) {
    console.error('Error fetching watchlist:', err)
  } finally {
    isLoading.value = false
  }
}

async function removeCoin(coinId) {
  try {
    await api.delete(`/watchlist/${coinId}`)
    // Optimistic update - remove from local state immediately
    coins.value = coins.value.filter(item => item.coin_id !== coinId)
  } catch (err) {
    console.error('Error removing coin:', err)
  }
}

// Lifecycle
onMounted(() => {
  fetchWatchlist()
})
</script>

<style scoped>
.watchlist-view {
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

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.empty-message {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-lg);
}

.btn-explore {
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.btn-explore:hover {
  background: var(--color-primary-light);
}

/* Table */
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

.btn-delete {
  padding: var(--spacing-xs);
  font-size: var(--font-size-lg);
  transition: transform var(--transition-fast);
}

.btn-delete:hover {
  transform: scale(1.2);
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
}
</style>