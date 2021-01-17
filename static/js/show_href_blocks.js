(function() {

    'use strict';



    var href = document.getElementsByClassName("href-block-relative");


    for (var i = 0; i < href.length; i++) {

        href[i].onclick = function(e) {

            e = e || event;

            var target = e.target || e.srcElement;

            if (target.tagName == 'INPUT') {
                return;
            }

            var divs = this.getElementsByClassName("href-block");

            for (var j = 0; j < divs.length; j++) {

                divs[j].style.display = divs[j].style.display == "block" ? "none" : "block";
            }
        }
    }

})();