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
              <b-tooltip label="[Shift + Space]" position="is-bottom" type="is-dark">
                <button class="button is-light"
                        @click="prev()"
                        :disabled="!hasPrevFrame && !hasPrevObject">
                  Prev
                </button>
              </b-tooltip>
              <b-tooltip label="[Space]" position="is-bottom" type="is-dark">
                <button class="button is-light"
                    @click="next()"
                    :disabled="!hasNextFrame && !hasNextObject">
                  Next
                </button>
              </b-tooltip>
            </div>
          </div><!-- ./level-left -->
          <div class="level-right">
            <button class="button is-light"
                @click="toggleSegmentations">Toggle Segmentations</button>
          </div><!-- ./level-right -->
        </div><!-- ./level -->
      </div><!-- ./column -->

      <div class="column">
        <header class="subtitle">Frame Annotation</header>
        <!-- <label class="label">Occluded?</label>
        <div class="field has-addons">
          <b-radio-button v-model="currentOcclusionFlag" :native-value="0">No</b-radio-button>
          <b-radio-button v-model="currentOcclusionFlag" :native-value="1">Partially</b-radio-button>
          <b-radio-button v-model="currentOcclusionFlag" :native-value="2">Fully</b-radio-button>
        </div> -->
        <div class="field">
          <label class="label">Brush Size</label>
          <input type="range" min="1" max="100" v-model="brushSize">
        </div>
        <button class="button is-light"
            @click="clearAnnotationCanvas" v-if="!currentUserAnnotation">Clear [C]</button>
        <button class="button is-danger"
            @click="removeAnnotation"
            v-else>Remove Annotation</button>
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
  name: 'GuidedPlayer',
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
      showAnnotations: true, // whether to show annotation overlay
      animationFrameRequest: null, // window animation frame request

      brushSize: 20, // brush size of annotation
      isAnnotating: true,
      isPainting: false,
      hasPainted: false,
      position: {
        offsetX: 0,
        offsetY: 0
      },
      line: []
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

    brushColor () {
      if (this.selectedObject != null && this.selectedObject.color != null) {
        return this.selectedObject.color
      } else {
        return null
      }
    },
    // currentOcclusionFlag: {
    //   get () {
    //     if (this.currentFrame) {
    //       let flags = this.currentFrame.user_occlusion_flags.filter(f => f.segmented_object_id === this.selectedObject.id)
    //       if (flags.length > 0) return flags[0].occluded
    //     }
    //     return -1
    //   },
    //   set (newValue) {
    //     let flag = this.currentFrame.user_occlusion_flags.filter(f => f.segmented_object_id === this.selectedObject.id)
    //     if (flag.length >= 1) {
    //       this.updateOcclusionFlag(flag[0].id, newValue)
    //     } else {
    //       this.addOcclusionFlag(newValue)
    //     }
    //   }
    // },
    // isAnnotating () { return this.currentOcclusionFlag > 0 },
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
        if (this.frames.length > 0) this.drawFrame()
      }
    },
    selectedObject () {
      this.clearAnnotationCanvas()
      if (this.frames.length > 0) this.drawFrame()
    },
    '$route': function () {
      this.currentFrameIdx = 0
      this.selectedObjectIdx = 0
    }
  },

  methods: {
    /* Annotation mode methods  */
    // addOcclusionFlag (status) {
    //   API.post(`occlusion_flags/`, {
    //     frame: this.currentFrame.id,
    //     segmented_object_id: this.selectedObject.id,
    //     occluded: status
    //   }).then(response => {
    //     let flag = response.data
    //     this.currentFrame.user_occlusion_flags.push({
    //       id: flag.id,
    //       occluded: flag.occluded,
    //       segmented_object_id: flag.segmented_object_id
    //     })
    //   })
    // },
    // updateOcclusionFlag (flagId, status) {
    //   API.patch(`occlusion_flags/${flagId}`, { occluded: status })
    //     .then(response => {
    //       let flag = this.currentFrame.user_occlusion_flags.find(f => f.id === flagId)
    //       flag.occluded = status
    //     })
    // },
    saveAnnotation () {
      console.log('Saving annotation for frame ' + this.currentFrame.sequence_number)
      this.clear(this.outputCanvasContext)
      this.outputCanvasContext.drawImage(
        this.$refs.annotationCanvas, 0, 0,
        this.$refs.outputCanvas.width, this.$refs.outputCanvas.height)
      let annotationImg = this.$refs.outputCanvas.toDataURL('image/png')
      let currentFrame = this.currentFrame
      API.post('annotations/', {
        frame: this.currentFrame.id,
        file: annotationImg,
        segmented_object_id: this.selectedObject.id
      }).then(response => {
        currentFrame.user_occlusion_annotations.push(response.data)
      }).catch(e => {
        console.log(e)
      })
    },
    updateAnnotation () {
      console.log('Updating annotation for frame ' + this.currentFrame.sequence_number)
      this.clear(this.outputCanvasContext)
      this.outputCanvasContext.drawImage(
        this.$refs.annotationCanvas, 0, 0,
        this.$refs.outputCanvas.width, this.$refs.outputCanvas.height)
      let annotationImg = this.$refs.outputCanvas.toDataURL('image/png')
      let id = this.currentUserAnnotation.id
      API.patch(`annotations/${id}`, {
        file: annotationImg
      }).catch(e => {
        console.log(e)
      })
    },
    removeAnnotation () {
      let annotation = this.currentUserAnnotation
      let currentFrame = this.currentFrame
      if (!_.isEmpty(annotation)) {
        API.delete(`annotations/${annotation.id}`)
          .then(response => {
            currentFrame.user_occlusion_annotations = currentFrame.user_occlusion_annotations.filter(a => {
              return a.id !== annotation.id
            })
            this.clear(this.annotationCanvasContext)
          }).catch(e => {
            console.log(e)
          })
      }
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
    reset () { this.goToFrame(0) },
    nextFrame () { if (this.hasNextFrame) this.goToFrame(this.currentFrameIdx + this.stepSize) },
    prevFrame () { if (this.hasPrevFrame) this.goToFrame(this.currentFrameIdx - this.stepSize) },
    goToFrame (frame) {
      this.currentFrameIdx = frame
      if (this.frames.length > 0) this.drawFrame()
    },

    nextObject () { this.selectedObjectIdx++ },
    prevObject () { this.selectedObjectIdx-- },

    next () {
      if (this.isAnnotating && this.hasPainted) {
        if (this.currentUserAnnotation) {
          this.updateAnnotation()
        } else {
          this.saveAnnotation()
        }
        this.clearAnnotationCanvas()
      }

      if (this.hasNextFrame) {
        this.nextFrame()
      } else if (this.hasNextObject) {
        this.currentFrameIdx = 0
        this.nextObject()
      } else {
        this.$emit('reachedAnnotationEnd')
      }
    },
    prev () {
      if (this.hasPrevFrame) {
        this.prevFrame()
      } else if (this.hasPrevObject) {
        this.currentFrameIdx = this.frames.length - (this.frames.length % this.stepSize)
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
    this.outputCanvasContext = this.$refs.outputCanvas.getContext('2d')
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
