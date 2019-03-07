import Vue from 'vue'
import Router from 'vue-router'
import Main from './views/Main.vue'
import Annotate from './views/Annotate.vue'

Vue.use(Router)

export default new Router({
  routes: [
    {
      path: '/',
      name: 'main',
      component: Main
    },
    {
      path: '/annotate/:videoId',
      name: 'annotate',
      component: Annotate,
      props (route) {
        const props = { ...route.params }
        props.videoId = Number(props.videoId)
        return props
      }
    }
  ]
})
