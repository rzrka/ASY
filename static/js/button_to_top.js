(function() {

   'use strict';

    function trackScroll() {

      var scrolled = window.pageYOffset;

      if (scrolled > 100) {

        goTopBtn.classList.add('to_top_visible');

      }

      if (scrolled < 100) {

        goTopBtn.classList.remove('to_top_visible');

      }

    }

  

    function backToTop() {

      if (window.pageYOffset > 0) {

        window.scrollBy(0, -30);

        setTimeout(backToTop, 0);

      }

    }

    var goTopBtn = document.querySelector('.to_top');

    window.addEventListener('scroll', trackScroll);

    goTopBtn.addEventListener('click', backToTop);

  })();