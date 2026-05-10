/**
 * Crypto Tracker - Watchlist Store (Pinia)
 * 
 * Quản lý trạng thái watchlist của user:
 * - State: coins, isLoading, error
 * - Actions: fetchWatchlist, addCoin, removeCoin
 * 
 * WHY: Tách riêng watchlist state giúp reuse ở HomeView, WatchlistView, CoinDetailView
 * HOW: Dùng Pinia Composition API với storeToRefs cho reactivity
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { api } from '@/services/api'

export const useWatchlistStore = defineStore('watchlist', () => {
  // =====================================================
  // STATE
  // =====================================================
  const coins = ref([])
  const isLoading = ref(false)
  const error = ref(null)

  // =====================================================
  // ACTIONS
  // =====================================================

  /**
   * Lấy danh sách watchlist từ API
   * API endpoint trả về watchlist items (chỉ có coin_id, created_at)
   * Sau đó gọi /coins để lấy thông tin chi tiết coins
   */
  async function fetchWatchlist() {
    isLoading.value = true
    error.value = null

    try {
      // Lấy danh sách watchlist items (chỉ có coin_id)
      // _skipAuthRedirect: true → báo interceptor không tự redirect, store tự xử lý 401
      const response = await api.get('/watchlist/', { _skipAuthRedirect: true })
      const watchlistItems = response.data.watchlist || []
      
      // Nếu không có items, trả về empty array
      if (watchlistItems.length === 0) {
        coins.value = []
        return
      }

      // Lấy thông tin chi tiết từng coin
      // Gọi /coins để lấy thông tin (hoặc gọi từng /coins/{id})
      const coinIds = watchlistItems.map(item => item.coin_id)
      
      // Gọi API lấy coins detail - fetch từng coin để lấy đầy đủ thông tin
      const coinDetailsPromises = coinIds.map(async (coinId) => {
        try {
          const res = await api.get(`/coins/${coinId}`)
          return res.data.coin
        } catch (err) {
          console.warn(`Failed to fetch coin ${coinId}:`, err)
          return null
        }
      })

      const coinDetails = await Promise.all(coinDetailsPromises)
      coins.value = coinDetails.filter(Boolean)

    } catch (err) {
      // Phân biệt lỗi 401 (token hết hạn) với lỗi khác
      if (err.response?.status === 401) {
        error.value = 'Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.'
      } else {
        error.value = 'Không thể tải watchlist'
      }
      console.error('Error fetching watchlist:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Thêm coin vào watchlist
   * @param {string} coinId - ID của coin cần thêm
   */
  async function addCoin(coinId) {
    try {
      await api.post('/watchlist/', { coin_id: coinId }, { _skipAuthRedirect: true })
      
      // Fetch lại thông tin coin để thêm vào local state
      const res = await api.get(`/coins/${coinId}`)
      if (res.data.coin && !coins.value.find(c => c.id === coinId)) {
        coins.value.push(res.data.coin)
      }
      
      return true
    } catch (err) {
      if (err.response?.status === 401) {
        throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
      }
      const errorMsg = err.response?.data?.error || 'Không thể thêm vào watchlist'
      throw new Error(errorMsg)
    }
  }

  /**
   * Xóa coin khỏi watchlist
   * @param {string} coinId - ID của coin cần xóa
   */
  async function removeCoin(coinId) {
    try {
      await api.delete(`/watchlist/${coinId}/`, { _skipAuthRedirect: true })
      
      // Xóa khỏi local state
      coins.value = coins.value.filter(c => c.id !== coinId)
      
      return true
    } catch (err) {
      if (err.response?.status === 401) {
        throw new Error('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.')
      }
      const errorMsg = err.response?.data?.error || 'Không thể xóa khỏi watchlist'
      throw new Error(errorMsg)
    }
  }

  /**
   * Kiểm tra coin có trong watchlist không
   * @param {string} coinId - ID của coin
   */
  function hasCoin(coinId) {
    return coins.value.some(c => c.id === coinId)
  }

  /**
   * Clear watchlist (khi logout)
   */
  function clear() {
    coins.value = []
    error.value = null
  }

  // =====================================================
  // RETURN
  // =====================================================
  return {
    // State
    coins,
    isLoading,
    error,

    // Actions
    fetchWatchlist,
    addCoin,
    removeCoin,
    hasCoin,
    clear
  }
})