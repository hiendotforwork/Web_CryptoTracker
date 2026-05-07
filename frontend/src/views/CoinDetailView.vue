<template>
  <div class="coin-detail-view">
    <div class="container">
      <!-- Loading State -->
      <div class="loading" v-if="isLoading">
        <div class="skeleton-detail">
          <div class="skeleton-header"></div>
          <div class="skeleton-chart"></div>
        </div>
      </div>
      
      <!-- Error State -->
      <div class="error-state" v-else-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="btn-back" @click="$router.push('/')">Về trang chủ</button>
      </div>
      
      <!-- Coin Detail -->
      <div class="content" v-else-if="coin">
        <!-- Header -->
        <header class="coin-header">
          <div class="coin-info">
            <img :src="coin.image" :alt="coin.name" class="coin-icon" />
            <div class="coin-title">
              <h1 class="coin-name">{{ coin.name }}</h1>
              <span class="coin-symbol">{{ coin.symbol.toUpperCase() }}</span>
            </div>
            <span class="coin-rank">#{{ coin.market_cap_rank }}</span>
          </div>
          
          <div class="coin-price">
            <span class="price-value">${{ formatPrice(coin.current_price) }}</span>
            <span 
              class="price-change"
              :class="{ 'positive': coin.price_change_percentage_24h > 0, 'negative': coin.price_change_percentage_24h < 0 }"
            >
              {{ coin.price_change_percentage_24h > 0 ? '▲' : '▼' }}
              {{ Math.abs(coin.price_change_percentage_24h).toFixed(2) }}%
            </span>
          </div>
        </header>
        
        <!-- Chart -->
        <div class="chart-container">
          <div class="chart-tabs">
            <button 
              v-for="period in periods" 
              :key="period.value"
              class="btn-tab"
              :class="{ active: selectedPeriod === period.value }"
              @click="selectPeriod(period.value)"
            >
              {{ period.label }}
            </button>
          </div>
          
          <div ref="chartContainer" class="chart-wrapper"></div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <span class="stat-label">Market Cap</span>
            <span class="stat-value">${{ formatLargeNumber(coin.market_cap) }}</span>
          </div>
          
          <div class="stat-card">
            <span class="stat-label">Volume 24h</span>
            <span class="stat-value">${{ formatLargeNumber(coin.total_volume) }}</span>
          </div>
          
          <div class="stat-card">
            <span class="stat-label">All Time High</span>
            <span class="stat-value">${{ formatPrice(coin.ath) }}</span>
          </div>
          
          <div class="stat-card">
            <span class="stat-label">All Time Low</span>
            <span class="stat-value">${{ formatPrice(coin.atl) }}</span>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="actions">
          <button 
            v-if="isAuthenticated && !hasCoin(coin.id)"
            class="btn-action btn-add"
            @click="addToWatchlist(coin.id)"
          >
            Thêm vào Watchlist
          </button>
          <button 
            v-else-if="isAuthenticated && hasCoin(coin.id)"
            class="btn-action btn-remove"
            @click="removeFromWatchlist(coin.id)"
          >
            Xóa khỏi Watchlist
          </button>
          <button 
            class="btn-action btn-compare"
            @click="goToCompare"
          >
            So sánh
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createChart } from 'lightweight-charts'
import { useAuthStore } from '@/stores/auth'
import { api } from '@/services/api'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// State
const coin = ref(null)
const prices = ref([])
const isLoading = ref(true)
const error = ref(null)
const chart = ref(null)
const chartSeries = ref(null)
const selectedPeriod = ref(7)

// Period options
const periods = [
  { label: '24H', value: 1 },
  { label: '7D', value: 7 },
  { label: '30D', value: 30 },
  { label: '90D', value: 90 },
  { label: '1Y', value: 365 }
]

// Computed
const isAuthenticated = computed(() => authStore.isAuthenticated)

// Methods
function formatPrice(price) {
  if (!price) return '0.00'
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatLargeNumber(num) {
  if (!num) return '0'
  if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T'
  if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B'
  if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M'
  if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K'
  return num.toString()
}

function hasCoin(coinId) {
  return false // Will be implemented with watchlist store
}

function selectPeriod(period) {
  selectedPeriod.value = period
  fetchCoinHistory(period)
}

async function fetchCoinDetail() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await api.get(`/coins/${route.params.id}`)
    coin.value = response.data.coin
  } catch (err) {
    error.value = 'Không tìm thấy coin'
  } finally {
    isLoading.value = false
  }
}

