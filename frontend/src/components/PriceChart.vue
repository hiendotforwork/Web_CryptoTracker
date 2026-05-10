<template>
  <div class="price-chart">
    <!-- Chart Tabs -->
    <div v-if="showTabs" class="chart-tabs">
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

    <!-- Chart Container -->
    <div ref="chartContainer" class="chart-wrapper"></div>
  </div>
</template>

<script setup>
/**
 * PriceChart Component
 * 
 * What: Component hiển thị biểu đồ giá sử dụng TradingView Lightweight Charts
 * Why: Tách riêng để tái sử dụng cho CoinDetailView và CompareChart
 * How: Dùng lightweight-charts với AreaSeries, tự động resize, cleanup khi unmount
 */

import { ref, onMounted, onUnmounted, watch } from 'vue'
import { createChart, AreaSeries } from 'lightweight-charts'

// Props definition
const props = defineProps({
  /** Dữ liệu giá: Array of [timestamp_ms, price] */
  prices: {
    type: Array,
    default: () => []
  },
  /** Màu đường line */
  lineColor: {
    type: String,
    default: '#3d6b8a'
  },
  /** Màu gradient top */
  topColor: {
    type: String,
    default: 'rgba(61, 107, 138, 0.4)'
  },
  /** Màu gradient bottom */
  bottomColor: {
    type: String,
    default: 'rgba(61, 107, 138, 0.1)'
  },
  /** Chiều cao chart */
  height: {
    type: Number,
    default: 400
  },
  /** Có hiện tabs chọn period không */
  showTabs: {
    type: Boolean,
    default: true
  },
  /** Period được chọn (days) - emit khi thay đổi */
  period: {
    type: Number,
    default: 7
  }
})

// Emits definition
const emit = defineEmits(['period-change'])

// Refs
const chartContainer = ref(null)
const chart = ref(null)
const chartSeries = ref(null)
const selectedPeriod = ref(props.period)

// Resize observer
let resizeObserver = null

// Period options
const periods = [
  { label: '24H', value: 1 },
  { label: '7D', value: 7 },
  { label: '30D', value: 30 },
  { label: '90D', value: 90 },
  { label: '1Y', value: 365 }
]

/**
 * Khởi tạo chart với config
 */
function initChart() {
  if (!chartContainer.value) return

  // Cleanup existing chart
  cleanupChart()

  chart.value = createChart(chartContainer.value, {
    width: chartContainer.value.clientWidth,
    height: props.height,
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

  // Dùng API v4+: addSeries thay vì addAreaSeries (deprecated từ v4)
  chartSeries.value = chart.value.addSeries(AreaSeries, {
    lineColor: props.lineColor,
    topColor: props.topColor,
    bottomColor: props.bottomColor,
    lineWidth: 2
  })

  // Setup resize observer
  setupResizeObserver()
}

/**
 * Cleanup chart khi unmount
 */
function cleanupChart() {
  if (chart.value) {
    chart.value.remove()
    chart.value = null
    chartSeries.value = null
  }
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
}

/**
 * Setup ResizeObserver cho responsive
 */
function setupResizeObserver() {
  if (!chartContainer.value) return

  resizeObserver = new ResizeObserver(() => {
    if (chart.value && chartContainer.value) {
      chart.value.resize(chartContainer.value.clientWidth, props.height)
    }
  })
  resizeObserver.observe(chartContainer.value)
}

/**
 * Update chart với dữ liệu mới
 */
function updateChart() {
  if (!chartSeries.value || !props.prices?.length) return

  // Convert timestamp: API trả milliseconds → chart cần seconds
  const data = props.prices.map(([ts, value]) => ({
    time: Math.floor(ts / 1000),
    value
  }))

  chartSeries.value.setData(data)
  chart.value?.timeScale().fitContent()
}

/**
 * Chọn period mới
 */
function selectPeriod(period) {
  selectedPeriod.value = period
  emit('period-change', period)
}

/**
 * Watch prices thay đổi → update chart
 */
watch(() => props.prices, () => {
  updateChart()
}, { deep: true })

/**
 * Watch height thay đổi → resize chart
 */
watch(() => props.height, (newHeight) => {
  if (chart.value && chartContainer.value) {
    chart.value.resize(chartContainer.value.clientWidth, newHeight)
  }
})

// Lifecycle
onMounted(() => {
  initChart()
  updateChart()
})

onUnmounted(() => {
  cleanupChart()
})
</script>

<style scoped>
.price-chart {
  width: 100%;
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
  cursor: pointer;
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
  width: 100%;
  height: 400px;
}

/* Responsive */
@media (max-width: 768px) {
  .chart-wrapper {
    height: 300px;
  }
}
</style>