<template>
  <div class="not-found-view">
    <div class="container">
      <div class="content">
        <h1 class="error-code">404</h1>
        <h2 class="error-title">Không tìm thấy trang</h2>
        <p class="error-message">Trang bạn đang tìm kiếm không tồn tại hoặc đã được di chuyển.</p>
        <button class="btn-home" @click="$router.push('/')">Về trang chủ</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  document.title = '404 - Không tìm thấy'
})
</script>

<style scoped>
.not-found-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.content {
  text-align: center;
}

.error-code {
  font-size: 8rem;
  font-weight: 800;
  color: var(--color-primary);
  line-height: 1;
  margin-bottom: var(--spacing-md);
  opacity: 0.5;
}

.error-title {
  font-size: var(--font-size-3xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-md);
}

.error-message {
  color: var(--color-text-secondary);
  margin-bottom: var(--spacing-xl);
  max-width: 400px;
}

.btn-home {
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-weight: 600;
  font-size: var(--font-size-base);
  transition: all var(--transition-fast);
}

.btn-home:hover {
  background: var(--color-primary-light);
}

/* Responsive */
@media (max-width: 768px) {
  .error-code {
    font-size: 6rem;
  }
  
  .error-title {
    font-size: var(--font-size-2xl);
  }
}
</style>