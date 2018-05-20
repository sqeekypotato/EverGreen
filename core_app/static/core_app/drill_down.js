$(document).ready(function() {
    console.log("drill down ready!");

    $.ajaxSetup({
      beforeSend: function (xhr, settings) {
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
    
    var first_chart = $(".drilldown:first")
    var ctx_drill = document.getElementById('BarChartDrillDown').getContext('2d');

    //first post to get information on original page display
    $.ajax({
        type: "POST",
        url: "/drill_down/",
        data: {
            'value': $(first_chart).attr("value")
        },
        dataType: 'json',

        success: function (results) {
            chart_drill_down(results, 1)
            chart_side_values(results)
        }
    });

    // when button is clicked it updates the chart
    $(".drilldown").click(function () {
        $.ajax({
            type: "POST",
            url: "/drill_down/",
            data: {
                'value': $(this).attr("value")
            },
            dataType: 'json',

            success: function (results) {
                chart_drill_down(results, 0)
                chart_side_values(results)

            }
        });
    });

    // chart logic
    function chart_drill_down(results, first) {
        if(first == 0){
            drill_down_chart.destroy();
        }

        var categories = results['debits']
        var myValues = $.map(categories, function (value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }

        drill_down_chart = new Chart(ctx_drill, {
            type: 'bar',
            data: {
                labels: results['labels'],
                datasets: [
                  {
                      label: "Spending for Month",
                      backgroundColor: colours,
                      data: results['debits']
                  },
                    {
                        label: "Earnings for Month",
                        backgroundColor: colours,
                        data: results['credits']
                    }
                ]
            },
            options: {
                onClick: function(evt) {
                    var activePoints = this.getElementsAtEvent(evt);
                    if (activePoints[0]) {
                        var chartData = activePoints[0]['_chart'].config.data;
                        var idx = activePoints[0]['_index'];

                        var label = chartData.labels[idx];
                        var value = chartData.datasets[0].data[idx];


                    }

                    $.ajax({
                        type: "POST",
                        url: "/drill_down_chart_click/",
                        data: {'name': results['cat_tag'],
                            'value':label
                        },
                        dataType: 'json',

                        success: function() {
                            console.log('success for transaction details');
                            window.location.href = "/display_transaction_details/";
                        },

                    });



                },


                legend: { display: false },
                title: {
                    display: true,
                    text: results['Title']
                }
            }
        });

    }

    // updates the values on the side of the chart
    function chart_side_values(results) {
        $("#monthly_budget").text(results['budget'])
        $("#spent_last_month").text(results['tag_chart_last_month'])
        $("#ytd_average_spent").text(results['tag_chart_ytd'])
    }

});