<template>
  <section class="section">
    <div class="container is-fluid">
      <div class="box">
        <div class="level">
          <div class="level-left">
            <h1 class="is-size-3">
              Video ID: <strong>{{ video.id }}</strong> | Dataset: <strong>{{ video.dataset }}</strong>
            </h1>
          </div><!-- ../level-left -->
          <div class="level-right">
            <div class="buttons has-addons">
              <router-link to="/" class="button">Video List</router-link>
              <button class="button">Next Video</button>
            </div>
          </div><!-- ./level-right -->
        </div><!-- ./level -->
        <player :user="user" :video="video" v-show="!loading"></player>
      </div><!-- ./box -->
    </div><!-- ./container -->
  </section>
</template>

<script>
import { API } from '@/api'
import Player from '@/components/Player'

export default {
  name: 'Annotate',
  props: ['user'],
  components: { Player },

  data () {
    return {
      video: {
        id: '',
        dataset: '',
        frames: []
      },
      loading: false
    }
  },

  watch: {
    '$route' (to, old) {
      if ('videoId' in to.params) {
        this.getVideo()
      }
    }
  },

  methods: {
    getVideo () {
      this.loading = true
      API.get(`videos/${this.$route.params.videoId}`)
        .then(response => {
          this.video = response.data
          this.loading = false
        })
        .catch(e => {
          console.log(e)
        })
    }
  },

  mounted () {
    this.getVideo()
  }
}
</script>
