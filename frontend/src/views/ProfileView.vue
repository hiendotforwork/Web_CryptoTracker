<!--
  ProfileView.vue — Trang quản lý tài khoản cá nhân

  What: Cho phép người dùng đổi mật khẩu, đổi username, hoặc xóa tài khoản
  Why:  Các thao tác nhạy cảm cần xác nhận bằng mật khẩu hiện tại để đảm bảo bảo mật
  How:  3 section độc lập, mỗi form gọi action tương ứng trong auth store
-->
<template>
  <main class="profile-page">
    <div class="container">

      <!-- Page Header -->
      <div class="page-header">
        <div class="page-header-icon">
          <UserIcon />
        </div>
        <div>
          <h1 class="page-title">Tài khoản</h1>
          <p class="page-subtitle">Xin chào, <strong>{{ user?.username }}</strong></p>
        </div>
      </div>

      <div class="profile-sections">

        <!-- ── Section 1: Đổi mật khẩu ─────────────────────────── -->
        <section class="profile-card">
          <h2 class="card-title">
            <LockIcon class="card-icon" />
            Đổi mật khẩu
          </h2>

          <form @submit.prevent="submitChangePassword" class="profile-form" novalidate>
            <div class="form-group">
              <label for="cp-current" class="form-label">Mật khẩu hiện tại</label>
              <input
                id="cp-current"
                v-model="changePasswordForm.current"
                type="password"
                class="form-input"
                :class="{ 'input-error': passwordError }"
                placeholder="Nhập mật khẩu hiện tại"
                autocomplete="current-password"
                required
              />
            </div>
            <div class="form-group">
              <label for="cp-new" class="form-label">Mật khẩu mới</label>
              <input
                id="cp-new"
                v-model="changePasswordForm.newPass"
                type="password"
                class="form-input"
                :class="{ 'input-error': passwordError }"
                placeholder="Tối thiểu 6 ký tự"
                autocomplete="new-password"
                required
              />
            </div>
            <div class="form-group">
              <label for="cp-confirm" class="form-label">Xác nhận mật khẩu mới</label>
              <input
                id="cp-confirm"
                v-model="changePasswordForm.confirm"
                type="password"
                class="form-input"
                :class="{ 'input-error': passwordError }"
                placeholder="Nhập lại mật khẩu mới"
                autocomplete="new-password"
                required
              />
            </div>

            <p v-if="passwordError" class="form-error" role="alert">{{ passwordError }}</p>
            <p v-if="passwordSuccess" class="form-success" role="status">{{ passwordSuccess }}</p>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="passwordLoading"
              aria-label="Lưu mật khẩu mới"
            >
              <span v-if="passwordLoading" class="btn-spinner" aria-hidden="true"></span>
              <span>{{ passwordLoading ? 'Đang lưu...' : 'Lưu mật khẩu mới' }}</span>
            </button>
          </form>
        </section>

        <!-- ── Section 2: Đổi tên đăng nhập ────────────────────── -->
        <section class="profile-card">
          <h2 class="card-title">
            <PenIcon class="card-icon" />
            Đổi tên đăng nhập
          </h2>

          <form @submit.prevent="submitChangeUsername" class="profile-form" novalidate>
            <div class="form-group">
              <label for="cu-new" class="form-label">Tên đăng nhập mới</label>
              <input
                id="cu-new"
                v-model="changeUsernameForm.newUsername"
                type="text"
                class="form-input"
                :class="{ 'input-error': usernameError }"
                placeholder="3–50 ký tự"
                autocomplete="username"
                required
              />
            </div>
            <div class="form-group">
              <label for="cu-pass" class="form-label">Mật khẩu xác nhận</label>
              <input
                id="cu-pass"
                v-model="changeUsernameForm.password"
                type="password"
                class="form-input"
                :class="{ 'input-error': usernameError }"
                placeholder="Nhập mật khẩu hiện tại để xác nhận"
                autocomplete="current-password"
                required
              />
            </div>

            <p v-if="usernameError" class="form-error" role="alert">{{ usernameError }}</p>
            <p v-if="usernameSuccess" class="form-success" role="status">{{ usernameSuccess }}</p>

            <button
              type="submit"
              class="btn btn-primary"
              :disabled="usernameLoading"
              aria-label="Lưu tên đăng nhập mới"
            >
              <span v-if="usernameLoading" class="btn-spinner" aria-hidden="true"></span>
              <span>{{ usernameLoading ? 'Đang lưu...' : 'Lưu tên đăng nhập' }}</span>
            </button>
          </form>
        </section>

        <!-- ── Section 3: Xóa tài khoản (Danger Zone) ───────────── -->
        <section class="profile-card danger-zone">
          <h2 class="card-title card-title-danger">
            <TrashIcon class="card-icon" />
            Xóa tài khoản
          </h2>
          <p class="danger-description">
            Hành động này <strong>không thể hoàn tác</strong>. Toàn bộ dữ liệu watchlist
            sẽ bị xóa vĩnh viễn.
          </p>

          <!-- Bước 1: Nút mở form xác nhận -->
          <button
            v-if="!showDeleteConfirm"
            class="btn btn-danger-outline"
            @click="showDeleteConfirm = true"
            aria-label="Mở form xác nhận xóa tài khoản"
          >
            Tôi muốn xóa tài khoản
          </button>

          <!-- Bước 2: Form xác nhận xóa -->
          <form
            v-else
            @submit.prevent="submitDeleteAccount"
            class="profile-form"
            novalidate
          >
            <div class="form-group">
              <label for="da-pass" class="form-label">Nhập mật khẩu để xác nhận</label>
              <input
                id="da-pass"
                v-model="deleteAccountForm.password"
                type="password"
                class="form-input input-danger"
                :class="{ 'input-error': deleteError }"
                placeholder="Mật khẩu hiện tại"
                autocomplete="current-password"
                required
              />
            </div>

            <p v-if="deleteError" class="form-error" role="alert">{{ deleteError }}</p>

            <div class="btn-group">
              <button
                type="submit"
                class="btn btn-danger"
                :disabled="deleteLoading"
                aria-label="Xác nhận xóa tài khoản"
              >
                <span v-if="deleteLoading" class="btn-spinner" aria-hidden="true"></span>
                <span>{{ deleteLoading ? 'Đang xóa...' : 'Xác nhận xóa tài khoản' }}</span>
              </button>
              <button
                type="button"
                class="btn btn-secondary"
                @click="cancelDelete"
                aria-label="Hủy bỏ xóa tài khoản"
              >
                Hủy
              </button>
            </div>
          </form>
        </section>

      </div>
    </div>
  </main>
