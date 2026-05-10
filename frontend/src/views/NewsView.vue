<template>
  <div class="news-view">
    <!-- Animated background decoration -->
    <div class="bg-decoration">
      <div class="bg-glow bg-glow-1"></div>
      <div class="bg-glow bg-glow-2"></div>
    </div>

    <div class="container">
      <!-- Header -->
      <header class="page-header">
        <h1 class="page-title">
          <span class="title-accent">Tin tức</span> Crypto
        </h1>
        <p class="page-subtitle">
          Cập nhật tin tức mới nhất về thị trường cryptocurrency
        </p>
      </header>

      <!-- Stats Bar -->
      <div class="stats-bar" v-if="!isLoading && !error">
        <div class="stat-item">
          <span class="stat-value">{{ news.length }}</span>
          <span class="stat-label">Tin tức</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat-item">
          <span class="stat-value">{{ totalPages }}</span>
          <span class="stat-label">Trang</span>
        </div>
      </div>

      <!-- Search -->
      <div class="search-wrapper">
        <div class="search-bar">
          <svg
            class="search-icon"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.35-4.35" />
          </svg>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="Tìm kiếm tin tức..."
            class="search-input"
            @input="handleSearch"
            aria-label="Tìm kiếm tin tức"
          />
          <button
            v-if="searchQuery"
            class="search-clear"
            @click="clearSearch"
            aria-label="Xóa tìm kiếm"
          >
            <svg
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div class="loading" v-if="isLoading">
        <div class="loading-header">
          <div class="skeleton skeleton-text skeleton-title"></div>
          <div class="skeleton skeleton-text skeleton-subtitle"></div>
        </div>
        <div class="news-grid">
          <div class="skeleton skeleton-card" v-for="i in 6" :key="i"></div>
        </div>
      </div>

      <!-- Error -->
      <div class="error-state" v-else-if="error">
        <div class="error-icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="fetchNews()">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="23 4 23 10 17 10" />
            <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
          </svg>
          Thử lại
        </button>
      </div>

      <!-- Empty -->
      <div class="empty-state" v-else-if="filteredNews.length === 0">
        <div class="empty-icon">
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.5"
          >
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </div>
        <p class="empty-message">
          {{ searchQuery ? 'Không tìm thấy tin tức phù hợp' : 'Chưa có tin tức nào' }}
        </p>
        <p class="empty-hint" v-if="searchQuery">
          Thử từ khóa khác
        </p>
      </div>

      <!-- News Grid with stagger animation -->
      <div class="news-grid" v-else>
        <NewsCard
          v-for="(article, index) in filteredNews"
          :key="article.id || index"
          :article="article"
          :style="{ animationDelay: `${index * 50}ms` }"
        />
      </div>

      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1 && !isLoading && !error">
        <button
          class="btn-page"
          :disabled="currentPage <= 1"
          @click="changePage(currentPage - 1)"
          :aria-label="'Trang trước'"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <span class="page-info">
          <span class="page-current">{{ currentPage }}</span>
          <span class="page-separator">/</span>
          <span class="page-total">{{ totalPages }}</span>
        </span>

        <button
          class="btn-page"
          :disabled="currentPage >= totalPages"
          @click="changePage(currentPage + 1)"
          :aria-label="'Trang sau'"
        >
          <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <polyline points="9 18 15 12 9 6" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * NewsView - Trang tin tức Crypto
 *
 * What: Hiển thị danh sách tin tức với search, pagination
 * Why: Route /news - cung cấp thông tin thị trường cho user
 * How: Dùng NewsCard component, debounce search 300ms, CSS Grid auto-fill
 */

import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'
import NewsCard from '@/components/NewsCard.vue'

// State
const news = ref([])
const isLoading = ref(true)
const error = ref(null)
const searchQuery = ref('')
const currentPage = ref(1)
const totalPages = ref(1)
const newsPerPage = 12

// Debounce timer
let searchTimer = null

// Computed
const filteredNews = computed(() => {
  if (!searchQuery.value) return news.value
  const query = searchQuery.value.toLowerCase()
  return news.value.filter(
    (article) =>
      article.title.toLowerCase().includes(query) ||
      article.source?.toLowerCase().includes(query)
  )
})

/**
 * Handle search input với debounce 300ms
 */
function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchNews()
  }, 300)
}

/**
 * Clear search query
 */
function clearSearch() {
  searchQuery.value = ''
  currentPage.value = 1
  fetchNews()
}

/**
 * Change page
 * @param {number} page
 */
function changePage(page) {
  currentPage.value = page
  fetchNews()

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

/**
 * Fetch news từ API
 */
async function fetchNews() {
  isLoading.value = true
  error.value = null

  try {
    const response = await api.get(
      `/news/?page=${currentPage.value}&per_page=${newsPerPage}`
    )
    news.value = response.data.news || []
    totalPages.value = response.data.total_pages || 1
  } catch (err) {
    error.value = 'Không thể tải tin tức. Vui lòng thử lại.'
    console.error('Error fetching news:', err)
  } finally {
    isLoading.value = false
  }
}

// Lifecycle
onMounted(() => {
  fetchNews()
})
</script>

<style scoped>
.news-view {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
  position: relative;
  overflow: hidden;
}

/* Background decoration */
.bg-decoration {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-glow {
  position: absolute;
  border-radius: 50%;
  filter: blur(120px);
  opacity: 0.05;
}

.bg-glow-1 {
  width: 600px;
  height: 600px;
  background: var(--color-primary);
  top: -200px;
  right: -200px;
}

.bg-glow-2 {
  width: 400px;
  height: 400px;
  background: var(--color-primary-light);
  bottom: -100px;
  left: -100px;
}

/* Ensure content is above background */
.container {
  position: relative;
  z-index: 1;
}

/* =====================================================
   HEADER
   ===================================================== */
.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-sm);
  letter-spacing: -0.02em;
}

