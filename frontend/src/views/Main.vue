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
      </div>
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
            <div class="level">
              <b-switch v-model="includeSkipped">Include skipped</b-switch>
            </div>
          </div>
        </div>
        <table class="table is-fullwidth">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Video Name</th>
              <th>Total Annotations</th>
              <th>Your Annotations</th>
              <th>Objects</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="video in videos" :key="video.id" :class="{
              'is-annotated': video.n_user_annotations > 0,
              'is-skipped': video.skip}">
              <td>{{ video.dataset }}</td>
              <td>{{ video.name }}</td>
              <td>{{ video.n_annotations }}</td>
              <td>{{ video.n_user_annotations }}</td>
              <td>{{ video.n_objects }}</td>
              <td class="has-addons">
                <router-link :to="'annotate/' + video.id"
                             class="button is-primary is-small">Annotate</router-link>
              </td>
            </tr>
          </tbody>
        </table>
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
      includeSkipped: false
    }
  },

  methods: {
    startAnnotating () {
      let batch = this.videos.slice(this.startIdx)
      if (!this.includeSkipped) batch = batch.filter(v => !v.skip)
      this.$router.push({
        name: 'annotate',
        params: {
          videoId: batch[0].id,
          idx: 0,
          videos: batch
        }
      })
    }
  },

  created () {
    API.get('videos')
      .then(response => {
        this.videos = response.data
      })
      .catch(e => {
        console.log(e)
      })

    API.get('summary')
      .then(response => {
        this.stats = response.data
      }).catch(e => console.log(e))
  }
}
</script>
