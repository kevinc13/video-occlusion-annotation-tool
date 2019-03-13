<template>
  <section class="section">
    <div class="container is-fluid">
      <div class="box">
        <nav class="level">
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Users</p>
              <p class="title">{{ stats.n_users }}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Datasets</p>
              <p class="title">{{ stats.n_datasets }}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Videos</p>
              <p class="title">{{ stats.n_videos }}</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Occlusion Annotations</p>
              <p class="title">{{ stats.n_occlusion_annotations }}</p>
            </div>
          </div>
        </nav>
      </div><!-- ./level -->
      <div class="box">
        <h1 class="title">Video List</h1>
        <div class="level">
          <div class="level-left">
            <div class="level-item">
              <button class="button is-primary" @click="startAnnotating">Start Annotating</button>
            </div>
            <div class="level-item">
              <p style="margin-right: 1em;">From:</p>
              <b-select v-model="startIdx" placeholder="From">
                <option :value="i" v-for="(v, i) in videos" :key="i">
                  {{ v.id }} | {{ v.name }}
                </option>
              </b-select>
            </div>
            <div class="level-item">
              <b-switch v-model="includeSkipped">Include skipped</b-switch>
            </div>
          </div><!-- ./level-left -->
          <div class="level-right">
            <b-dropdown v-model="pagination.limit" position="is-bottom-left">
              <button class="button" slot="trigger">
                <span>Limit: {{ pagination.limit }}</span>
                <span class="icon is-small">
                  <i class="fas fa-angle-down" aria-hidden="true"></i>
                </span>
              </button>
              <b-dropdown-item :value="10">10</b-dropdown-item>
              <b-dropdown-item :value="15">15</b-dropdown-item>
              <b-dropdown-item :value="20">20</b-dropdown-item>
            </b-dropdown>
          </div><!-- ./level-right -->
        </div><!-- ./level -->
        <b-table
          :data="videos"

          paginated
          backend-pagination
          :current-page="requestParams.page"
          :total="pagination.total"
          :per-page="pagination.limit"
          @page-change="onPageChange"

          backend-sorting
          default-sort-direction="asc"
          :default-sort="['id', 'asc']"
          @sort="onSort">
          <template slot-scope="props">
            <b-table-column field="dataset" label="Dataset">
              {{ props.row.dataset }}
            </b-table-column>
            <b-table-column field="id" label="Video ID" sortable>
              {{ props.row.id }}
            </b-table-column>
            <b-table-column field="name" label="Video Name">
              {{ props.row.name }}
            </b-table-column>
            <b-table-column field="n_annotations" label="Total Annotations">
              {{ props.row.n_annotations }}
            </b-table-column>
            <b-table-column field="n_user_annotations" label="Your Annotations" sortable>
              {{ props.row.n_user_annotations }}
            </b-table-column>
            <b-table-column field="n_objects" label="Objects">
              {{ props.row.n_objects }}
            </b-table-column>
            <b-table-column label="Actions">
              <router-link :to="{
                name: 'annotate',
                params: { backQueryParams: requestParams, videoId: props.row.id}
                }" class="button is-primary is-small">Annotate</router-link>
            </b-table-column>
          </template>
        </b-table>
      </div>
    </div>
  </section>
</template>

<style scoped>
.is-annotated { background-color: rgba(35, 209, 96, .2); }
.is-skipped { background-color: rgba(255, 5, 55, .2); }
</style>

<script>
import { API } from '@/api'
export default {
  name: 'Main',
  props: ['user'],

  data () {
    return {
      videos: [],
      stats: {
        n_users: 0,
        n_videos: 0,
        n_datasets: 0,
        n_occlusion_annotations: 0
      },
      startIdx: 0,
      includeSkipped: false,
      requestParams: {
        page: 1,
        ordering: 'id',
        limit: 10
      },
      pagination: {
        total: 0,
        limit: 10
      }
    }
  },

  watch: {
    'pagination.limit': function (val, _) {
      this.requestParams.limit = val
      this.updateQueryParams()
      this.getVideos()
    },
    'stats.n_videos': function (val, _) {
      this.pagination.total = val
    }
  },

  methods: {
    startAnnotating () {
      let batch = this.videos.slice(this.startIdx)
      if (!this.includeSkipped) batch = batch.filter(v => !v.skip)
      this.$router.push({
        name: 'annotate',
        params: {
          backQueryParams: this.requestParams,
          videoId: batch[0].id,
          idx: 0,
          videos: batch
        }
      })
    },

    getVideos () {
      API.get('videos', { params: this.requestParams })
        .then(response => {
          if ('results' in response.data) {
            this.videos = response.data.results
          } else {
            this.videos = response.data
          }
        })
        .catch(e => {
          console.log(e)
        })
    },

    getSummary () {
      API.get('summary')
        .then(response => {
          this.stats = response.data
        }).catch(e => console.log(e))
    },

    onSort (field, order) {
      let direction = (order === 'asc') ? '' : '-'
      this.requestParams.ordering = direction + field
      this.updateQueryParams()
      this.getVideos()
    },

    onPageChange (page) {
      this.requestParams.page = page
      this.updateQueryParams()
      this.getVideos()
    },

    updateQueryParams () {
      this.$router.push({
        name: 'main',
        query: this.requestParams
      })
    }
  },

  created () {
    if ('page' in this.$route.query) this.requestParams.page = Number(this.$route.query.page)
    if ('limit' in this.$route.query) this.requestParams.limit = Number(this.$route.query.limit)

    this.getVideos()
    this.getSummary()
  }
}
</script>
