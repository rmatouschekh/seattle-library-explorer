/*
 * library-busy-times.js
 * Josiah Misplon and Rebecca Hicke
 * 2020-11-23
 *
 * Thanks to Jeff Ondich for help with implementing chartist
 *
 * Javascript for creating charts of library business based on day of the week and season.
 */

window.onload = initialize;

function initialize() {
    var dayOfWeekSelector= document.getElementById('day_of_week');
    var seasonSelector = document.getElementById('season');
    if (dayOfWeekSelector && seasonSelector){
    dayOfWeekSelector.onchange = onSelectorChanged;
    dayOfWeekSelector.value= 'Monday';
    seasonSelector.onchange = onSelectorChanged;
    seasonSelector.value = 'Spring';
    createCheckoutChart('Monday', 'Spring')
    }


}

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}


function onSelectorChanged() {
     var dayOfWeekSelector= document.getElementById('day_of_week');
     var seasonSelector= document.getElementById('season');
     if (dayOfWeekSelector && seasonSelector) {
              var dayOfWeek= dayOfWeekSelector.value;
              var season = seasonSelector.value;
              createCheckoutChart(dayOfWeek,season); }
}


function createCheckoutChart(dayOfWeek, season) {
/// Retrieves hourly checkout data based on dayOfWeek and season and makes and displays a chart based on the data

     var url = '';
     url = getAPIBaseURL() + '/checkout_hourly?day_of_week=' +dayOfWeek +'&season=' + season;


     fetch(url, {method: 'get'})

     .then((response) => response.json())

     .then(function(hours) {
         var labels = [];
         var checkoutData = [];
         const hourArray = Object.entries(hours)
         for (var k = 0; k < 24; k++) {
             var checkouts = ''
             if (k >= hourArray.length){
                checkouts+= '0'
             }
             else{
                checkouts+=hourArray[k][1]
             }
             labels.push(k);
             checkoutData.push({meta: k, value: checkouts});
         }
         var options = { seriesBarDistance: 60,
                         axisX: { labelInterpolationFnc: function(value, index) {
                                     return index % 1 === 0 ? value : null;
                                 }
                         },
                       };
         var data = { labels: labels, series: [checkoutData] };

         var chart = new Chartist.Bar('#hourly_checkouts_chart', data, options);
         var checkoutsTitle = document.getElementById('hourly_checkouts_title');
         if (checkoutsTitle) {
              checkoutsTitle.innerHTML = 'Number of Checkouts on ' + dayOfWeek+ " during " + season;
              }

    });
}
