import Vue from 'vue'
import App from './App.vue'
import router from './router'

import './assets/scss/main.scss'

Vue.config.productionTip = false

// Global event bus
window.events = new Vue()

// Flash messages
window.flash = (message, type = 'is-success') => {
  window.events.$emit('flash', { message, type })
}

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')
