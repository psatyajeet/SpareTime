var homepage = false;
var eventPage = false;
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
                  //  makeUser(response.name, response.id);
                return;
            })        
        } else if(eventPage) {
            $loginButton = $("#loginButton");
            $loginButton.html("Logout");
            $loginButton.attr("id", "logoutButton");  
        }else {
            FB.api('/me', function(response) {
              $.get('makeUser', {'name' : response.name, 'fbid': response.id}, function (data, status) {
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
            if(!homepage && !eventPage) {
                location.reload(true);
            }
        });
    } else {
        $.get('deleteCookie', function (data, status) {}).done(function() {
        }).done(function() {
            if(!homepage && !eventPage) {
                location.reload(true);
            }
        });
    }
});
};

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

var changeFormat = function(newFormat) {
    $.get('changeFormat', {'format': newFormat}, function (data, status) {
            format = newFormat;
            formatCalendar(format, data);
            }, "json").done( function() {
                populateEvents();

                });};

function makeUser(name, id) {
    $.get('makeUser', {'name' : name, 'fbid': id}, function (data, status) {
    }).done(function() {
                window.open('http://localhost:8000/', '_self');
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
var friendIDs = [];

function ShowMyName() {
    FB.api('/me/friends', function(response) {
        if(response.data) {
            friends = response.data;
            friendIDs = [];
            $.each(response.data, function(index, friend) {
                friendIDs.push(friend.id);
            });
            var inputData = JSON.stringify(friendIDs);
            $.post('getUsersWithAccount',{'id': {'param': inputData}}, function(data, status) {
                var validFriends = [];
                for (var i = 0; i < data.length; i++) {
                    validFriends.push(data[i].user);
                }
                for (var i = 0; i < friends.length; i++) {
                    if (validFriends.indexOf(friends[i].id) == -1) {
                        friends.splice(i,1);
                        i--;
                    }
                }
                friendIDs = [];
                $.each(friends, function(index, friend) {
                    friendNames.push(friend.name);
                    friendIDs.push(friend.id);
                });
                nonRemovedFriends = friendNames.slice(0);
                $('.friendComplete').removeAttr('disabled');
            }, "json");


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
