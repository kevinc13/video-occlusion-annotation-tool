<template>
  <section class="section">
    <div class="container is-fluid">
      <h1 class="title">Annotate Video ({{ idx + 1 }}/{{ Math.max(videos.length, 1) }})</h1>
      <div class="box">
        <div class="level">
          <div class="level-left">
            <h1 class="is-size-4">
              Name: <strong>{{ video.name }}</strong> | Dataset: <strong>{{ video.dataset }}</strong>
            </h1>
          </div>
          <div class="level-right">
            <div class="level-item">
              <b-tooltip label="Video List" type="is-dark">
                <router-link :to="{ name: 'main', query: backQueryParams }" class="button">
                  <i class="fas fa-list"></i>
                </router-link>
              </b-tooltip>
            </div><!-- ./level-item -->
            <div class="level-item" v-show="hasPrev || hasNext">
              <div class="buttons has-addons">
                <b-tooltip label="Previous Video" type="is-dark">
                  <button class="button"
                    v-show="hasPrev"
                    v-shortkey="['arrowleft']"
                    @shortkey="prevVideo"
                    @click="prevVideo">&leftarrow;</button>
                </b-tooltip>
                <b-tooltip label="Next Video" type="is-dark">
                  <button class="button"
                    v-show="hasNext"
                    v-shortkey="['arrowright']"
                    @shortkey="nextVideo"
                    @click="nextVideo">&rightarrow;</button>
                </b-tooltip>
              </div><!-- ./buttons -->
            </div><!-- ./level-item -->
            <div class="level-item">
              <b-tooltip label="[X]" type="is-dark" v-if="!video.skip">
                <button class="button is-danger"
                  v-shortkey="['x']"
                  @shortkey="setVideoSkipStatus(true)"
                  @click="setVideoSkipStatus(true)">Skip</button>
              </b-tooltip>
              <b-tooltip label="[U]" type="is-dark" v-else>
                <button class="button"
                  v-shortkey="['u']"
                  @shortkey="setVideoSkipStatus(false)"
                  @click="setVideoSkipStatus(false)">Un-skip [U]</button>
              </b-tooltip>
            </div><!-- ./level-item -->
            <div class="level-item">
              <router-link :to="{
                name: 'review',
                params: { backQueryParams: backQueryParams, videoId: videoId, videos: videos, idx: idx }
                }" class="button is-success">Review</router-link>
            </div><!-- ./level-item -->
          </div><!-- ./level-right -->
        </div><!-- ./level -->
        <div class="skipped-overlay" v-show="video.skip">
          <h1 class="has-text-centered has-text-weight-bold is-size-3">Skipped</h1>
        </div>
        <guided-player :user="user" :video="video" v-show="!loading"
         @reachedAnnotationEnd="review()"></guided-player>
      </div><!-- ./box -->
    </div><!-- ./container -->
  </section>
</template>

<style scoped>
.skipped-overlay {
  background-color: rgba(255, 255, 255, 0.95);
  position: absolute;
  z-index: 999;
  top: 8rem;
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
    },

    review () {
      this.$router.push({
        name: 'review',
        params: {
          backQueryParams: this.backQueryParams,
          videoId: this.videoId,
          idx: this.idx,
          videos: this.videos
        }
      })
    }
  },

  mounted () {
    this.getVideo(this.videoId)
  }
}
</script>
