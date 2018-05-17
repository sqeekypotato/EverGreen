$(document).ready(function() {
  console.log("ready to chart!");

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

  var balanceChart;
  var categoryChart;
  var tagChart;
  var incomeCatChart;
  var incomeTagsChart;
  var ctx = document.getElementById('balanceChart').getContext('2d');
  var ctx2 = document.getElementById('categoryChart').getContext('2d');
  var ctx3 = document.getElementById('tagChart').getContext('2d');
  var ctx4 = document.getElementById('incomeChart').getContext('2d');
  var ctx5 = document.getElementById('incomeTags').getContext('2d');
  var getdata = $.post('/first_charts/');

    getdata.done(function(results){
    chartBalance(results, 1);
    chartCat(results, 1);
    chartTag(results, 1);
    incomeChart(results, 1);
    incomeTags(results, 1);
    $("#month_form").hide();
    $("#tagContainer").hide();
    $("#income_tag_container").hide();
});

    $("#id_years").change(function() {
        $("#tagContainer").hide();
        $("#income_tag_container").hide();
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
               updateCatDropdowns()
               chartBalance(results, 0);
               chartCat(results, 0);
               incomeChart(results, 0);
               if(value=="All"){
                $("#month_form").hide();}else {
                    $("#month_form").show();
                }
               chartTag(results, 0);
               $(".session_title").text(results['session_title'])
            }
        });
    });

    $("#id_monthNum").change(function() {
        $("#tagContainer").hide();
        $("#income_tag_container").hide();
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
                updateCatDropdowns()
               chartBalance(results, 0);
               chartCat(results, 0);
               chartTag(results, 0);
               incomeChart(results, 0);
//               $('#id_categories option[value=All]').attr('selected','selected');
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
                if(value != 'All'){
                    $("#tagContainer").show();
                    chartTag(results, 0);
                }
            }
        });
    });

    $("#id_income_categories").change(function() {
        formName = $(this).attr('name');
        value = $(this).val();
        if(value == 'All'){
            $("#income_tag_container").hide();
        }
        $.ajax({
            type: "POST",
            url: "/new_income_tag_data/",
            data: {'name': formName,
                    'value':value
                    },
            dataType: 'json',

            success: function(results){
                if(value != 'All'){
                    $("#income_tag_container").show();
                    incomeTags(results, 0);
                }
            }
        });
    });

    function updateMonths(year){
        $.ajax({
            type: "POST",
            url: "/get_months/",
            data: {'year': year
                    },
            dataType: 'json',

            success: function(results){
                var $el = $("#id_monthNum");
                $el.empty(); // remove old options
                $.each(results, function (key, value) {
                    console.log(value)
                  $el.append($("<option></option>")
                     .attr("value", value).text(value));

                });
            }
        });

    }

    function updateCatDropdowns(){
        $.ajax({
            type: "POST",
            url: "/update_cat_dropdown/",
            data: {
                    },
            dataType: 'json',

            success: function(results){
                var $el = $("#id_categories");
                $el.empty(); // remove old options
                $.each(results['debit'], function(key,value) {
                  $el.append($("<option></option>")
                     .attr("value", value).text(value));

                });
               var $el = $("#id_income_categories");
                $el.empty(); // remove old options
                $.each(results['credit'], function(key,value) {
                  $el.append($("<option></option>")
                     .attr("value", value).text(value));

                });
            }
        });

    }

    function chartBalance(results, first){
    console.log('balance chart!')
      if (first == 0){
       balanceChart.destroy();
      }
      balanceChart = new Chart.Line(ctx, {
      options:{
            onClick: function(evt) {
                  console.log('click event!')
                  var activePoints = this.getElementsAtEvent(evt);
                  if (activePoints[0]) {
                    var chartData = activePoints[0]['_chart'].config.data;
                    var idx = activePoints[0]['_index'];

                    var label = chartData.labels[idx];
                    var value = chartData.datasets[0].data[idx];


                  }

                  $.ajax({
                    type: "POST",
                    url: "/transaction_details/",
                    data: {'name': 'all',
                            'value':label
                            },
                    dataType: 'json',

                    success: function() {
                     console.log('success for transaction details');
                     window.location.href = "/display_transaction_details/";
                  },

                });



                }
          },
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
//        create chart
        var categories = results['cat_vals']
        var myValues = $.map(categories, function(value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
          if (first == 0){
           categoryChart.destroy();
          }
          categoryChart = new Chart(ctx2, {
          type: 'doughnut',
          options:{
            onClick: function(evt) {
                  console.log('click event!')
                  var activePoints = this.getElementsAtEvent(evt);
                  if (activePoints[0]) {
                    var chartData = activePoints[0]['_chart'].config.data;
                    var idx = activePoints[0]['_index'];

                    var label = chartData.labels[idx];
                    var value = chartData.datasets[0].data[idx];


                  }

                  $.ajax({
                    type: "POST",
                    url: "/transaction_details/",
                    data: {'name': 'category',
                            'value':label
                            },
                    dataType: 'json',

                    success: function() {
                     console.log('success for transaction details');
                     window.location.href = "/display_transaction_details/";
                  },

                });

                }
          },
          data:{
          labels: results['cat_labels'],
          datasets: [
              {
                  backgroundColor: colours,
                  data: myValues
              }
          ]
          },
        });

}

    function chartTag(results, first){
        var myValues1 = $.map(results['tag_vals'], function(value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues1.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
      if (first == 0){
       tagChart.destroy();
      }
      tagChart = new Chart(ctx3, {
      type: 'doughnut',
      options:{
            onClick: function(evt) {
                  console.log('click event!')
                  var activePoints = this.getElementsAtEvent(evt);
                  if (activePoints[0]) {
                    var chartData = activePoints[0]['_chart'].config.data;
                    var idx = activePoints[0]['_index'];

                    var label = chartData.labels[idx];
                    var value = chartData.datasets[0].data[idx];


                  }

                  $.ajax({
                    type: "POST",
                    url: "/transaction_details/",
                    data: {'name': 'tag',
                            'value':label
                            },
                    dataType: 'json',

                    success: function() {
                     console.log('success for transaction details');
                     window.location.href = "/display_transaction_details/";
                  },

                });

                }
          },
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

    function incomeChart(results, first){
        var myValues = $.map(results['inc_vals'], function(value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
      if (first == 0){
       incomeCatChart.destroy();
      }
      incomeCatChart = new Chart(ctx4, {
      type: 'doughnut',
      options:{
            onClick: function(evt) {
                  console.log('click event!')
                  var activePoints = this.getElementsAtEvent(evt);
                  if (activePoints[0]) {
                    var chartData = activePoints[0]['_chart'].config.data;
                    var idx = activePoints[0]['_index'];

                    var label = chartData.labels[idx];
                    var value = chartData.datasets[0].data[idx];


                  }

                  $.ajax({
                    type: "POST",
                    url: "/transaction_details/",
                    data: {'name': 'category',
                            'value':label
                            },
                    dataType: 'json',

                    success: function() {
                     console.log('success for transaction details');
                     window.location.href = "/display_transaction_details/";
                  },

                });

                }
          },
      data:{
      labels: results['inc_labels'],
      datasets: [

          {
              backgroundColor: colours,
              data: myValues
          }
      ]
      }
    });
}

    function incomeTags(results, first){
        var myValues2 = $.map(results['income_tag_vals'], function(value, key) { return value });
        var colours = []
        for (var i = 0; i < myValues2.length; i++) {
            colours.push('rgb(' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ',' + (Math.floor(Math.random() * 256)) + ')')
        }
      if (first == 0){
       incomeTagsChart.destroy();
      }
      incomeTagsChart = new Chart(ctx5, {
      type: 'doughnut',
      options:{
            onClick: function(evt) {
                  console.log('click event!')
                  var activePoints = this.getElementsAtEvent(evt);
                  if (activePoints[0]) {
                    var chartData = activePoints[0]['_chart'].config.data;
                    var idx = activePoints[0]['_index'];

                    var label = chartData.labels[idx];
                    var value = chartData.datasets[0].data[idx];


                  }

                  $.ajax({
                    type: "POST",
                    url: "/transaction_details/",
                    data: {'name': 'tag',
                            'value':label
                            },
                    dataType: 'json',

                    success: function() {
                     console.log('success for transaction details');
                     window.location.href = "/display_transaction_details/";
                  },

                });

                }
          },
      data:{
      labels: results['income_tag_labels'],
      datasets: [

          {
              backgroundColor: colours,
              data: myValues2
          }
      ]
      }
    });
}












});