$(function() {

    function resize_table_box() {
        $('.table_div').each(function() {
            var box_width = $(this).outerWidth();
            var table_width = $(this).children('table').prop('scrollWidth');
            $(this).removeClass('scroll-left');
            if (table_width > box_width) {
                $(this).addClass('scroll-right');
            } else {
                $(this).removeClass('scroll-right');
            }
        });
    }

    function scrollRight(element) {
        var max_width = element[0].scrollWidth;
        if (max_width == element.scrollLeft())
            return true;
        else
            return false;
    }

    function delete_shadows_box() {
        $('.table_div').each(function() {
            $(this).removeClass('scroll-left');
            $(this).removeClass('scroll-right');
        });
    }

    function set_table_shadows() {
        var parent = $(this).parent();
        if ($(this).scrollLeft() + $(this).innerWidth() >= $(this)[0].scrollWidth - 1) {
            if (parent.hasClass('scroll-right')) {
                parent.removeClass('scroll-right');
            }
        } else if ($(this).scrollLeft() === 0) {
            if (parent.hasClass('scroll-left')) {
                parent.removeClass('scroll-left');
            }
        } else {
            if (!parent.hasClass('scroll-right')) {
                parent.addClass('scroll-right');
            }
            if (!parent.hasClass('scroll-left')) {
                parent.addClass('scroll-left');
            }
        }
    }
    try {
        resize_function = function() {
            delete_shadows_box();
        };
    } catch {}

    resize_table_box();
    $(window).on('resize', function() {
        resize_table_box();
    });

    $('.table_div table').on('scroll', set_table_shadows);
});