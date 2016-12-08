$(document).ready(function() {
    $('input[type="radio"]').click(function() {
        var upl_but=$(this).closest('tr').next('tr').children("td").children("input");
        var url_but=$(this).closest('tr').next('tr').next('tr').children("td").children("input");
        var id1=upl_but.attr("id");
        var id2=url_but.attr("id");
        var name1=upl_but.attr("name");
        var name2=url_but.attr("name");
        if($(this).filter(':checked').val()=="url") {
            upl_but.prop("disabled", true);
            upl_but.val('');
            url_but.prop("disabled", false);
            upl_but.attr("id", id2);
            upl_but.attr("name", name2);
            url_but.attr("id", id1);
            url_but.attr("name", name1);
            if (upl_but.prop("required")) {
              url_but.prop("required", true);
              upl_but.prop("required", false);
            }
        }
        else {
            upl_but.prop("disabled", false);
            url_but.prop("disabled", true);
            url_but.val('');
            upl_but.attr("id", id2);
            upl_but.attr("name", name2);
            url_but.attr("id", id1);
            url_but.attr("name", name1);
            if (url_but.prop("required")) {
              upl_but.prop("required", true);
              url_but.prop("required", false);
            }
        };
    });
});
