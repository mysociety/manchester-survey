(function($) {
    $('#a1f').on('click', function() {
        if ( $('#a1f').prop('checked') ) {
            $('input[name="1"]').prop('disabled', 1);
            $('input[name="a1other"]').prop('disabled', 1);
            $('#a1f').prop('disabled', 0);
        } else {
            $('input[name="a1other"]').prop('disabled', 0);
            $('input[name="1"]').prop('disabled', 0);
        }
    });

    function toggle_on_oclass(el) {
        the_el = $(el);
        oclass = the_el.attr('oclass');
        oclass_str = 'input[oclass="' + oclass + '"]';
        toggle_others(the_el, oclass_str);
    }

    function toggle_on_name(el) {
        the_el = $(el);
        name = the_el.prop('name');
        name_str = 'input[name="' + name + '"]';
        toggle_others(the_el, name_str);
    }

    function toggle_others(el, name_str) {
        if ( el.prop('checked') ) {
            $(name_str).prop('disabled', 1);
            el.prop('disabled', 0);
        } else {
            $(name_str).prop('disabled', 0);
        }
    }

    $('.table-exclusive').each( function(idx, el) {
        $(el).on('click', function() { toggle_on_oclass(this); });
    });

    $('.exclusive').each( function(idx, el) {
        $(el).on('click', function() { toggle_on_name(this); });
    });

    function toggle_optional() {
        el = $(this);
        id_str = '#' + el.attr('opt');
        if ( el.prop('checked') ) {
            $(id_str).show();
        } else {
            $(id_str).hide();
        }
    }

    $('.optional').each( function(idx, el) {
        the_el = $(el);
        the_el.on('click', toggle_optional);
    });

    $('#screen15-2').hide();
    $('#screen16-2').hide();
    $('#submit_button').hide();
    $('.back').show();

    $('li.last').prepend('<span id="last_of">of </span>');
})(jQuery);
