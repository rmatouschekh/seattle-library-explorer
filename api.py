'''
    api.py
    Josiah Misplon and Rebecca Hicke, 2020-11-09
    

     API to support the library search and data website.
'''
import sys
import flask
import json
import config
import psycopg2
from datetime import datetime

from config import password
from config import database
from config import user

api = flask.Blueprint('api', __name__)

def get_connection():
    '''
    Returns a connection to the database described in the config module.
    '''
    return psycopg2.connect(database=config.database,
                            user=config.user,
                             password=config.password)


#Helping functions

def execute_cursor(query, argument_tuple):
    '''
    Create a cursor for the given query, passing the arguments in argument_tuple.
    '''
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, argument_tuple)
        return cursor
    except Exception as e:
        print(e, file=sys.stderr)
        exit()
        return

def get_basic_information_from_bib_number_list(bib_number_list):
    '''
    Returns a list of dictionaries, where each dictionary corresponds to a bib_number from bib_number list and
    contains the title, author, publication year, count, and format_group and format_subgroup information.
    '''
    basic_information_for_listed_bib_numbers = []
    bib_numbers_string = ''
    for bib_number in bib_number_list:
        bib_numbers_string += str(bib_number) + ','
    bib_numbers_string=bib_numbers_string[:-1]
    query = '''SELECT collection_items.bib_number, collection_items.title, collection_items.author_name, collection_items.publication_year,
            collection_items.count, format_groups.name, format_subgroups.name
            FROM collection_items LEFT JOIN types ON collection_items.type_id = types.type_id LEFT JOIN format_groups ON
            format_groups.format_group_id = types.format_group_id LEFT JOIN format_subgroups ON format_subgroups.format_subgroup_id = types.format_subgroup_id WHERE collection_items.bib_number IN ( ''' + bib_numbers_string + ''' ) ORDER BY collection_items.bib_number ASC'''
    cursor = execute_cursor(query, (bib_numbers_string,))
    if cursor:
        for row in cursor:
            media={}
            media['bibnum']=row[0]
            media['title']=row[1]
            media['author']=row[2]
            publication_year = row[3]
            if not (isinstance(publication_year, int)):
                publication_year = 'Unknown'
            media['publication_year']=publication_year
            media['count']=row[4]
            media['format_group']=row[5]
            format_subgroup = row[6]
            if len(format_subgroup) == 0 or format_subgroup == "null":
                format_subgroup = "general"
            media['format_subgroup']=format_subgroup
            basic_information_for_listed_bib_numbers.append(media)
    return basic_information_for_listed_bib_numbers


def get_subjects_ids_from_bib_number(bib_number):
    '''
    For a given bib number, return the subject_ids of all related subjects as found in the subject_links database.
    '''
    query = ''' SELECT subject_id from subject_links WHERE %s = bib_number'''
    subject_id_list = []
    
    cursor = execute_cursor(query, (bib_number,))
    
    if cursor:
        for row in cursor:
            if row[0] not in subject_id_list:
                subject_id_list.append(row[0])
    return subject_id_list

def get_locations_from_bib_number(bib_number):
    '''
    For a given bib_number, return all the branches at which that item can be found.
    '''
    query ='''SELECT locations.branch_name FROM locations INNER JOIN location_links ON location_links.location_id = locations.location_id WHERE location_links.bib_number = %s'''
    branches = []
    
    cursor = execute_cursor(query, (bib_number,))
    
    if cursor:
        for row in cursor:
            if row[0] not in branches:
                branches.append(row[0])
    return branches
    
def get_collection_from_bib_number(bib_number):
    '''
    For a given bib_number, return the collection the item is a part of.
    '''
    query ='''SELECT collections.description FROM collection_items INNER JOIN collections ON collection_items.collection_id = collections.collection_id WHERE collection_items.bib_number = %s'''
    collection = ''
    
    cursor = execute_cursor(query, (bib_number,))
    
    if cursor:
        collection_results = cursor.fetchone()
        collection = collection_results[0]
    return collection


#Primary functions
@api.route('/locations/<bib_number>')
def get_locations_JSON_from_bib_number(bib_number):
    '''
    Returns JSON  list of locations where bib_number is located.
    '''
    location_results = get_locations_from_bib_number(bib_number)
    return json.dumps(location_results)


