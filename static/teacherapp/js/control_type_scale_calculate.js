(function() {

    'use strict';

    var calculate_items = document.getElementsByClassName("input-scale-transform");

    for (let index = calculate_items.length - 1; index >= 0; index--) {
        var elem = '<span class="span-proc"></span>';
        calculate_items[index].insertAdjacentHTML('afterEnd', elem);
    }

    function calculatePoints() {
        let last_elem = 0;
        for (let index = calculate_items.length - 1; index >= 0; index--) {
            let this_value = calculate_items[index].value;
            var elem = '(от ' + last_elem + ' до ' + this_value + ')';
            calculate_items[index].nextSibling.innerHTML = elem;
            last_elem = Number(this_value) + 1;
        }
    }

    calculatePoints();

    for (var i = 0; i < calculate_items.length; i++) {
        calculate_items[i].oninput = function(e) {
            calculatePoints();
        };
    }


})();