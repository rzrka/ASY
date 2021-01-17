/* set verification_criterion id on hidden input */
(function() {

    'use strict';

    (function($) {
        $.fn.myfunction = function(criterion) {
            $('#id_TeleWorkCriterionsCommentForm-teleworkcriterion').val(criterion);
        };
    })(jQuery);

    $('*[data-iframe="add_comment"]').each(function(index) {
        $(this).on("click", function() {
            var button = $(this);
            $(this).closest('*[data-criterion]').each(function(same) {
                var criterion = $(this).data('criterion'); // get data-criterion
                if ($('#' + button.data('iframe')).hasClass('display_none')) {
                    $('#' + button.data('iframe')).myfunction(criterion);
                }
            });
        });
    });

    // CSRF code
    function getCookie(name) {
        var cookieValue = null;
        var i = 0;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (i; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    var csrftoken = getCookie('csrftoken');

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
        crossDomain: false, // obviates need for sameOrigin test
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type)) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });
    // end CSRF

    $('#save_comment').on('click', function() {
        var text = $('#id_TeleWorkCriterionsCommentForm-text').val();
        var comment_type = $('#id_TeleWorkCriterionsCommentForm-comment_type').val();
        var teleworkcriterion = $('#id_TeleWorkCriterionsCommentForm-teleworkcriterion').val();
        if (!text) {
            return;
        }
        $.ajax({
            url: url_addres,
            headers: { "X-CSRFToken": csrftoken },
            method: 'POST',
            data: {
                'text': text,
                'comment_type': comment_type,
                'teleworkcriterion': teleworkcriterion,
            },
            success: function(data) {
                console.log(data);
                $('#add_comment').addClass('display_none');
                $('#id_TeleWorkCriterionsCommentForm-text').val('');
                $('#id_TeleWorkCriterionsCommentForm-teleworkcriterion').val('');
                text = data.text;
                comment_type = data.comment_type;
                teleworkcriterion = data.teleworkcriterion;
                var comment_id = data.comment_id;
                $('*[data-criterion="' + teleworkcriterion + '"]')
                    .find('span:nth-child(3) a[data-iframe="add_comment"]')
                    .before(' <div data-comment_id="' + comment_id + '" class="comment">' + text + '<a class="comment_delete"></a></div>');
            },
            error: function(data) {
                console.log(data);
            }
        });

    });

    $('div[data-criterion]').on('click', 'a.comment_delete', function() {
        var div_parent = $(this).closest('div');
        var teleworkcomment = div_parent.data('comment_id'); // get comment_id of telework comment
        $.ajax({
            url: url_delete_addres,
            headers: { "X-CSRFToken": csrftoken },
            method: 'POST',
            data: {
                'teleworkcomment': teleworkcomment,
            },
            success: function(data) {
                if (data.success) {
                    div_parent.remove();
                }
            },
            error: function(data) {
                console.log(data);
            }
        });
    });

    function get_weight_from_inputs(span) { // получение из текущей строки коэфициента выбранного веса и полного веса критерия
        var inputs = $(span).find('input'); // получение всех inputов
        var out_weight = 0;
        var full_weight = $(span).data('weight'); // полный вес критерия
        if (inputs[0] === undefined) { // получение всех inputов
            inputs = $(span).find('select');
        }
        if (inputs.is(':radio')) { // 2-балльная шкала
            inputs.each(function(index) {
                if (inputs.eq(index).is(':checked')) {
                    out_weight += inputs.eq(index).val(); // if зачет - 1 незачет - 0
                }
            });
        } else if (inputs.is('[type="number"]')) { // n(100)-балльная шкала, тут осуществляется просмотр кастомного перевода (вызов ajax итд)
            inputs.each(function(index, element) {
                out_weight += $(element).val();
                out_weight /= parseFloat($(span).data('scale')); // получение от 0 до 1 (translate to n to 100)
            });
        } else if (inputs[0].tagName == 'SELECT') { // 5-балльная шкала
            inputs.each(function(index, element) {
                out_weight += $(element).find('option:selected').val(); // five = 1, four = 0.75, three - 0.5, two - 0.25
                out_weight /= 5.0;
            });
        }
        return [out_weight, full_weight]; // out_weight - это коэфициент
    }

    function get_subcriterions_weight(weight) { // получение всех подкритериев
        var main_div = weight.closest('.subcriterions');
        var prev_div = main_div.prev();
        var prev_div_wight_span = prev_div.find('.weight');
        var all_weight = 0; // сумма всех весов подкритериев
        var chosed_weight = 0; // сумма всех выбранных весов
        weight.closest('.subcriterions').find('.weight').each(function(index, element) {
            var weight = get_weight_from_inputs(element);
            chosed_weight += parseFloat(weight[0]) * parseFloat(weight[1]);
            all_weight += parseFloat(weight[1]);
        });
        // chosed_weight - сумма весов выбранных подкритериев
        // all_weight - сумма весов всех подкритериев
        var output = chosed_weight * 100.0 / all_weight; // весь выбранный вес
        var scale_dimension = prev_div_wight_span.data('scale');
        output = parseFloat(output) * parseFloat(scale_dimension) / 100.0;
        if (prev_div_wight_span.data('scale') == 5 && output.toFixed(0) < 2) {
            output = 2;
        } else if (prev_div_wight_span.data('scale') == 2) {
            output = Math.floor(output);
        }
        var $element = prev_div_wight_span.find('.recommended'); // создание или получение дива с рекомендациями
        if (!$element.length)
            $element = $('<div class="recommended"></div>').appendTo(prev_div_wight_span);
        var text_output = output.toFixed(0);
        if (parseFloat(prev_div_wight_span.data('scale')) == 2 && text_output == 1) {
            text_output = 'Зачет';
        } else if (parseFloat(prev_div_wight_span.data('scale')) == 2 && text_output == 0) {
            text_output = 'Незачет';
        }

        //console.log(prev_div_wight_span.data('scale') + ' ' + text_output);
        $element.text('(рек. - ' + text_output + ')');
        // изменяет значение главного критерия
        prev_div_wight_span.find('input, select').each(function(index, element) {
            if (!$(element).is(':radio')) {
                $(element).val(output.toFixed(0));
            } else {
                var name = $(element).attr("name");
                $("input[name=" + name + "][value=" + output.toFixed(0) + "]").prop('checked', true);
            }
        });

        function_toggle();
    }

    function get_criterion_weight() { //получение всех критериев
        var all_weight = 0; // сумма всех весов критериев
        var chosed_weight = 0; // сумма всех выбранных весов
        $('.weight').each(function(index) {
            var weight_iteration = $(this);
            if (!weight_iteration.data('general_criterion')) {
                var weights = get_weight_from_inputs(weight_iteration);
                chosed_weight += parseFloat(weights[0]) * parseFloat(weights[1]);
                all_weight += parseFloat(weights[1]);
            }
        });
        var output = chosed_weight * parseFloat(job_scale) / all_weight; // подсчет 
        if (job_scale == 5 && output.toFixed(0) < 2) {
            output = 2;
        } else if (job_scale == 2) {
            output = Math.floor(output);
        }
        var $element = $('span.recommended');
        if (!$element.length)
            $element = $('<span class="recommended"></span>').appendTo($('.pass_div'));
        var text_output = output.toFixed(0);
        if (job_scale == 2 && text_output == 1) {
            text_output = 'Зачет';
        } else if (job_scale == 2 && text_output == 0) {
            text_output = 'Незачет';
        }
        $element.text('(рек. - ' + text_output + ')');
        $('#id_TeleWork_grade-grade').val(output.toFixed(0));
        var event = new Event('change');
        var event_element = document.getElementById('id_TeleWork_grade-grade');
        event_element.dispatchEvent(event);
    }

    $('.weight').each(function(index) {
        var weight = $(this);
        $(this).find('input, select').on('change', function() {
            if (weight.data('general_criterion')) { // все субкритерии
                get_subcriterions_weight(weight);
            }
            get_criterion_weight(); // все критерии
            set_numberimputs_color(); // цвета inputов[type=number]
        });

    });
    $('.color_numberinput_grade').each(function() {
        $(this).find('input[type="number"]').on('change', function() {
            set_numberimputs_color();
        });
    });
    set_numberimputs_color();
})();