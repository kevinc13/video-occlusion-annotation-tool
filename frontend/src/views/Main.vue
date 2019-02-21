<template>
  <section class="section">
    <div class="container is-fluid">
      <div class="box">
        <nav class="level">
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Users</p>
              <p class="title">1</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Datasets</p>
              <p class="title">2</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Videos</p>
              <p class="title">2</p>
            </div>
          </div>
          <div class="level-item has-text-centered">
            <div>
              <p class="heading">Occlusion Annotations</p>
              <p class="title">0</p>
            </div>
          </div>
        </nav>
      </div>
      <div class="box">
        <h1 class="title">Video List</h1>
        <table class="table is-fullwidth">
          <thead>
            <tr>
              <th>Dataset</th>
              <th>Video ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="video in videos" :key="video.id">
              <td>{{ video.dataset }}</td>
              <td>{{ video.id }}</td>
              <td>
                <router-link :to="'annotate/' + video.id" class="button is-primary is-small">Annotate</router-link>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </section>
</template>

<script>
import { API } from '@/api'
export default {
  name: 'Main',
  props: ['user'],

  data () {
    return {
      videos: []
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
  }
}
</script>
