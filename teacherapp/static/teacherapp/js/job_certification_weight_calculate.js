(function() {

    'use strict';

    var calculate_items = document.getElementsByClassName("calculate-list-item");

    function calculateRationing() {
        var sum_weight = 0;
        for (var i = 0; i < calculate_items.length; i++) {
            var is_choosed = calculate_items[i].getElementsByClassName("is_choosed_checkbox")[0];
            if (is_choosed.checked) {
                var weight = calculate_items[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0].value;
                if (Number.isInteger(+weight)) {
                    sum_weight += Number.parseInt(weight);
                }
            }
        }
        if (!isNaN(sum_weight)) {
            for (var i = 0; i < calculate_items.length; i++) {
                var is_choosed = calculate_items[i].getElementsByClassName("is_choosed_checkbox")[0];
                if (is_choosed.checked) {
                    var weight = calculate_items[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0].value;
                    var weight_norm = calculate_items[i].getElementsByClassName("weight_norm")[0];
                    if (Number.isInteger(+weight)) {
                        if (!isNaN((Number.parseInt(weight) / Number.parseInt(sum_weight) * 100.0).toFixed(1))) {
                            weight_norm.innerHTML = (Number.parseInt(weight) / Number.parseInt(sum_weight) * 100.0).toFixed(1);
                        } else {
                            weight_norm.innerHTML = 0;
                        }

                    } else {
                        weight_norm.innerHTML = "Нет";
                    }
                } else {
                    var weight_norm = calculate_items[i].getElementsByClassName("weight_norm")[0];
                    weight_norm.innerHTML = "-";
                }
            }
        }
    }

    calculateRationing();

    for (var i = 0; i < calculate_items.length; i++) {
        var weight = calculate_items[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0];
        weight.oninput = function() {
            calculateRationing();
        };
        var checkbox = calculate_items[i].getElementsByClassName("is_choosed_checkbox")[0]
        checkbox.oninput = function() {
            calculateRationing();
        };
    }
})();