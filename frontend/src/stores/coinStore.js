/**
 * Crypto Tracker - Coin Store (Pinia)
 * 
 * Quản lý trạng thái danh sách coins:
 * - State: coins, totalPages, isLoading, error
 * - Actions: fetchCoins(page, searchQuery)
 * 
 * WHY: Tách state management giúp HomeView và WatchlistView dùng chung logic
 * HOW: Dùng Pinia Composition API với storeToRefs cho reactivity
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const useCoinStore = defineStore('coins', () => {
  // =====================================================
  // STATE
  // =====================================================
  const coins = ref([])
  const totalPages = ref(1)
  const isLoading = ref(false)
  const error = ref(null)
  const currentPage = ref(1)

  // =====================================================
  // ACTIONS
  // =====================================================

  /**
   * Lấy danh sách coins từ API
   * @param {number} page - Số trang (mặc định 1)
   * @param {string} searchQuery - Query tìm kiếm (optional)
   */
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

  /**
   * Refresh dữ liệu - gọi lại API với page hiện tại
   */
  async function refresh() {
    await fetchCoins(currentPage.value)
  }

  // =====================================================
  // RETURN
  // =====================================================
  return {
    // State
    coins,
    totalPages,
    isLoading,
    error,
    currentPage,

    // Actions
    fetchCoins,
    refresh
  }
})