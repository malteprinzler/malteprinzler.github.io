function setupVideoVisibilityObserver() {
    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            var video = entry.target;

            if (entry.isIntersecting) {
                // Video has entered the screen: play it
                safePlay(video);
            } else {
                // Video has left the screen: pause and reset to frame 0
                video.pause();
                video.currentTime = 0;
            }
        });
    }, {
        root: null,        // Observe relative to the browser viewport
        threshold: 0.01     // Trigger when at least 30% of the video is visible
    });

    // Attach the observer to all videos inside your slider items
    var videos = document.querySelectorAll(".slider-item video");
    videos.forEach(function (video) {
        // Ensure browser autoplay prerequisites are strictly enforced
        video.muted = true;
        video.playsInline = true;
        video.loop = true;
        observer.observe(video);
    });
}

function getBlenderrenderVideoPath(originalPath) {
    // Map non-blenderrender triplet videos to their blenderrender counterparts.
    // Example:
    //   static/videos/thanks_for_watching_triplets/triplet_01.mp4
    // ->static/videos/thanks_for_watching_triplets/triplet_blenderrender_01.mp4
    return originalPath
            .replace("/triplet_", "/triplet_blenderrender_");

}

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function safePlay(video) {
    var playPromise = video.play();
    if (playPromise && typeof playPromise.catch === "function") {
        playPromise.catch(function () {});
    }
}

function applySplitPosition(compareContainer, split) {
    var clamped = clamp(split, 0.02, 0.98);
    var splitPercent = (clamped * 100).toFixed(2) + "%";
    var leftVideo = compareContainer.querySelector(".split-video-left");
    var rightVideo = compareContainer.querySelector(".split-video-right");
    var divider = compareContainer.querySelector(".split-divider");
    leftVideo.style.clipPath = "inset(0 " + (100 - clamped * 100).toFixed(2) + "% 0 0)";
    rightVideo.style.clipPath = "inset(0 0 0 " + splitPercent + ")";
    divider.style.left = splitPercent;
}

function setupInteractiveSplitCarousel(carouselId) {
    var items = document.querySelectorAll(carouselId + " .item");
    items.forEach(function (item) {
        if (item.querySelector(".split-video-compare")) {
            return;
        }

        var originalVideo = item.querySelector("video");
        if (!originalVideo) {
            return;
        }
        var sourceElement = originalVideo.querySelector("source");
        if (!sourceElement || !sourceElement.src) {
            return;
        }

        var baseVideoPath = sourceElement.getAttribute("src");
        var blenderrenderPath = getBlenderrenderVideoPath(baseVideoPath);
        if (blenderrenderPath === baseVideoPath) {
            return;
        }

        var compareContainer = document.createElement("div");
        compareContainer.className = "split-video-compare";
        compareContainer.dataset.split = "0.0"; // left edge => only blenderrender

        var leftVideo = document.createElement("video");
        leftVideo.className = "split-video split-video-left";
        leftVideo.setAttribute("autoplay", "");
        leftVideo.setAttribute("muted", "");
        leftVideo.setAttribute("playsinline", "");
        leftVideo.autoplay = true;
        leftVideo.muted = true;
        leftVideo.loop = true;
        leftVideo.playsInline = true;
        leftVideo.src = baseVideoPath;

        var rightVideo = document.createElement("video");
        rightVideo.className = "split-video split-video-right";
        rightVideo.setAttribute("autoplay", "");
        rightVideo.setAttribute("muted", "");
        rightVideo.setAttribute("playsinline", "");
        rightVideo.autoplay = true;
        rightVideo.muted = true;
        rightVideo.loop = true;
        rightVideo.playsInline = true;
        rightVideo.src = blenderrenderPath;

        var divider = document.createElement("div");
        divider.className = "split-divider";

        compareContainer.appendChild(leftVideo);
        compareContainer.appendChild(rightVideo);
        compareContainer.appendChild(divider);
        item.replaceChild(compareContainer, originalVideo);
        applySplitPosition(compareContainer, 0.0);

        var updateFromClientX = function (clientX) {
            var rect = compareContainer.getBoundingClientRect();
            var split = (clientX - rect.left) / rect.width;
            compareContainer.dataset.split = clamp(split, 0, 1).toString();
            applySplitPosition(compareContainer, split);
        };

        compareContainer.addEventListener("mousemove", function (event) {
            updateFromClientX(event.clientX);
        });
        compareContainer.addEventListener("touchstart", function (event) {
            if (event.touches.length > 0) {
                updateFromClientX(event.touches[0].clientX);
            }
        }, {passive: true});
        compareContainer.addEventListener("touchmove", function (event) {
            if (event.touches.length > 0) {
                updateFromClientX(event.touches[0].clientX);
            }
        }, {passive: true});

        // Keep both videos synchronized in time and playback state.
        var syncTime = function (sourceVideo, targetVideo) {
            if (Math.abs(targetVideo.currentTime - sourceVideo.currentTime) > 0.12) {
                targetVideo.currentTime = sourceVideo.currentTime;
            }
        };
        leftVideo.addEventListener("timeupdate", function () { syncTime(leftVideo, rightVideo); });
        rightVideo.addEventListener("timeupdate", function () { syncTime(rightVideo, leftVideo); });
        leftVideo.addEventListener("play", function () { 
            if (rightVideo.paused) rightVideo.play(); 
        });
        rightVideo.addEventListener("play", function () { 
            if (leftVideo.paused) leftVideo.play(); 
        });
        leftVideo.addEventListener("pause", function () { 
            if (!rightVideo.paused) rightVideo.pause(); 
        });
        rightVideo.addEventListener("pause", function () { 
            if (!leftVideo.paused) leftVideo.pause(); 
        });

    });
}

