<template>
  <div class="coin-table">
    <!-- Table Header -->
    <div class="table-header">
      <span class="col-rank">#</span>
      <span class="col-name">Tên</span>
      <span class="col-price">Giá</span>
      <span class="col-change">24h %</span>
      <span class="col-action"></span>
    </div>
    
    <!-- Table Rows -->
    <div 
      v-for="(coin, index) in coins" 
      :key="coin.id"
      class="table-row"
      @click="handleRowClick(coin.id)"
    >
      <span class="col-rank">{{ getDisplayIndex(index) }}</span>
      
      <span class="col-name">
        <img 
          :src="coin.image" 
          :alt="coin.name" 
          class="coin-icon"
          loading="lazy"
        />
        <span class="coin-name">{{ coin.name }}</span>
        <span class="coin-symbol">{{ coin.symbol?.toUpperCase() }}</span>
      </span>
      
      <span class="col-price">
        ${{ formatPrice(coin.current_price) }}
      </span>
      
      <span 
        class="col-change"
        :class="{ 
          'positive': coin.price_change_percentage_24h > 0, 
          'negative': coin.price_change_percentage_24h < 0 
        }"
      >
        <span class="change-icon">{{ coin.price_change_percentage_24h > 0 ? '▲' : '▼' }}</span>
        {{ Math.abs(coin.price_change_percentage_24h || 0).toFixed(2) }}%
      </span>
      
      <span class="col-action" @click.stop>
        <button 
          v-if="mode === 'default' && isAuthenticated && !addedCoins.includes(coin.id)"
          class="btn-add"
          @click="handleAddToWatchlist(coin.id)"
          aria-label="Thêm vào watchlist"
        >
          +
        </button>
        <button 
          v-else-if="mode === 'watchlist'"
          class="btn-remove"
          @click="handleRemoveFromWatchlist(coin.id)"
          aria-label="Xóa khỏi watchlist"
        >
          ×
        </button>
        <span v-else-if="addedCoins.includes(coin.id)" class="added-badge" aria-label="Đã thêm vào watchlist">
          ★
        </span>
      </span>
    </div>
    
    <!-- Empty State -->
    <div v-if="coins.length === 0" class="empty-state">
      <p>Không tìm thấy coin nào</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// =====================================================
// PROPS
// =====================================================
const props = defineProps({
  /**
   * Danh sách coins hiển thị
   */
  coins: {
    type: Array,
    required: true,
    default: () => []
  },
  
  /**
   * Chế độ hiển thị: 'default' hoặc 'watchlist'
   */
  mode: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'watchlist'].includes(value)
  },
  
  /**
   * Page hiện tại (để tính display index)
   */
  page: {
    type: Number,
    default: 1
  },
  
  /**
   * Số coins mỗi trang
   */
  perPage: {
    type: Number,
    default: 25
  },
  
  /**
   * Danh sách ID coins đã thêm vào watchlist
   */
  addedCoins: {
    type: Array,
    default: () => []
  }
})

// =====================================================
// EMITS
// =====================================================
const emit = defineEmits([
  'add-to-watchlist',
  'remove-from-watchlist'
])

// =====================================================
// STORE & COMPOSABLES
// =====================================================
const router = useRouter()
const authStore = useAuthStore()
const { isAuthenticated } = storeToRefs(authStore)

// =====================================================
// STATE
// =====================================================

// =====================================================
// COMPUTED
// =====================================================

// =====================================================
// METHODS
// =====================================================

/**
 * Tính display index cho coin (dựa trên page và index trong mảng)
 */
function getDisplayIndex(index) {
  return (props.page - 1) * props.perPage + index + 1
}

/**
 * Format giá với separators
 */
function formatPrice(price) {
  if (!price && price !== 0) return '0.00'
  return price.toLocaleString('en-US', { 
    minimumFractionDigits: 2, 
    maximumFractionDigits: 2 
  })
}

/**
 * Navigate đến trang chi tiết coin
 */
function handleRowClick(coinId) {
  router.push(`/coin/${coinId}`)
}

/**
 * Thêm coin vào watchlist
 */
function handleAddToWatchlist(coinId) {
  emit('add-to-watchlist', coinId)
}

/**
 * Xóa coin khỏi watchlist
 */
function handleRemoveFromWatchlist(coinId) {
  emit('remove-from-watchlist', coinId)
}
</script>

<style scoped>
.coin-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

/* =====================================================
   TABLE HEADER
   ===================================================== */
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

/* =====================================================
   TABLE ROW
   ===================================================== */
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

/* =====================================================
   COLUMNS
   ===================================================== */
.col-rank {
  color: var(--color-text-secondary);
  font-weight: 500;
  font-size: var(--font-size-sm);
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
  flex-shrink: 0;
}

.coin-name {
  font-weight: 500;
  color: var(--color-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
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
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
}

.change-icon {
  font-size: 10px;
}

.col-change.positive {
  color: var(--color-success);
}

.col-change.negative {
  color: var(--color-danger);
}

.col-action {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* =====================================================
   BUTTONS
   ===================================================== */
.btn-add {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: 600;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-add:hover {
  background: var(--color-primary-light);
  transform: scale(1.05);
}

.btn-remove {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-md);
  background: var(--color-danger);
  color: var(--color-text-primary);
  font-size: var(--font-size-lg);
  font-weight: 600;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove:hover {
  opacity: 0.8;
}

.added-badge {
  color: var(--color-success);
  font-weight: 600;
  font-size: var(--font-size-lg);
}

/* =====================================================
   EMPTY STATE
   ===================================================== */
.empty-state {
  padding: var(--spacing-2xl);
  text-align: center;
  color: var(--color-text-secondary);
}

/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 768px) {
  .table-header {
    display: none;
  }
  
  .table-row {
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
  }
  
  .col-rank {
    display: none;
  }
  
  .col-name {
    flex-direction: row;
    align-items: center;
    grid-column: 1 / -1;
  }
  
  .coin-name {
    max-width: 120px;
  }
  
  .coin-icon {
    width: 24px;
    height: 24px;
  }
  
  .col-price,
  .col-change {
    font-size: var(--font-size-sm);
    justify-content: flex-end;
  }
  
  .col-action {
    position: absolute;
    right: var(--spacing-md);
    bottom: var(--spacing-md);
  }
  
  .table-row {
    position: relative;
  }
}
</style>