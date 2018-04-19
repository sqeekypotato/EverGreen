$(document).ready(function() {
  console.log("ready to chart!");

  var balanceChart;
  var categoryChart;
  var ctx = document.getElementById('balanceChart').getContext('2d');
//  var ctx2 = document.getElementById('categoryChart').getContext('2d');
  var getdata = $.post('/first_charts/');

  getdata.done(function(results){

//    $("#month").hide();
    chartBalance(results, 1);
});

    $("#id_years").change(function() {
        console.log("Change!");

        formName = $(this).attr('name');
        value = $(this).val();

        console.log(formName, value)

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
        console.log(results)
      if (first == 0){
       balanceChart.destroy();
    //       categoryChart.destroy();
      }
      balanceChart = new Chart.Line(ctx, {
      data:{
      labels: results['labelList'],
      datasets: [

          {
              label: "Debits",
              backgroundColor: "rgba(153,255,51,0.6)",
              data: results['debitList']
          },
          {
              label: "Credits",
              backgroundColor: "rgba(255,153,0,0.6)",
              data: results['creditList']
          },
          {
              label: "Balance",
              backgroundColor: "rgba(0,153,255,0.8)",
              data: results['balanceList']
          }
      ]
      }
    });
}

});