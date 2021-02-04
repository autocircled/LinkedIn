from urllib.request import urlopen
# pip install beautifulsoup4
from bs4 import BeautifulSoup as soup
from pathlib import Path
import json
# pip install python-dateutil --user
import dateutil.parser
import random
from random import seed
from random import choice
from datetime import datetime, timedelta
import os
import io

# get redirected URL from LinkedIn
import re
from urllib.parse import unquote


seed(1)
sequence = [(i) for i in range(10)]
print(sequence)
# check if previously added any minutes
count_minutes = Path("min-count.txt")
if os.path.getsize(count_minutes) > 0:
	p = open(count_minutes, "r")
	q = p.readlines()
	random_mins = int(q[0])
else:
	random_mins = 0
	
#print(random_mins)

# open HTTP connection
def openConnection(url):
	# open connection and grabbing the page
	with urlopen(url) as uClient:
                page_html = uClient.read()
                uClient.close()
	return page_html

def scrap(url):
	global random_mins
	random_mins += choice(sequence)
	now = datetime.now() + timedelta(hours= -6)
	now2 =  datetime.now() + timedelta(hours= -6, minutes=random_mins)


	page_html = openConnection(url)
	# html parsing
	page_soup = soup(page_html, "html.parser")

	# job container
	job_container = page_soup.find('section', attrs = {'class':'core-rail'})

	# Job informations
	#Title
	title = job_container.h1.text
	
	#link
	link = url
	link_found = 'no'
	link_source = job_container.findAll("a", class_='apply-button apply-button--link', attrs={'data-tracking-control-name':'public_jobs_apply-link-offsite'})
	# print(link_source[1].get('href'))
	# print(len(link_source))
	if len(link_source) > 0:
		# print("Link found")
		link_found = 'yes'
		raw_link = link_source[1].get('href')
		filter_link = re.findall('url=\s*([a-zA-Z0-9%-]+)', raw_link)
		link = unquote(filter_link[0])
		
	else:
		print("Link not found")
	
	
	# Company
	company_container = job_container.find('a', attrs = {'class':'topcard__org-name-link'})
	company = company_container.text

	# Location
	span_list = page_soup.findAll('span', attrs = {'class':'topcard__flavor'})
	locations = span_list[1].text.split(",")

	# Contents
	# Container
	content_container = page_soup.find('section', attrs = {'class':'description'})

	# description container
	description_container = content_container.find('div', attrs = {'class':'description__text description__text--rich'})

	# Job Description
	# description = description_container.p.text

	# Job criteria container
	criteria_container = content_container.find('ul', attrs = {'class':'job-criteria__list'})
	all_criterias = criteria_container.findAll('li')
	seniority = all_criterias[0].span.text
	job_type = all_criterias[1].span.text
	job_functions_container = all_criterias[2].findAll('span')
	job_industies_container = all_criterias[3].findAll('span')

	# get json data
	json_data = "".join(page_soup.find('script', {'type':'application/ld+json'}).contents)
	j = json.loads(json_data)
	# Load as JSON
	# j = json.loads(json_data)
	
	# data parse
	d = dateutil.parser.parse(j['validThrough'])
	
	# new formatted date
	dl = d.strftime('%Y%m%d') # deadline of job
	st = now2.strftime("%Y-%m-%d %H:%M:%S")
	ft = now2.strftime('%A, %d %b %Y %H:%M:%S')
	rt = now2.strftime('%Y%m%d-%H%M%S')
	ct = now.strftime('%Y%m%d') # Current year/month/day
	
	# check if deadline is over
	if ct > dl :
		print('Deadline is over!!!!!!!!!!!!')
		exit() # exit script execution
	
	# open file for writing
	filename = Path("append.xml")
	#f=open(filename, "a+")
	with io.open(filename, "a+", encoding="utf-8") as f:

		# writing job info
		f.write("<item>\r")
		f.write("\t<title>%s</title>\r" % (title) )
		f.write("\t<pubDate>%s</pubDate>\r" % (ft) )
		f.write("\t<wp:post_date><![CDATA[%s]]></wp:post_date>\r" % (st) )
		f.write("\t<content:encoded><![CDATA[%s]]></content:encoded>\r" % (description_container) )
		f.write("\t<wp:post_name><![CDATA[%s - %s]]></wp:post_name>\r" % (title, rt))
		f.write("\t<wp:status><![CDATA[future]]></wp:status>\r")
		f.write("\t<wp:post_type><![CDATA[jobs]]></wp:post_type>\r")

		# company
		f.write("\t<category domain=\"company\" nicename=\"%s\"><![CDATA[%s]]></category>\r" % (company, company) )

		# locations as location
		for location in locations:
			location = location.strip()
			f.write("\t<category domain=\"location\" nicename=\"%s\"><![CDATA[%s]]></category>\r" % (location, location) )

		# job_functions
		count = 0
		while (count < len(job_functions_container)):
			value = job_functions_container[count].text
			f.write("\t<category domain=\"job_type\" nicename=\"%s\"><![CDATA[%s]]></category>\r" % (value, value) )
			count = count + 1

		# job_industies
		count = 0
		while(count < len(job_industies_container)):
			value = job_industies_container[count].text
			f.write("\t<category domain=\"job_industry\" nicename=\"%s\"><![CDATA[%s]]></category>\r" % (value, value) )
			count = count + 1

		# Seniority
		if seniority == 'Entry level':
			senior_value = 'entry'
		elif seniority == 'Internship':
			senior_value = 'intern'
		elif seniority == 'Associate':
			senior_value = 'associate'
		elif seniority == 'Mid-Senior level':
			senior_value = 'mid_senior'
		elif seniority == 'Director':
			senior_value = 'director'
		elif seniority == 'Executive':
			senior_value = 'executive'
		else:
			senior_value = 'not_applicable'

		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[seniority_level]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[%s]]></wp:meta_value>\r\t</wp:postmeta>\r" % (senior_value) )
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_seniority_level]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5de7c56f447e5]]></wp:meta_value>\r\t</wp:postmeta>\r")

		# Job Type
		if job_type == ('Full-time') or job_type == ('Fulltime'):
			job_type_value = 'FULL_TIME'
		elif job_type == 'Part-time':
			job_type_value = 'PART_TIME'
		elif job_type == 'Contract':
			job_type_value = 'CONTRACTOR'
		elif job_type == 'Temporary':
			job_type_value = 'TEMPORARY'
		elif job_type == 'Intern' or job_type == 'Internship':
			job_type_value = 'INTERN'
		elif job_type == 'Volunteer':
			job_type_value = 'VOLUNTEER'
		else:
			job_type_value = 'OTHER'

		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[employment_type]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[%s]]></wp:meta_value>\r\t</wp:postmeta>\r" % (job_type_value) )
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_employment_type]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5de7c710447e6]]></wp:meta_value>\r\t</wp:postmeta>\r")


		# JSON DATA
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[json_from_linkedin]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[<script type=\"application/ld+json\">%s</script>]]></wp:meta_value>\r\t</wp:postmeta>\r" % (json_data) )
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_json_from_linkedin]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5de7c8cc966f6]]></wp:meta_value>\r\t</wp:postmeta>\r")
		# Deadline 
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[deadline_job]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[%s]]></wp:meta_value>\r\t</wp:postmeta>\r" % (dl))
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_deadline_job]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5df0612112792]]></wp:meta_value>\r\t</wp:postmeta>\r")
		
		if link_found == 'yes':
			f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[platform]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[other]]></wp:meta_value>\r\t</wp:postmeta>\r")
		else:
			f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[platform]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[linkedin]]></wp:meta_value>\r\t</wp:postmeta>\r")
		
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_platform]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5decd5c11221c]]></wp:meta_value>\r\t</wp:postmeta>\r")
							
		
		# Apply Now
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[apply_now]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[%s]]></wp:meta_value>\r\t</wp:postmeta>\r" % (link))
		f.write("\t<wp:postmeta>\r\t\t<wp:meta_key><![CDATA[_apply_now]]></wp:meta_key>\r\t\t<wp:meta_value><![CDATA[field_5de87eceae8fa]]></wp:meta_value></wp:postmeta>\r")

		f.write("</item>\r")
	
		f.close()
	min_calc = Path("min-count.txt")
	mcl=open(min_calc, "w")
	mcl.write("%s" % (random_mins))
	mcl.close()


