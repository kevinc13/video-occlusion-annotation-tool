<template>
  <section class="section">
    <div class="container is-fluid">
      <div class="box">
        <div class="level">
          <div class="level-left">
            <h1 class="is-size-3">
              Video: <strong>{{ video.name }}</strong> | Dataset: <strong>{{ video.dataset }}</strong>
            </h1>
          </div><!-- ../level-left -->
          <div class="level-right">
            <div class="level-item">
              <router-link :to="{ name: 'main', query: backQueryParams }" class="button">Video List</router-link>
            </div><!-- ./level-item -->
            <div class="level-item">
              <button class="button is-danger"
                v-if="!video.skip"
                v-shortkey="['x']"
                @shortkey="setVideoSkipStatus(true)"
                @click="setVideoSkipStatus(true)">Skip [X]</button>
              <button class="button"
                v-else
                v-shortkey="['u']"
                @shortkey="setVideoSkipStatus(false)"
                @click="setVideoSkipStatus(false)">Un-skip [U]</button>
            </div><!-- ./level-item -->
            <div class="buttons has-addons">
              <button class="button"
                v-show="hasPrev"
                v-shortkey="['arrowleft']"
                @shortkey="prevVideo"
                @click="prevVideo">Prev Video (&leftarrow;)</button>
              <button class="button"
                v-show="hasNext"
                v-shortkey="['arrowright']"
                @shortkey="nextVideo"
                @click="nextVideo">Next Video (&rightarrow;)</button>
            </div>
          </div><!-- ./level-right -->
        </div><!-- ./level -->
        <div class="skipped-overlay" v-show="video.skip">
          <h1 class="has-text-centered has-text-weight-bold is-size-3">Skipped</h1>
        </div>
        <guided-player :user="user" :video="video" v-show="!loading"></guided-player>
      </div><!-- ./box -->
    </div><!-- ./container -->
  </section>
</template>

<style scoped>
.skipped-overlay {
  background-color: rgba(255, 255, 255, 0.95);
  position: absolute;
  z-index: 999;
  top: 5rem;
  right: 1.25rem;
  left: 1.25rem;
  bottom: 1.25rem;
  padding-top: 10rem;
}
</style>

<script>
import { API } from '@/api'
import GuidedPlayer from '@/components/GuidedPlayer'

export default {
  name: 'Annotate',
  props: {
    user: { type: Object },
    idx: {
      type: Number,
      default: () => { return 0 }
    },
    videoId: {
      type: Number
    },
    videos: {
      type: Array,
      default: () => { return [] }
    },
    backQueryParams: {
      type: Object,
      default: () => { return {} }
    }
  },
  components: { GuidedPlayer },

  data () {
    return {
      video: {
        id: -1,
        dataset: '',
        frames: [],
        segmented_objects: []
      },
      loading: false
    }
  },

  watch: {
    videoId (to) {
      this.getVideo(to)
    }
  },

  computed: {
    hasNext () { return this.idx < this.videos.length - 1 },
    hasPrev () { return this.idx > 0 }
  },

  methods: {
    getVideo (id) {
      this.loading = true
      API.get(`videos/${id}`)
        .then(response => {
          this.video = response.data
          this.loading = false
        })
        .catch(e => {
          console.log(e)
        })
    },

    prevVideo () {
      if (this.hasPrev) {
        let idx = this.idx - 1
        this.$router.push({
          name: 'annotate',
          params: {
            videoId: this.videos[idx].id,
            idx: idx,
            videos: this.videos
          }
        })
      }
    },
    nextVideo () {
      if (this.hasNext) {
        let idx = this.idx + 1
        this.$router.push({
          name: 'annotate',
          params: {
            videoId: this.videos[idx].id,
            idx: idx,
            videos: this.videos
          }
        })
      }
    },

    setVideoSkipStatus (status) {
      API.patch(`videos/${this.videoId}`, { skip: status })
        .then(response => {
          this.video.skip = status
        })
        .catch(e => console.log(e))
    }
  },

  mounted () {
    this.getVideo(this.videoId)
  }
}
</script>
