# Seattle Library Explorer

AUTHORS: Rebecca Hicke and Josiah Misplon – Fall 2020
	 Instructions and supplementary code by Professor Jeff Ondich at Carleton College

DATA: Collection and checkout information from the Seattle Public Library System (2005-2017)

      Copyright information: https://data.seattle.gov/stories/s/Data-Policy/6ukr-wvup/
      To get the data most efficiently: https://www.kaggle.com/seattle-public-library/seattle-library-checkout-records?select=Checkouts_By_Title_Data_Lens_2005.csv
      There are separate files for each of the years from 2005 to 2017, in addition to a file for the library collection and a file that contains information on abbreviations used elsewhere in the data.

TO RUN: Neither the database nor the data cleaning code are included in this github. 
        If you're interested in running this application, you are welcome to clean the data and create a database named 'library' using Postgres, then run the below commands to create the appropriate tables in the database:

        CREATE TABLE collection_items (
    		bib_number INT,
		title TEXT,
    		author_name TEXT,
   		publication_year INT,
		publisher TEXT,
    		type_id INT,
    		collection_id INT,
		count INT
        );

        CREATE TABLE locations (
		location_id INT,
		code TEXT,
		branch_name TEXT
	);

	CREATE TABLE location_links (
		bib_number INT,
		location_id INT,
		count INT
	);

	CREATE TABLE types (
		type_id INT,
		code TEXT,
		description TEXT,
		format_group_id INT,
		format_subgroup_id INT,
		category_group_id INT
	);

	CREATE TABLE collections (
		collection_id INT,
		code TEXT,
		description TEXT,
		format_group_id INT,
		format_subgroup_id INT,
		category_group_id INT,
		category_subgroup_id INT
	);

	CREATE TABLE format_groups (
		format_group_id INT,
		name TEXT
	);

	CREATE TABLE format_subgroups (
		format_subgroup_id INT,
		name TEXT
	);

	CREATE TABLE category_groups (
		category_group_id INT,
		name TEXT
	);

	CREATE TABLE category_subgroups (
		category_subgroup_id INT,
		name TEXT
	);

	CREATE TABLE subjects (
		subject_id INT,
		subject_name TEXT
	);

	CREATE TABLE subject_links (
		bib_number INT,
		subject_id INT
	);

	CREATE TABLE checkout_events (
		bib_number INT,
		checkout_timestamp TIMESTAMP
	);

	Then, import the cleaned data to the tables in the database.