function isSliderItemActive(sliderItem) {
    return sliderItem.classList.contains("is-active") || sliderItem.getAttribute("aria-hidden") === "false";
}


function createCarousel(carouselId) {
    var slidesToShow = carouselId === "#match-results-carousel" ? 1 : 1;
    bulmaCarousel.attach(carouselId, {
        slidesToScroll: slidesToShow,
        slidesToShow: slidesToShow,
        loop: true,
        autoplay: true,
        autoplaySpeed: 50000,
    });
}

$(document).ready(function () {
    // 1. Setup your split DOM elements first
    setupInteractiveSplitCarousel("#match-results-carousel");

    // 2. Initialize the carousels
    createCarousel("#match-results-carousel");
    createCarousel("#nvs-baseline-comparison-carousel");
    createCarousel("#avatar-baseline-comparison-carousel");

    // 3. Start watching the videos for visibility
    setupVideoVisibilityObserver();
});

// From https://dorverbin.github.io/refnerf/.
// This is based on: http://thenewcode.com/364/Interactive-Before-and-After-Video-Comparison-in-HTML5-Canvas
// With additional modifications based on: https://jsfiddle.net/7sk5k4gp/13/

function playVids(videoId) {
    var videoMerge = document.getElementById(videoId + "Merge");
    var vid = document.getElementById(videoId);

    var position = 0.5;
    var vidWidth = vid.videoWidth / 2;
    var vidHeight = vid.videoHeight;

    var mergeContext = videoMerge.getContext("2d");


    if (vid.readyState > 3) {
        vid.play();

        function trackLocation(e) {
            // Normalize to [0, 1]
            bcr = videoMerge.getBoundingClientRect();
            position = ((e.pageX - bcr.x) / bcr.width);
            // videoMerge.setAttribute('data-position', position);
        }
        function trackLocationTouch(e) {
            // Normalize to [0, 1]
            bcr = videoMerge.getBoundingClientRect();
            position = ((e.touches[0].pageX - bcr.x) / bcr.width);
        }

        videoMerge.addEventListener("mousemove", trackLocation, false);
        videoMerge.addEventListener("touchstart", trackLocationTouch, false);
        videoMerge.addEventListener("touchmove", trackLocationTouch, false);

        function drawLoop() {
            mergeContext.drawImage(vid, 0, 0, vidWidth, vidHeight, 0, 0, vidWidth, vidHeight);
            var colStart = (vidWidth * position).clamp(0.0, vidWidth);
            var colWidth = (vidWidth - (vidWidth * position)).clamp(0.0, vidWidth);
            mergeContext.drawImage(vid, colStart + vidWidth, 0, colWidth, vidHeight, colStart, 0, colWidth, vidHeight);
            requestAnimationFrame(drawLoop);

            // // Draw border
            // mergeContext.beginPath();
            // mergeContext.moveTo(vidWidth * position, 0);
            // mergeContext.lineTo(vidWidth * position, vidHeight);
            // mergeContext.closePath()
            // mergeContext.strokeStyle = "#444444";
            // mergeContext.lineWidth = 5;
            // mergeContext.stroke();
        }
        requestAnimationFrame(drawLoop);
    }
}

Number.prototype.clamp = function (min, max) {
    return Math.min(Math.max(this, min), max);
};


function resizeAndPlay(element) {
    var cv = document.getElementById(element.id + "Merge");
    cv.width = element.videoWidth / 2;
    cv.height = element.videoHeight;
    element.play();
    element.style.height = "0px";  // Hide video without stopping it

    playVids(element.id);
}