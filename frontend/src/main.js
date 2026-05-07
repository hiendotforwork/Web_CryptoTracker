/**
 * Crypto Tracker - Main Entry Point
 * 
 * Khởi tạo Vue app với router, Pinia, và CSS variables.
 */

// =====================================================
// IMPORTS
// =====================================================
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

// Import CSS
import './assets/styles/main.css'

// =====================================================
// CREATE APP
// =====================================================
const app = createApp(App)

// Use Pinia
app.use(createPinia())

// Use Router
app.use(router)

// Mount
app.mount('#app')