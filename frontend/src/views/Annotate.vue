<template>
  <section class="section">
    <div class="container is-fluid">
      <h1 class="tags">
         <span class="tag is-primary is-large">Annotation Mode</span>
         <span class="tag is-light is-large">{{ idx + 1 }} of {{ Math.max(videos.length, 1) }}</span>
      </h1>
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
              <b-tooltip label="This video has no occlusions, skip"
                         type="is-dark" v-if="!hasNoOcclusions">
                <button class="button"
                  @click="addFlag('NO')">No occlusions</button>
              </b-tooltip>
              <b-tooltip label="This video has occlusions, un-skip"
                         type="is-dark" v-else>
                <button class="button"
                  @click="removeFlag('NO')">Has occlusions</button>
              </b-tooltip>
            </div><!-- ./level-item -->
            <div class="level-item">
              <b-tooltip label="I'm unsure about something, skip"
                         type="is-dark" v-if="!isUnsure">
                <button class="button"
                  @click="addFlag('UN')">?</button>
              </b-tooltip>
              <b-tooltip label="I'm no longer unsure, un-skip"
                         type="is-dark" v-else>
                <button class="button"
                  @click="removeFlag('UN')">Un-skip</button>
              </b-tooltip>
            </div><!-- ./level-item -->
            <div class="level-item">
              <router-link :to="{
                name: 'review',
                params: { backQueryParams: backQueryParams, videoId: videoId, videos: videos, idx: idx }
                }" class="button is-warning">Review</router-link>
            </div><!-- ./level-item -->
          </div><!-- ./level-right -->
        </div><!-- ./level -->
        <div class="skipped-overlay" v-show="hasNoOcclusions || isUnsure">
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
        video_flags: [],
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
    hasPrev () { return this.idx > 0 },
    hasNoOcclusions () {
      return Boolean(this.video.video_flags.find(f => f.flag === 'NO'))
    },
    isUnsure () {
      return Boolean(this.video.video_flags.find(f => f.flag === 'UN'))
    }
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

    addFlag (flag) {
      API.post(`video_flags/`, { video_id: this.videoId, flag: flag })
        .then(response => {
          this.video.video_flags.push(response.data)
        })
        .catch(e => console.log(e))
    },

    removeFlag (flagType) {
      let flag = this.video.video_flags.find(f => f.flag === flagType)
      if (flag) {
        API.delete(`video_flags/${flag.id}`)
          .then(response => {
            this.video.video_flags = this.video.video_flags.filter(f => f.id !== flag.id)
          })
          .catch(e => console.log(e))
      }
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
