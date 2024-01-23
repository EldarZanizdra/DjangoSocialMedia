function userFollow() {
    $('#follow').click(function () {
        var follow = $(this);
        $.ajax(follow.data('url'), {
            'type': 'POST',
            'async': true,
            'dataType': 'json',
            'data': {
                'follow': follow.data('id'),
                'is_followed': document.getElementById('is_follow').dataset.for,
                'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val()
            },
            'success': function (data) {
                if (data['is_follow'] == 1) {
                    document.getElementById('is_follow').dataset.for = 1;
                    document.getElementById('follow').className = 'profile_unfol';
                    document.getElementById('followers').innerHTML = data['followers'];
                    document.getElementById('action').innerHTML = 'Unfollow';
                } else {
                    document.getElementById('is_follow').dataset.for = 0;
                    document.getElementById('follow').className = 'profile_fol';
                    document.getElementById('followers').innerHTML = data['followers'];
                    document.getElementById('action').innerHTML = 'Follow';
                }
            }
        });
    });
}

$(document).ready(function () {
    if (document.getElementById('is_follow').dataset.for == '0') {
        document.getElementById('follow').className = 'profile_fol';
        document.getElementById('action').innerHTML = 'Follow';
    } else {
        document.getElementById('follow').className = 'profile_unfol';
        document.getElementById('action').innerHTML = 'Unfollow';
    }
    userFollow();
});
