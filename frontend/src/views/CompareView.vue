<template>
  <div class="compare-view">
    <div class="container">
      <!-- Header -->
      <header class="page-header">
        <h1 class="page-title">So sánh Coin</h1>
        <p class="page-subtitle">So sánh hiệu suất giữa 2 coins</p>
      </header>

      <!-- Compare Chart Component -->
      <CompareChart 
        v-if="coin1Id"
        :coin1-id="coin1Id"
        :period="selectedPeriod"
        @coin2-select="handleCoin2Select"
      />

      <!-- Error State -->
      <div v-else class="error-state">
        <p class="error-message">Không có coin để so sánh</p>
        <button class="btn-back" @click="goBack">Về trang chủ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * CompareView - Trang so sánh 2 coins
 * 
 * What: Trang cho phép so sánh giá 2 coins với biểu đồ
 * Why: Route /compare
 * How: Sử dụng CompareChart component, đọc coin1 từ query params
 */

import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CompareChart from '@/components/CompareChart.vue'

const route = useRoute()
const router = useRouter()

// State
const coin1Id = ref('')
const selectedPeriod = ref(7)

/**
 * Go back to previous page
 */
function goBack() {
  router.push('/')
}

/**
 * Handle coin 2 selection
 */
function handleCoin2Select(coin2) {
  console.log('Coin 2 selected:', coin2.id)
}

// Lifecycle
onMounted(() => {
  // Lấy coin1 từ query params
  coin1Id.value = route.query.coin1 || ''
})
</script>

<style scoped>
.compare-view {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
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
  cursor: pointer;
  border: none;
  transition: background var(--transition-fast);
}

.btn-back:hover {
  background: var(--color-primary-light);
}
</style>