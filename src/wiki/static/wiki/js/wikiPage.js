// $(document).ready(function () {
//     // Create toggle button when toc is closed
//     // let flagToggled = $("<span class='f-s-t-c'>Page Flagged for Spoilers</span>")
//     // let flag = $('#f-s-t');

//     // // Toggle between open and closed states
//     // $(document).on('click', '#f-s-t', function () {
//     //     $(this).replaceWith(flagToggled);

//     // });

//     // $(document).on('click', '#f-s-t-c', function () {
//     //     $(this).replaceWith(flag);
//     // });

// });
// $(document).on('click', '#flag-spoilers-button-off, #flag-spoilers-button-on', function (event) {
//     event.preventDefault();  // Prevent form submission/reload

//     var $button = $(this);  // Store reference to the clicked button

//     $.ajax({
//         type: "POST",
//         url: "",  // Your form's action URL
//         data: $button.closest('form').serialize(),  // Serialize the form data
//         success: function (response) {
//             if ($button.attr('id') === 'flag-spoilers-button-off') {
//                 $button.html('<span class="fa fa-flag"></span> Page flagged for spoilers')
//                     .attr('id', 'flag-spoilers-button-on')
//                     .removeClass('btn-warning')
//                     .addClass('btn-danger');
//             } else {
//                 $button.html('<span class="fa fa-flag"></span> Flag Spoilers')
//                     .attr('id', 'flag-spoilers-button-off')
//                     .removeClass('btn-danger')
//                     .addClass('btn-warning');
//             }
//         }
//     });
// });
