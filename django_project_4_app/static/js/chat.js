$(document).ready(function() {
    $(document).on('click', '#input', function() {
        var btn = $(this);
        console.log(btn);

        $.ajax(btn.data('url'), {
            type: 'POST',
            async: true,
            dataType: 'json',
            data: {
                'message': $('#id_body').val(),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(data) {
                $('#messages').append('<p class="u_msg">' + data.message + '</p><br>');
                $('#id_body').val('');
            }
        });
    });
});
