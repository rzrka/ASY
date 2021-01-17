(function() {

    'use strict';

    var calculate_items = document.getElementsByClassName("calculate-list-item");
    var calculate_subitem_groups = document.getElementsByClassName("subcriterions");

    function calculateRationing() {
        var sum_weight = 0;
        for (var i = 0; i < calculate_items.length; i++) {
            var weight = calculate_items[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0].value;
            if (Number.isInteger(+weight)) {
                sum_weight += Number.parseInt(weight);
            }
        }
        if (!isNaN(sum_weight)) {
            for (var i = 0; i < calculate_items.length; i++) {
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
            }
        }
    }

    function calculateRationingSubitems() {
        var sum_weight = []
        for (var i = 0; i < calculate_subitem_groups.length; i++) {
            var calculate_subitems = calculate_subitem_groups[i].getElementsByClassName("calculate-list-subitem");
            var sum = 0;
            for (var j = 0; j < calculate_subitems.length; j++) {
                var weight = calculate_subitems[j].getElementsByClassName("weight")[0].getElementsByTagName('input')[0].value;
                if (Number.isInteger(+weight)) {
                    sum += Number.parseInt(weight);
                }
            }
            sum_weight[i] = sum;
        }

        for (var i = 0; i < calculate_subitem_groups.length; i++) {
            if (!isNaN(sum_weight[i])) {
                var calculate_subitems = calculate_subitem_groups[i].getElementsByClassName("calculate-list-subitem");
                for (var j = 0; j < calculate_subitems.length; j++) {
                    var weight = calculate_subitems[j].getElementsByClassName("weight")[0].getElementsByTagName('input')[0].value;
                    var weight_norm = calculate_subitems[j].getElementsByClassName("weight_norm")[0];
                    if (Number.isInteger(+weight)) {
                        weight_norm.innerHTML = (Number.parseInt(weight) / Number.parseInt(sum_weight) * 100.0).toFixed(1);
                    } else {
                        weight_norm.innerHTML = "Нет";
                    }
                }
            }
        }
    }

    calculateRationing();
    calculateRationingSubitems();

    for (var i = 0; i < calculate_items.length; i++) {
        var weight = calculate_items[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0];
        weight.oninput = function() {
            calculateRationing();
        };
    }
    var all_subitems = document.getElementsByClassName("calculate-list-subitem");
    for (var i = 0; i < all_subitems.length; i++) {
        var weight = all_subitems[i].getElementsByClassName("weight")[0].getElementsByTagName('input')[0];
        weight.oninput = function() {
            calculateRationingSubitems();
        };
    }
})();