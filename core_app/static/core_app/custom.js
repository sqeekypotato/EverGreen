$(document).ready(function() {

  $.ajaxSetup({
     beforeSend: function(xhr, settings) {
         function getCookie(name) {
             var cookieValue = null;
             if (document.cookie && document.cookie != '') {
                 var cookies = document.cookie.split(';');
                 for (var i = 0; i < cookies.length; i++) {
                     var cookie = jQuery.trim(cookies[i]);
                     // Does this cookie string begin with the name we want?
                     if (cookie.substring(0, name.length + 1) == (name + '=')) {
                         cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                         break;
                     }
                 }
             }
             return cookieValue;
         }
         if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
             // Only send the token to relative URLs i.e. locally.
             xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
         }
     }
});

  console.log("ready to go!");

    $("form :input").change(function() {
        console.log("Change!");

        formNumber = $(this).attr('name');
        var text = formNumber.replace('cat_', '');
        category = $(this).val();

//        console.log(formNumber, category)

        $.ajax({
            type: "POST",
            url: "/get_tag/",
            data: {'number': formNumber,
                    'category':category
                    },
            dataType: 'json',

            success: function(results){
               var tag_list = results['tags'];
               console.log('#tag_option'+text);
               $('#tag_option'+text).empty();
                var i;
                for (i = 0; i < tag_list.length; ++i) {
                    $('#tag_option'+text).append('<option value="' + tag_list[i] + '">');
                }
            }
        });

        });






});