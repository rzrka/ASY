(function() {

    'use strict';

    function containsObject(obj, list) {
        var i;
        for (i = 0; i < list.length; i++) {
            if (list[i] === obj) {
                return true;
            }
        }
        return false;
    }
    try {
        $('.input_table').parent().each(function(index) {
            if ($(this).hasClass("iframe-row")) {
                $(this).css({ margin: '0 20px', width: 'calc(100% - 40px)' });
            }
        });
    } catch {

    }


    //var show_buttons = document.getElementsByClassName('btn_delete');
    var show_buttons = document.querySelectorAll('[data-iframe]');
    let iframes = new Set();

    for (let i = 0; i < show_buttons.length; i++) {

        var iframe = document.getElementById(show_buttons[i].dataset.iframe);
        show_buttons[i].addEventListener("click", function() {
            iframe.classList.toggle('display_none');
        });
        iframes.add(iframe);
        // var close_buttons = iframe.getElementsByClassName('iframe-element-close');
        // for (let j = 0; j < close_buttons.length; j++) {
        //     close_buttons[j].addEventListener("click", function() {
        //         iframe.classList.toggle('display_none');
        //     });
        // }

        // var close_iframe_btn = iframe.getElementsByClassName('btn_cancel')[0];
        // close_iframe_btn.addEventListener("click", function() {
        //     iframe.classList.toggle('display_none');
        // });
    }

    iframes.forEach(function(iframe) {    
        var close_buttons = iframe.getElementsByClassName('iframe-element-close');
        for (let j = 0; j < close_buttons.length; j++) {
            close_buttons[j].addEventListener("click", function() {
                iframe.classList.toggle('display_none');
            });
        }
    })
})();