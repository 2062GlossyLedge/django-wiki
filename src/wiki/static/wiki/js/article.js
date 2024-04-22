$(document).ready(function() {

  $('.wiki-article .article-list ul, .wiki-article .toc ul').each(function() {
    $(this).addClass('list-group');
  });



  $('.wiki-article').find('p').on('click', function(event) {
      if(isHighlighted){
      $(this).css("background-color", $(this).css("background-color") === "rgb(255, 0, 0)" ? "" : "red");
      }
  });

  
  });
 

