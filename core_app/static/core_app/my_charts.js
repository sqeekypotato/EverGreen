$(document).ready(function() {
  console.log("ready to chart!");

  var balanceChart;
  var categoryChart;
  var ctx = document.getElementById('balanceChart').getContext('2d');
//  var ctx2 = document.getElementById('categoryChart').getContext('2d');
  var getdata = $.post('/first_charts/');

  getdata.done(function(results){
    chartBalance(results, 1);
    $("#month_form").hide();

});

    $("#id_years").change(function() {
        console.log("Change!");

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
               chartBalance(results, 0);
               if(value=="All"){
                $("#month_form").hide();}else {
                    $("#month_form").show();
                }

            }
        });
    });

    $("#id_monthNum").change(function() {
        console.log("Change!");

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
            }
        });
    });


//
//
    function chartBalance(results, first){
        console.log('first chart!')
      if (first == 0){
       balanceChart.destroy();
    //       categoryChart.destroy();
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