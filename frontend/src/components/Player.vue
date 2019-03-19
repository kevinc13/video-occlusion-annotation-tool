<template>
  <div class="columns">
    <div class="column is-three-quarters">
      <!-- Output canvas, used for resizing (hidden) -->
      <div ref="canvasWrapper">
        <canvas ref="outputCanvas" style="display: none;" width="1280" height="720"></canvas>
        <div class="canvas-layers" :style="{ 'width': width + 'px', 'height': height + 'px' }">
          <canvas ref="videoCanvas" id="videoCanvas"
            :width="width" :height="height"></canvas>
          <canvas ref="segmentationCanvas" id="segmentationCanvas"
            :width="width" :height="height" v-show="showSegmentations"></canvas>
          <canvas ref="annotationCanvas" id="annotationCanvas" :width="width" :height="height"
            @mousedown="onMouseDown" @mousemove="onMouseMove"
            @mouseup="endPaintEvent" @mouseleave="endPaintEvent"></canvas>
        </div><!-- ./canvas-layers -->
      </div>
      <!-- Playback information -->
      <div class="level">
        <div class="level-left">
          <p>Frame: {{ this.currentFrame }} | Sequence Number: {{ currentSequenceNumber }}</p>
        </div>
        <div class="level-right">
          <p>Total Frames: {{ this.frames.length }}</p>
        </div>
      </div>

      <!-- Playback controls -->
      <div class="level">
        <div class="level-left">
          <div class="level-item has-addons">
            <button class="button is-light"
                v-shortkey="['shift', '{']"
                @shortkey="stepBackward(5)"
                @click="stepBackward(5)">
              <span class="icon">
                <i class="fas fa-backward"></i>
              </span>
            </button>
            <button class="button is-light"
                v-shortkey="['[']"
                @shortkey="stepBackward(1)"
                @click="stepBackward(1)">
              <span class="icon">
                <i class="fas fa-step-backward"></i>
              </span>
            </button>
            <button class="button is-light" @click="pause" v-show="!isAnnotating">
              <span class="icon">
                <i class="fas fa-pause"></i>
              </span>
            </button>
            <button class="button is-light" @click="play" v-show="!isAnnotating">
              <span class="icon">
                <i class="fas fa-play"></i>
              </span>
            </button>
            <button class="button is-light"
                v-shortkey="[']']"
                @shortkey="stepForward(1)"
                @click="stepForward(1)">
              <span class="icon">
                <i class="fas fa-step-forward"></i>
              </span>
            </button>
            <button class="button is-light"
                v-shortkey="['shift', '}']"
                @shortkey="stepForward(5)"
                @click="stepForward(5)">
              <span class="icon">
                <i class="fas fa-forward"></i>
              </span>
            </button>
            <button class="button is-light" @click="reset" v-show="!isAnnotating">
              <span class="icon">
                <i class="fas fa-undo"></i>
              </span>
            </button>
          </div><!-- ./level-item ./buttons -->
          <div class="level-item">
            <button class="button is-light"
              v-shortkey.once="['t']"
              @shortkey="toggleSegmentations"
              @click="toggleSegmentations">Toggle Segmentations (t)</button>
          </div>
        </div><!-- ./level-left -->
        <div class="level-right">
          <button class="button is-primary"
                  v-shortkey.once="['n']"
                  @shortkey="beginAnnotating"
                  @click="beginAnnotating"
                  v-show="!isAnnotating">New Annotation (n)</button>
        </div><!-- ./level-right -->
      </div><!-- ./level -->

      <div class="level" v-show="isAnnotating">
        <div class="level-left">
          <div class="level-item">
            <b-select placeholder="Object" v-model="selectedObject">
              <option :value="obj" v-for="obj in video.segmented_objects" :key="obj.id">
                ID: {{ obj.id }} | {{ obj.name }} | {{ obj.color }}
              </option>
            </b-select>
          </div><!-- ./level-item -->
          <div class="level-item">
            <input type="range" min="1" max="100" v-model="brushSize">
          </div>
        </div><!-- ./level-left -->
        <div class="level-right">
          <div class="level-item">
            <button class="button is-light" v-shortkey.once="['c']"
              @shortkey="clearAnnotationCanvas"
              @click="clearAnnotationCanvas">Clear (c)</button>
          </div><!-- ./level-item -->
          <div class="level-item">
            <button class="button is-light" v-shortkey.once="['esc']"
              @shortkey="stopAnnotating"
              @click="stopAnnotating">Exit (esc)</button>
          </div>
          <button class="button is-primary"
            v-shortkey.once="['s']"
            @shortkey="saveAnnotation"
            @click="saveAnnotation"
            :disabled="!hasPainted || selectedObject == null || selectedObject.color == null">Save (s)</button>
        </div><!-- ./level-right -->
      </div><!-- ./level -->
    </div><!-- ./column -->

    <div class="column">
      <header class="subtitle">Frame Annotations ({{ currentAnnotations.length }})</header>
      <table class="table" v-if="currentAnnotations.length > 0">
        <thead>
          <td>Username</td>
          <td>Object</td>
          <td>Actions</td>
        </thead>
        <tbody>
          <tr v-for="annotation in currentAnnotations" :key="annotation.id">
            <td>{{ annotation.user.username }}</td>
            <td>{{ annotation.segmented_object.name }} - {{ annotation.segmented_object.id }}</td>
            <td class="has-addons">
              <button v-if="annotation.user.id == user.id"
                    class="button is-small is-danger" @click="removeAnnotation(annotation.id)">Remove</button>
              <a v-else :href="annotation.path" class="button is-small">Link</a>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No annotations found</p>
    </div><!-- ./column -->

  </div><!-- ./player -->
