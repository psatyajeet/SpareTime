var currentlyViewing = -1;
var currentlyMoving = -1;
var currentlyMovingY = 0;
var currentlyClicking = -1;
var canEdit = true;
var currentlyMovingStart = new Date();
var currentlyMovingEnd = new Date();


function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    crossDomain: false, // obviates need for sameOrigin test
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type)) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

var notifications = "";

var getNotifications = function() {
    notifications = "";
    $.ajax({
        type: "GET",
        url: 'getNotificationsRequest',
        async: false,
        success: function (data, status) {
        $popover = $('#notificationButton');

        $.each(data, function (index, dat) {
            creators = ''
            $.each(dat.creators, function (index, c) {creators = creators + c.name + ' '});
            var notify = '<div class="alert alert-info requestAlert eventID'+dat.id+'"> '+
                '<p>You have a new event request: '+dat.title+ ' from :' + creators + '</p> '+
                '<div class="row-fluid"> '+
                '<div class="span6"> '+
                '<button class="btn btn-block btn-success acceptRequest eventID'+dat.id+'" type="button">Accept</button> '+
                '</div> '+
                '<div class="span6"> '+
                '<button class="btn btn-block btn-danger rejectRequest eventID'+dat.id+'" type="button">Reject</button>      '+
                '</div> '+
                '</div> '+
                '</div>';
            notifications += notify;
//            var $acceptButtons = $('.acceptRequest').last();
//            var $rejectButtons = $('.rejectRequest').last();
//            $($acceptButtons.get(index)).on('click', function(e) {
//                acceptNotification(dat.id);
//                $notify.remove();
//            });
//            $($rejectButtons.get(index)).on('click', function(e) {
//                rejectNotification(dat.id);
//                $notify.remove();
//            });
            
        });


    }, 
    dataType: "json"});
};

var latestNotification = function() {
    getNotifications();
    return notifications;
};

var populateEvents = function() {
    if (format == "weekly")
        populateWeekEvents();
    else
        populateMonthEvents();
};


var populateMonthEvents = function() {
    $.get('populateMonthEvents', function (data, status) {
        $monthEntries = $(".calendarMonthEntry");
        var numEvents = [];
        for (i = 0; i < $monthEntries.length; i++) {
            numEvents[i] = [];
        }
        $(".monthEvent, .monthExtra").remove();
        for (var i = 0; i < data.length; i++) {
            $entry = $($monthEntries.get(data[i].day)).children();
            if ($entry.children().length >= 2) {
                numEvents[parseInt(data[i].day)].push(data[i]);
            } else {
                $monthEvent = $('<div id="'+data[i].id+'" class="monthEvent">'+data[i].title+'</div>');
                $entry.append($monthEvent);
            }
        }

        for (i = 0; i < $monthEntries.length; i++) {
            
            if (numEvents[i].length > 0) {
                    $popover = $('<a href="#" onclick="return false" class="popoverMonthlyEvent" rel="popover" data-title="More Events" data-toggle="popover" data-placement="right" title="">+ '+numEvents[i].length+' More</a>');
                    $extra = $('<div class="monthExtra"></div>');
                    $extra.html($popover);
                    $entry.append($extra);
                    monthEvents = "";
                    for (var j = 0; j < numEvents[i].length; j++) {
                        monthEvents += '<div id="'+numEvents[i][j].id+'" class="monthEvent">'+numEvents[i][j].title+'</div>';
                    }
                    $popover.popover({html: true, trigger: 'manual', content: monthEvents, position: 'on right'});


                    var canClosePopover = true;
                    var onPopoverLink = false;

                    $popover.on("mouseenter", function() {
                        onPopoverLink = true;
                        $(this).popover('show');
                        var $pop = $(this);
                        canClosePopover = true;

                        $(this).next().on("mouseenter", function() {
                            canClosePopover = false;
                        });
                        $(this).next().on("mouseleave", function() {
                            if (!onPopoverLink) {
                                setTimeout(function() {
                                    if (!onPopoverLink)
                                    $pop.popover('hide');
                                canClosePopover = true;
                                }, 250);
                            }
                        });

                    });

                    $popover.on("mouseleave", function() {
                        var $pop = $(this);
                        onPopoverLink = false;
                        setTimeout(function() {
                            if (canClosePopover && !onPopoverLink)
                                $pop.popover('hide');
                        }, 250);
                    });
            }
        }

        $(document).on('click', '.monthEvent', function (){
            openID($(this).attr('id'));
            return false;
        });
    }, "json");
};

