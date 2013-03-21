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


var $cells = $(".calendarEntry, .calendarHalfHour");
var startx = 0
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

$cells.on("mouseover", function(eventObject) {
    eventObject.preventDefault();
    var index = $cells.index($(this));
    var hour = parseInt(index/7);
    if (eventObject.which == 1) {
        topY = $reference.offset().top;
        bottomY = $reference.offset().top+$(this).height();

        var height = (hour-starty);

        if (height >= 0) {
            $dragged.height($(this).offset().top+$(this).height() +
                2*borderWidth - topY);
            $dragged.offset({top: topY});

            startHour = starty;
            endHour = (starty+1+height);
        } 
        if (height < 0) {
            $dragged.height(bottomY - $(this).offset().top + 2*borderWidth);
            $dragged.offset({top: $(this).offset().top});

            startHour = (starty+height);
            endHour = (starty+1);
        }


    }
});

$cells.on("mouseup", function(eventObject) {
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

        $('#eventModal').modal();
    }

    starty = -1;
});