</template>

<style scoped>
.canvas-layers {
  position: relative;
  margin-bottom: 0.5rem;
}
.canvas-layers canvas {
  position: absolute;
  left: 0;
  top: 0;
}
#videoCanvas { z-index: 0; }
#segmentationCanvas {
  z-index: 1;
  opacity: 0.7;
}
#annotationCanvas { z-index: 2; }
</style>

<script>
import _ from 'lodash'
import { API } from '@/api'

export default {
  name: 'Player',
  props: {
    'user': { type: Object, default: {} },
    'video': { type: Object, default: {} }
  },
  data () {
    return {
      width: 853.33, // Default width
      height: 480, // Default height
      outputCanvasContext: null,
      videoCanvasContext: null,
      annotationCanvasContext: null,

      frames: [], // video frames
      currentFrame: 0, // current frame
      rate: 10, // playback framerate
      paused: true, // whether video is paused
      showSegmentations: false, // whether to show segmentation overlay
      showAnnotations: false, // whether to show annotation overlay
      animationFrameRequest: null, // window animation frame request

      isAnnotating: false, // whether we are in annotation mode
      brushSize: 20, // brush size of annotation
      isPainting: false,
      hasPainted: false,
      position: {
        offsetX: 0,
        offsetY: 0
      },
      line: [],
      selectedObject: null
    }
  },

  computed: {
    currentSequenceNumber () {
      return (this.frames.length > 0) ? this.frames[this.currentFrame].sequence_number : 0
    },
    currentAnnotations () {
      return (this.frames.length > 0) ? this.frames[this.currentFrame].occlusion_annotations : []
    },
    brushColor () {
      if (this.selectedObject != null && this.selectedObject.color != null) {
        return this.selectedObject.color
      } else {
        return null
      }
    },
    hasUserAnnotation () {
      return this.currentAnnotations.filter(a => {
        return a.user.id === this.user.id
      }).length > 0
    },
    ready () {
      return {
        userReady: !_.isEmpty(this.user),
        videoReady: !_.isEmpty(this.video)
      }
    }
  },

  watch: {
    ready (newVal, _) {
      if (newVal.userReady && newVal.videoReady) {
        this.frames = this.video.frames.slice().sort((a, b) => {
          return a.sequence_number - b.sequence_number
        })
        if (this.frames.length > 0) this.reset()
      }
    },

    selectedObject () { this.clearAnnotationCanvas() }
  },

  methods: {
    /* Annotation mode methods  */
    beginAnnotating () {
      if (!this.paused) this.pause()
      this.isAnnotating = true
    },
    stopAnnotating () {
      this.clear(this.annotationCanvasContext)
      this.isAnnotating = false
    },
    saveAnnotation () {
      if (!this.isAnnotating || this.selectedObject == null || this.selectedObject.color == null) return

      this.clear(this.outputCanvasContext)
      this.outputCanvasContext.drawImage(
        this.$refs.annotationCanvas, 0, 0,
        this.$refs.outputCanvas.width, this.$refs.outputCanvas.height)
      let annotationImg = this.$refs.outputCanvas.toDataURL('image/png')
      API.post('annotations/', {
        frame: this.frames[this.currentFrame].id,
        file: annotationImg,
        segmented_object_id: this.selectedObject.id
      }).then(response => {
        this.frames[this.currentFrame].occlusion_annotations.push(response.data)
        this.clear(this.annotationCanvasContext)
        // this.stepForward(1)
      }).catch(e => {
        console.log(e)
      })
    },
    removeAnnotation (id) {
      API.delete(`annotations/${id}`)
        .then(response => {
          this.frames[this.currentFrame].occlusion_annotations = this.frames[this.currentFrame].occlusion_annotations.filter(a => {
            return a.id !== id
          })
          this.clear(this.annotationCanvasContext)
        }).catch(e => {
          console.log(e)
        })
    },
    clear (context) { context.clearRect(0, 0, context.canvas.width, context.canvas.height) },
    clearAnnotationCanvas () {
      this.clear(this.annotationCanvasContext)
      this.hasPainted = false
    },
    onMouseDown (event) {
      if (this.isAnnotating && this.selectedObject != null) {
        const { offsetX, offsetY } = event
        this.hasPainted = true
        this.isPainting = true
        this.position = { offsetX, offsetY }
      }
    },
    endPaintEvent () { if (this.isPainting) this.isPainting = false },
    onMouseMove (event) {
      if (this.isPainting && this.selectedObject != null) {
        const { offsetX, offsetY } = event
        const offSetData = { offsetX, offsetY }
        const positionInfo = {
          start: { ...this.position },
          stop: { ...offSetData }
        }
        this.line = this.line.concat(positionInfo)
        this.paint(offSetData)
      }
    },
    paint (currentPosition) {
      const { offsetX, offsetY } = currentPosition
      const { offsetX: x, offsetY: y } = this.position
      this.annotationCanvasContext.beginPath()
      this.annotationCanvasContext.lineWidth = this.brushSize
      this.annotationCanvasContext.lineJoin = 'round'
      this.annotationCanvasContext.lineCap = 'round'
      this.annotationCanvasContext.strokeStyle = this.brushColor
      this.annotationCanvasContext.moveTo(x, y)
      this.annotationCanvasContext.lineTo(offsetX, offsetY)
      this.annotationCanvasContext.stroke()
      this.position = { offsetX, offsetY }
    },

    /* Playback methods */
    play () {
      if (this.paused && this.frames.length > 0) {
        this.paused = false
        this.render()
        this.drawFrame()
      }
    },
    pause () {
      this.paused = true
      window.cancelAnimationFrame(this.animationFrameRequest)
    },
    reset () { this.goToFrame(0) },
    stepForward (numFrames) { if (this.currentFrame < this.frames.length - numFrames) this.goToFrame(this.currentFrame + numFrames) },
    stepBackward (numFrames) { if (this.currentFrame >= numFrames) this.goToFrame(this.currentFrame - numFrames) },
    goToFrame (frame) {
      this.pause()
      this.currentFrame = frame
      this.drawFrame()
    },

    /* Rendering/drawing methods */
    updateCanvasDimensions (e) {
      this.width = this.$refs.canvasWrapper.clientWidth
      this.height = this.width / 1280 * 720
      if (this.frames.length > 0) this.drawFrame()
    },

    toggleSegmentations () {
      this.showSegmentations = !this.showSegmentations
      if (this.showSegmentations) this.drawSegmentation()
    },

    render () {
      var now
      var then = Date.now()
      var delta
      let interval = 1000 / this.rate
      let numFrames = this.frames.length

      const processFrame = () => {
        now = Date.now()
        delta = now - then

        if (delta > interval) {
          then = now - (delta % interval)
          if (!this.paused) {
            if (this.currentFrame >= numFrames - 1) {
              this.pause()
            } else {
              this.currentFrame += 1
              this.drawFrame()
            }
          }
        }

        this.animationFrameRequest = window.requestAnimationFrame(processFrame)
      }

      this.animationFrameRequest = window.requestAnimationFrame(processFrame)
    },

    drawFrame () {
      let img = new Image()
      let frame = this.frames[this.currentFrame]
      img.src = frame.path
      img.onload = () => {
        this.videoCanvasContext.imageSmoothingEnabled = false
        this.videoCanvasContext.drawImage(
          img, 0, 0, this.width, this.height)
      }

      if (this.showSegmentations && 'frame_segmentation' in frame) this.drawSegmentation()
      this.drawAnnotation()
    },

    drawSegmentation () {
      let segmentationImg = new Image()
      segmentationImg.src = this.frames[this.currentFrame].frame_segmentation.path
      segmentationImg.onload = () => {
        this.segmentationCanvasContext.imageSmoothingEnabled = false
        this.segmentationCanvasContext.drawImage(
          segmentationImg, 0, 0, this.width, this.height)
      }
    },

    drawAnnotation () {
      this.clear(this.annotationCanvasContext)
      let userAnnotation = this.currentAnnotations.filter(a => {
        return a.user.id === this.user.id
      })
      if (userAnnotation.length >= 1) {
        let annotationImg = new Image()
        annotationImg.src = userAnnotation[0].path
        annotationImg.onload = () => {
          this.annotationCanvasContext.drawImage(
            annotationImg, 0, 0, this.width, this.height
          )
        }
      }
    },

    initializeRequestAnimationFrame () {
      // http://paulirish.com/2011/requestanimationframe-for-smart-animating/
      // http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
      // requestAnimationFrame polyfill by Erik Möller. fixes from Paul Irish and Tino Zijdel
      // MIT license

      let lastTime = 0
      const vendors = ['ms', 'moz', 'webkit', 'o']
      for (let x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
        window.requestAnimationFrame = window[`${vendors[x]}RequestAnimationFrame`]
        window.cancelAnimationFrame = window[`${vendors[x]}CancelAnimationFrame`] ||
                                      window[`${vendors[x]}CancelRequestAnimationFrame`]
      }

      if (!window.requestAnimationFrame) {
        window.requestAnimationFrame = (callback, element) => {
          const currTime = new Date().getTime()
          const timeToCall = Math.max(0, 16 - (currTime - lastTime))
          // eslint-disable-next-line
          const id = window.setTimeout(() => { callback(currTime + timeToCall) }, timeToCall)
          lastTime = currTime + timeToCall
          return id
        }
      }

      if (!window.cancelAnimationFrame) window.cancelAnimationFrame = (id) => { clearTimeout(id) }
    }
  },

  mounted () {
    this.outputCanvasContext = this.$refs.outputCanvas.getContext('2d')
    this.videoCanvasContext = this.$refs.videoCanvas.getContext('2d')
    this.segmentationCanvasContext = this.$refs.segmentationCanvas.getContext('2d')
    this.annotationCanvasContext = this.$refs.annotationCanvas.getContext('2d')

    // Setup requestAnimationFrame polyfill
    this.initializeRequestAnimationFrame()
    // Setup correct canvas dimensions
    this.updateCanvasDimensions()
    // Anytime the window size changes, we'll have to update the canvas dimensions
    window.addEventListener('resize', this.updateCanvasDimensions)
  }
}
</script>