var populateWeekEvents = function() {
    processEvents = function(data, status) {
        $('.event').remove();
        $overview = $('.overview');
        var x = $('.hourEntry').width();
        var widths = [7];
        $entries = $('.calendarEntry');
        for(var i = 0; i < 200; i++) {
            widths[i] = $($entries.get(i)).width();
        }
        var cumWidths = [7];
        $entries = $('.calendarEntry');
        var reference = $('.overview').offset().left;
        for(var i = 0; i < 7; i++) {
            cumWidths[i] = $($entries.get(i)).offset().left-reference;
        }
        var height = $('.calendarEntry').height();
        var eventBorderWidth = 4;
        var cellBorderWidth = 1;
        var bufferWidth = 4;
        $.each(data, function(index, dat) {
            if (dat.notif)
                $div = $('<div class="event notif" id="'+dat.id+'"><p>'+dat.title+'</p></div>');
            else {
                if (dat.canEdit)
                    $div = $('<div class="event canEdit" id="'+dat.id+'"><p>'+dat.title+'</p></div>');
                else
                    $div = $('<div class="event" id="'+dat.id+'"><p>'+dat.title+'</p></div>');
            }
            $div.height((height+cellBorderWidth)*(dat.end - dat.start)*2-bufferWidth-eventBorderWidth);
            $div.width((widths[dat.day])*dat.width-eventBorderWidth-bufferWidth);
            $div.offset({top: (height+cellBorderWidth)*dat.start*2, 
                left: cumWidths[dat.day]+widths[dat.day]*dat.x + 1});
            $div.css('z-index', index);

            //left: x + cumWidths[dat.day]+widths[dat.day]*dat.x + 
            //    borderWidth*(dat.day+3)});

            $overview.prepend($div);
    });


    $('.event').off('click');
    $('.event').off('mousedown');
    $('.event').off('mouseup');
    $('.event').off('mousemove');
    $('.event').on('mousedown', function(event){
        event.preventDefault();
        currentlyClicking = 1;

        currentlyMoving = $(this).attr("id");
        currentlyMovingID = $(this).attr("id")
        $.post('getEventData', {"id": currentlyMovingID}, function (data, status) {
            currentlyMovingEnd = new Date(data.endms);
            currentlyMovingStart = new Date(data.startms);
        }, 'json');
        currentlyMovingY = event.pageY - $(this).offset().top;

        if (-1 == $(this).attr("class").indexOf("notif")) {
            canEdit = true;
        } else {
            canEdit = false;
        }

    });
    $('.event').on('click', function (){
        if (currentlyClicking == 1) {
            openID($(this).attr('id'));
        }
        return false;
    });
    $('.event').on('mousemove', function (event){
        var x = event.pageX;
        var y = event.pageY-currentlyMovingY;

        $cells.each(function(index) {
            if (y >= $(this).offset().top && 
                y <= $(this).offset().top + $(this).height() + borderWidth&&
                x >= $(this).offset().left && 
                x <= $(this).offset().left + $(this).width() + borderWidth) {
                currentlyClicking = -1;
                tableOver($(this), event);
            }
        });
        if (canEdit && currentlyClicking == -1 && currentlyMoving == $(this).attr("id")) {
            $(this).width($cells.width());
            $(this).attr("class", "event movingEvent");
        }

    });
    $('.event').on('mouseup', function (event){
        var x = event.pageX;
        var y = Math.max(event.pageY-currentlyMovingY, $cells.offset().top);
        var called = false;
        $cells.each(function(index) {
            if (y >= $(this).offset().top && 
                y <= $(this).offset().top + $(this).height() + borderWidth &&
                x >= $(this).offset().left && 
                x <= $(this).offset().left + $(this).width() + borderWidth) {
                tableUp($(this), event);
                called = true;
            }
        });
        if (!called) {
            currentlyMoving = -1;
            populateEvents();
            tableUp(null, event);
        }
        currentlyMovingY = 0
        return false;
    });
    };


    $.get('populateEvents', function (data, status) {
        /*$.get('getNotificationsRequests', function (data2, status) {
            data = data2.concat(data);
            processEvents(data, status)
        }, "json");*/
        processEvents(data, status)
    }, "json");

};