async function fetchCoinHistory(days = 7) {
  try {
    const response = await api.get(`/coins/${route.params.id}/history?days=${days}`)
    prices.value = response.data.prices || []
    updateChart()
  } catch (err) {
    console.error('Error fetching history:', err)
  }
}

function initChart() {
  if (!chartContainer.value) return
  
  chart.value = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: 400,
    layout: {
      background: { type: 'solid', color: '#1a3a5c' },
      textColor: '#8ab4c4'
    },
    grid: {
      vertLines: { color: '#0d1a26' },
      horzLines: { color: '#0d1a26' }
    },
    crosshair: {
      mode: 1
    },
    rightPriceScale: {
      borderColor: '#3d6b8a'
    },
    timeScale: {
      borderColor: '#3d6b8a',
      timeVisible: true,
      secondsVisible: false
    }
  })
  
  chartSeries.value = chart.value.addAreaSeries({
    lineColor: '#3d6b8a',
    topColor: 'rgba(61, 107, 138, 0.4)',
    bottomColor: 'rgba(61, 107, 138, 0.1)',
    lineWidth: 2
  })
}

function updateChart() {
  if (!chartSeries.value || !prices.value.length) return
  
  const data = prices.value.map(([ts, value]) => ({
    time: Math.floor(ts / 1000),
    value
  }))
  
  chartSeries.value.setData(data)
  chart.value?.timeScale().fitContent()
}

function addToWatchlist(coinId) {
  // Will be implemented later
}

function removeFromWatchlist(coinId) {
  // Will be implemented later
}

function goToCompare() {
  router.push(`/compare?coin1=${coin.value.id}`)
}

// Lifecycle
onMounted(async () => {
  await fetchCoinDetail()
  if (coin.value) {
    initChart()
    fetchCoinHistory(selectedPeriod.value)
  }
})

onUnmounted(() => {
  if (chart.value) {
    chart.value.remove()
    chart.value = null
  }
})

// Watch for resize
watch(() => route.params.id, () => {
  fetchCoinDetail()
})
</script>

<style scoped>
.coin-detail-view {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
}

/* Skeleton */
.skeleton-detail {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
}

.skeleton-header {
  height: 100px;
  border-radius: var(--radius-lg);
}

.skeleton-chart {
  height: 400px;
  border-radius: var(--radius-lg);
}

/* Error */
.error-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-md);
  font-size: var(--font-size-lg);
}

.btn-back {
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
}

/* Header */
.coin-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: var(--spacing-xl);
  flex-wrap: wrap;
  gap: var(--spacing-lg);
}

.coin-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.coin-icon {
  width: 56px;
  height: 56px;
  border-radius: 50%;
}

.coin-title {
  display: flex;
  flex-direction: column;
}

.coin-name {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.coin-symbol {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.coin-rank {
  padding: var(--spacing-xs) var(--spacing-sm);
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
}

.coin-price {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.price-value {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
}

.price-change {
  font-size: var(--font-size-base);
  font-weight: 500;
}

.price-change.positive {
  color: var(--color-success);
}

.price-change.negative {
  color: var(--color-danger);
}

/* Chart */
.chart-container {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
}

.chart-tabs {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-lg);
}

.btn-tab {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-tab:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-tab.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

.chart-wrapper {
  height: 400px;
}

/* Stats */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--spacing-lg);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.stat-label {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.stat-value {
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: 600;
}

/* Actions */
.actions {
  display: flex;
  gap: var(--spacing-md);
  flex-wrap: wrap;
}

.btn-action {
  padding: var(--spacing-md) var(--spacing-xl);
  border-radius: var(--radius-md);
  font-weight: 600;
  transition: all var(--transition-fast);
}

.btn-add {
  background: var(--color-success);
  color: var(--color-text-primary);
}

.btn-add:hover {
  opacity: 0.9;
}

.btn-remove {
  background: var(--color-danger);
  color: var(--color-text-primary);
}

.btn-remove:hover {
  opacity: 0.9;
}

.btn-compare {
  background: var(--color-primary);
  color: var(--color-text-primary);
}

.btn-compare:hover {
  background: var(--color-primary-light);
}

/* Responsive */
@media (max-width: 768px) {
  .coin-header {
    flex-direction: column;
  }
  
  .coin-price {
    align-items: flex-start;
  }
  
  .price-value {
    font-size: var(--font-size-2xl);
  }
  
  .chart-wrapper {
    height: 300px;
  }
}
</style>