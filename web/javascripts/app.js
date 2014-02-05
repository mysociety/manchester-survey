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

    function toggle_others(id, name) {
        id_str = '#' + id;
        name_str = 'input[name="' + name + '"]';
        if ( $(id_str).prop('checked') ) {
            $(name_str).prop('disabled', 1);
            $(id_str).prop('disabled', 0);
        } else {
            $(name_str).prop('disabled', 0);
        }
    }

    $('.exclusive').each( function(idx, el) {
        the_el = $(el);
        id = the_el.prop('id');
        id_str = '#' + id;
        name = the_el.prop('name');
        the_el.on('click', function() { toggle_others(id, name); });
    });

    function toggle_fourteen_optional() {
        if ( $(this).prop('checked') ) {
            $('#screen14-2').show();
        } else {
            $('#screen14-2').hide();
        }
    }

    $('input[name="14community"][value="f"]').on('click', toggle_fourteen_optional);
    $('input[name="14political"][value="f"]').on('click', toggle_fourteen_optional);

    $('#screen14-2').hide();
    $('#submit_button').hide();
})(jQuery);