.title-accent {
  background: linear-gradient(
    135deg,
    var(--color-primary-light) 0%,
    var(--color-primary) 100%
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
}

/* =====================================================
   STATS BAR
   ===================================================== */
.stats-bar {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md) var(--spacing-xl);
  background: linear-gradient(
    145deg,
    rgba(26, 58, 92, 0.5) 0%,
    rgba(13, 26, 38, 0.5) 100%
  );
  border: 1px solid rgba(61, 107, 138, 0.2);
  border-radius: var(--radius-lg);
  backdrop-filter: blur(10px);
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
}

.stat-value {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-primary-light);
  line-height: 1;
}

.stat-label {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background: linear-gradient(
    to bottom,
    transparent,
    var(--color-border),
    transparent
  );
}

/* =====================================================
   SEARCH
   ===================================================== */
.search-wrapper {
  display: flex;
  justify-content: center;
  margin-bottom: var(--spacing-xl);
}

.search-bar {
  position: relative;
  width: 100%;
  max-width: 500px;
}

.search-icon {
  position: absolute;
  left: var(--spacing-md);
  top: 50%;
  transform: translateY(-50%);
  width: 20px;
  height: 20px;
  color: var(--color-text-secondary);
  pointer-events: none;
  transition: color 0.2s ease;
}

.search-input {
  width: 100%;
  padding: var(--spacing-md) var(--spacing-2xl);
  padding-left: calc(var(--spacing-md) * 2 + 20px);
  background: linear-gradient(
    145deg,
    var(--color-bg-secondary) 0%,
    rgba(26, 58, 92, 0.8) 100%
  );
  border: 1px solid var(--color-border);
  border-radius: var(--radius-full);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: all 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(61, 107, 138, 0.15),
    0 0 20px rgba(61, 107, 138, 0.1);
}

.search-input:focus + .search-icon {
  color: var(--color-primary-light);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-clear {
  position: absolute;
  right: var(--spacing-sm);
  top: 50%;
  transform: translateY(-50%);
  padding: var(--spacing-xs);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: color 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.search-clear:hover {
  color: var(--color-text-primary);
}

.search-clear svg {
  width: 18px;
  height: 18px;
}

/* =====================================================
   NEWS GRID
   ===================================================== */
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: var(--spacing-lg);
}

/* =====================================================
   SKELETON LOADING
   ===================================================== */
.loading {
  animation: fadeIn 0.3s ease;
}

.loading-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.skeleton {
  background: linear-gradient(
    90deg,
    var(--color-bg-secondary) 25%,
    rgba(61, 107, 138, 0.2) 50%,
    var(--color-bg-secondary) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-lg);
}

@keyframes shimmer {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

.skeleton-text {
  height: 20px;
  margin: 0 auto var(--spacing-sm);
}

.skeleton-title {
  width: 250px;
  height: 36px;
  margin-bottom: var(--spacing-sm);
}

.skeleton-subtitle {
  width: 400px;
  height: 20px;
}

.skeleton-card {
  height: 160px;
}

/* =====================================================
   EMPTY STATE
   ===================================================== */
.empty-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
}

.empty-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  color: var(--color-text-secondary);
  opacity: 0.5;
}

.empty-icon svg {
  width: 100%;
  height: 100%;
}

.empty-message {
  color: var(--color-text-primary);
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
}

.empty-hint {
  color: var(--color-text-secondary);
  font-size: var(--font-size-base);
}

/* =====================================================
   ERROR STATE
   ===================================================== */
.error-state {
  text-align: center;
  padding: var(--spacing-3xl) var(--spacing-xl);
}

.error-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto var(--spacing-lg);
  color: var(--color-danger);
  opacity: 0.8;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-lg);
  font-size: var(--font-size-lg);
}

.btn-retry {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-xl);
  background: linear-gradient(
    135deg,
    var(--color-primary) 0%,
    var(--color-primary-light) 100%
  );
  border: none;
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-retry:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 20px -5px rgba(61, 107, 138, 0.3);
}

.btn-retry svg {
  width: 18px;
  height: 18px;
}

/* =====================================================
   PAGINATION
   ===================================================== */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-xl);
  margin-top: var(--spacing-2xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid rgba(61, 107, 138, 0.2);
}

.btn-page {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: all 0.3s ease;
  cursor: pointer;
}

.btn-page:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
  transform: translateY(-2px);
  box-shadow: 0 8px 16px -4px rgba(61, 107, 138, 0.2);
}

.btn-page:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.btn-page svg {
  width: 20px;
  height: 20px;
}

.page-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-base);
}

.page-current {
  font-weight: 700;
  color: var(--color-primary-light);
}

.page-separator {
  color: var(--color-text-secondary);
}

.page-total {
  color: var(--color-text-secondary);
}

/* =====================================================
   RESPONSIVE
   ===================================================== */
@media (max-width: 768px) {
  .page-title {
    font-size: var(--font-size-2xl);
  }

  .stats-bar {
    padding: var(--spacing-sm) var(--spacing-lg);
  }

  .stat-value {
    font-size: var(--font-size-xl);
  }

  .news-grid {
    grid-template-columns: 1fr;
  }

  .skeleton-subtitle {
    width: 250px;
  }

  .pagination {
    gap: var(--spacing-md);
  }
}
</style>
