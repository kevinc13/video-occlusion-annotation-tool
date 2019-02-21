<template>
  <div id="app">
    <navbar :user="user" />
    <keep-alive>
      <router-view :user="user"/>
    </keep-alive>
  </div>
</template>

<script>
import Navbar from '@/components/Navbar'
import { API } from '@/api'

export default {
  name: 'App',

  components: { Navbar },

  data () {
    return {
      user: {}
    }
  },

  methods: {
    getUser () {
      API.get('users/self')
        .then(response => {
          this.user = response.data
        })
        .catch(e => {
          console.log(e)
        })
    }
  },

  created () {
    this.getUser()
  }
}
</script>
