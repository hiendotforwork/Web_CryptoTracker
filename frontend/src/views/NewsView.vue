<template>
  <div class="news-view">
    <div class="container">
      <header class="page-header">
        <h1 class="page-title">Tin tức Crypto</h1>
        <p class="page-subtitle">Cập nhật tin tức mới nhất về thị trường cryptocurrency</p>
      </header>
      
      <!-- Search -->
      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Tìm kiếm tin tức..."
          class="search-input"
          @input="handleSearch"
        />
      </div>
      
      <!-- Loading -->
      <div class="loading" v-if="isLoading">
        <div class="news-grid">
          <div class="skeleton-card" v-for="i in 6" :key="i"></div>
        </div>
      </div>
      
      <!-- Error -->
      <div class="error-state" v-else-if="error">
        <p class="error-message">{{ error }}</p>
        <button class="btn-retry" @click="fetchNews()">Thử lại</button>
      </div>
      
      <!-- Empty -->
      <div class="empty-state" v-else-if="filteredNews.length === 0">
        <p class="empty-message">Không tìm thấy tin tức phù hợp</p>
      </div>
      
      <!-- News Grid -->
      <div class="news-grid" v-else>
        <article 
          class="news-card" 
          v-for="article in filteredNews" 
          :key="article.id"
        >
          <a 
            :href="article.url" 
            target="_blank" 
            rel="noopener noreferrer"
            class="news-link"
          >
            <h2 class="news-title">{{ article.title }}</h2>
            <div class="news-meta">
              <span class="news-source">{{ article.source }}</span>
              <span class="news-date">{{ formatDate(article.published_at) }}</span>
            </div>
          </a>
        </article>
      </div>
      
      <!-- Pagination -->
      <div class="pagination" v-if="totalPages > 1">
        <button 
          class="btn-page" 
          :disabled="currentPage <= 1"
          @click="changePage(currentPage - 1)"
        >
          Trước
        </button>
        <span class="page-info">Trang {{ currentPage }} / {{ totalPages }}</span>
        <button 
          class="btn-page" 
          :disabled="currentPage >= totalPages"
          @click="changePage(currentPage + 1)"
        >
          Sau
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { api } from '@/services/api'

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
  return news.value.filter(article => 
    article.title.toLowerCase().includes(query) ||
    article.source?.toLowerCase().includes(query)
  )
})

// Methods
function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('vi-VN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

function handleSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    currentPage.value = 1
    fetchNews()
  }, 300)
}

function changePage(page) {
  currentPage.value = page
  fetchNews()
}

async function fetchNews() {
  isLoading.value = true
  error.value = null
  
  try {
    const response = await api.get(`/news?page=${currentPage.value}&per_page=${newsPerPage}`)
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

/* Search */
.search-bar {
  margin-bottom: var(--spacing-xl);
}

.search-input {
  width: 100%;
  max-width: 400px;
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
  display: block;
  margin: 0 auto;
}

.search-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

/* News Grid */
.news-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-lg);
}

/* News Card */
.news-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
}

.news-link {
  display: block;
  padding: var(--spacing-lg);
  color: inherit;
  text-decoration: none;
}

.news-link:focus {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}

.news-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-sm);
}

.news-source {
  color: var(--color-primary-light);
  font-weight: 500;
}

.news-date {
  color: var(--color-text-secondary);
}

/* Skeleton */
.skeleton-card {
  height: 150px;
  border-radius: var(--radius-lg);
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.empty-message {
  color: var(--color-text-secondary);
  font-size: var(--font-size-lg);
}

/* Error */
.error-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-md);
}

.btn-retry {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-2xl);
}

.btn-page {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  transition: all var(--transition-fast);
}

.btn-page:hover:not(:disabled) {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.btn-page:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: var(--color-text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .news-grid {
    grid-template-columns: 1fr;
  }
}
</style>