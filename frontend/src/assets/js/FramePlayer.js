/*
    frameplayer.js
    A video player without video files, just JSON. Based on "images frames" thought to mobile devices!

    @author: Vagner Santana
    @link: http://github.com/vagnervjs/frame-video
    @version: 0.2.0
    @since: 04/10/2013
*/

/* eslint-disable */
export default class FramePlayer {
    constructor(el, options) {
        this.divCont = document.getElementById(el)
        this.elem = el
        this.jsonVideoSrc = this.divCont.getAttribute('data-vidsrc')
        this.rate = 20
        this.controls = true
        this.paused = false
        this.width = '480px'
        this.height = '320px'
        this.backwards = false
        this.currentFrame = -1
        this.startFrame = 0
        this.radius = null

        this.setOptions(options)
        this.initializeRequestAnimationFrame()

        this.img = document.createElement('img')
        this.canvas = document.createElement('canvas')
        this.context = this.canvas.getContext('2d')
        this.divCont.appendChild(this.canvas)
    }

    setOptions(options) {
        if ('rate' in options) { this.rate = options.rate }
        if ('controls' in options) { this.controls = options.controls}
        if ('autoplay' in options) { if (!options.autoplay) { this.paused = true } }
        if ('width' in options) { this.width = options.width }
        if ('height' in options) { this.height = options.height }
        if ('startFrame' in options) { this.startFrame = this.currentFrame = options.startFrame }
        if ('backwards' in options) { this.backwards = options.backwards }
        if ('radius' in options) {
            const currentStyle = document.createElement('style')
                currentStyle.setAttribute('id', `style-${this.elem}`);
                currentStyle.innerHTML = `#${this.elem}, .frames-${this.elem}{ border-radius: ${options.radius}; overflow: hidden;}`;
                document.head.appendChild(currentStyle);
        }

        this.divCont.style.width = this.width;
        this.divCont.style.height = this.height;
        
        if(this.controls) {
            this.createControlBar();
        }
    }

    render(player) {
        let now;
        let then = Date.now();
        const interval = 1000/player.rate;
        let delta;
        const videoFramesNum = player.jsonVideoFile.frames.length;

        const processFrame = () => {

            now = Date.now();
            delta = now - then;

            if (delta > interval) {
                then = now - (delta % interval);

                if(!player.paused) {

                    player.currentFrame = (player.backwards) ? player.currentFrame -= 1 : player.currentFrame += 1;

                    if (player.currentFrame >= videoFramesNum) player.currentFrame = 0;
                    else if (player.currentFrame < 0) player.currentFrame = videoFramesNum-1;

                    player.drawFrame(player);
                }
            }

            window.requestAnimationFrame(processFrame);
        };


        window.requestAnimationFrame(processFrame);
    }

    drawFrame(player) {
        player.img.src = player.jsonVideoFile.frames[player.currentFrame];
        player.context.drawImage(player.img, 0, 0, player.canvas.width, player.canvas.height);
    }

    createControlBar() {
        const _self = this;
        const controlBar = document.createElement('div');
        controlBar.setAttribute('class', 'fp-ctrl');
        controlBar.style.width = this.width;

        // Pause Button
        const btnPause = document.createElement('button');
        btnPause.setAttribute('id', `pause-${_self.elem}`);
        btnPause.setAttribute('class', 'fp-btn');
        btnPause.innerHTML = 'Pause';
        btnPause.addEventListener('click', () => {
                _self.pause();
            }, false
        );
        controlBar.appendChild(btnPause);

        // Play Button
        const btnPlay = document.createElement('button');
        btnPlay.setAttribute('id', `play-${_self.elem}`);
        btnPlay.setAttribute('class', 'fp-btn');
        btnPlay.innerHTML = 'Play';
        btnPlay.addEventListener('click', () => {
                _self.resume();
            }, false
        );
        controlBar.appendChild(btnPlay);

        // Backwards Button
        const btnBackwards = document.createElement('button');
        btnBackwards.setAttribute('id', `backwards-${_self.elem}`);
        btnBackwards.setAttribute('class', 'fp-btn');
        btnBackwards.innerHTML = 'Backward';
        btnBackwards.addEventListener('click', () => {
                _self.reverse()
            }, false
        );
        controlBar.appendChild(btnBackwards);

        // Display Play/Pause Button
        _self.paused ? btnPause.style.display = 'none' : btnPlay.style.display = 'none';

        // Filter Select
        const selectFilter = document.createElement('select');

        const options = ['normal', 'grayscale', 'sepia', 'invert'];

        for (let i = 0, t = options.length; i < t; i++) {
            const $option = document.createElement('option');

            $option.setAttribute('value', options[i]);
            $option.innerHTML = options[i];
            selectFilter.appendChild($option);
        }

        selectFilter.setAttribute('id', `filter-${_self.elem}`);
        selectFilter.setAttribute('class', 'fp-select');
        selectFilter.addEventListener('change', function() {
                _self.setFilter(this.value);
            }, false
        );
        controlBar.appendChild(selectFilter);

        const toFrameLabel = document.createElement('label');
        const toFrameInput = document.createElement('input');
        const toFrameSubmit = document.createElement('input');

        toFrameLabel.className =  "to-frame";

        toFrameInput.type = 'text';
        toFrameInput.name = 'frame';
        toFrameInput.value = _self.startFrame;
        toFrameInput.className =  "to-frame";
        _self.toFrameInput = toFrameInput;

        toFrameSubmit.type = 'submit';
        toFrameSubmit.value = 'go to frame';

        toFrameSubmit.onclick = () => {
            value = parseInt(toFrameInput.value, 10)
            _self.gotoFrame(value);
        }

        toFrameLabel.appendChild(toFrameInput);
        toFrameLabel.appendChild(toFrameSubmit);
        controlBar.appendChild(toFrameLabel);

        // Add control bar
        this.divCont.appendChild(controlBar);
    }

