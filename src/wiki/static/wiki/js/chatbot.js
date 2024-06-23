//press enter to submit query
$(document).ready(function () {
    styleMessages();

    $('#prompt').on('keypress', function (e) {
        if (e.which == 13 && !e.shiftKey) {
            e.preventDefault();
            $('#query-chatbot').submit();
            sendMessage();
        }
    });


    function styleMessages() {
        $('#chatbot-history p').each(function (index) {
            if (index % 2 === 0) {
                $(this).removeClass().addClass('human-message');
            } else {
                $(this).removeClass().addClass('chatbot-message');
            }
        });
    }
    // Toggle button active state
    $('#spoiler-free').click(function () {
        $(this).addClass('active').removeClass('inactive');
        $('#all-context').removeClass('active').addClass('inactive');
    });

    $('#all-context').click(function () {
        $(this).addClass('active').removeClass('inactive');
        $('#spoiler-free').removeClass('active').addClass('inactive');
    });

    // Change color on hover
    $("#spoiler-free-toggle-label").mouseenter(function () {

        $(this).css("color", "black");
    });

    $("#spoiler-free-toggle-label").mouseleave(function () {
        $(this).css("color", "#0c9c8c");
    });

    // Scrolls to the bottom of the chatbot history
    $('#chatbot-history').scrollTop($('#chatbot-history')[0].scrollHeight);

    // $('#dropdown-button').click(function () {
    //     $('#dropdown-menu').toggle();
    //     $(this).toggleClass('open');
    // });



});