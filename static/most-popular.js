/*
 * most-popular.js
 * Josiah Misplon and Rebecca Hicke
 * 2020-11-23
 *
 * Javascript for most popular page.
 */

window.onload = initialize;

function initialize() {
    var monthSelector= document.getElementById('month');
    var yearSelector = document.getElementById('year');
    var mediaSelector = document.getElementById('media');
    if (monthSelector && yearSelector && mediaSelector){
      monthSelector.onchange = onMediaSelectorChanged;
      yearSelector.onchange = onMediaSelectorChanged;
      mediaSelector.onchange = onMediaSelectorChanged;
    }
    onMediaSelectorChanged();
}

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}

function onMediaSelectorChanged() {
  //Retrieves values from selectors and makes the appropriate call to the popular_media endpoint if a type of item has been selected or to popular_collections if Collections was chosen
    var monthSelector = document.getElementById('month');
    var yearSelector = document.getElementById('year');
    var mediaSelector = document.getElementById('media');
    if (monthSelector && yearSelector && mediaSelector) {
        var media = mediaSelector.value;
        var month = monthSelector.value;
        var year = yearSelector.value;
        if (media != "Collection") {
          var url = getAPIBaseURL() + '/popular_media/' + media + '/' + month + '/' + String(year);
          fetch(url, {method: 'get'})
          .then((response) => response.json())
          .then(function(results) {
              tableBody =  '<tr> <th>Title</th> <th>Author</th> <th>Publication Year</th> <th>Publisher</th> <th>Type</th> <th>Collection</th> <th>Locations</th></tr>';
              for (var k = 0; k < results.length; k++) {
                  var result = results[k];
                  locations = result['locations'];
                  locationResult = "";
                  for (var j = 0; j <locations.length; j++) {
                    locationResult += locations[j];
                    if (!(j == locations.length-1)) {
                      locationResult += ", ";
                    }
                  }
                  tableBody += '<tr>'
                            + '<td> ' + result['title'] + '</td>'
                            + '<td>' + result['author_name'] + '</td>'
                            + '<td>' + result['publication_year'] + '</td>'
                            + '<td>' + result['publisher'] + '</td>'
                            + '<td>' + result['type'] + '</td>'
                            + '<td>' + result['collection'] + '</td>'
                            + '<td>' + locationResult + '</td>'
                            + '</tr>\n';
                  }
              var popularMediaResultsElement = document.getElementById('popular_media_results');
              if (popularMediaResultsElement) {
                  popularMediaResultsElement.innerHTML = tableBody;
              }
          })

          .catch(function(error) {
              console.log(error);
          });
      }
      else {
        var url = getAPIBaseURL() + '/popular_collections/' + month + '/' + String(year);
        fetch(url, {method: 'get'})
        .then((response) => response.json())
        .then(function(results) {
            tableBody =  '<tr> <th>Collection</th> <th>Number of Checkouts in Time Range</th> </tr>';
            for (var k = 0; k < results.length; k++) {
                var result = results[k];
                tableBody += '<tr>'
                          + '<td> ' + result['collection'] + '</td>'
                          + '<td>' + result['count'] + '</td>'
                          + '</tr>\n';
                }
            var popularMediaResultsElement = document.getElementById('popular_media_results');
            if (popularMediaResultsElement) {
                popularMediaResultsElement.innerHTML = tableBody;
            }
        })

        .catch(function(error) {
            console.log(error);
        });
      }
    }
}
