var inputs = document.querySelectorAll('input[type="file"]');

Array.prototype.forEach.call(inputs, function(input) {
    var label = input.nextElementSibling,
        labelVal = label.innerHTML;

    function set_label_text(e) {
        var fileName = '';
        if (this.files && this.files.length > 1)
            fileName = (this.getAttribute('data-multiple-caption') || '').replace('{count}', this.files.length);
        else
            fileName = e.target.value.split('\\').pop();
        if (fileName)
            label.querySelector('span').innerHTML = fileName;
        else
            label.innerHTML = labelVal;
    }

    input.addEventListener('change', set_label_text);
});