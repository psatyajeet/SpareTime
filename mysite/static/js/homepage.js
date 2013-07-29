$(document).ready(function(){
    $('#signupModal').modal({'show': false, 'keyboard': true});
    $('#signinModal').modal({'show': false, 'keyboard': true});

    $('#signupModal').on('shown', function() {
        $('.friendComplete').val("");
        $('.friendComplete').focus();
    });
    $('#signinModal').on('shown', function() {
        $('.friendComplete').val("");
        $('.friendComplete').focus();
    });

    $("#signupCancel").on("click", function() {
        $('#signupModal').modal('hide');
    });
    $("#signinCancel").on("click", function() {
        $('#signinModal').modal('hide');
    });
})


function login() {
    FB.getLoginStatus(function(response){
        if (response.status === 'connected') {
            $("#loginButton").html("Logout");
            $("#loginButton").attr("id", "logoutButton");
            FB.api('/me', function(response) {
                makeUser(response.name, response.id);
            })
        } else {
            FB.login(function(response) {
                if (response.authResponse) {
                    $("#loginButton").html("Logout");
                    $("#loginButton").attr("id", "logoutButton");
                    FB.api('/me', function(response) {
                        makeUser(response.name, response.id);
                    })
                } else {
                    // cancelled
                }
            });
        }
    });
}

function logout() {
    $.get('deleteCookie', function (data, status) {}).done(function() {
        location.reload(true)
    });

    FB.logout(function(response) {
    });

}