@api.route('/media') 
def get_media_search():
    '''
    Returns JSON list of dictionaries that contain details of library collection for media items such that any given search parameter
    is a substring or matches (for ints and booleans) a media item's parameter.
    '''

    media_list = []

    search_term = flask.request.args.get('all_fields', default= '',  type=str)
    title = flask.request.args.get('title', default='', type=str)
    author = flask.request.args.get('author', default='', type=str)
    current_year = datetime.now().year
    unpublishable_year = current_year+50
    publication_year = flask.request.args.get('publication_year', default=unpublishable_year, type=int)
    media_type= flask.request.args.get('media_type', default='', type=str)
    media_sub_type=flask.request.args.get('media_sub_type', default ='', type=str)
    search_term_wildcarded = '%' + search_term + '%'
    title_wildcarded = '%' + title + '%'
    author_wildcarded = '%' + author + '%'
    query = '''SELECT collection_items.bib_number, collection_items.title, collection_items.author_name, collection_items.publication_year,
            format_groups.name, format_subgroups.name
            FROM collection_items LEFT JOIN types ON collection_items.type_id = types.type_id LEFT JOIN format_groups ON
            format_groups.format_group_id = types.format_group_id LEFT JOIN format_subgroups ON format_subgroups.format_subgroup_id = types.format_subgroup_id
            WHERE
            (LOWER(collection_items.title) LIKE LOWER(%s) OR LOWER(collection_items.author_name) LIKE LOWER(%s)) AND
            (LOWER(collection_items.title) LIKE LOWER(%s) OR %s = '') AND (LOWER(collection_items.author_name) LIKE LOWER(%s) OR %s ='') AND
            (collection_items.publication_year = %s OR %s = (date_part('year', current_date) + 50) ) AND ( %s IN ('',  format_groups.name ) ) AND ( %s IN ('',  format_subgroups.name ) )LIMIT 100
            '''
    media_matched_to_search=[]
    cursor = execute_cursor(query, (search_term_wildcarded, search_term_wildcarded, title_wildcarded, title_wildcarded, author_wildcarded, author_wildcarded,publication_year,publication_year, media_type, media_sub_type,))
    if cursor:
        for row in cursor:
            media={}
            media['bib_num']=row[0]
            media['title']=row[1]
            media['author']=row[2]
            publication_year = row[3]
            if not (isinstance(publication_year, int)):
                publication_year = 'Unknown'
            media['publication_year']=publication_year
            media['format_group']=row[4]
            format_subgroup = row[5]
            if len(format_subgroup) == 0 or format_subgroup == "null":
                format_subgroup = "general"
            media['format_subgroup']=format_subgroup
            media_matched_to_search.append(media)

    return json.dumps(media_matched_to_search)



@api.route('/checkout_hourly')
def get_checkouts_hourly():
    '''
    Returns JSON dictionary containing key-value pairs of hours and counts of books checked out during that hour, with entries ordered by hour, ascending.
    '''
    seasons_defined_by_month = {'Spring':[3,4,5], 'Summer':[6,7,8],'Fall':[9,10,11], 'Winter':[12,1,2], 'All year':[1,2,3,4,5,6,7,8,9,10,11,12]}
    number_for_day_of_week = {'Sunday': 0 , 'Monday': 1, 'Tuesday': 2, 'Wednesday':3, 'Thursday': 4, 'Friday': 5, 'Saturday': 6}
    checkout_hourly_totals = {}
    checkout_hourly_sorted={}
    day_of_week_input = flask.request.args.get('day_of_week', default="Monday", type=str) #eliminate option for all days of week)
    season_input = flask.request.args.get('season', default='Spring', type=str) #eliminate option for all seasons
    query = '''SELECT EXTRACT(HOUR FROM checkout_timestamp) FROM checkout_events WHERE ('''
    season= seasons_defined_by_month[season_input]
    day_of_week = number_for_day_of_week[day_of_week_input]
    for month in season:
        query+= '(EXTRACT (MONTH FROM checkout_timestamp)) =' +str(month) + ' OR '
    query=query[:-3]
    query+= ' ) AND (EXTRACT (DOW FROM checkout_timestamp) ) =' + str(day_of_week)
    cursor = execute_cursor(query, ())
    if cursor:
        for row in cursor:
            hour = row[0]
            checkout_hourly_totals[int(float(hour))]= checkout_hourly_totals.get(int(float(hour)),0) + 1
        for i in range(0,24):
            checkout_hourly_totals[i]= checkout_hourly_totals.get(i,0)
        checkout_hourly_sorted= {key: val for key, val in sorted(checkout_hourly_totals.items(), key = lambda ele: ele[0])}
    return json.dumps(checkout_hourly_sorted)

