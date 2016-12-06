$(document).ready(function() {
  if($('input[type="radio"]:checked').val()=="url") {
            ($(this).closest('td').next('td').next('td')).prop("disabled", false);
        };
});
});
