(function () {
    'use strict';

    const player = document.querySelector('[data-interactive-player]');
    if (!player) {
        return;
    }

    const audio = player.querySelector('[data-audio]');
    const video = player.querySelector('[data-video]');
    const songSelect = player.querySelector('[data-song-select]');
    const movieSelect = player.querySelector('[data-movie-select]');
    const playToggle = player.querySelector('[data-play-toggle]');
    const status = player.querySelector('[data-player-status]');
    let audioSource;
    let effects = [];
    let isSynchronizing = false;
    let shouldKeepPlaying = false;

    function setStatus(message, isError) {
        status.textContent = message;
        status.classList.toggle('interactive__status--error', Boolean(isError));
    }

    function selectedOption(select) {
        return select.options[select.selectedIndex];
    }

    function numericEffectValue(parameters, name, fallback) {
        const value = Number(parameters[name]);
        return Number.isFinite(value) ? value : fallback;
    }

    function disposeEffects() {
        effects.forEach(function (effect) {
            effect.dispose();
        });
        effects = [];
    }

    function createEffects(parameters) {
        if (!window.Tone || !parameters || typeof parameters !== 'object') {
            return;
        }

        const destination = Tone.getDestination();
        let output = destination;
        const nodes = [];

        if (parameters.volume && typeof parameters.volume === 'number') {
            const volume = new Tone.Volume(parameters.volume);
            volume.connect(output);
            output = volume;
            nodes.push(volume);
        }
        if (parameters.reverb && typeof parameters.reverb === 'object') {
            const reverb = new Tone.Reverb(parameters.reverb);
            reverb.connect(output);
            output = reverb;
            nodes.push(reverb);
        }
        if (parameters.delay && typeof parameters.delay === 'object') {
            const delay = new Tone.FeedbackDelay(parameters.delay);
            delay.connect(output);
            output = delay;
            nodes.push(delay);
        }
        if (parameters.filter && typeof parameters.filter === 'object') {
            const filter = new Tone.Filter(parameters.filter);
            filter.connect(output);
            output = filter;
            nodes.push(filter);
        }
        if (parameters.distortion && typeof parameters.distortion === 'object') {
            const distortion = new Tone.Distortion(parameters.distortion);
            distortion.connect(output);
            output = distortion;
            nodes.push(distortion);
        }

        if (nodes.length) {
            Tone.connect(audioSource, output);
            effects = nodes;
        }
    }

    function savedEffectParameters() {
        const option = selectedOption(songSelect);
        try {
            return JSON.parse(option.dataset.effects || '{}');
        } catch (error) {
            setStatus('This song has invalid effect settings; playing it dry.', true);
            return {};
        }
    }

    function rebuildEffects(parameters) {
        disposeEffects();
        if (!window.Tone || !audioSource) {
            return;
        }

        audioSource.disconnect();
        if (parameters === undefined) {
            parameters = savedEffectParameters();
        }
        try {
            createEffects(parameters);
        } catch (error) {
            disposeEffects();
            setStatus('This song has unsupported effect settings; playing it dry.', true);
            return false;
        }
        if (!effects.length) {
            audioSource.connect(Tone.getContext().rawContext.destination);
        }
        return true;
    }

    function initializeAudioGraph() {
        if (!window.Tone || audioSource) {
            return;
        }
        audioSource = Tone.getContext().rawContext.createMediaElementSource(audio);
        rebuildEffects();
    }

    function temporaryEffectParameters() {
        const getValue = function (name) {
            return Number(player.querySelector('[data-effect-input="' + name + '"]').value);
        };
        const parameters = {};
        const volume = getValue('volume');
        const filterType = player.querySelector('[data-effect-input="filter-type"]').value;
        const reverbWet = getValue('reverb-wet');
        const delayWet = getValue('delay-wet');
        const distortionAmount = getValue('distortion-amount');
        const distortionWet = getValue('distortion-wet');

        if (volume !== 0) {
            parameters.volume = volume;
        }
        if (filterType !== 'off') {
            parameters.filter = {
                type: filterType,
                frequency: getValue('filter-frequency'),
                Q: 1,
            };
        }
        if (reverbWet > 0) {
            parameters.reverb = {
                decay: getValue('reverb-decay'),
                wet: reverbWet,
            };
        }
        if (delayWet > 0) {
            parameters.delay = {
                delayTime: getValue('delay-time'),
                feedback: getValue('delay-feedback'),
                wet: delayWet,
            };
        }
        if (distortionAmount > 0 && distortionWet > 0) {
            parameters.distortion = {
                distortion: distortionAmount,
                wet: distortionWet,
            };
        }
        return parameters;
    }

    function savedMovieEffectParameters() {
        const option = selectedOption(movieSelect);
        try {
            return JSON.parse(option.dataset.effects || '{}');
        } catch (error) {
            setStatus('This movie has invalid effect settings; showing it normally.', true);
            return {};
        }
    }

    function movieEffectParameters() {
        const getValue = function (name) {
            return Number(player.querySelector('[data-movie-effect-input="' + name + '"]').value);
        };
        return {
            brightness: getValue('brightness'),
            contrast: getValue('contrast'),
            saturate: getValue('saturate'),
            hue_rotate: getValue('hue_rotate'),
            blur: getValue('blur'),
            sepia: getValue('sepia'),
            grayscale: getValue('grayscale'),
        };
    }

    function applyMovieEffects(parameters) {
        const values = parameters || {};
        const brightness = numericEffectValue(values, 'brightness', 1);
        const contrast = numericEffectValue(values, 'contrast', 1);
        const saturate = numericEffectValue(values, 'saturate', 1);
        const hueRotate = numericEffectValue(values, 'hue_rotate', 0);
        const blur = numericEffectValue(values, 'blur', 0);
        const sepia = numericEffectValue(values, 'sepia', 0);
        const grayscale = numericEffectValue(values, 'grayscale', 0);
        video.style.filter = [
            'brightness(' + brightness + ')',
            'contrast(' + contrast + ')',
            'saturate(' + saturate + ')',
            'hue-rotate(' + hueRotate + 'deg)',
            'blur(' + blur + 'px)',
            'sepia(' + sepia + ')',
            'grayscale(' + grayscale + ')',
        ].join(' ');
    }

    function updateMovieEffectOutput(input) {
        const output = player.querySelector('[data-movie-effect-output="' + input.id + '"]');
        if (!output) {
            return;
        }
        const value = Number(input.value);
        if (input.id === 'movie-effect-hue') {
            output.textContent = value + ' degrees';
        } else if (input.id === 'movie-effect-blur') {
            output.textContent = value.toFixed(1) + ' px';
        } else {
            output.textContent = Math.round(value * 100) + '%';
        }
    }

    function applyTemporaryMovieEffects() {
        applyMovieEffects(movieEffectParameters());
        setStatus('Temporary movie effects active; saved movie settings are unchanged.');
    }

    function updateEffectOutput(input) {
        const output = player.querySelector('[data-effect-output="' + input.id + '"]');
        if (!output) {
            return;
        }
        const value = Number(input.value);
        if (input.id === 'effect-volume') {
            output.textContent = value + ' dB';
        } else if (input.id === 'effect-filter-frequency') {
            output.textContent = value + ' Hz';
        } else if (input.id === 'effect-reverb-decay' || input.id === 'effect-delay-time') {
            output.textContent = value.toFixed(2) + ' s';
        } else {
            output.textContent = Math.round(value * 100) + '%';
        }
    }

    function applyTemporaryEffects() {
        if (rebuildEffects(temporaryEffectParameters())) {
            setStatus('Temporary effects active; saved song settings are unchanged.');
        }
    }

    function syncTime(source) {
        if (isSynchronizing || source !== audio || !Number.isFinite(source.currentTime)
            || video.readyState < 1 || !Number.isFinite(video.duration) || video.duration <= 0) {
            return;
        }
        isSynchronizing = true;
        const videoTime = source.currentTime % video.duration;
        if (Math.abs(video.currentTime - videoTime) > 0.15) {
            video.currentTime = videoTime;
        }
        isSynchronizing = false;
    }

    function syncPlayback(source, shouldPlay) {
        const target = source === audio ? video : audio;
        syncTime(source);
        if (shouldPlay) {
            target.play().catch(function () {
                setStatus('Playback was blocked. Use the play button to start both.', true);
            });
        } else {
            target.pause();
        }
    }

    function updatePlayButton() {
        playToggle.textContent = audio.paused && video.paused ? 'Play together' : 'Pause together';
    }

    function resetPlayback() {
        shouldKeepPlaying = false;
        audio.pause();
        video.pause();
        audio.currentTime = 0;
        video.currentTime = 0;
        updatePlayButton();
    }

    function resumePlayback() {
        if (!shouldKeepPlaying || document.hidden) {
            return;
        }
        const context = window.Tone && Tone.getContext().rawContext;
        const resumeAudio = context && context.state === 'suspended'
            ? context.resume()
            : Promise.resolve();
        resumeAudio.then(function () {
            return Promise.all([audio.play(), video.play()]);
        }).then(updatePlayButton).catch(function () {
            setStatus('Playback paused while the page was unfocused. Press Play together to resume.', true);
        });
    }

    function loadSong() {
        resetPlayback();
        const option = selectedOption(songSelect);
        if (!option.value) {
            audio.removeAttribute('src');
            audio.load();
            playToggle.disabled = true;
            setStatus('Select a song and a movie to begin.');
            return;
        }
        audio.src = option.dataset.audioUrl;
        audio.load();
        initializeAudioGraph();
        rebuildEffects();
        playToggle.disabled = !movieSelect.value;
        setStatus(movieSelect.value ? 'Ready to play together.' : 'Select a movie to complete the pair.');
    }

    function loadMovie() {
        resetPlayback();
        const option = selectedOption(movieSelect);
        if (!option.value) {
            video.removeAttribute('src');
            video.style.removeProperty('filter');
            video.load();
            playToggle.disabled = true;
            setStatus('Select a song and a movie to begin.');
            return;
        }
        video.src = option.dataset.videoUrl;
        video.muted = true;
        video.loop = true;
        applyMovieEffects(savedMovieEffectParameters());
        video.load();
        playToggle.disabled = !songSelect.value;
        setStatus(songSelect.value ? 'Ready to play together.' : 'Select a song to complete the pair.');
    }

    songSelect.addEventListener('change', loadSong);
    movieSelect.addEventListener('change', loadMovie);
    player.querySelectorAll('[data-effect-input]').forEach(function (input) {
        input.addEventListener('input', function () {
            updateEffectOutput(input);
            applyTemporaryEffects();
        });
        updateEffectOutput(input);
    });
    player.querySelectorAll('[data-movie-effect-input]').forEach(function (input) {
        input.addEventListener('input', function () {
            updateMovieEffectOutput(input);
            applyTemporaryMovieEffects();
        });
        updateMovieEffectOutput(input);
    });
    playToggle.addEventListener('click', function () {
        if (audio.paused || video.paused) {
            shouldKeepPlaying = true;
            const startAudio = window.Tone ? Tone.start() : Promise.resolve();
            startAudio.then(function () {
                syncTime(audio);
                return Promise.all([audio.play(), video.play()]);
            }).then(updatePlayButton).catch(function () {
                shouldKeepPlaying = false;
                setStatus('Playback could not start. Check that both media files are available.', true);
            });
        } else {
            shouldKeepPlaying = false;
            audio.pause();
            video.pause();
            updatePlayButton();
        }
    });

    audio.addEventListener('play', function () { syncPlayback(audio, true); updatePlayButton(); });
    audio.addEventListener('pause', function () { syncPlayback(audio, false); updatePlayButton(); });
    video.addEventListener('play', function () { syncPlayback(video, true); updatePlayButton(); });
    video.addEventListener('pause', function () { syncPlayback(video, false); updatePlayButton(); });
    audio.addEventListener('timeupdate', function () { syncTime(audio); });
    audio.addEventListener('ended', function () {
        shouldKeepPlaying = false;
        video.pause();
        setStatus('Song finished. Choose another pair to play again.');
        updatePlayButton();
    });
    audio.addEventListener('error', function () { setStatus('The selected song could not be loaded.', true); });
    video.addEventListener('error', function () { setStatus('The selected movie could not be loaded.', true); });
    document.addEventListener('visibilitychange', resumePlayback);
    window.addEventListener('focus', resumePlayback);
}());