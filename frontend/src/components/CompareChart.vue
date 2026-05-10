<template>
  <div class="compare-chart">
    <!-- Search Inputs -->
    <div class="search-row">
      <!-- Coin 1 (Readonly - passed from parent) -->
      <div class="search-input-wrapper">
        <label class="input-label">Coin 1</label>
        <div class="coin-display" :style="{ borderColor: '#225095' }">
          <img v-if="coin1Data?.image" :src="coin1Data.image" :alt="coin1Data.name" class="coin-icon" />
          <span class="coin-name">{{ coin1Data?.name || 'Chọn coin' }}</span>
        </div>
      </div>

      <!-- Coin 2 (Searchable) -->
      <div class="search-input-wrapper">
        <label class="input-label">Coin 2</label>
        <div class="search-container" ref="searchContainer2">
          <input
            v-if="!coin2Data"
            type="text"
            v-model="searchQuery2"
            placeholder="Tìm kiếm coin..."
            class="search-input"
            @input="handleSearch2"
            @focus="showDropdown2 = true"
            aria-label="Tìm kiếm coin 2"
          />
          <div v-else class="coin-display selected" :style="{ borderColor: '#fac901' }">
            <img :src="coin2Data.image" :alt="coin2Data.name" class="coin-icon" />
            <span class="coin-name">{{ coin2Data.name }}</span>
            <button class="btn-clear" @click="clearCoin2" aria-label="Xóa coin 2">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/>
                <line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>

          <!-- Dropdown Results -->
          <div v-if="showDropdown2 && searchResults2.length > 0" class="search-dropdown">
            <div
              v-for="coin in searchResults2"
              :key="coin.id"
              class="dropdown-item"
              @click="selectCoin2(coin)"
            >
              <img :src="coin.image" :alt="coin.name" class="coin-icon" />
              <span class="coin-name">{{ coin.name }}</span>
              <span class="coin-symbol">{{ coin.symbol?.toUpperCase() }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Chart Controls -->
    <div class="chart-controls">
      <!-- Period Selector -->
      <div class="period-selector">
        <button
          v-for="period in periods"
          :key="period.value"
          class="btn-period"
          :class="{ active: selectedPeriod === period.value }"
          @click="selectPeriod(period.value)"
        >
          {{ period.label }}
        </button>
      </div>

      <!-- Chart Type Toggle -->
      <div class="toggle-group">
        <button
          class="btn-toggle"
          :class="{ active: chartType === 'line' }"
          @click="setChartType('line')"
        >
          Line
        </button>
        <button
          class="btn-toggle"
          :class="{ active: chartType === 'area' }"
          @click="setChartType('area')"
        >
          Area
        </button>
      </div>

      <!-- Normalize Toggle -->
      <label class="normalize-toggle">
        <input type="checkbox" v-model="isNormalized" />
        <span>Normalize (%)</span>
      </label>
    </div>

    <!-- Chart Container -->
    <div ref="chartContainer" class="chart-wrapper"></div>

    <!-- Legend -->
    <div class="chart-legend">
      <div class="legend-item">
        <span class="legend-color" style="background: #225095"></span>
        <span class="legend-name">{{ coin1Data?.name || 'Coin 1' }}</span>
      </div>
      <div v-if="coin2Data" class="legend-item">
        <span class="legend-color" style="background: #fac901"></span>
        <span class="legend-name">{{ coin2Data.name }}</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="chart-loading">
      <div class="spinner"></div>
      <span>Đang tải dữ liệu...</span>
    </div>
  </div>
</template>

<script setup>
/**
 * CompareChart Component
 * 
 * What: Component so sánh 2 coins bằng biểu đồ line/area
 * Why: Tái sử dụng cho CompareView và CoinDetailView
 * How: Dùng 2 LineSeries với màu khác nhau, support normalize, debounce search
 */

import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { createChart, AreaSeries, LineSeries } from 'lightweight-charts'
import { api } from '@/services/api'

// Props
const props = defineProps({
  /** Coin 1 ID */
  coin1Id: {
    type: String,
    required: true
  },
  /** Period được chọn (days) */
  period: {
    type: Number,
    default: 7
  }
})

// Emits
const emit = defineEmits(['coin2-select'])

// Refs
const chartContainer = ref(null)
const searchContainer2 = ref(null)
const searchQuery2 = ref('')
const showDropdown2 = ref(false)
const searchResults2 = ref([])

// State
const coin1Data = ref(null)
const coin2Data = ref(null)
const coin1Prices = ref([])
const coin2Prices = ref([])
const selectedPeriod = ref(props.period)
const chartType = ref('area') // 'line' | 'area'
const isNormalized = ref(false)
const isLoading = ref(false)

// Chart
const chart = ref(null)
const series1 = ref(null)
const series2 = ref(null)

// Debounce
let searchTimeout = null

// Period options
const periods = [
  { label: '24H', value: 1 },
  { label: '7D', value: 7 },
  { label: '30D', value: 30 },
  { label: '90D', value: 90 }
]

// Resize observer
let resizeObserver = null

/**
 * Fetch coin 1 info và prices
 */
async function fetchCoin1() {
  try {
    const response = await api.get(`/coins/${props.coin1Id}`)
    coin1Data.value = response.data.coin
    
    // Fetch prices
    const pricesRes = await api.get(`/coins/${props.coin1Id}/history?days=${selectedPeriod.value}`)
    coin1Prices.value = pricesRes.data.prices || []
    
    updateChart()
  } catch (err) {
    console.error('Error fetching coin1:', err)
  }
}

/**
 * Search coin 2
 */
async function searchCoins(query) {
  if (!query.trim()) {
    searchResults2.value = []
    return
  }

  try {
    const response = await api.get(`/coins/search?q=${encodeURIComponent(query)}`)
    // API trả về { coins: [...] }
    searchResults2.value = response.data.coins?.slice(0, 8) || []
  } catch (err) {
    console.error('Error searching coins:', err)
    searchResults2.value = []
  }
}

/**
 * Handle search input với debounce
 */
function handleSearch2() {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    searchCoins(searchQuery2.value)
  }, 300)
}

