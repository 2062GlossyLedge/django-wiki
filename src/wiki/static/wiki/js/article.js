$(document).ready(function() {

  $('.wiki-article .article-list ul, .wiki-article .toc ul').each(function() {
    $(this).addClass('list-group');
  });

  // Change color on hover
   $("#flag-spoilers-button").mouseenter(function() {
  
      $(this).css("color", "#5F3229"); 
    });

    $("#flag-spoilers-button").mouseleave(function() {
      $(this).css("color", "#c26451");
    });

  let flagging = false

  //to enable flagging 
  $('#flag-spoilers-button').on('click', () =>{
    flagging = !flagging;
       })


//highlights clicked text in p tag as red
  $('.wiki-article').find('p').on('click', function(event) {
    if(flagging){
      $(this).css("background-color", $(this).css("background-color") === "rgb(255, 0, 0)" ? "" : "red");
    }
  });

 

  
  });
 

