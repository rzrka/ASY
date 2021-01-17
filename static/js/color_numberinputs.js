function get_grade_from_procent(procent) {
    if (procent == 100)
        return 5;
    else if (procent > 50)
        return 4;
    else if (procent > 30)
        return 3;
    else if (procent > 0)
        return 2;
    else
        return 1;
}

function set_numberimputs_color() {
    $('.weight').each(function(index) {
        var weight_iteration = $(this);
        $(this).find('input[type="number"]').each(function(index, element) {
            $(element).val(Math.min($(element).val(), weight_iteration.data('scale')));
            $(element).val(Math.max($(element).val(), $(element).attr('min')));
            $(element).removeClass(general_classes[$(element).data('class')]);
            var procent = parseFloat($(element).val()) * 100.0 / parseFloat(weight_iteration.data('scale'));
            var grade = get_grade_from_procent(procent);
            $(element).addClass(general_classes[grade]);
            $(element).data('class', grade);
        });

    });

    /* для степени выполнения работы */
    $('.color_numberinput_grade').each(function() {
        var weight_iteration = $(this);
        $(this).find('input[type="number"]').each(function(index, element) {
            $(element).val(Math.min($(element).val(), weight_iteration.data('scale')));
            $(element).val(Math.max($(element).val(), $(element).attr('min')));
            $(element).removeClass(general_classes[$(element).data('class')]);
            var procent = parseFloat($(element).val()) * 100.0 / parseFloat(weight_iteration.data('scale'));
            var grade = get_grade_from_procent(procent);
            $(element).addClass(general_classes[grade]);
            $(element).data('class', grade);
        });
    });
}