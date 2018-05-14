$(document).ready(function() {


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
                    $('#tag_option'+text).append("<option value='" + tag_list[i] + "'>");
                }
            }
        });

        });






});