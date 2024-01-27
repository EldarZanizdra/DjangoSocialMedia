function comment(){
    $('#btnCom').click(function(){
        var button = $(this)
        $.ajax(button.data('url'), {
            'type': 'POST',
            'async': true,
            'dataType': 'json',
            'data': {
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'typeSend': true,
                'text': $('#text').val()
            },
            'success': function(data){
                document.getElementById('comAnswer').innerHTML = data['comment'];
                $('#comAnswer').style.visibility = 'visible';
            }
        })
    })
}

