var slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  var i;
  var slides = document.getElementsByClassName("item-slide");
  var captionText = document.getElementById("caption");
  if (n > slides.length) {slideIndex = 1}
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
      slides[i].style.display = "none";
  }
}

bulmaCarousel.attach('#results-carousel', {
            slidesToScroll: 1,
            slidesToShow: 1,
            infinite: true,
            autoplay: false,
            pagination: false,
        });
bulmaCarousel.attach('#results-carousel-4', {
            slidesToScroll: 4,
            slidesToShow: 4,
            infinite: true,
            autoplay: false,
            pagination: false,
        });