function sendMessage() {
    $('#btn').click(function () {
        var button = $(this);
        $.ajax(button.data('url'), {
            'type': 'POST',
            'async': true,
            'dataType': 'json',
            'data': {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'typeSend': true,
                'text': $('#text').val()
            },
            'success': function (data) {
                if (data && data.message) {
                    appendMessage(data.message);
                    $('#messages').scrollTop($('#messages')[0].scrollHeight);
                }
            }
        });
    });
}

function appendMessage(text) {
    $('#messages').append('<p class="u_msg">' + text + '</p>');
    $('#id_text').val('');
}

$(document).ready(function () {
    sendMessage();
});