/**
 * Select coin 2 từ dropdown
 */
function selectCoin2(coin) {
  coin2Data.value = coin
  searchQuery2.value = ''
  showDropdown2.value = false
  fetchCoin2()
  
  emit('coin2-select', coin)
}

/**
 * Clear coin 2
 */
function clearCoin2() {
  coin2Data.value = null
  coin2Prices.value = []
  updateChart()
}

/**
 * Fetch coin 2 prices
 */
async function fetchCoin2() {
  if (!coin2Data.value) return

  try {
    isLoading.value = true
    const response = await api.get(`/coins/${coin2Data.value.id}/history?days=${selectedPeriod.value}`)
    coin2Prices.value = response.data.prices || []
    updateChart()
  } catch (err) {
    console.error('Error fetching coin2:', err)
  } finally {
    isLoading.value = false
  }
}

/**
 * Convert prices data cho chart
 * Nếu normalize = true, tính % change từ giá base
 */
function convertPrices(prices, normalize = false) {
  if (!prices?.length) return []

  return prices.map(([ts, price]) => {
    const time = Math.floor(ts / 1000)
    
    if (normalize) {
      const basePrice = prices[0][1]
      const value = ((price - basePrice) / basePrice) * 100
      return { time, value }
    }
    
    return { time, value: price }
  })
}

/**
 * Normalize function (theo PLAN.md)
 */
function normalize(prices) {
  if (!prices?.length) return []
  
  const base = prices[0][1]
  return prices.map(([ts, p]) => ({
    time: Math.floor(ts / 1000),
    value: ((p - base) / base) * 100
  }))
}

/**
 * Init chart
 */
function initChart() {
  if (!chartContainer.value) return

  // Cleanup
  if (chart.value) {
    chart.value.remove()
    chart.value = null
    series1.value = null
    series2.value = null
  }

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

  // Add series - Dùng API v4+: addSeries thay vì addAreaSeries/addLineSeries
  if (chartType.value === 'area') {
    series1.value = chart.value.addSeries(AreaSeries, {
      lineColor: '#225095',
      topColor: 'rgba(34, 80, 149, 0.4)',
      bottomColor: 'rgba(34, 80, 149, 0.1)',
      lineWidth: 2
    })
    
    if (coin2Data.value) {
      series2.value = chart.value.addSeries(AreaSeries, {
        lineColor: '#fac901',
        topColor: 'rgba(250, 201, 1, 0.4)',
        bottomColor: 'rgba(250, 201, 1, 0.1)',
        lineWidth: 2
      })
    }
  } else {
    series1.value = chart.value.addSeries(LineSeries, {
      color: '#225095',
      lineWidth: 2
    })
    
    if (coin2Data.value) {
      series2.value = chart.value.addSeries(LineSeries, {
        color: '#fac901',
        lineWidth: 2
      })
    }
  }

  // Setup resize
  setupResizeObserver()
}

/**
 * Update chart với dữ liệu mới
 */
