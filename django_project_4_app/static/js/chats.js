$(function(){
    $(document).click(function(event) {
        var clickedElement = $(event.target);
        console.log(clickedElement);

        if (clickedElement.hasClass('profile-image') || clickedElement.hasClass('btn_snd') || clickedElement.hasClass('open')) {
            var chatId = clickedElement.data('id');
            var chatUrl = clickedElement.data('url');

            if ($('#chat').html() == '') {
                $.ajax(chatUrl, {
                    type: 'POST',
                    async: true,
                    dataType: 'json',
                    data: {
                        'chat': chatId,
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                    },
                    success: function(data) {
                        $('#chat').html(data);
                    }
                });
            } else {
                $('#chat').html('');
            }
        } else if (clickedElement.attr('id') == 'input') {
            $.ajax(clickedElement.data('url'), {
                type: 'POST',
                async: true,
                dataType: 'json',
                data: {
                    'message': $('#id_body').val(),
                    'chat': clickedElement.data('id'),
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                success: function(data) {
                    $('#messages').append('<div class="row"><div><p class="u_msg float-end">' + data.message + '</p><br></div></div>');
                    $('#id_body').val('');
                }
            });
        }
    });
});