$(document).on('click', '.requestAlert', function(e) {
    var classes = $(this).attr('class');
    var eventID = "eventID"
    var substr = classes.substr(classes.indexOf(eventID) + eventID.length);
    var first = substr.split()[0];

    $.post('goToEvent', {"id": first}, function (data, status) {
        formatCalendar("weekly", data);
    }, "json").done(function() {
        populateEvents();
    });
});

var acceptRequest = function($object) {
    var classes = $object.attr('class');
    var eventID = "eventID"
    var substr = classes.substr(classes.indexOf(eventID) + eventID.length);
    var first = substr.split()[0];
    acceptNotification(first);
    var container = $object.parent().parent().parent();
    container.slideUp();
};

$(document).on('click', '.acceptRequest', function(e) {
    acceptRequest($(this));
});

$(document).on('click', '#acceptEvent', function(e) {
    $('#eventModal').modal('hide');
    acceptNotification(currentlyViewing);
});


var rejectRequest = function($object) {
    var classes = $object.attr('class');
    var eventID = "eventID"
    var substr = classes.substr(classes.indexOf(eventID) + eventID.length);
    var first = substr.split()[0];
    rejectNotification(first);
    var container = $object.parent().parent().parent();
    container.slideUp();
}

$(document).on('click', '.rejectRequest', function(e) {
    rejectRequest($(this));
});

$(document).on('click', '#rejectEvent', function(e) {
    $('#eventModal').modal('hide');
    rejectNotification(currentlyViewing);
});

var openID = function(id) {
    clearModal();

    $.post('getEventData', {"id": id}, function (data, status) {
        $("#eventName").val(data.title);
        $("#eventDescription").val(data.description);
        $("#eventLocation").val(data.location);
        $("#startTime").val(data.start);
        $("#endTime").val(data.end);

        $('#createEvent').hide();
        $('#eventURL').show();
        var url = document.URL+'?id='+id;
        $('#eventURL').html('<a href="'+url+'">'+url+'</a>');

        if(data.canEdit) {
           $('#editEvent').show();
           $('#deleteEvent').show();
           if(data.repeat){
               $('#deleteEventThis').show();
           } else {
                $('#deleteEventThis').hide();
           }
        } else {
            if (data.notif) {
                $('#acceptEvent').show();
                $('#rejectEvent').show();
                $('#deleteEventThis').hide();
            }else{
                $('#deleteEvent').show();
                $('#deleteEventThis').hide();
            }
        } 
        $('#eventModal').modal();
        $('a[href=#eventInformationTab]').tab('show');
        $('#eventModal').on('shown', function(){                    
            $('#eventName').focus();
        });
        document.getElementById(data.kind).checked = true
        
        currentlyViewing = data.id;

    }, "json");
}

var refreshComments = function () {
    $.get('getComments',{'id': currentlyViewing}, function(data, status) {
        $commentSpace = $('#commentSpace');
        insideComments = "";
        $.each(data, function(index, dat) {
            insideComments += '<div class="comment alert alert-info"><span class="commentName">'+dat.name+':</span> '+dat.comment+'</br><div class="commentDate">'+dat.date+'</div></div>';
        });
        $commentSpace.html(insideComments);
    }, "json");
};


