$(document).ready(function() {
    $('input[type="radio"]').click(function() {
        if($(this).filter(':checked').val()=="url") {
            ($(this).closest('tr').next('tr').children("td").children("input")).prop("disabled", true);
            ($(this).closest('tr').next('tr').next('tr').children("td").children("input")).prop("disabled", false);
        }
        else {
            ($(this).closest('tr').next('tr').children("td").children("input")).prop("disabled", false);
            ($(this).closest('tr').next('tr').next('tr').children("td").children("input")).prop("disabled", true);
        };
});
});