    play() {
        this.getFile(this.jsonVideoSrc, player => {
            if (player.paused) {
                player.render(player);
                player.drawFrame(player);
            }else{
                player.render(player);
            }
        });
    }

    resume() {
        const btnPlay = document.getElementById(`play-${this.elem}`);
        const btnPause = document.getElementById(`pause-${this.elem}`);

        btnPlay.style.display = 'none';
        btnPause.style.display = 'block';
        this.paused = false;
    }

    pause() {
        const btnPlay = document.getElementById(`play-${this.elem}`);
        const btnPause = document.getElementById(`pause-${this.elem}`);

        btnPlay.style.display = 'block';
        btnPause.style.display = 'none';
        this.paused = true;
    }

    reverse() {
        const btnBackwards = document.getElementById(`backwards-${this.elem}`);
        this.backwards = !this.backwards;
        value = this.backwards ? 'Forward' :'Backward';
        btnBackwards.innerHTML = value;
    }

    gotoFrame(value) {

        if (value !== parseInt(value, 10)) return;

        this.currentFrame = this.startFrame = this.toFrameInput.value = value;

        if (this.jsonVideoFile === undefined) {
            this.play();
        } else {
            this.drawFrame(this);
        }
    }

    setFilter(filter) {
        const canvas = document.querySelector(`#${this.elem} canvas`);

        switch (filter) {
          case 'normal':
            canvas.setAttribute('class', '');
            break;
          case 'grayscale':
            canvas.setAttribute('class', 'fp-grayscale');
            break;
          case 'sepia':
            canvas.setAttribute('class', 'fp-sepia');
            break;
          case 'invert':
            canvas.setAttribute('class', 'fp-invert');
            break;
          default:
            break;
        }
    }

    getFile(src, callback) {
        let _HTTP = new XMLHttpRequest();
        const _self = this;
        const p = document.createElement('p');

        console.log(_HTTP)
        if (_HTTP) {
            _HTTP.open('GET', src, true);
            _HTTP.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');
            _HTTP.send(null);

            _HTTP.onprogress = () => {
                p.innerHTML = 'Loading...';
                p.setAttribute('class', 'fp-loading');
                _self.divCont.appendChild(p);
            };

            if (typeof(_HTTP.onload) !== undefined) {
                _HTTP.onload = function() {
                    _self.divCont.removeChild(p);
                    _self.jsonVideoFile = JSON.parse(this.responseText)
                    callback(_self);
                    _HTTP = null;
                };
            } else {
                _HTTP.onreadystatechange = function() {
                    if (_HTTP.readyState === 4) {
                        _self.divCont.removeChild(p);
                        _self.jsonVideoFile = JSON.parse(this.responseText)
                        callback(_self);
                        _HTTP = null;
                    }
                };
            }
        } else {
            throw('Error loading file.');
        }
    }

    // Polyfill
    initializeRequestAnimationFrame() {
        // http://paulirish.com/2011/requestanimationframe-for-smart-animating/
        // http://my.opera.com/emoller/blog/2011/12/20/requestanimationframe-for-smart-er-animating
        // requestAnimationFrame polyfill by Erik Möller. fixes from Paul Irish and Tino Zijdel
        // MIT license

        let lastTime = 0;
        const vendors = ['ms', 'moz', 'webkit', 'o'];
        for(let x = 0; x < vendors.length && !window.requestAnimationFrame; ++x) {
            window.requestAnimationFrame = window[`${vendors[x]}RequestAnimationFrame`];
            window.cancelAnimationFrame = window[`${vendors[x]}CancelAnimationFrame`]
                                       || window[`${vendors[x]}CancelRequestAnimationFrame`];
        }

        if (!window.requestAnimationFrame)
            window.requestAnimationFrame = (callback, element) => {
                const currTime = new Date().getTime();
                const timeToCall = Math.max(0, 16 - (currTime - lastTime));
                const id = window.setTimeout(() => { callback(currTime + timeToCall); },
                  timeToCall);
                lastTime = currTime + timeToCall;
                return id;
            };

        if (!window.cancelAnimationFrame)
            window.cancelAnimationFrame = id => {
                clearTimeout(id);
            };
    }
}
