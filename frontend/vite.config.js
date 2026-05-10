import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  test: {
    // Môi trường DOM giả lập — cần thiết để mount Vue component
    environment: 'jsdom',
    // Cho phép dùng describe/it/expect mà không cần import mỗi file
    globals: true,
    // Thừa hưởng alias '@/' từ resolve.alias phía trên
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})