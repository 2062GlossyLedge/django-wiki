$(document).ready(function () {
    // Create toggle button when toc is closed
    let flagToggled = $("<span class='f-s-t-c'>Page Flagged for Spoilers</span>")
    let flag = $('#f-s-t');

    // Toggle between open and closed states
    $(document).on('click', '#f-s-t', function () {
        $(this).replaceWith(flagToggled);

    });

    $(document).on('click', '#f-s-t-c', function () {
        $(this).replaceWith(flag);
    });

});