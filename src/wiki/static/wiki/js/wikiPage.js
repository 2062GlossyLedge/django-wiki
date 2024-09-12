$(document).ready(function () {
    // Create toggle button when toc is closed
    let tocTitleClosed = $("<button id='toctitleclosed'>Contents</button>")
    let tocTitle = $('.toctitle');

    // Toggle between open and closed states
    $(document).on('click', '.toctitle', function () {
        $(this).replaceWith(tocTitleClosed);
        $(".list-group").toggle();
    });

    $(document).on('click', '#toctitleclosed', function () {
        $(this).replaceWith(tocTitle);
        $(".list-group").toggle();
    });

});