$(document).ready(function(){
    populateEvents();

    getNotifications();
    $popover = $('#notificationButton');
    $popover.popover({title: "Notifications", placement: "bottom", html: true, content: function() {return latestNotification()} });

    $('#modalComments').hide();
    $('#modalPeople').hide();
    $('a[href=#peopleTab]').on('shown', function (e) {
        $('#modalEventInformation').hide();
        $('#modalComments').hide();
        $('#modalPeople').show();
        $.get('getPeople', {'id': currentlyViewing}, function (data, status) {
            var filler = '';
            $.each(data.creators, function(index, dat) {
                filler += dat.name + '<br>';
            });
            $('#createdEvent').html(filler);

            filler = '';
            $.each(data.coming, function(index, dat) {
                filler += dat.name + '<br>';
            });
            $('#comingToEvent').html(filler);

            filler = '';
            $.each(data.rejected, function(index, dat) {
                filler += dat.name + '<br>';
            });
            $('#notComingToEvent').html(filler);

            filler = '';
            $.each(data.unanswered, function(index, dat) {
                filler += dat.name + '<br>';
            });
            $('#needToRespondToEvent').html(filler);

        }, 'json');
    });

    $('a[href=#eventInformationTab]').on('shown', function (e) {
        $('#modalEventInformation').show();
        $('#modalComments').hide();
        $('#modalPeople').hide();
    });

    $('a[href=#commentsTab]').on('shown', function (e) {
        $('#modalEventInformation').hide();
        $('#modalPeople').hide();
        $('#commentTextBox').val("");
        $('#modalComments').show();
        refreshComments();

        })
    $('#postComment').on('click', function (e) {
        $.post('comment',{'id': currentlyViewing, 'comment': $('#commentTextBox').val()}, function(data, status) {
            refreshComments();
        }, "json");
        });

});

var updateCalendar = function(amount) {

    uncolorCells();
    removeToolTips();
    if (format === "monthly") {
        $.post('changeMonth', {"amount": amount}, function (data, status) {
            formatCalendar("monthly", data);
        }, "json").done(function() {
            populateMonthEvents();
        });
    } else {
        $.post('changeWeek', {"amount": amount}, function (data, status) {
            formatCalendar("weekly", data);
        }, "json").done(function() {
            populateEvents();
        });
    }
};

var formatCalendar = function(format, data) {
    if (format === "monthly") {
        $("#weekname").html(data.header);
        $month = $(".calendarMonthTable");
        html = ''

            html += '<table><tbody>'; 
        for (var i = 0; i < data.weeks.length; i++) {
            html += '<tr class="calendarRow">'; 
            for (var j = 0; j < data.weeks[i].length; j++) {

                html += '<td class="calendarMonthEntry'; 
                    if (data.weeks[i][j].today)
                        html += ' calendarToday';
                if (!data.weeks[i][j].thisMonth)
                    html += ' otherMonth';
                html += '" width="14.3%">'+data.weeks[i][j].date+'<div></div></td>'; 
            }
            html += '</tr>'; 
        }
        html += '</tbody></table>'; 

        $month.html(html);

        var $monthCells = $(".calendarMonthEntry");

        $monthCells.on("mousedown", function(event) {
            event.preventDefault();
        });


    } else {
        $("#weekname").html(data.header);
        $.each(data.dates, function(index, date) {
            dates[index] = new Date(date.year,
                date.month,
                date.day);
        });
        var $cells1 = $(".calendarEntry");
        var $cells2 = $(".calendarHalfHour");
        $cells1.removeClass("calendarToday");
        $cells2.removeClass("calendarToday");

        var hasToday = -1;
        $(".headings.weekly").each(function(index) {
            $(this).html(data.days[index].title);
            if (data.days[index].today === true) {
                hasToday = index;
            }
        });


        if (hasToday >= 0) {
            $cells1.each(function(index) {
                if (index % 7 == hasToday)
                $(this).addClass("calendarToday");
            });
            $cells2.each(function(index) {
                if (index % 7 == hasToday)
                $(this).addClass("calendarToday");
            });
        }
    }
};

$("#calendarBack").click(function() {updateCalendar(-1)});
$("#calendarToday").click(function() {updateCalendar(0)});
$("#calendarForward").click(function() {updateCalendar(1)});



