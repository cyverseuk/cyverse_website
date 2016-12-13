$(document).ready(function() {
  $(".dropbtn").click(function() {
    $("#prof_dropdown").toggle();
  });
  $(document).click(function(event) {
    if(!$(event.target).closest('#prof_dropdown').length) {
        if($('#prof_dropdown').is(":visible")) {
            $('#prof_dropdown').hide();
        };
    };        
  });
});
