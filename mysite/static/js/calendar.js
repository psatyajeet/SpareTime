$("#notificationButton").show()
$("#dLabel").show()

$(document).ready(function(){
    var scrollBar = $('#scrollbar1');
    scrollBar.tinyscrollbar({wheel: 34});
    scrollBar.tinyscrollbar_update(272);
    if (format == "weekly")
        $("#monthlyCalendar").hide();
    else
        $("#weeklyCalendar").hide();
    if (hasNotification==true){
        addExclamation($('#notificationButton').parent(), "notificationExclamation");
    }

    $('#modal-repeat').hide()
    if($("#repeatEventsCheckbox").is(':checked')){
        $('#modal-repeat').show()
        if($('#repeat-option-time-period').val()=="daily"){
            $('#repeat-daily').show()
        }
        else if($('#repeat-option-time-period').val()=="weekly"){
            $('#repeat-weekly').show()
        }
        else if($('#repeat-option-time-period').val()=="monthly"){
            $('#repeat-monthly').show()
            if($('#dayweek').is(':checked')){
                $('#repeat-by-info').show();
            }
        }
        else if($('#repeat-option-time-period').val()=="yearly"){
            $('#repeat-yearly').show()
        }
    }
    else{
        $('#modal-repeat').hide()
        $('#repeat-daily').hide()
        $('#repeat-weekly').hide()
        $('#repeat-monthly').hide()
        $('#repeat-yearly').hide()
    }

    $('#repeatEventsCheckbox').change(function (){
        $('#modal-repeat').hide()
        if($(this).is(':checked')){
            $('#modal-repeat').show()
            if($('#repeat-option-time-period').val()=="daily"){
                $('#repeat-daily').show()
            }
            else if($('#repeat-option-time-period').val()=="weekly"){
                $('#repeat-weekly').show()
            }
            else if($('#repeat-option-time-period').val()=="monthly"){
                $('#repeat-monthly').show()
            }
            else if($('#repeat-option-time-period').val()=="yearly"){
                $('#repeat-yearly').show()
            }
        }
        else{
            $('#modal-repeat').hide()
            $('#repeat-daily').hide()
            $('#repeat-weekly').hide()
            $('#repeat-monthly').hide()
            $('#repeat-yearly').hide()
        }
    });

    $('#repeat-option-time-period').change(function (){
        $('#repeat-daily').hide()
        $('#repeat-weekly').hide()
        $('#repeat-monthly').hide()
        $('#repeat-yearly').hide()
        if($(this).val()=="daily"){
            $('#repeat-daily').show()
        }
        else if($(this).val()=="weekly"){
            $('#repeat-weekly').show()
        }
        else if($(this).val()=="monthly"){
            $('#repeat-monthly').show()
        }
        else if($(this).val()=="yearly"){
            $('#repeat-yearly').show()
        }
    });

    $('#daymonth').change(function(){
        if($(this).is(':checked')){
            $('#repeat-by-info').hide();
        }
        else
        {
            $('#repeat-by-info').show();
        }
    });

    $('#dayweek').change(function(){
        if($(this).is(':checked')){
            $('#repeat-by-info').show();
        }
        else
        {
            $('#repeat-by-info').hide();
        }
    });

});


$("#repeatPopover").popover()

var clearModal = function () {
    $("#eventName").val("");
    $("#eventDescription").val("");
    $("#eventLocation").val("");
    $('#editEvent').hide();
    $('#deleteEvent').hide();
    $('#acceptEvent').hide();
    $('#rejectEvent').hide();

    $("#modalEventEditable").show();
    $("#modalEventNotEditable").hide();

    $("#commentTextBox").val("");
    $(".friendComplete").val("");

    $('#modal-repeat').hide();
    $('#repeat-daily').hide();
    $('#repeat-weekly').hide();
    $('#repeat-monthly').hide();
    $('#repeat-by-info').hide();
    $('#repeat-yearly').hide();

    $('#repeatEventsCheckbox').attr('checked', false);
    $('#repeat-option-time-period').val('daily');


    $('#dinterval').val('1');
    $('#dNever').prop('checked', false);
    $('#dAfter').prop('checked', false);
    $('#dafterOccurrences').val('');
    $('#dOn').prop('checked', false);
    $('#donEndRepeat').val('');

    $('#winterval').val('1');
    $('[name="repeatOn"]').prop('checked', false);
    $('#wNever').prop('checked', false);
    $('#wAfter').prop('checked', false);
    $('#wafterOccurrences').val('');
    $('#wOn').prop('checked', false);
    $('#wonEndRepeat').val('');

    $('#minterval').val('1');
    $('#daymonth').prop('checked', true);
    $('#dayweek').prop('checked', false);
    $('#weekinmonth').val('1');
    $('#mNever').prop('checked', false);
    $('#mAfter').prop('checked', false);
    $('#mafterOccurrences').val('');
    $('#mOn').prop('checked', false);
    $('#monEndRepeat').val('');

    $('#yinterval').val('1');
    $('#yNever').prop('checked', false);
    $('#yAfter').prop('checked', false);
    $('#yafterOccurrences').val('');
    $('#yOn').prop('checked', false);
    $('#yonEndRepeat').val('');
}

var gcal = function(resp) {
    $.post('gcal', {'responseJSON' : JSON.stringify(resp)}, function (data, status) {
    }).done(function() {
            populateEvents();
        });
}


$("#gcal").click(gcal);



