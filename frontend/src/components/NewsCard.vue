<template>
  <article class="news-card">
    <a
      :href="article.url"
      target="_blank"
      rel="noopener noreferrer"
      class="news-link"
      :aria-label="`Đọc tin: ${article.title}`"
    >
      <div class="card-content">
        <h2 class="news-title">{{ article.title }}</h2>
        <div class="news-meta">
          <span class="news-source">{{ article.source }}</span>
          <span class="news-date">{{ formatDate(article.published_at) }}</span>
        </div>
      </div>
    </a>
  </article>
</template>

<script setup>
/**
 * NewsCard Component
 *
 * What: Hiển thị một card tin tức với title, source, ngày đăng
 * Why: Component riêng để tái sử dụng, dễ bảo trì và test
 * How: Nhận dữ liệu qua prop `article`, format ngày theo locale vi-VN
 */

// Props definition
const props = defineProps({
  article: {
    type: Object,
    required: true,
    validator(value) {
      return (
        value &&
        typeof value.title === 'string' &&
        typeof value.url === 'string'
      )
    }
  }
})

/**
 * Format ngày theo locale Việt Nam
 * @param {string} dateStr - ISO date string
 * @returns {string} Ngày định dạng "1 thg 1, 2024"
 */
function formatDate(dateStr) {
  if (!dateStr) return ''

  const date = new Date(dateStr)

  // Kiểm tra date hợp lệ
  if (isNaN(date.getTime())) return ''

  return date.toLocaleDateString('vi-VN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}
</script>

<style scoped>
.news-card {
  background: linear-gradient(
    145deg,
    var(--color-bg-secondary) 0%,
    rgba(26, 58, 92, 0.8) 100%
  );
  border: 1px solid transparent;
  border-radius: var(--radius-lg);
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
}

/* Gradient border effect on hover */
.news-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: var(--radius-lg);
  padding: 1px;
  background: linear-gradient(
    135deg,
    transparent 0%,
    transparent 40%,
    var(--color-primary-light) 50%,
    transparent 60%,
    transparent 100%
  );
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.news-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 20px 40px -10px rgba(204, 41, 54, 0.15),
              0 0 20px rgba(204, 41, 54, 0.05);
}

.news-card:hover::before {
  opacity: 1;
}

.news-link {
  display: block;
  padding: var(--spacing-lg);
  color: inherit;
  text-decoration: none;
  height: 100%;
}

.news-link:focus-visible {
  outline: 2px solid var(--color-primary-light);
  outline-offset: 2px;
  border-radius: var(--radius-lg);
}

.card-content {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 140px;
}

.news-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  transition: color 0.2s ease;
}

.news-card:hover .news-title {
  color: var(--color-primary-light);
}

.news-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: auto;
  font-size: var(--font-size-sm);
  gap: var(--spacing-sm);
}

.news-source {
  color: var(--color-primary-light);
  font-weight: 500;
  position: relative;
  padding-left: var(--spacing-sm);
}

.news-source::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--color-primary-light);
}

.news-date {
  color: var(--color-text-secondary);
  font-size: 0.8125rem;
  white-space: nowrap;
}

/* Glow pulse animation for cards */
@keyframes cardGlow {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(204, 41, 54, 0);
  }
  50% {
    box-shadow: 0 0 20px 2px rgba(204, 41, 54, 0.08);
  }
}

/* Stagger animation cho cards */
.news-card {
  opacity: 0;
  animation: cardEnter 0.4s ease forwards;
}

@keyframes cardEnter {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
