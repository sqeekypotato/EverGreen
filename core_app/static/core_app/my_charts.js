$(document).ready(function() {
  console.log("ready to chart!");

  var balanceChart;
  var categoryChart;
  var tagChart;
  var ctx = document.getElementById('balanceChart').getContext('2d');
  var ctx2 = document.getElementById('categoryChart').getContext('2d');
  var ctx3 = document.getElementById('tagChart').getContext('2d');
  var getdata = $.post('/first_charts/');

    getdata.done(function(results){
    chartBalance(results, 1);
    chartCat(results, 1);
    chartTag(results, 1);
    $("#month_form").hide();
    $("#tagContainer").hide();

});

    $("#id_years").change(function() {
        console.log("Change!");
        $("#tagContainer").hide();
        formName = $(this).attr('name');
        value = $(this).val();
        updateMonths(value)
        $.ajax({
            type: "POST",
            url: "/new_chart_data/",
            data: {'name': formName,
                    'value':value
                    },
            dataType: 'json',

            success: function(results){
               console.log('success!')
               $('#id_categories option[value=All]').attr('selected','selected');
               chartBalance(results, 0);
               chartCat(results, 0);
               if(value=="All"){
                $("#month_form").hide();}else {
                    $("#month_form").show();
                }
               chartTag(results, 0);
            }
        });
    });

    $("#id_monthNum").change(function() {
        $("#tagContainer").hide();
        formName = $(this).attr('name');
        value = $(this).val();

        $.ajax({
            type: "POST",
            url: "/new_chart_data/",
            data: {'name': formName,
                    'value':value
                    },
            dataType: 'json',

            success: function(results){
               console.log('success!')
               chartBalance(results, 0);
               chartCat(results, 0);
               chartTag(results, 0);
               $('#id_categories option[value=All]').attr('selected','selected');
            }
        });
    });

    $("#id_categories").change(function() {
        formName = $(this).attr('name');
        value = $(this).val();
        if(value == 'All'){
            $("#tagContainer").hide();
        }
        $.ajax({
            type: "POST",
            url: "/new_tag_data/",
            data: {'name': formName,
                    'value':value
                    },
            dataType: 'json',

            success: function(results){
               console.log('success!')
                if(value != 'All'){
                    $("#tagContainer").show();
                    chartTag(results, 0);
                }
            }
        });
    });

    function chartBalance(results, first){
        console.log('balance chart!')
      if (first == 0){
       balanceChart.destroy();
      }
      balanceChart = new Chart.Line(ctx, {
      data:{
      labels: results['labels'],
      datasets: [

          {
              label: "Debits",
              backgroundColor: "rgba(153,255,51,0.6)",
              data: results['debits']
          },
          {
              label: "Credits",
              backgroundColor: "rgba(255,153,0,0.6)",
              data: results['credits']
          },
          {
              label: "Balance",
              backgroundColor: "rgba(0,153,255,0.8)",
              data: results['balance']
          }
      ]
      }
    });
}

    function chartCat(results, first){
        console.log('category chart!')
        var myValues = $.map(results['cat_vals'], function(value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
      if (first == 0){
       categoryChart.destroy();
      }
      categoryChart = new Chart(ctx2, {
      type: 'doughnut',
      data:{
      labels: results['cat_labels'],
      datasets: [

          {
              backgroundColor: colours,
              data: myValues
          }
      ]
      }
    });
}

    function chartTag(results, first){
        console.log('tag chart!')
        var myValues1 = $.map(results['tag_vals'], function(value, key) { return value });
        console.log(myValues1)
        var colours = []
        for (var i = 0; i < myValues1.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
      if (first == 0){
       tagChart.destroy();
      }
      tagChart = new Chart(ctx3, {
      type: 'doughnut',
      data:{
      labels: results['tag_labels'],
      datasets: [

          {
              backgroundColor: colours,
              data: myValues1
          }
      ]
      }
    });
}

    function updateMonths(year){
        $.ajax({
            type: "POST",
            url: "/get_months/",
            data: {'year': year
                    },
            dataType: 'json',

            success: function(results){
               console.log('month update success!')
               console.log(results)
               var $el = $("#id_monthNum");
                $el.empty(); // remove old options
                $.each(results, function(key,value) {
                  $el.append($("<option></option>")
                     .attr("value", key).text(value));

                });
            }
        });

    }
});