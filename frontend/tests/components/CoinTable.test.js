/**
 * tests/components/CoinTable.test.js
 *
 * What: Unit tests cho CoinTable component
 * Why: Đảm bảo render đúng props và logic hiển thị nút theo mode/auth
 * How: Dùng @vue/test-utils mount(), mock vue-router và Pinia auth store
 */

import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'

// =====================================================
// MOCK vue-router (CoinTable dùng useRouter để navigate)
// =====================================================
const mockPush = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push: mockPush })
}))

// Import component sau khi mock đã được thiết lập
import CoinTable from '@/components/CoinTable.vue'
import { useAuthStore } from '@/stores/auth'

// =====================================================
// DỮ LIỆU MẪU — dùng chung giữa các test
// =====================================================
const sampleCoins = [
  {
    id: 'bitcoin',
    name: 'Bitcoin',
    symbol: 'btc',
    current_price: 42000,
    price_change_percentage_24h: 2.5,
    image: 'https://example.com/btc.png',
    market_cap_rank: 1
  },
  {
    id: 'ethereum',
    name: 'Ethereum',
    symbol: 'eth',
    current_price: 2500,
    price_change_percentage_24h: -1.2,
    image: 'https://example.com/eth.png',
    market_cap_rank: 2
  }
]

describe('CoinTable', () => {
  beforeEach(() => {
    // Khởi tạo Pinia mới trước mỗi test — isolation tuyệt đối
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  // -------------------------------------------------------------------
  // Test #1: Render đúng tên coin, symbol và giá
  // -------------------------------------------------------------------
  it('renders coin name, symbol and price', () => {
    const wrapper = mount(CoinTable, {
      props: {
        coins: sampleCoins,
        mode: 'default'
      }
    })

    // Kiểm tra Bitcoin xuất hiện
    expect(wrapper.text()).toContain('Bitcoin')
    expect(wrapper.text()).toContain('BTC')
    // Kiểm tra giá (toLocaleString có thể trả "42,000.00")
    expect(wrapper.text()).toContain('42')

    // Kiểm tra Ethereum xuất hiện
    expect(wrapper.text()).toContain('Ethereum')
    expect(wrapper.text()).toContain('ETH')
  })

  // -------------------------------------------------------------------
  // Test #2: Hiển thị nút "+" khi mode=default VÀ isAuthenticated=true
  // -------------------------------------------------------------------
  it('shows add button when mode is default and authenticated', async () => {
    // Override store → user đã đăng nhập
    const authStore = useAuthStore()
    authStore.token = 'fake-token'

    const wrapper = mount(CoinTable, {
      props: {
        coins: sampleCoins,
        mode: 'default',
        addedCoins: [] // Chưa thêm coin nào
      }
    })

    // Phải có ít nhất 1 nút "+" (btn-add)
    const addButtons = wrapper.findAll('.btn-add')
    expect(addButtons.length).toBeGreaterThan(0)
  })

  // -------------------------------------------------------------------
  // Test #3: Ẩn nút "+" khi chưa đăng nhập (isAuthenticated=false)
  // -------------------------------------------------------------------
  it('hides add button when not authenticated', () => {
    // token mặc định rỗng -> isAuthenticated = false
    const wrapper = mount(CoinTable, {
      props: {
        coins: sampleCoins,
        mode: 'default',
        addedCoins: []
      }
    })

    // Không được có nút btn-add khi chưa auth
    const addButtons = wrapper.findAll('.btn-add')
    expect(addButtons.length).toBe(0)
  })

  // -------------------------------------------------------------------
  // Test #4: Hiển thị nút "×" khi mode=watchlist
  // -------------------------------------------------------------------
  it('shows delete button when mode is watchlist', () => {
    const wrapper = mount(CoinTable, {
      props: {
        coins: sampleCoins,
        mode: 'watchlist'
      }
    })

    // Phải có đúng số nút "×" bằng số coins
    const removeButtons = wrapper.findAll('.btn-remove')
    expect(removeButtons.length).toBe(sampleCoins.length)
  })

  // -------------------------------------------------------------------
  // Test #5: Click vào row navigate đến trang coin detail
  // -------------------------------------------------------------------
  it('navigates to coin detail on row click', async () => {
    const wrapper = mount(CoinTable, {
      props: {
        coins: sampleCoins,
        mode: 'default'
      }
    })

    // Click vào row đầu tiên
    const firstRow = wrapper.find('.table-row')
    await firstRow.trigger('click')

    // Kiểm tra router.push được gọi với đúng path
    expect(mockPush).toHaveBeenCalledWith('/coin/bitcoin')
  })
})