</template>

<script setup>
/**
 * ProfileView — Quản lý tài khoản
 *
 * Composition API: 3 form section hoàn toàn độc lập về state.
 * Mỗi form có isLoading, error, success riêng để tránh UI lẫn lộn.
 */
import { ref, h } from 'vue'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

// Inline SVG icon components (nhất quán với cách App.vue định nghĩa icon)
const UserIcon = {
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('path', { d: 'M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2' }),
    h('circle', { cx: '12', cy: '7', r: '4' })
  ])
}
const LockIcon = {
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('rect', { x: '3', y: '11', width: '18', height: '11', rx: '2', ry: '2' }),
    h('path', { d: 'M7 11V7a5 5 0 0 1 10 0v4' })
  ])
}
const PenIcon = {
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('path', { d: 'M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7' }),
    h('path', { d: 'M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z' })
  ])
}
const TrashIcon = {
  render: () => h('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': '2', 'stroke-linecap': 'round', 'stroke-linejoin': 'round' }, [
    h('polyline', { points: '3 6 5 6 21 6' }),
    h('path', { d: 'M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6' }),
    h('path', { d: 'M10 11v6' }),
    h('path', { d: 'M14 11v6' }),
    h('path', { d: 'M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2' })
  ])
}

const router = useRouter()
const authStore = useAuthStore()
// storeToRefs giữ nguyên reactivity của user ref từ Pinia store
const { user } = storeToRefs(authStore)

// ── Section 1: Đổi mật khẩu ──────────────────────────────────
const changePasswordForm = ref({ current: '', newPass: '', confirm: '' })
const passwordLoading = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

async function submitChangePassword() {
  passwordError.value = ''
  passwordSuccess.value = ''

  const { current, newPass, confirm } = changePasswordForm.value

  if (!current || !newPass || !confirm) {
    passwordError.value = 'Vui lòng điền đầy đủ tất cả các trường'
    return
  }
  if (newPass.length < 6) {
    passwordError.value = 'Mật khẩu mới phải ít nhất 6 ký tự'
    return
  }
  if (newPass !== confirm) {
    passwordError.value = 'Mật khẩu mới và xác nhận không khớp'
    return
  }

  passwordLoading.value = true
  try {
    await authStore.changePassword(current, newPass)
    passwordSuccess.value = 'Đổi mật khẩu thành công!'
    changePasswordForm.value = { current: '', newPass: '', confirm: '' }
  } catch (err) {
    passwordError.value = err.response?.data?.error || 'Đã có lỗi xảy ra, vui lòng thử lại'
  } finally {
    passwordLoading.value = false
  }
}

// ── Section 2: Đổi username ───────────────────────────────────
const changeUsernameForm = ref({ newUsername: '', password: '' })
const usernameLoading = ref(false)
const usernameError = ref('')
const usernameSuccess = ref('')

