$(document).on('click', '#like-btn', function(event) {
    var btn = $(this);
    var likeAmountElement = btn.closest('.likes').find('.like_amount');
    var isLikedElement = btn.closest('.likes').find('.is_liked');

    $.ajax({
        url: btn.data('url'),
        type: 'POST',
        dataType: 'json',
        data: {
            like_submit: true,
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(data) {
            if (data.success) {
                var likeCount = parseInt(data.like_am, 10) || 0;

                likeAmountElement.text(data.liked ? likeCount + 1 : likeCount);
                isLikedElement.attr('data-for', data.liked ? 1 : 0);
                btn.text(data.liked ? 'Unlike' : 'Like');
            } else {
                console.error('Error in like submission');
            }
        },
        error: function(xhr, textStatus, errorThrown) {
            console.error('Error in AJAX request');
            console.error('Status:', textStatus);
            console.error('Error:', errorThrown);
            console.error('Response:', xhr.responseText);
        }
    });
});







