<template>
  <div class="auth-view">
    <div class="auth-container">
      <div class="auth-card">
        <header class="auth-header">
          <h1 class="auth-title">
            {{ isLoginMode ? 'Đăng nhập' : 'Đăng ký' }}
          </h1>
          <p class="auth-subtitle">
            {{ isLoginMode ? 'Chào mừng trở lại!' : 'Tạo tài khoản mới' }}
          </p>
        </header>
        
        <form @submit.prevent="handleSubmit" class="auth-form">
          <!-- Login Form -->
          <template v-if="isLoginMode">
            <div class="form-group">
              <label for="username" class="form-label">Tên đăng nhập</label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-input"
                placeholder="Nhập tên đăng nhập"
                autocomplete="username"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="password" class="form-label">Mật khẩu</label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="Nhập mật khẩu"
                autocomplete="current-password"
                required
              />
            </div>
          </template>
          
          <!-- Register Form -->
          <template v-else>
            <div class="form-group">
              <label for="username" class="form-label">Tên đăng nhập</label>
              <input
                id="username"
                v-model="form.username"
                type="text"
                class="form-input"
                placeholder="Nhập tên đăng nhập"
                autocomplete="username"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="email" class="form-label">Email</label>
              <input
                id="email"
                v-model="form.email"
                type="email"
                class="form-input"
                placeholder="Nhập email"
                autocomplete="email"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="password" class="form-label">Mật khẩu</label>
              <input
                id="password"
                v-model="form.password"
                type="password"
                class="form-input"
                placeholder="Nhập mật khẩu (ít nhất 6 ký tự)"
                autocomplete="new-password"
                required
              />
            </div>
            
            <div class="form-group">
              <label for="confirmPassword" class="form-label">Xác nhận mật khẩu</label>
              <input
                id="confirmPassword"
                v-model="form.confirmPassword"
                type="password"
                class="form-input"
                placeholder="Nhập lại mật khẩu"
                autocomplete="new-password"
                required
              />
            </div>
          </template>
          
          <!-- Error Message -->
          <div v-if="errorMsg" class="error-alert">
            {{ errorMsg }}
          </div>
          
          <!-- Submit Button -->
          <button 
            type="submit" 
            class="btn-submit"
            :disabled="isLoading"
          >
            <span v-if="isLoading" class="spinner"></span>
            <span v-else>{{ isLoginMode ? 'Đăng nhập' : 'Đăng ký' }}</span>
          </button>
        </form>
        
        <!-- Toggle Mode -->
        <footer class="auth-footer">
          <p class="toggle-text">
            {{ isLoginMode ? 'Chưa có tài khoản?' : 'Đã có tài khoản?' }}
            <button 
              type="button" 
              class="btn-toggle"
              @click="toggleMode"
            >
              {{ isLoginMode ? 'Đăng ký ngay' : 'Đăng nhập' }}
            </button>
          </p>
        </footer>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, inject } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

// Nhận showToast từ App.vue qua provide/inject
const showToast = inject('showToast')

// State
const isLoginMode = ref(true)
const isLoading = ref(false)
const errorMsg = ref('')

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// Methods
function toggleMode() {
  isLoginMode.value = !isLoginMode.value
  errorMsg.value = ''
  form.username = ''
  form.email = ''
  form.password = ''
  form.confirmPassword = ''
}

async function handleSubmit() {
  errorMsg.value = ''
  
  // Client-side validation
  if (!form.username || !form.password) {
    errorMsg.value = 'Vui lòng điền đầy đủ thông tin'
    return
  }
  
  if (!isLoginMode.value) {
    if (form.password.length < 6) {
      errorMsg.value = 'Mật khẩu phải ít nhất 6 ký tự'
      return
    }
    
    if (form.password !== form.confirmPassword) {
      errorMsg.value = 'Mật khẩu xác nhận không khớp'
      return
    }
  }
  
  isLoading.value = true
  
  try {
    if (isLoginMode.value) {
      await authStore.login(form.username, form.password)
      // Redirect sau đăng nhập thành công
      const redirect = route.query.redirect || '/'
      router.push(redirect)
    } else {
      await authStore.register({
        username: form.username,
        email: form.email,
        password: form.password
      })
      // Đăng ký thành công → chuyển sang form đăng nhập + hiển thị toast
      toggleMode()
      showToast?.('Đăng ký thành công! Mời đăng nhập.', 'success')
    }
  } catch (err) {
    errorMsg.value = err.response?.data?.error || 'Đã có lỗi xảy ra'
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.auth-view {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-xl);
}

.auth-container {
  width: 100%;
  max-width: 420px;
}

.auth-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow-lg);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.auth-title {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: var(--spacing-xs);
}

.auth-subtitle {
  color: var(--color-text-secondary);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
}

.form-label {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--color-text-secondary);
}

.form-input {
  padding: var(--spacing-md);
  background: var(--color-bg-primary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  transition: border-color var(--transition-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.form-input::placeholder {
  color: var(--color-text-secondary);
  opacity: 0.7;
}

.error-alert {
  padding: var(--spacing-md);
  background: rgba(204, 41, 54, 0.1);
  border: 1px solid var(--color-danger);
  border-radius: var(--radius-md);
  color: var(--color-danger);
  font-size: var(--font-size-sm);
  text-align: center;
}

.btn-submit {
  padding: var(--spacing-md);
  background: var(--color-primary);
  border-radius: var(--radius-md);
  color: var(--color-text-primary);
  font-size: var(--font-size-base);
  font-weight: 600;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
  min-height: 48px;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-primary-light);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 2px solid var(--color-text-secondary);
  border-top-color: var(--color-text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.auth-footer {
  margin-top: var(--spacing-xl);
  text-align: center;
}

.toggle-text {
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
}

.btn-toggle {
  color: var(--color-primary-light);
  font-weight: 600;
  margin-left: var(--spacing-xs);
}

.btn-toggle:hover {
  text-decoration: underline;
}
</style>