async function submitChangeUsername() {
  usernameError.value = ''
  usernameSuccess.value = ''

  const { newUsername, password } = changeUsernameForm.value

  if (!newUsername || !password) {
    usernameError.value = 'Vui lòng điền đầy đủ tất cả các trường'
    return
  }
  if (newUsername.length < 3 || newUsername.length > 50) {
    usernameError.value = 'Username phải từ 3 đến 50 ký tự'
    return
  }

  usernameLoading.value = true
  try {
    const result = await authStore.changeUsername(newUsername, password)
    usernameSuccess.value = `Đổi thành công! Tên đăng nhập mới: ${result.user.username}`
    changeUsernameForm.value = { newUsername: '', password: '' }
  } catch (err) {
    usernameError.value = err.response?.data?.error || 'Đã có lỗi xảy ra, vui lòng thử lại'
  } finally {
    usernameLoading.value = false
  }
}

// ── Section 3: Xóa tài khoản ─────────────────────────────────
const showDeleteConfirm = ref(false)
const deleteAccountForm = ref({ password: '' })
const deleteLoading = ref(false)
const deleteError = ref('')

function cancelDelete() {
  showDeleteConfirm.value = false
  deleteAccountForm.value = { password: '' }
  deleteError.value = ''
}

async function submitDeleteAccount() {
  deleteError.value = ''

  if (!deleteAccountForm.value.password) {
    deleteError.value = 'Vui lòng nhập mật khẩu để xác nhận'
    return
  }

  deleteLoading.value = true
  try {
    await authStore.deleteAccount(deleteAccountForm.value.password)
    // authStore.deleteAccount() đã gọi logout() bên trong
    router.push('/auth')
  } catch (err) {
    deleteError.value = err.response?.data?.error || 'Đã có lỗi xảy ra, vui lòng thử lại'
  } finally {
    deleteLoading.value = false
  }
}
</script>

<style scoped>
/* ── Layout ─────────────────────────────────────────────────── */
.profile-page {
  min-height: 100vh;
  padding: 2rem 0 4rem;
}

.container {
  max-width: 640px;
  margin: 0 auto;
  padding: 0 1rem;
}

/* ── Page Header ─────────────────────────────────────────────── */
.page-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 2rem;
}

.page-header-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--color-accent, #cc2936), var(--color-primary, #1a3a5c));
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--color-text, #ffffff);
  margin: 0 0 0.25rem;
}

.page-subtitle {
  font-size: 0.9rem;
  color: var(--color-text-muted, #a0b4c8);
  margin: 0;
}

/* ── Profile Sections ────────────────────────────────────────── */
.profile-sections {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.profile-card {
  background: rgba(26, 58, 92, 0.4);
  border: 1px solid rgba(204, 41, 54, 0.3);
  border-radius: 12px;
  padding: 1.5rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text, #ffffff);
  margin: 0 0 1.25rem;
}

.card-icon {
  width: 1.1rem;
  height: 1.1rem;
  color: var(--color-accent, #cc2936);
}

/* ── Form ────────────────────────────────────────────────────── */
.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.form-label {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted, #a0b4c8);
}

.form-input {
  background: rgba(10, 22, 40, 0.6);
  border: 1px solid rgba(204, 41, 54, 0.4);
  border-radius: 8px;
  padding: 0.6rem 0.9rem;
  color: var(--color-text, #ffffff);
  font-size: 0.95rem;
  width: 100%;
  box-sizing: border-box;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent, #cc2936);
}

.form-input.input-error {
  border-color: #e05555;
}

.input-danger {
  border-color: rgba(204, 41, 54, 0.4);
}

.form-error {
  font-size: 0.85rem;
  color: #e05555;
  margin: 0;
}

.form-success {
  font-size: 0.85rem;
  color: #4caf7d;
  margin: 0;
}

/* ── Buttons ─────────────────────────────────────────────────── */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.6rem 1.2rem;
  border-radius: 8px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: opacity 0.2s, background 0.2s;
  align-self: flex-start;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #cc2936, #1a3a5c);
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  opacity: 0.85;
}

.btn-secondary {
  background: rgba(204, 41, 54, 0.2);
  color: #a0b4c8;
  border: 1px solid rgba(204, 41, 54, 0.3);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(204, 41, 54, 0.3);
}

.btn-danger {
  background: #c0392b;
  color: #fff;
}

.btn-danger:hover:not(:disabled) {
  background: #a93226;
}

.btn-danger-outline {
  background: transparent;
  color: #e05555;
  border: 1px solid rgba(204, 41, 54, 0.5);
}

.btn-danger-outline:hover {
  background: rgba(204, 41, 54, 0.1);
}

.btn-group {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* ── Danger Zone ─────────────────────────────────────────────── */
.danger-zone {
  border-color: rgba(204, 41, 54, 0.25);
}

.card-title-danger {
  color: #e05555;
}

.card-title-danger .card-icon {
  color: #e05555;
}

.danger-description {
  font-size: 0.9rem;
  color: var(--color-text-muted, #a0b4c8);
  margin: 0 0 1.25rem;
  line-height: 1.5;
}

/* ── Spinner ─────────────────────────────────────────────────── */
.btn-spinner {
  width: 0.9rem;
  height: 0.9rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
