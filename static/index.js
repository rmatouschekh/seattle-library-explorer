/*
 * index.js
 * Josiah Misplon and Rebecca Hicke
 * 2020-11-23
 *
 * Javascript for search and initially displaying most popular data from October 2017.
 */

window.onload = initialize;

function initialize() {
///Sets up search button and displays sample of Most Popular for October 2017
    var url = getAPIBaseURL() + '/popular_media/Book/October/2017';
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
        var starterPopularMediaElement = document.getElementById('starter_popular_media');
        if (starterPopularMediaElement) {
            starterPopularMediaElement.innerHTML = tableBody;
        }
    })

    var element = document.getElementById('search_button');
    if (element) {
        element.onclick = onSearchButton;
    }
}

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}

function onSearchButton() {
    var searchValue = document.getElementById('search_string').value;

    var url = getAPIBaseURL() + '/media?all_fields=' +searchValue;

    fetch(url, {method: 'get'})

    .then((response) => response.json())

    .then(function(results) {
         tableBody =  '<tr> <th>Title</th> <th>Author</th> <th>Publication Year</th> <th>Count</th> </tr>';
        for (var k = 0; k < results.length; k++) {
            var result = results[k];
            tableBody += '<tr>'
                      + '<td> ' + result['title'] + '</td>'
                      + '<td>' + result['author'] + '</td>'
                      + '<td>' + result['publication_year'] + '</td>'
                       + '<td>' + result['count'] + '</td>';
                      + '</tr>\n';
            }
        var mediaSearchResultsElement = document.getElementById('search_results');
        if (mediaSearchResultsElement) {
            mediaSearchResultsElement.innerHTML = tableBody;
        }
    })

    .catch(function(error) {
        console.log(error);
    });
}
