var logoutGmail = function(){
    window.open('https://www.google.com/accounts/Logout?continue=https://appengine.google.com/_ah/logout?continue=http://localhost:8000/', '_self');
}

// Enter a client ID for a web application from the Google Developer Console.
// The provided clientId will only work if the sample is run directly from
// https://google-api-javascript-client.googlecode.com/hg/samples/authSample.html
// In your Developer Console project, add a JavaScript origin that corresponds to the domain
// where you will be running the script.
var clientId = '984176055001-8d2phedubon1coodjcrti1m0r198mp7a.apps.googleusercontent.com';

// Enter the API key from the Google Develoepr Console - to handle any unauthenticated
// requests in the code.
// The provided key works for this sample only when run from
// https://google-api-javascript-client.googlecode.com/hg/samples/authSample.html
// To use in your own application, replace this API key with your own.
var apiKey = 'AIzaSyBWD6GSRwVl4lDZHFuzzPsRPb9cG0f8vKc';

// To enter one or more authentication scopes, refer to the documentation for the API.
var scopes = 'https://www.googleapis.com/auth/calendar';

// Use a button to handle authentication the first time.
function handleClientLoad() {
    gapi.client.setApiKey(apiKey);
    window.setTimeout(checkAuth,1);
}

function checkAuth() {
    gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, handleAuthResult);
}


function handleAuthResult(authResult) {
    if (authResult && !authResult.error) {
        getGoogleEvents();
    } else {
        alert("Couldn't authorize")
    }
}

function handleAuthClick(event) {
    gapi.auth.authorize({client_id: clientId, scope: scopes, immediate: false}, handleAuthResult);
    return false;
}

// Load the API and make an API call.  Display the results on the screen.
function getGoogleEvents() {

    var request = gapi.client.request({
        'path': '/calendar/v3/users/me/calendarList',
    });
    request.execute(function (resp) {
        $.each(resp.items, function (index, dat){
            if(dat.id.indexOf("#") == -1){
                var restRequest = gapi.client.request({
                    'path': '/calendar/v3/calendars/'+dat.id+'/events',
                    'params': {'timeMax': '2014-01-01T16:00:00-04:00', 'timeMin': '2013-02-01T16:00:00-04:00'}
                });

                restRequest.execute(function(resp) {
                    gcal(resp);
                });
            }
        });
    });
}

