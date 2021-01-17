$(document).ready(function() {

    // // Клик по ссылке "Закрыть".
    // $('.popup-close').click(function() {
    //     $(this).parents('.popup-fade').fadeOut();
    //     return false;
    // });

    function getWidth() {
        return Math.max(
            document.body.scrollWidth,
            document.documentElement.scrollWidth,
            document.body.offsetWidth,
            document.documentElement.offsetWidth,
            document.documentElement.clientWidth
        );
    }

    function close_all(show_table_div, scroll_div) {
        show_table_div.remove();
        scroll_div.remove();
        $('body').removeClass('overflow_hidden');
    }

    function excel_export(table, filename) {
        table.table2excel({
            exclude_inputs: true,
            name: "Worksheet 1",
            filename: filename, //do not include extension
            fileext: ".xls" // file extension
        });
    }

    $('.table_div').each(function(index, element) {
        if (!$(element).find('*').is('.table_button')) { // если нет, то создать
            $(element).append('<button type="button" class="table_button cursor-pointer"><img class="png_widen" src="' + img_path + '" alt="widen"></button>');
        }
        if (!$(element).find('*').is('.table_excel_save_button')) { // если нет, то создать
            $(element).append('<button type="button" class="table_excel_save_button cursor-pointer"><img class="png_excel" src="' + excel_img_path + '" alt="save excel"></button>');
        }
        var buttons = $(element).find('.table_button');
        var excel_buttons = $(element).find('.table_excel_save_button');
        var tables = $(element); //$(element).find('table_div');
        buttons.click(function(index) {
            var button = $(this);
            tables.each(function(index) {
                $(this).toggleClass('table_fixed');
                if (!$(this).hasClass('table_fixed')) {
                    $(this).removeAttr("style");
                    button.removeAttr("style");
                    $(this).next().removeAttr("style");
                    button.find('img').attr("src", img_path);
                    try {
                        resize_function();
                    } catch {}
                    return;
                }
                var all_width = $(window).width();
                var rez_width = Math.min(all_width, $(this).find('table')[0].scrollWidth);
                var margin = parseInt($(this).css('margin-top'));
                var style = 'width: ' + rez_width + 'px !important; margin-top: 0 !important; margin-bottom: 0 !important;';
                $(this).attr('style', style);
                if (rez_width == all_width) {
                    $(this).offset({ left: 0 });
                } else {
                    var left = all_width / 2 - rez_width / 2;
                    $(this).offset({ left: left });
                }

                //button.offset({ left: all_width / 2 });
                button.find('img').attr("src", close_img_path);
                try {
                    resize_function();
                } catch {}
            });
        });

        excel_buttons.click(function(index) {
            var button = $(this);
            tables.each(function(index, element) {
                var filename = "Таблица";
                if ($(this).find('table').data('table_name')) {
                    filename = $(this).find('table').data('table_name');
                }
                excel_export($(this), filename);
            });
        });
    });
});