var createEvent = function() {
    d = invitedFriendsID;
    var radios = document.getElementsByName('optionsRadios');
    var kind = 'PR'
    for (var i = 0, length = radios.length; i < length; i++) {
        if (radios[i].checked) {
            kind = (radios[i].value);
        }
    }

    if ($("#repeatEventsCheckbox").is(':checked')){
        var rrule='RRULE:';
        if($('#repeat-option-time-period').val()=="daily"){
            rrule+='FREQ=DAILY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            rrule+=';INTERVAL='+$("#interval").val();
        }
        else if($('#repeat-option-time-period').val()=="weekly"){
            rrule+='FREQ=WEEKLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
            var byday='';
            if ($('$SU').is(':checked')){
                byday+='SU';
            }
            if ($('$MO').is(':checked')){
                byday+='MO';
            }
            if ($('$TU').is(':checked')){
                byday+='TU';
            }
            if ($('$WE').is(':checked')){
                byday+='WE';
            }
            if ($('$TH').is(':checked')){
                byday+='TH';
            }
            if ($('$FR').is(':checked')){
                byday+='FR';
            }
            if ($('$SA').is(':checked')){
                byday+='SA';
            }
            if (byday!='')
                rrule+=';'+'BYDAY='+byday;
        }
        else if($('#repeat-option-time-period').val()=="monthly"){
            rrule+='FREQ=MONTHLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
            if ($("#dayweek").is(':checked')){
                rrule+=';BYDAY='+$("#weekinmonth").val();
                if ($('$SU').is(':checked')){
                    rrule+='SU';
                }
                if ($('$MO').is(':checked')){
                    rrule+='MO';
                }
                if ($('$TU').is(':checked')){
                    rrule+='TU';
                }
                if ($('$WE').is(':checked')){
                    rrule+='WE';
                }
                if ($('$TH').is(':checked')){
                    rrule+='TH';
                }
                if ($('$FR').is(':checked')){
                    rrule+='FR';
                }
                if ($('$SA').is(':checked')){
                    rrule+='SA';
                }
            }
        }
        else if($('#repeat-option-time-period').val()=="yearly"){
            rrule+='FREQ=YEARLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
        }
    }
    $.post('submitEvent', {"title": $("#eventName").val(), 
        "description": $("#eventDescription").val(),
        "location": $("#eventLocation").val(),
        "startTime": $("#startTime").val(),
        "endTime": $("#endTime").val(), 
        "RRULE": rrule,
        "friendIDs": JSON.stringify(d),
        "kind" : kind},
        "json").done(function (data, status) {
        uncolorCells();
        populateEvents();
    });
    $('#eventModal').modal('hide');
}
$("#createEvent").click(function() {createEvent()});

var deleteEvent = function(deleteAll) {
    $.post('deleteEvent', {"id": currentlyViewing, "all" : deleteAll}, 
            "json").done(function (data, status) {
        populateEvents();
    });
    $('#eventModal').modal('hide');
}

$("#deleteEvent").click(function() {deleteEvent("all")});
$("#deleteEventThis").click(function() {deleteEvent("this")});

var editEvent = function() {
    if ($("#repeatEventsCheckbox").is(':checked')){
        var rrule='RRULE:';
        if($('#repeat-option-time-period').val()=="daily"){
            rrule+='FREQ=DAILY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            rrule+=';INTERVAL='+$("#interval").val();
        }
        else if($('#repeat-option-time-period').val()=="weekly"){
            rrule+='FREQ=WEEKLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
            var byday='';
            if ($('$SU').is(':checked')){
                byday+='SU';
            }
            if ($('$MO').is(':checked')){
                byday+='MO';
            }
            if ($('$TU').is(':checked')){
                byday+='TU';
            }
            if ($('$WE').is(':checked')){
                byday+='WE';
            }
            if ($('$TH').is(':checked')){
                byday+='TH';
            }
            if ($('$FR').is(':checked')){
                byday+='FR';
            }
            if ($('$SA').is(':checked')){
                byday+='SA';
            }
            if (byday!='')
                rrule+=';'+'BYDAY='+byday;
        }
        else if($('#repeat-option-time-period').val()=="monthly"){
            rrule+='FREQ=MONTHLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
            if ($("#dayweek").is(':checked')){
                rrule+=';BYDAY='+$("#weekinmonth").val();
                if ($('$SU').is(':checked')){
                    rrule+='SU';
                }
                if ($('$MO').is(':checked')){
                    rrule+='MO';
                }
                if ($('$TU').is(':checked')){
                    rrule+='TU';
                }
                if ($('$WE').is(':checked')){
                    rrule+='WE';
                }
                if ($('$TH').is(':checked')){
                    rrule+='TH';
                }
                if ($('$FR').is(':checked')){
                    rrule+='FR';
                }
                if ($('$SA').is(':checked')){
                    rrule+='SA';
                }
            }
        }
        else if($('#repeat-option-time-period').val()=="yearly"){
            rrule+='FREQ=YEARLY';
            if ($('#After').is(':checked')){
                rrule+=';COUNT='+$("#afterOccurrences").val();
            }
            else if ($('#On').is(':checked')){
                rrule+=';UNTIL='+$("#onEndRepeat").val();
            }
            if ($("#interval").val()!=1){
                rrule+=';INTERVAL='+$("#interval").val();
            }
        }
    }
    $.post('editEvent', {"title": $("#eventName").val(), 
        "description": $("#eventDescription").val(),
        "location": $("#eventLocation").val(),
        "startTime": $("#startTime").val(),
        "endTime": $("#endTime").val(),
        "RRULE": rrule,
        "id": currentlyViewing}, 
        "json").done(function (data, status) {
        populateEvents();
    });
    $('#eventModal').modal('hide');
}
$("#editEvent").click(function() {editEvent()});





