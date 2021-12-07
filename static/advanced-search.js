/*
 * advanced-search.js
 * Josiah Misplon and Rebecca Hicke
 * 2020-11-23
 *
 * Javascript for advanced search.
 */

window.onload = initialize;

function initialize() {

    var submit = document.getElementById('search_button');
    if (submit) {
        submit.onclick = onSubmitButton;
    }


}

function getAPIBaseURL() {
    var baseURL = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/api';
    return baseURL;
}

function onSubmitButton() {
///Retrieves results from search with given search fields and updates table to display them
    var searchTitle= document.getElementById('search_title').value;
    var searchAuthor= document.getElementById('search_author').value;
    var searchPublicationYear= document.getElementById('search_publication_year').value;
    var searchMediaSubType= document.getElementById('search_media_sub_type').value;
    var searchTermArray = [searchTitle, searchAuthor,searchPublicationYear,searchMediaSubType];
    var searchStringPair = ['title','author','publication_year','media_sub_type'];
    var url = getAPIBaseURL() + '/media?';
    for (var j = 0; j < searchTermArray.length; j++) {
        if (!(searchTermArray[j]  === "")) {
        url+= searchStringPair[j] + '=' + searchTermArray[j] + '&' ;
        }
    }
    url = url.substring(0, url.length - 1);

    fetch(url, {method: 'get'})

    .then((response) => response.json())

    .then(function(results) {
         tableBody =  '<tr> <th>Title</th> <th>Author</th> <th>Publication Year</th> <th> Media Type </th> </tr>';
        for (var k = 0; k < results.length; k++) {
            var result = results[k];
            tableBody += '<tr>'
                      + '<td onclick="getRecommendationsAndDetails(' + result['bib_num'] + ",'" + result['title'] +"')\">"
                      + '<span style="text-decoration: underline; color: #0000cc;cursor: pointer; width: 100%, height:100%">' + result['title'] + ' </span> </td>'
                      + '<td>' + result['author'] + '</td>'
                      + '<td>' + result['publication_year'] + '</td>'
                       +'<td>' +result['format_group'] + ' - ' + result['format_subgroup'] + '</td>'
                      + '</tr>\n';
            }
        var mediaSearchResultsElement = document.getElementById('search_results');
        if (mediaSearchResultsElement) {
            mediaSearchResultsElement.innerHTML = tableBody;
        }
        var recommendationsInstructions = document.getElementById("recommendation_instructions");
        if (recommendationsInstructions){
          recommendationsInstructions.innerHTML = 'Click on item titles to see recommendations of similar media and the locations the item can be found at';
        }
        var locationsTable= document.getElementById('location_results');
        if (locationsTable) {
          locationsTable.innerHTML = '';
        }
        var recommendationsTitle = document.getElementById("recommended_books_title");
        if (recommendationsTitle){
          recommendationsTitle.innerHTML = '';
        }
    }
    )

    .catch(function(error) {
        console.log(error);
    });
}


function getRecommendationsAndDetails(bib_number, title) {
    // Updates page to show recommendations for and list locations that have a given bib_number item
    var urlForLocations = getAPIBaseURL() + '/locations/' + bib_number;

    fetch(urlForLocations, {method: 'get'})

    .then((response) => response.json())

    .then(function(locationList) {
        var tableBody = '<tr><th> Locations that have: "' + title +'" </th></tr>';
        for (var k = 0; k < locationList.length; k++) {
            tableBody += '<tr>'
            + '<td>' + locationList[k]+ '</td>'
            + '</tr>';
        }
        var resultsTableElement = document.getElementById('location_results');
        if (resultsTableElement) {
            resultsTableElement.innerHTML = tableBody;
        }
    })

    .catch(function(error) {
        console.log(error);
    });

    var urlForRecommendations = getAPIBaseURL() + '/recommendations/' + bib_number;

        fetch(urlForRecommendations, {method: 'get'})

        .then((response) => response.json())

        .then(function(recommendedBooks) {
            var tableBody = '<tr><th> Title </th> <th> Author </th> <th> Publication Year </th> <th> Format </th> <th> Exact Subjects Match? </th>  </tr>';
            for (var k = 0; k < recommendedBooks.length; k++) {
                tableBody += '<tr>'
                + '<td>' + recommendedBooks[k]['title'] + '</td>'
                + '<td>' + recommendedBooks[k]['author'] + '</td>'
                + '<td>' + recommendedBooks[k]['publication_year'] + '</td>'
                + '<td>' +recommendedBooks[k]['format_group'] + ' - ' + recommendedBooks[k]['format_subgroup'] + '</td>'
                + '<td>' + recommendedBooks[k]['exact_match'] + '</td>'
                + '</tr>';
            }
            var resultsTableElement = document.getElementById('search_results');
            if (resultsTableElement) {
                resultsTableElement.innerHTML = tableBody;
            }
            var recommendationsTitle = document.getElementById("recommended_books_title");
            if (recommendationsTitle){
                recommendationsTitle.innerHTML = 'Recommended items  in the collection for "' + title + '"'
            }
            var recommendationsInstructions = document.getElementById("recommendation_instructions");
            if (recommendationsInstructions){
              recommendationsInstructions.innerHTML = '';
            }

        })

        .catch(function(error) {
            console.log(error);
        });

}
