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

    $('#a12c').on('click', function() {
        if ( $('#a12c').prop('checked') ) {
            $('input[name="12"]').prop('disabled', 1);
            $('#a12c').prop('disabled', 0);
        } else {
            $('input[name="12"]').prop('disabled', 0);
        }
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
})(jQuery);
