//press enter to submit query
$(document).ready(function () {
    $('#prompt').on('keypress', function (e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            $('#query-chatbot').submit();
        }
    });
});