@api.route('/popular_media/<media>/<month>/<year>')
def get_popular_media(media, month, year):
    '''
    Returns a list of JSON dictionaries where each dictionary contains the title,
    author name, publication year, publisher, type, collection, locations, and count of one of the 25 most checked out
    items of the selected media type within the year range.
    '''
    media = media.replace("_", " ")
    month_dictionary = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    query = '''SELECT collection_items.bib_number, collection_items.title, collection_items.author_name, collection_items.publication_year, collection_items.publisher, types.description, COUNT(*) AS counted FROM checkout_events INNER JOIN collection_items ON checkout_events.bib_number=collection_items.bib_number INNER JOIN types ON collection_items.type_id=types.type_id INNER JOIN format_subgroups ON types.format_subgroup_id=format_subgroups.format_subgroup_id WHERE '''
    if month == "All_months" and year != "0":
        query += '''EXTRACT (YEAR from checkout_timestamp) = %s AND '''
        argument_tuple = (year, media,)
    elif month != "All_months" and year == "0":
        query += '''EXTRACT (MONTH from checkout_timestamp) = %s AND '''
        argument_tuple = (month_dictionary[month], media,)
    elif month == "All_months" and year == "0":
        argument_tuple = (media,)
    else:
        query += '''EXTRACT (YEAR from checkout_timestamp) = %s AND EXTRACT (MONTH from checkout_timestamp) = %s AND '''
        argument_tuple = (year, month_dictionary[month], media,)
    query += '''format_subgroups.name = %s GROUP BY collection_items.bib_number, collection_items.title, collection_items.author_name, collection_items.publication_year, collection_items.publisher, types.description ORDER BY counted DESC LIMIT 25'''
    cursor = execute_cursor(query, argument_tuple)
    popular_media = []
    if cursor:
        for row in cursor:
            media_dictionary = {}
            media_dictionary['title'] = row[1]
            media_dictionary['author_name'] = row[2]
            media_dictionary['publication_year'] = row[3]
            media_dictionary['publisher'] = row[4]
            media_dictionary['type'] = row[5]
            media_dictionary['collection'] = get_collection_from_bib_number(str(row[0]))
            media_dictionary['locations'] = get_locations_from_bib_number(str(row[0]))
            popular_media.append(media_dictionary)
    return json.dumps(popular_media)

@api.route('/popular_collections/<month>/<year>')
def get_popular_collections(month, year):
    '''
    Returns a list of JSON dictionaries where each dictionary contains a descritpion and number of times checked out of the 10 most popular collections in a given year range
    '''
    month_dictionary = {'January':1, 'February':2, 'March':3, 'April':4, 'May':5, 'June':6, 'July':7, 'August':8, 'September':9, 'October':10, 'November':11, 'December':12}
    query = '''SELECT collections.description, COUNT(*) AS counted FROM checkout_events INNER JOIN collection_items ON checkout_events.bib_number=collection_items.bib_number INNER JOIN collections ON collections.collection_id=collection_items.collection_id '''
    if month == "All_months" and year != "0":
        query += '''WHERE EXTRACT (YEAR from checkout_timestamp) = %s '''
        argument_tuple = (year,)
    elif month != "All_months" and year == "0":
        query += '''WHERE EXTRACT (MONTH from checkout_timestamp) = %s '''
        argument_tuple = (month_dictionary[month],)
    elif month == "All_months" and year == "0":
        argument_tuple = ()
    else:
        query += '''WHERE EXTRACT (YEAR from checkout_timestamp) = %s AND EXTRACT (MONTH from checkout_timestamp) = %s '''
        argument_tuple = (year, month_dictionary[month],)
    query += '''GROUP BY collections.description ORDER BY counted DESC LIMIT 10'''
    cursor = execute_cursor(query, argument_tuple)
    popular_collections = []
    for row in cursor:
        collection_dictionary = {}
        collection_dictionary["collection"] = row[0]
        collection_dictionary["count"] = int(row[1])
        popular_collections.append(collection_dictionary)
    return json.dumps(popular_collections)
    
@api.route('recommendations/<bib_number>')
def get_recommendations(bib_number):
    '''
    Returns a JSON list of dictionaries with each dictionary representing basic information about a library item recommended based on subject similarity.
    '''
    subject_id_list = get_subjects_ids_from_bib_number(bib_number)
    subject_ids = ''
    for id in subject_id_list:
        subject_ids += str(id) +','
    subject_ids = subject_ids[:-1]
    query = ''' SELECT bib_number, COUNT(DISTINCT subject_id) FROM subject_links WHERE subject_id IN (''' + subject_ids + ''') AND bib_number != %s GROUP BY bib_number ORDER BY COUNT(*) DESC LIMIT 10'''
    cursor = execute_cursor(query, (bib_number,))
    recommended_bib_numbers =[]
    number_of_matched_subjects=[]
    for row in cursor:
        recommended_bib_numbers.append(row[0])
        number_of_matched_subjects.append(int(row[1]))
    recommendations_with_basic_information = []
    recommendations_with_basic_information = get_basic_information_from_bib_number_list(recommended_bib_numbers)
    for index in range(len(recommendations_with_basic_information)):
        if len(subject_id_list) == number_of_matched_subjects[index]:
            recommendations_with_basic_information[index].update({"exact_match": "Yes" })
        else:
            recommendations_with_basic_information[index].update({"exact_match": "No" })
    return json.dumps(recommendations_with_basic_information)
