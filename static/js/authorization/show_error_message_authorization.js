(function() {

   'use strict';

   let error_message = document.querySelector('.error-message');

   const CONST_TIME = 10;

   let time = 0;

   let timerwork = true;

    function show_message() {

      if (timerwork) {

        timerwork = false;

        timer();

        return;

      }

      error_message.classList.toggle('width_show');

    }

    function timer() {

      time += 1;

      if (time > CONST_TIME) {

        timerwork=false

        show_message();

      } else if(timerwork){

        setTimeout(timer, 1000);

      }

    }

    var errorbtn = document.querySelector('.error');

    errorbtn.addEventListener('mouseover', show_message);

    errorbtn.addEventListener('mouseout', show_message);

    timer();

  })();