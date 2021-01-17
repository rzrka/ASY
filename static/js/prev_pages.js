(function() {

   'use strict';

    let btn_prev_pages = document.getElementsByClassName('btn_prev_pages')[0];

    function showPagesList() {
        let pages_list = document.getElementsByClassName('pages_list')[0];
        pages_list.classList.toggle('active');
        btn_prev_pages.classList.toggle('active');
    }

    btn_prev_pages.addEventListener('click', showPagesList);

})();