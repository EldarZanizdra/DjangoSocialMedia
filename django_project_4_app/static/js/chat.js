function sendMessage() {
    $('#btn').click(function () {
        var button = $(this);
        var message_id = $('#message_id').val();

        $.ajax(button.data('url'), {
            'type': 'POST',
            'async': true,
            'dataType': 'json',
            'data': {
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                'typeSend': true,
                'text': $('#text').val(),
                'message_id': message_id
            },
            'success': function (data) {
                if (data && data.message) {
                    if (message_id) {
                        updateMessage(message_id, data.message);
                    } else {
                        appendMessage(data.message, data.sender);
                        $('#messages').scrollTop($('#messages')[0].scrollHeight);
                    }

                    $('#message_id').val('');
                    $('#text').val('');
                }
            }
        });
    });

    $('.edit-btn').click(function () {
        var message_id = $(this).data('message-id');
        var message_text = $('#messages').find('[data-message-id="' + message_id + '"] .message-text').text();
        var message_user = $('#messages').find('[data-message-id="' + message_id + '"] .message-user').text();
        $('#message_id').val(message_id);
        $('#text').val(message_text);
    });
}

function appendMessage(text, sender) {
    var newMessage = $('<p class="u_msg" data-message-id="{{ m.id }}">');
    newMessage.append('<span class="message-text">' + text + '</span>');
    newMessage.append('<span class="message-user">' + sender + '</span>');
    newMessage.append('<button class="edit-btn" data-message-id="{{ m.id }}">Edit</button>');

    $('#messages').append(newMessage);
}

function updateMessage(message_id, text) {
    $('#messages').find('[data-message-id="' + message_id + '"] .message-text').text(text);
}

$(document).ready(function () {
    sendMessage();
});