$(function() {
    $('#datetimepicker').datetimepicker({
        language: 'en',
        pick12HourFormat: true,
        pickSeconds: false
    });
});

$(function() {
    $('#datetimepicker2').datetimepicker({
        language: 'en',
        pick12HourFormat: true,
        pickSeconds: false
    });
});

// Stop text selection on monthly calendar

var $monthCells = $(".calendarMonthEntry");

$monthCells.on("mousedown", function(event) {
    event.preventDefault();
});

var $cells = $(".calendarEntry, .calendarHalfHour");

var startx = 0;
var starty = -1;
var topY = 0;
var bottomY = 0;
var startHour = -1;
var endHour = -1;
var $dragged = $(".dragged");
var $reference;
var borderWidth = 1;
$cells.on("mousedown", function(eventObject) {
    eventObject.preventDefault();
    var index = $cells.index($(this));
    startx = index%7;
    starty = parseInt(index/7);
    startHour = starty;
    endHour = (starty+1);

    topY = $(this).offset().top;
    bottomY = $(this).offset().top+$(this).height();
    var height = (bottomY-topY+borderWidth);
    var width = ($(this).width()+borderWidth);

    $dragged.height(height);
    $dragged.width(width);
    $dragged.show();
    $dragged.offset({ top: topY+borderWidth, left: $(this).offset().left+borderWidth })
    $reference = $(this);
});

var tableOver = function(cell, eventObject) {
    if (!canEdit)
        return;
    if (starty != -1) {
        eventObject.preventDefault();
        var index = $cells.index(cell);
        var hour = parseInt(index/7);
        if (eventObject.which === 1 && $reference !== null) {
            topY = $reference.offset().top;
            bottomY = $reference.offset().top+cell.height();

            var height = (hour-starty);

            if (height >= 0) {
                $dragged.height(cell.offset().top+cell.height() +
                        2*borderWidth - topY);
                $dragged.offset({top: topY});

                startHour = starty;
                endHour = (starty+1+height);
            } 
            if (height < 0) {
                $dragged.height(bottomY - cell.offset().top + 2*borderWidth);
                $dragged.offset({top: cell.offset().top});

                startHour = (starty+height);
                endHour = (starty+1);
            }
        }
    }
    if (currentlyMoving != -1) {
        
        var index = $cells.index(cell);
        var hour = parseInt(index/7);
        var delta = hour/2.0 - (currentlyMovingStart.getHours() + currentlyMovingStart.getMinutes()/60.0);
        var newEnd = currentlyMovingEnd.getHours() + currentlyMovingEnd.getMinutes()/60.0 + delta;
        var length = currentlyMovingEnd.getHours() + currentlyMovingEnd.getMinutes()/60.0 - (currentlyMovingStart.getHours() + currentlyMovingStart.getMinutes()/60.0);
        if (newEnd <= 24) {
            $('#'+currentlyMoving).offset({top: cell.offset().top,
                left: cell.offset().left});
        } else {
            $lastCell = $($cells.get($cells.length - 7 - (length * 2 - 1)* 7 + index%7));
            $('#'+currentlyMoving).offset({top: $lastCell.offset().top,
                left: $lastCell.offset().left});
        }
    }
}


