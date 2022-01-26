import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import json
from time import sleep
from tqdm import tqdm



def generate_ApplyBoard():
	"""Find current jobs on ApplyBoard.com, scrape each link for job data, return job data in a pandas DataFrame."""


	# creating the pandas dataframe:
	dataframe = pd.DataFrame(
		columns = ["Title", "Location", "Description", "Apply_Link", "Company Name", "Date Posted", "HTML",
                 "DescriptionBS4", "Type"])

	driver = webdriver.Chrome('./chromedriver')
	#driver.maximize_window()

	jobs_page_url = "https://www.applyboard.com/careers#view-positions"
	driver.get(jobs_page_url)

	# driver.maximize_window() 
	sleep(3)

	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//li[@class="lever-job"]'))
			)
		print('Found jobs!')
	except NoSuchElementException:
		pass

	# list of all the job links on ApplyBoard page:
	jobs = []
	jobs_elements = driver.find_elements_by_xpath('//a[@class="lever-job-title"]')

	for j in jobs_elements:
		jobs.append(j.get_attribute('href'))

	driver.close()
	print('Number of jobs found: ' + str(len(jobs)))

	# iterating through the individual job links
	# (for testing, since there are too many jobs, change jobs to jobs[:number of jobs you want to scrape])
	for job in tqdm(jobs):
		# print('job link: ' + job)
		source = urllib.request.urlopen(job).read()
		soup = BeautifulSoup(source, 'lxml')
		data = json.loads(soup.find('script', type="application/ld+json").string)

		
		# title:
		title = data['title']

		# location:
		location = data['jobLocation']['address']['addressLocality']

		# description:
		full_description = data['description']
		
		# start_index = full_description.find('Role\n')
		# end_index = full_description.find('\nLife at ApplyBoard\n')
		# description = full_description[start_index:end_index]

		
		desc_list = []
		desc_list.append(full_description)

		additional = soup.find_all('h3')
		for a in additional:
			for b in a.parent.contents:
				desc_list.append(b.text)

		#print(description)
		description = '\n'.join(desc_list)

		# apply link:
		apply_link = soup.find('a', string='Apply for this job')['href']

		# company name:
		company_name = data['hiringOrganization']['name']

		# date posted:
		date_posted = data['datePosted']

		# employment type:
		employment_type = data['employmentType']

		# appending job information to dataframe:
		dataframe = dataframe.append({'Title': title,
                                      'Location': location,
                                      'Description': description,
                                      'Apply_Link': apply_link,
                                      'Company Name': company_name,
                                      'Date Posted': date_posted,
                                      'HTML': None,
                                      'DescriptionBS4': None,
                                      'Type': employment_type},
                                      ignore_index=True)

		

	return dataframe
	
# testing:
def generateApplyBoard_test():
	generate_ApplyBoard().to_csv(r'applyboard_data.csv', index = False)


 # uncomment to test:
# generateApplyBoard_test()