var changeFormat = function(newFormat) {
    $.get('changeFormat', {'format': newFormat}, function (data, status) {
        uncolorCells();
        removeToolTips();
        format = newFormat;
        formatCalendar(format, data);
    }, "json").done( function() {

            populateEvents();

        });};


$("#weeklyButton").click(function() {
    $("#monthlyCalendar").hide();
    $('.event').remove();
    $("#weeklyCalendar").show();
    format = "weekly";
    changeFormat("weekly");
});

$("#monthlyButton").click(function() {
    format = "monthly";
    changeFormat("monthly");
    $("#monthlyCalendar").show();
    $("#weeklyCalendar").hide();
});



var invitedFriendsID = [];
var nonRemovedFriends = [];

var addFriend = function(item) {
    var $invited = $('.invitedFriends');
    var $friendComplete = $('.friendComplete');
    $invited.append('<span class="invitedFriend" ><span>' + item + '</span><span class="friendCloseBox">X</span></span>');
    $friendComplete.val("");
    var index = friendNames.indexOf(item);
    invitedFriendsID.push(friends[index].id);
    index = nonRemovedFriends.indexOf(item);
    nonRemovedFriends.splice(index, 1);
}

$(document).on('click', '.friendCloseBox', function() {
    var name = $(this).siblings().html();
    var index = friendNames.indexOf(name);
    var index2 = invitedFriendsID.indexOf(friends[index].id);
    invitedFriendsID.splice(index2, 1);
    $(this).parent().remove();
    nonRemovedFriends.push(name);
});

$('.friendComplete').typeahead({
    source: function() {
        $("#InvitedNotif").hide()
        $("#InvitedNotifError").hide()
        return nonRemovedFriends;
    },
    'updater': addFriend,
    open: function (event, ui) {
        $('.ui-autocomplete').css('z-index', '99999');
    }});


$('#friendModal').modal({'show': false, 'keyboard': true});

$('#friendModal').on('shown', function() {
    $('.friendComplete').val("");
    $('.friendComplete').focus();
});

$("#chooseFriendsCancel").on("click", function() {
    $('#friendModal').modal('hide');
});

$("#showFriendAvailability").on("click", function() {
    $("#monthlyCalendar").hide();
    $('.event').remove();
    $("#weeklyCalendar").show();
    format = "weekly";
    changeFormat("weekly");

    $('#friendModal').modal('hide');

    if (invitedFriendsID.length > 0) {
        var inputData = JSON.stringify(invitedFriendsID);
        $.post('heatMap', {'data': {'param': inputData}}, function (data, status) {
            var values = [];
            var busy = [];
            $.each(data, function(index, dat) {
                values.push(dat.ratios);
                busy.push(dat.busy);
            });
            if (busy.length === 0) {
                uncolorCells();
                removeToolTips();
                showBlackScreen(false);
            } else {
                showBlackScreen(true);
                colorCells(values);
                removeToolTips()
                addToolTips(busy);
            }
        }, "json");
    }
});

var clearFriends = function() {
    $('.invitedFriends').html("");
    invitedFriendsID = [];
    nonRemovedFriends = friendNames.slice(0);
}

$("#addFriends").on("click", function() {
    clearFriends();
    $("#friendModal").modal('show');
});

// test make event button
$("#makeEvent").on("click", function() {
    clearModal();
    $('#createEvent').show();
    $('a[href=#eventInformationTab]').tab('show');
    $('#deleteEvent').hide();
    $('#editEvent').hide();
    $('#deleteEventThis').hide();
    $('#editEventThis').hide()

    $('#eventModal').modal();
    $('#eventModal').on('shown', function(){
        $('#eventName').focus();
    });
    $("#startTime").val("");
    $("#endTime").val("");
});

var $cells = $(".calendarEntry, .calendarHalfHour");

var showBlackScreen = function(validFriends) {
    var $black = $('#blackScreen');

    if (validFriends) {
        $('#noValidFriends').hide();
        $('#validFriends').show();
    } else {
        $('#noValidFriends').show();
        $('#validFriends').hide();
    }
    var $calendar = $('.overview').parent();
    $black.show();
    $calendar.hide();

    $black.on('click', function() {
        $black.hide();
        $calendar.show();
        $('.event').remove();
        populateEvents();
    });
}

var colorCells = function(values) {

    $cells.each(function(index, cell) {

        $(cell).css("background-color", "hsl("+(Math.floor(120*values[index]))+", 70%, 65%)");
    });
};

var addToolTips = function(values) {
    $cells.each(function(index, cell) {

        $child = $(cell).children().first();
        var cantCome = '<em>Unavailable Friends:</em><br>';
        var count = 0;
        $.each(values[index], function(index2, id) {

            /* var top = friends.length;
             var bot = 0;
             var i = Math.floor(top/2);
             // Binary Search
             while (friends[i].id != id && top!=bot) {
             var intID1 = parseInt(friends[i].id);
             var intID2 = parseInt(id);
             if (intID1 > intID2) {
             top = i;
             i = Math.floor((bot + i) /2);
             } else {
             bot = i;
             i = Math.ceil((top + i) / 2);
             }
             }*/

            cantCome += (id)+'<br>';
            count++;
        });
        if (count == 0)
            cantCome += 'None';
        var place = 'right';
        if (index % 7 > 3)
            place = 'left';
        $child.tooltip({html: true, title: cantCome, placement: place, container: "body"});
    });
};

var uncolorCells = function() {
    $cells.css("background-color", "");
    invitedFriendsID = [];
}

var removeToolTips = function(values) {
    $cells.each(function(index, cell) {

        $child = $(cell).children().first();
        $child.tooltip('destroy');
    });
};



