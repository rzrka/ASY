(function() {

    'use strict';

    let block_user = document.getElementsByClassName('block_user')[0];
    let drop_down_list = document.getElementsByClassName('block_user_menu')[0];

    function open_drop_down(event) {
        drop_down_list.classList.toggle('block_user_menu_visible');
    }

    block_user.addEventListener('mouseover', open_drop_down);
    block_user.addEventListener('mouseout', open_drop_down);

})();