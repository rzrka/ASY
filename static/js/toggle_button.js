(function() {

    'use strict';

    let btn_toggles = document.getElementsByClassName('btn_toggle');
    let select_toggles = document.getElementsByClassName('grades_select');

    let classes = {
        'Присутствует': 'plus',
        'Отсутствует': 'nb',
        'Отсутствует (по уважительной причине)': 'nbyv',
        'отлично': 'five',
        'хорошо': 'four',
        'удовл.': 'three',
        'неудовл.': 'two',
        '5': 'five',
        '4': 'four',
        '3': 'three',
        '2': 'low_three',
        '1': 'two',
        'зачет': 'five',
        'незачет': 'two',
        'Зачет': 'five',
        'Незачет': 'two',

    }

    function work() {
        Array.prototype.forEach.call(btn_toggles, function(element) {
            element.classList.remove(classes[element.dataset.class]);
        });
        Array.prototype.forEach.call(btn_toggles, function(element) {
            let inp = element.getElementsByTagName('input')[0];
            if (inp.checked) {
                element.classList.add(classes[element.dataset.class]);
            }
        });
    }

    function setSelect() {
        Array.prototype.forEach.call(select_toggles, function(element) {
            element.classList.remove(classes[element.dataset.class]);
        });
        Array.prototype.forEach.call(select_toggles, function(element) {
            element.classList.add(classes[element.options[element.selectedIndex].text]);
            element.dataset.class = element.options[element.selectedIndex].text;
        });
    }

    function getActive() {
        Array.prototype.forEach.call(btn_toggles, function(element) {
            element.addEventListener('click', work);
            //console.log(element.innerHTML);
        });

        Array.prototype.forEach.call(select_toggles, function(element) {
            element.addEventListener('change', setSelect);
        });
    }

    getActive();
    work();
    setSelect();

    try {
        general_classes = classes;
        function_toggle = function() {
            work();
            setSelect();
        };
    } catch {}

    // block_user.addEventListener('mouseover', open_drop_down);
    // window.addEventListener('scroll', move_user_icon);

})();