var homepage = false;

window.fbAsyncInit = function() {
    FB.init({
      appId      : '329753420461644', // Local App ID
      //appId      : '122925221235344', // Heroku App ID
      status     : true, // check login status
      cookie     : true, // enable cookies to allow the server to access the session
      xfbml      : true  // parse XFBML
    });

FB.getLoginStatus(function(response) {
    if (response.status === 'connected') {
        if(homepage) {
              homepage = false;
                FB.api('/me', function(response) {
                    makeUser(response.name, response.id);
                return;
            })        
        } else {
            FB.api('/me', function(response) {
              $.post('makeUser', {'name' : response.name, 'fbid': response.id}, function (data, status) {
                if(JSON.parse(data)[0]) {populateEvents();}})
            }) 
            
            ShowMyName();
            $loginButton = $("#loginButton");
            $loginButton.html("Logout");
            $loginButton.attr("id", "logoutButton");   
        }
    } else if (response.status === 'not_authorized') {
        $.get('deleteCookie', function (data, status) {}).done(function() {
        }).done(function() {
            if(!homepage) {
                location.reload(true);
            }
        });
    } else {
        $.get('deleteCookie', function (data, status) {}).done(function() {
        }).done(function() {
            if(!homepage) {
                location.reload(true);
            }
        });
    }
});
};

function login() {
    FB.login(function(response) {
        if (response.authResponse) {
            FB.api('/me', function(response) {
                makeUser(response.name, response.id);
            })
            $("#loginButton").html("Logout");
            $("#loginButton").attr("id", "logoutButton");

        } else {
            // cancelled
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

var changeFormat = function(newFormat) {
    $.get('changeFormat', {'format': newFormat}, function (data, status) {
            format = newFormat;
            formatCalendar(format, data);
            }, "json").done( function() {
                populateEvents();

                });};

function makeUser(name, id) {
    $.post('makeUser', {'name' : name, 'fbid': id}, function (data, status) {
    }).done(function() {
                location.reload(true);
                });
}
  // Load the SDK Asynchronously
  (function(d){
     var js, id = 'facebook-jssdk', ref = d.getElementsByTagName('script')[0];
     if (d.getElementById(id)) {return;}
     js = d.createElement('script'); js.id = id; js.async = true;
     js.src = "//connect.facebook.net/en_US/all.js";
     ref.parentNode.insertBefore(js, ref);
   }(document));



var friends;
var friendNames = [];

function ShowMyName() {
    FB.api('/me/friends', function(response) {
        if(response.data) {
            friends = response.data;
            $.each(response.data, function(index, friend) {
                friendNames.push(friend.name);
                });
        } else {
            console.log("Error!");
        }
    });         
    }

$(document).on("click", "#loginButton", function() {
    login();
});

$(document).on("click", "#logoutButton", function() {
    logout();
    $(this).html("Log In");
    $(this).attr("id", "loginButton");
});
