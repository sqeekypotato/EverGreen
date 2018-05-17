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
                $(this).addClass('background-color', 'red')
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
                legend: { display: false },
                title: {
                    display: true,
                    text: results['Title']
                }
            }
        });

    }

});