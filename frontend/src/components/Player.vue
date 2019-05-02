<template>
  <div class="guided-player">
    <div class="level" style="flex-wrap: wrap;">
      <div class="buttons">
        <button class="button"
                v-for="(obj, idx) in video.segmented_objects" :key="obj.id"
                @click="selectedObjectIdx = idx"
                :class="{ 'is-active': selectedObjectIdx === idx,
                          'is-white': selectedObjectIdx !== idx }">
          <p style="margin-right:1rem;">
            <strong>{{ obj.color_index }} | {{ obj.name }}</strong>
          </p>
          <div class="color-square" :style="{ 'background-color': obj.color }"></div>
        </button>
      </div><!-- ./buttons -->
    </div><!-- ./level -->
    <div class="columns">
      <div class="column is-three-quarters">
        <!-- Output canvas, used for resizing (hidden) -->
        <div ref="canvasWrapper">
          <div class="canvas-layers" :style="{ 'width': width + 'px', 'height': height + 'px' }">
            <canvas ref="videoCanvas" id="videoCanvas"
              :width="width" :height="height"></canvas>
            <canvas ref="segmentationCanvas" id="segmentationCanvas"
              :width="width" :height="height" v-show="showSegmentations"></canvas>
            <canvas ref="annotationCanvas" id="annotationCanvas"
              :width="width" :height="height"></canvas>
          </div><!-- ./canvas-layers -->
        </div>
        <!-- Playback information -->
        <div class="level">
          <div class="level-left">
            <p>Frame Index: {{ this.currentFrameIdx }} | Sequence Number: {{ currentSequenceNumber }}</p>
          </div>
          <div class="level-right">
            <p>Total Frames: {{ this.frames.length }}</p>
          </div>
        </div><!-- ./level -->

        <!-- Playback controls -->
        <div class="level">
          <div class="level-left">
            <div class="level-item has-addons">
              <button class="button is-light"
                      @click="prev()"
                      :disabled="!hasPrevFrame && !hasPrevObject">
                Prev
              </button>
              <button class="button is-light"
                      @click="next()"
                      :disabled="!hasNextFrame && !hasNextObject">
                Next
              </button>
            </div>
          </div><!-- ./level-left -->
          <div class="level-right">
            <button class="button is-light"
                @click="toggleSegmentations">Toggle Segmentations</button>
          </div><!-- ./level-right -->
        </div><!-- ./level -->
      </div><!-- ./column -->
    </div><!-- ./columns -->
  </div><!-- ./guided-player -->
</template>

