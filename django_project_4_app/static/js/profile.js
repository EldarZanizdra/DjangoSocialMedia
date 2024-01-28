function userFollow() {
    $('#follow').click(function () {
        var follow = $(this);
        $.ajax({
            type: 'POST',
            url: follow.data('url'),
            dataType: 'json',
            data: {
                'follow': follow.data('id'),
                'is_followed': $('#follow').data('for'),
            },
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            },
            success: function (data) {
                var isFollowed = data['is_follow'] === 1;
                $('#follow').data('for', isFollowed ? 1 : 0);
                $('#follow').toggleClass('profile_fol profile_unfol', !isFollowed);
                $('#followers').text(data['followers']);
                $('#action').text(isFollowed ? 'Unfollow' : 'Follow');
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

$(document).ready(function () {
    var isFollowed = $('#follow').data('for') === 1;
    $('#follow').toggleClass('profile_fol profile_unfol', !isFollowed);
    $('#action').text(isFollowed ? 'Unfollow' : 'Follow');
    userFollow();
});

$(document).ready(function () {
    $('#followersBtn').click(function () {
        // Fetch followers data and update the results container
        $.ajax({
            url: '/get_followers/',
            type: 'GET',
            success: function (data) {
                $('#resultsContainer').html(data.results);
                makeUsernamesClickable();  // Add this line to make usernames clickable
            },
            error: function () {
                console.log('Error fetching followers');
            }
        });
    });

    $('#followingBtn').click(function () {
        // Fetch following data and update the results container
        $.ajax({
            url: '/get_following/',
            type: 'GET',
            success: function (data) {
                $('#resultsContainer').html(data.results);
                makeUsernamesClickable();  // Add this line to make usernames clickable
            },
            error: function () {
                console.log('Error fetching following');
            }
        });
    });

    function makeUsernamesClickable() {
        $('.clickable-username').click(function () {
            var username = $(this).text().trim();
            window.location.href = '/profile/' + username + '/';
        });
    }
});




