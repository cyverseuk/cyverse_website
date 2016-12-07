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
        }
        else {
            upl_but.prop("disabled", false);
            url_but.prop("disabled", true);
            url_but.val('');
            upl_but.attr("id", id2);
            upl_but.attr("name", name2);
            url_but.attr("id", id1);
            url_but.attr("name", name1);
        };
    });
    $('input[type="submit"]').click(function() {
        alert("Your job will be submitted. This may take a while, please wait.")
    });
});