# started new technique

html_data = soup(open("linkedin.html", encoding='utf8'), "html.parser")
job_lists = html_data.findAll('li', attrs = {'class':'result-card'})
count = 0
links = []
progress_path = Path("progress.txt")

# Checking if there is already links in the file
if os.path.getsize(progress_path) == 0:
	
	# Creating a list of links
	for job in job_lists:
		links.append(job.a.get('href'))

	# shuffle all the links
	random.shuffle(links)
	
	# Opening file for store links to scrap
	with io.open(progress_path, "w") as pp:

		# Writing links in the file from list
		for link in links:
			pp.write( '%s\n' % link )

		# After write all the links file closed
		pp.close()


# if os.path.getsize(progress_path) == 0:
# 	pp = open(progress_path, "w")
# 	pp.write("%s" % (links))
# 	pp.close()
ready_links = []
with open(progress_path, 'r') as links:
	#URLs = opp.readlines()
	for link in links:
		currentPlace = link[:-1]
		ready_links.append(currentPlace)

while len(ready_links) > 0:

	try:
				#random.shuffle(ready_links)
				print(ready_links[len(ready_links)-1])
				scrap(ready_links[len(ready_links)-1])
		
	except:
                print("Something went wrong when writing to the file")
	
    
	print(len(ready_links)-1)
	ready_links.pop(len(ready_links)-1)
	with io.open(progress_path, "w", encoding="utf-8") as dff1:
		for link in ready_links:
			dff1.write("%s\n" % (link))
		dff1.close()
