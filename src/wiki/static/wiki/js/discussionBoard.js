function submitPost(content, article_id){
    if (content.trim() === "") {
        document.getElementById("discussion-input").value = ""; // Clear input
    } else {
        const csrfToken = document.getElementById("csrf-token").value;
        $.ajax({
            url: "_plugin/submit_discussion/",
            type: "POST",
            data: {
              'article_id': article_id,
              'content': content,
              'csrfmiddlewaretoken': csrfToken
            },
            success: function (response) {
                console.log("Post made successfully");
                // Refresh the page after a successful submission
                location.reload();
            }
          });
        document.getElementById("discussion-input").value = ""; // Clear input
    }
}

function toggleDiscussion() {
    const discussionContent = document.getElementById("discussion-content");
    if (discussionContent.style.display === "none" || discussionContent.style.display === "") {
        discussionContent.style.display = "block";
    } else {
        discussionContent.style.display = "none";
    }
}

function sendReport(report_type, article_id, post_id) {
    const csrfToken = document.getElementById("csrf-token").value;
    $.ajax({
      url: "_plugin/submit_discussion_report/",
      type: "POST",
      data: {
        'report_type': report_type,
        'curr_page': window.location.pathname,
        'article_id': article_id,
        'post_id': post_id,
        'csrfmiddlewaretoken': csrfToken
      },
      success: function (response) {
        console.log("Report sent successfully");
        // Refresh the page after a successful submission
        location.reload();
    }
    });
    reportDropdown(post_id)
  }

function reportDropdown(dropdownId) {
    // Toggle the dropdown visibility
    document.getElementById(dropdownId).classList.toggle("show");
  }