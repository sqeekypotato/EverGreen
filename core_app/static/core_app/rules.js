$(document).ready(function() {
    console.log("rules ready!");

    $('#id_ends_with').click(function () {
    if ($('#id_ends_with').is(':checked')) {
            $("#id_begins_with").prop('checked', false);
        } else{
            $("#id_begins_with").prop('checked', true);
        }
    });

    $('#id_begins_with').click(function () {
    if ($('#id_begins_with').is(':checked')) {
            $("#id_ends_with").prop('checked', false);
        } else{
            $("#id_ends_with").prop('checked', true);
        }
    });


});