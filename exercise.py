"""
The goal of the python program was to do the following:
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
         For example, an inspection might contain violation type numbers 6 and 7, and descriptions
         "Adequate handwashing facilities supplied & accessible" and "Proper hot and cold holding temperatures"
    2) We then placed this information in a sqlite3 database.
    3) We then query this info from the database, and print it to the console using pandas
"""

import sqlite3
from lxml import html
import requests
from lxml.html import tostring
import pandas as pd


page_url = ("http://ca.healthinspections.us/napa/search.cfm?start=1&1=1&sd=01/01/1970&ed=03/01/2017&kw1=&kw2=&kw3=&rel1=N.permitName&rel2=N.permitName&rel3=N.permitName&zc=&dtRng=YES&pre=similar")

# @method setup_db sets up our database and its connection then creates a table facilities
#
def setup_db():
    conn = sqlite3.connect('exercise.db')
    c = conn.cursor()
    
    # Create our initial table
    c.execute('''CREATE TABLE facilities (name text, address text, city text, 
    state text, zipcode integer, inspection_date text, inspection_type text, 
    violation_type_num integer, violation_des text)''')
    
    conn.commit() # save changes

# @method checkAddress(helper method) breaks the given string into address components-city, state, zipcode
# @param {String} address 
# @return {List} of our address components
#
def checkAddress(address):
    zipcode = ''
    state = ''
    city = ''
    address = address.split()
    if len(address) > 0 and len(address[-1]) == 5 and address[-1].isdigit():
        zipcode = address[-1]
    if len(address) > 1 and len(address[-2]) == 2 and address[-2].isalpha():
        state = address[-2]
        if len(address) > 2:
            city = address[-3]
    if len(address) > 3:
        address = " ".join(address[:-3])
    return [address, city, state, zipcode]

# @method scrape scraps website for info listed above, then reads it into pandas and prints it
#
def scrape():
    conn = sqlite3.connect('exercise.db')
    c = conn.cursor()
    
    root = html.parse(page_url)
    pages = root.xpath(".//a[@class='buttN']/@href") # the many pages' links

    # goes through multiple pages of facilities
    for page in pages:
        base_page = "http://ca.healthinspections.us/napa/"
        cur_page = requests.compat.urljoin(base_page, page) # makes link absolute instead of relative
        root = html.parse(cur_page)
        urls = root.xpath(".//a/@href") # looks for inspect. rep. links
        
        # goes through multiple facilities' inspection reports on each page
        for url in urls:
            base_url = "http://ca.healthinspections.us"
            if '..' in url: # our inspection report links contains the following
                new_url = url.replace('..', '')
                new_url = requests.compat.urljoin(base_url,new_url)
                root = html.parse(new_url)
                
                data = root.xpath("//div[@class = 'topSection']//text()") # most of info in under class = "topSection"

                facility_name = data[data.index([x for x in data if 'Facility Name' in x][0])+1]
                address = data[data.index([x for x in data if 'Address' in x][0])+1]
                address = checkAddress(address) # breaks address up 
                              
                page = requests.get(new_url) # grabbing out of compliance violations through image url
                root = html.fromstring(page.text)
                imageUrl = root.xpath('//img[contains(@src, "box_checked")]') # find all the checked boxes image urls
                
                tree = root.getroottree()
                violation_type_num = ''
                violation_des = ''
                for r in imageUrl: # loop gets location of out of compliance violations
                    path = tree.getpath(r)
                    if '/td[3]/img' in path: # want the 3rd col to be checked
                        violation = root.xpath(path.replace('/td[3]/img', '/td[1]//text()'))[0]
                        violation_type_num += violation.split()[0].replace('.', '') + ", "
                        violation_des += violation.split()[1] + ", "
                    
                # tidying up
                if violation_des[-2: ] == ", ":
                    violation_des = violation_des[:-2]
                if violation_type_num[-2: ] == ", ":
                    violation_type_num = violation_type_num[:-2]
                        
                inspection_date = data[data.index([x for x in data if 'Date' in x][0])+1]
                inspection_type = data[data.index([x for x in data if 'Inspection Type' in x][0])+1]
                
                total_info = [facility_name] + address + [inspection_date, inspection_type, violation_type_num, violation_des]
                
                c.execute("INSERT INTO facilities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", total_info) 
                conn.commit()

            else:
                pass
            
    print(pd.read('SELECT * FROM facilities', conn))  #final result
    conn.close()
 
# main program 
def main():
    #setup_db()
    scrape()


if __name__ == '__main__':
    main()
