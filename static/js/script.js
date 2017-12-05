$(function() {
    $('input').click(function() {
        // var user = $('#txtUsername1').val();
        // var pass = $('#txtPassword1').val();
        $.ajax({
            url: '/AloUser',
            data: $('.KekForm').serialize(),
            type: 'POST',
            success: function(response) {
                console.log(response);
            },
            error: function(error) {
                console.log(error);
            }
        });
    });
});