function updateChart() {
  if (!chart.value || !series1.value) return

  const data1 = isNormalized.value 
    ? normalize(coin1Prices.value)
    : convertPrices(coin1Prices.value)
  
  series1.value.setData(data1)

  if (series2.value && coin2Prices.value.length > 0) {
    const data2 = isNormalized.value
      ? normalize(coin2Prices.value)
      : convertPrices(coin2Prices.value)
    series2.value.setData(data2)
  }

  chart.value?.timeScale().fitContent()
}

/**
 * Setup resize observer
 */
function setupResizeObserver() {
  if (!chartContainer.value) return

  if (resizeObserver) {
    resizeObserver.disconnect()
  }

  resizeObserver = new ResizeObserver(() => {
    if (chart.value && chartContainer.value) {
      chart.value.resize(chartContainer.value.clientWidth, 400)
    }
  })
  resizeObserver.observe(chartContainer.value)
}

/**
 * Set chart type (line/area)
 */
function setChartType(type) {
  if (chartType.value === type) return
  chartType.value = type
  
  // Re-init chart với series mới
  initChart()
  updateChart()
}

/**
 * Select period
 */
function selectPeriod(period) {
  selectedPeriod.value = period
  
  // Fetch lại data
  fetchCoin1()
  if (coin2Data.value) {
    fetchCoin2()
  }
}

/**
 * Cleanup khi unmount
 */
function cleanupChart() {
  if (chart.value) {
    chart.value.remove()
    chart.value = null
    series1.value = null
    series2.value = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
}

// Click outside handler
function handleClickOutside(event) {
  if (searchContainer2.value && !searchContainer2.value.contains(event.target)) {
    showDropdown2.value = false
  }
}

// Lifecycle
// WHY: initChart() phải chạy TRƯỚC fetchCoin1() để chart instance tồn tại
// khi updateChart() được gọi từ bên trong fetchCoin1()
onMounted(async () => {
  initChart()
  await fetchCoin1()
  
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  cleanupChart()
  document.removeEventListener('click', handleClickOutside)
  clearTimeout(searchTimeout)
})

// Watch props
watch(() => props.coin1Id, () => {
  fetchCoin1()
})

watch(() => props.period, (newPeriod) => {
  selectedPeriod.value = newPeriod
})

// Watch normalize
watch(isNormalized, () => {
  updateChart()
})
</script>

<style scoped>
.compare-chart {
  width: 100%;
}

/* Search Row */
.search-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
}

.search-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.input-label {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--color-text-secondary);
}

.search-container {
  position: relative;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md);
  padding-left: var(--spacing-2xl);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

/* Coin Display */
.coin-display {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 2px solid;
  border-radius: var(--radius-md);
  min-height: 48px;
}

.coin-display.selected {
  padding-right: var(--spacing-sm);
}

.coin-icon {
  width: 24px;
  height: 24px;
  border-radius: 50%;
}

.coin-name {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--color-text-primary);
}

.coin-symbol {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.btn-clear {
  margin-left: auto;
  padding: var(--spacing-xs);
  background: transparent;
  border: none;
  cursor: pointer;
  color: var(--color-text-secondary);
}

.btn-clear:hover {
  color: var(--color-danger);
}

.btn-clear svg {
  width: 16px;
  height: 16px;
}

/* Dropdown */
.search-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  margin-top: var(--spacing-xs);
  max-height: 200px;
  overflow-y: auto;
  z-index: 100;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.dropdown-item:hover {
  background: var(--color-bg-tertiary);
}

/* Chart Controls */
.chart-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-lg);
  flex-wrap: wrap;
}

.period-selector {
  display: flex;
  gap: var(--spacing-xs);
}

.btn-period {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-period:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn-period.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-text-primary);
}

/* Toggle Group */
.toggle-group {
  display: flex;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.btn-toggle {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-toggle:hover {
  background: var(--color-bg-tertiary);
}

.btn-toggle.active {
  background: var(--color-primary);
  color: var(--color-text-primary);
}

/* Normalize Toggle */
.normalize-toggle {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.normalize-toggle input {
  width: 16px;
  height: 16px;
  accent-color: var(--color-primary);
}

/* Chart */
.chart-wrapper {
  width: 100%;
  height: 400px;
}

/* Legend */
.chart-legend {
  display: flex;
  gap: var(--spacing-xl);
  margin-top: var(--spacing-md);
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.legend-color {
  width: 16px;
  height: 4px;
  border-radius: 2px;
}

.legend-name {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

/* Loading */
.chart-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Responsive */
@media (max-width: 768px) {
  .search-row {
    grid-template-columns: 1fr;
  }
  
  .chart-controls {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .chart-wrapper {
    height: 300px;
  }
  
  .chart-legend {
    flex-direction: column;
    align-items: center;
  }
}
</style>