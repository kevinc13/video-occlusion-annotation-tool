<template>
  <section class="section">
    <div class="container is-fluid">
      <h1 class="title">
        Review | Video ({{ idx + 1 }}/{{ Math.max(videos.length, 1) }})
      </h1>
      <div class="box">
        <div class="level">
          <div class="level-left">
            <h1 class="is-size-4">
              Name: <strong>{{ video.name }}</strong> | Dataset: <strong>{{ video.dataset }}</strong>
            </h1>
          </div><!-- ./level-left -->
          <div class="level-right">
            <div class="level-item">
              <b-tooltip label="Video List" type="is-dark">
                <router-link :to="{ name: 'main', query: backQueryParams }" class="button">
                  <i class="fas fa-list"></i>
                </router-link>
              </b-tooltip>
            </div><!-- ./level-item -->
            <div class="level-item">
              <router-link :to="{
                name: 'annotate',
                params: { backQueryParams: backQueryParams, videoId: videoId, videos: videos, idx: idx }
                }" class="button">Annotate</router-link>
            </div><!-- ./level-item -->
            <div class="level-item" v-show="hasNext">
              <router-link :to="{
                name: 'annotate',
                params: { backQueryParams: backQueryParams, videoId: videos[idx + 1].id, videos: videos, idx: idx + 1 }
                }" class="button is-primary">Annotate Next</router-link>
            </div><!-- .level-item -->
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
  name: 'Review',
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
  components: { Player },

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
    hasNext () { return this.idx < this.videos.length - 1 }
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
    }
  },

  mounted () {
    this.getVideo(this.videoId)
  }
}
</script>