$cells.on("mouseover", function(eventObject) {
    var index = ($cells.index($(this))-Math.floor(currentlyMovingY/$cells.height())*7);
    if (index < 0) { 
        index = $cells.index($(this)) % 7;
    }
    var $cell = $($cells.get(index));
    tableOver($cell, eventObject);
});

var formatTime = function(date) {
    var time = (date.getMonth() + 1) + "/" + date.getDate()+"/";
    time += date.getFullYear() + " ";
    if (date.getHours() % 12 === 0)
        time += "12:";
    else
        time += (date.getHours()%12)+":";
    if (date.getMinutes() < 10)
        time += "0";
    time += date.getMinutes();
    if (date.getHours() < 12)
        time += " AM";
    else
        time += " PM";
    return time;
}

var tableUp = function($cell, eventObject) {
    if (!canEdit)
        return;
    if (starty != -1) {
        eventObject.preventDefault();
        $dragged.hide();

        var picker = $('#datetimepicker').data('datetimepicker');
        dates[startx].setHours(startHour/2);
        dates[startx].setMinutes(30*(startHour%2));
        picker.setLocalDate(dates[startx]);

        var picker2 = $('#datetimepicker2').data('datetimepicker');
        dates[startx].setHours(endHour/2);
        dates[startx].setMinutes(30*(endHour%2));
        picker2.setLocalDate(dates[startx]);

        clearModal();
        currentlyViewing = -1;

        $('#createEvent').show();

        $('a[href=#eventInformationTab]').tab('show');
        $('#deleteEvent').hide();
        $('#deleteEventThis').hide();
        $('#editEvent').hide();
        $('#eventURL').hide();
        $('#eventModal').modal();
        $('#eventModal').on('shown', function(){                    
            $('#eventName').focus();
        });
    }
    if (currentlyMoving != -1) {
        var index = $cells.index($cell);
        var x = index%7;
        var y = parseInt(index/7);


        var newStart = currentlyMovingStart.getHours() + currentlyMovingStart.getMinutes()/60.0;
        var delta = y/2.0 - (newStart);
        var newEnd = currentlyMovingEnd.getHours() + currentlyMovingEnd.getMinutes()/60.0 + delta;
        var length = currentlyMovingEnd.getHours() + currentlyMovingEnd.getMinutes()/60.0 - (currentlyMovingStart.getHours() + currentlyMovingStart.getMinutes()/60.0);

        // Check if the current start time pushes the event off the edge
        if (newEnd > 24) {
            y = parseInt(($cells.length - 7 - (length * 2 - 1)* 7 + index%7)/7);
        }
        if (y <= 0) {
            y = 0;
        }


        dates[x].setHours(y/2);
        dates[x].setMinutes(30*(y%2));
        var startTime = formatTime(dates[x]);

        $.post('changeStart', {"id": currentlyMovingID, "startTime": startTime}, "json");
        populateEvents()
    }
    currentlyMoving = -1;
    starty = -1;
}

$cells.on("mouseup", function(eventObject) {
    var index = $cells.index($(this)) - Math.floor(currentlyMovingY/$cells.height())*7;
    if (index < 0) { 
        index = $cells.index($(this)) % 7;
    }
    var $cell = $($cells.get(index));
    tableUp($cell, eventObject);

    return false;
});


$(document).on("mouseup", function(eventObject) {
    if (currentlyMoving != -1) {
        currentlyMoving = -1;
        populateEvents();
    }
    tableUp($(this), eventObject);
});


     
var acceptNotification = function(eventID) {
    $.post('acceptNotification', {"eventID": eventID}, "json").done(function (data, status) {
        setTimeout(function() { populateEvents();}, 250);
    });
};

var rejectNotification = function(eventID) {
    $.post('rejectNotification', {"eventID": eventID}, "json").done( function (data, status) {
        setTimeout(function() { populateEvents();}, 250);
    });
};


