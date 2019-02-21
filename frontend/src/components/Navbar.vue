<template>
  <nav class="navbar is-light" role="navigation" aria-label="main navigation">
    <div class="container is-fluid">
      <div class="navbar-brand">
        <a href="/" class="navbar-item"><span class="is-size-5">Vondrick Lab | Video Occlusion Annotation Tool</span></a>
      </div><!-- end navbar-brand -->

      <div class="navbar-menu">
        <div class="navbar-end">
          <div class="navbar-item has-dropdown is-hoverable">
            <a class="navbar-link">{{ user.username }}</a>
            <div class="navbar-dropdown is-right">
              <a href="/logout" class="navbar-item">Sign Out</a>
            </div><!-- end navbar-dropdown -->
          </div><!-- end navbar-item -->
        </div><!-- end navbar-end -->
      </div><!-- end navbar-menu -->

      <div class="navbar-burger">
        <span></span>
        <span></span>
        <span></span>
      </div><!-- end navbar burger -->
    </div><!-- end container -->
  </nav>
</template>

<script>
export default {
  name: 'Navbar',
  props: ['user']
}
</script>

<style scoped>
.navbar > .container { padding: 0 20px; }
</style>
