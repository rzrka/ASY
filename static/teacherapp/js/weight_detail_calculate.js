'use strict';

var weight = document.getElementsByClassName("weight")[0];
var weight_norm = document.getElementsByClassName("weight_norm")[0];

function calculateRationing(all_weights) {
    var weight_value = weight.value;
    var new_all_weights = all_weights + Number(weight_value);
    if (!isNaN(new_all_weights)) {
        if (Number.isInteger(+weight_value)) {
            weight_norm.value = (Number.parseInt(weight_value) / Number.parseInt(new_all_weights) * 100.0).toFixed(2);
        }
    }

}
// weight.oninput = function() {
//     calculateRationing();
// };