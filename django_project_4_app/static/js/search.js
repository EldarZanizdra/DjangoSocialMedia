$(function(){
    var debounceTimer;

    $('#id_search').keyup(function(){
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(function() {
            $.ajax('/search/', {
                'type': 'POST',
                'async': true,
                'dataType': 'json',
                'data': {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val(),
                    'input': $('#id_search').val()
                },
                'success': function(data){
                    var resultsContainer = document.getElementById('results');

                    resultsContainer.innerHTML = '';

                    resultsContainer.innerHTML = data.results;
                },
                'error': function(xhr, status, error){
                    console.error('Error in AJAX request:', status, error);
                }
            });
        }, 300);
    });
});