<style scoped>
.color-square {
  width: 25px;
  height: 25px;
}
.canvas-layers {
  position: relative;
  margin-bottom: 0.5rem;
  border: 10px solid #ffc107;
  box-sizing: content-box;
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

export default {
  name: 'Player',
  props: {
    'user': { type: Object },
    'video': { type: Object }
  },
  data () {
    return {
      width: 853.33, // Default width
      height: 480, // Default height
      outputCanvasContext: null,
      videoCanvasContext: null,
      annotationCanvasContext: null,
      selectedObjectIdx: 0,

      frames: [], // video frames
      currentFrameIdx: 0, // current frame idx
      stepSize: 3,
      showSegmentations: true, // whether to show segmentation overlay
      animationFrameRequest: null // window animation frame request
    }
  },

  computed: {
    currentFrame () { return (this.frames.length > 0) ? this.frames[this.currentFrameIdx] : null },
    currentSequenceNumber () { return (this.currentFrame) ? this.currentFrame.sequence_number : 0 },
    selectedObject () {
      if (this.video.segmented_objects.length === 0) return {}
      return this.video.segmented_objects[this.selectedObjectIdx]
    },

    hasNextObject () { return this.selectedObjectIdx < this.video.segmented_objects.length - 1 },
    hasPrevObject () { return this.selectedObjectIdx > 0 },

    hasNextFrame () { return this.currentFrameIdx < this.frames.length - this.stepSize },
    hasPrevFrame () { return this.currentFrameIdx >= this.stepSize },

    currentUserAnnotation () {
      if (!this.currentFrame) return null
      let annotation = this.currentFrame.user_occlusion_annotations.filter(a => {
        return a.segmented_object.id === this.selectedObject.id
      })
      return (annotation.length > 0) ? annotation[0] : null
    },
    // currentOcclusionFlag: {
    //   get () {
    //     if (this.currentFrame) {
    //       let flags = this.currentFrame.user_occlusion_flags.filter(f => f.segmented_object_id === this.selectedObject.id)
    //       if (flags.length > 0) {
    //         let flag = flags[0].occluded
    //         if (flag === 0) return 'No'
    //         if (flag === 1) return 'Partially'
    //         if (flag === 2) return 'Fully'
    //       }
    //     }
    //     return 'Not specified'
    //   }
    // },
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
    selectedObject () {
      this.clearAnnotationCanvas()
      this.reset()
    },
    '$route': function () {
      this.currentFrameIdx = 0
      this.selectedObjectIdx = 0
    }
  },

  methods: {
    clear (context) { context.clearRect(0, 0, context.canvas.width, context.canvas.height) },
    clearAnnotationCanvas () {
      this.clear(this.annotationCanvasContext)
      this.hasPainted = false
    },

    /* Playback methods */
    reset () { this.goToFrame(0) },
    nextFrame () { if (this.hasNextFrame) this.goToFrame(this.currentFrameIdx + this.stepSize) },
    prevFrame () { if (this.hasPrevFrame) this.goToFrame(this.currentFrameIdx - this.stepSize) },
    goToFrame (frame) {
      this.currentFrameIdx = frame
      if (this.frames.length > 0) this.drawFrame()
    },

    nextObject () {
      this.selectedObjectIdx++
    },
    prevObject () {
      this.selectedObjectIdx--
    },

    next () {
      if (this.hasNextFrame) {
        this.nextFrame()
      } else if (this.hasNextObject) {
        this.nextObject()
      }
    },
    prev () {
      if (this.hasPrevFrame) {
        this.prevFrame()
      } else if (this.hasPrevObject) {
        this.prevObject()
      }
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

    drawFrame () {
      let img = new Image()
      img.src = this.currentFrame.path
      img.onload = () => {
        this.videoCanvasContext.imageSmoothingEnabled = false
        this.videoCanvasContext.drawImage(
          img, 0, 0, this.width, this.height)
      }

      if (this.showSegmentations) this.drawSegmentation()
      this.drawAnnotation()
    },

    drawSegmentation () {
      let segmentationImg = new Image()
      let segs = this.currentFrame.frame_segmentations.filter(
        s => s.segmented_object_id === this.selectedObject.id)
      if (segs.length === 0) return
      segmentationImg.src = segs[0].path
      segmentationImg.onload = () => {
        this.segmentationCanvasContext.imageSmoothingEnabled = false
        this.segmentationCanvasContext.drawImage(
          segmentationImg, 0, 0, this.width, this.height)
      }
    },

    drawAnnotation () {
      this.clear(this.annotationCanvasContext)
      let annotation = this.currentFrame.user_occlusion_annotations.filter(a => {
        return a.segmented_object.id === this.selectedObject.id
      })
      if (annotation.length >= 1) {
        let annotationImg = new Image()
        let d = new Date()
        annotationImg.src = annotation[0].path + '?cache=' + d.getTime()
        annotationImg.onload = () => {
          this.annotationCanvasContext.drawImage(
            annotationImg, 0, 0, this.width, this.height
          )
        }
      }
    },

    handleKeyEvents (e) {
      if (e.shiftKey && e.key === ' ') {
        e.preventDefault()
        this.prev()
      } else if (!e.shiftKey && e.key === ' ') {
        e.preventDefault()
        this.next()
      }
    }
  },

  mounted () {
    this.videoCanvasContext = this.$refs.videoCanvas.getContext('2d')
    this.segmentationCanvasContext = this.$refs.segmentationCanvas.getContext('2d')
    this.annotationCanvasContext = this.$refs.annotationCanvas.getContext('2d')

    this.annotationCanvasContext.imageSmoothingEnabled = false

    // Setup requestAnimationFrame polyfill
    // this.initializeRequestAnimationFrame()
    // Setup correct canvas dimensions
    this.updateCanvasDimensions()
  },

  activated () {
    window.addEventListener('resize', this.updateCanvasDimensions)
    window.addEventListener('keydown', this.handleKeyEvents)
  },

  deactivated () {
    window.removeEventListener('resize', this.updateCanvasDimensions)
    window.removeEventListener('keydown', this.handleKeyEvents)
  }
}
</script>
