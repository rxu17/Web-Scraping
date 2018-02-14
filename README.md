# Web-Scraping

## Packages:
- sqlite3
- lxml
- pandas
- requests

## Goal(s):

The website url can be found [here.](http://ca.healthinspections.us/napa/search.cfm?start=1&1=1&sd=01/01/1970&ed=03/01/2017&kw1=&kw2=&kw3=&rel1=N.permitName&rel2=N.permitName&rel3=N.permitName&zc=&dtRng=YES&pre=similar) 

1) For each inspection for each facility on a single page of results from the Napa county health
department website (url given below), we scraped the following information:
- Facility name
- Address (just street info, not city, state, or zip)
- City
- State
- Zipcode
- Inspection date
- Inspection type
- For each out-of-compliance violation type, scrape the violation type number and corresponding description.

2) We then placed this information in a sqlite3 database.
3) We then query this info from the database, and print it to the console using pandas

## Results:
In progress...
