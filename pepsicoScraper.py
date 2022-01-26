import selenium
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from selenium.webdriver.common.by import By 
from selenium.common.exceptions import NoSuchElementException
import pandas as pd 
from bs4 import BeautifulSoup
import json
from time import sleep 
from tqdm import tqdm
import urllib.request
from selenium.webdriver.chrome.options import Options

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)

def generate_Pepsico():
	dataframe = pd.DataFrame(
		columns = ["Title", "Location", "Description", "Apply_Link", "Company Name", "Date Posted", "HTML",
                 "DescriptionBS4", "Type", "Category", "Valid_Until"])

	driver = webdriver.Chrome('./chromedriver')
	driver.maximize_window()

	url = 'https://www.pepsicojobs.com/canada/jobs?stretchUnits=KILOMETERS&stretch=10&location=Canada'
	driver.get(url)

	sleep(3)

	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//p[@class="job-title"]'))
			)
		print('Found ' + driver.find_element_by_xpath('//h2[@id="search-results-indicator"]').get_attribute('innerHTML') + '!')
	except NoSuchElementException:
		pass

	sleep(3)

	try:
		chat_element_close = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//button[@id="_apply_showhide"]'))
			)
		cookie_element_close = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located((By.XPATH, '//a[@class="deny-button"]'))
			)
		chat_element_close.click()
		cookie_element_close.click()
		# driver.find_element_by_xpath('//button[@id="_apply_showhide"]').click()
		# driver.find_element_by_xpath('//a[@class="deny-button"]').click()
	except:
		print('Problem with connection or webdriver, run the script again!')




	jobs = []

	counter = 0
	flag = True
	while flag:

		driver.execute_script("window.scrollTo(0, 1080);")

		next_button = WebDriverWait(driver, 20).until(
			EC.presence_of_element_located((By.XPATH, '//button[@aria-label="JOBS.NEXT_PAGE_ARIA_LABEL"]'))
			)

		job_elements = driver.find_elements_by_xpath('//a[@class="job-title-link"]')
		for j in job_elements:
			jobs.append(j.get_attribute('href'))

		counter = counter + len(job_elements)
		print("{f1} job links added.".format(f1 = str(counter)))

		if not next_button.is_enabled():
			flag = False
		else:
			next_button.click()


	

	for job in tqdm(jobs):

		try:
			pass_flag = False

			read_attempts = 0
			while read_attempts < 3:
				try:
					source = urllib.request.urlopen(job).read()
					soup = BeautifulSoup(source, 'lxml')
					data = json.loads(soup.find('script', type="application/ld+json").string)
					break
				except:
					if read_attempts < 2:
						print('\nCould not read data from: {crashed_link} \nTrying again...'.format(crashed_link = job))
					if read_attempts >= 2:
						pass_flag = True

				read_attempts += 1
				

			driver.get(job)

			for a in range(3):
				try:
					WebDriverWait(driver, 5).until(
					EC.presence_of_element_located((By.XPATH, '//span[@token-data="LP.LOGO-TEXT"]'))
					)
					break
				except NoSuchElementException:
					print('\nCould not load page! ({e1} / 3 tries)'.format(e1 = str(a+1)))
					if a >= 2:
						pass_flag = True
					

			if pass_flag:

				print('\nPassing to next item due to error in reading or loading page!')
				continue


			# title:
			title = data['title']

			# location: 
			location = data['jobLocation']['address']['addressLocality'] + ' / ' + data['jobLocation']['address']['addressRegion'] + ', '+ data['jobLocation']['address']['addressCountry']

			# description: 
			full_description = driver.find_element(By.XPATH, '//article[@id="description-body"]').get_attribute('innerHTML')
			desc_soup = BeautifulSoup(full_description, 'lxml')
			description = desc_soup.get_text(separator = '\n')

			# apply link:
			apply_link = driver.find_element(By.XPATH, '//a[@id="link-apply"]').get_attribute('href')

			# company name:
			company_name = data['hiringOrganization']['name']

			# date posted: 
			date_posted = data['datePosted']

			# employment type: 
			employment_type = BeautifulSoup(full_description[full_description.find('Job Type:'):], 'lxml').get_text().replace('Job Type:', '')

			# category: 
			category = driver.find_element(By.XPATH, '//li[@id="header-categories"]/span').get_attribute('innerHTML')

			# valid until: 
			valid_until = data['validThrough']

			# appending job information to dataframe:
			dataframe = dataframe.append({'Title': title,
	                                      'Location': location,
	                                      'Description': description,
	                                      'Apply_Link': apply_link,
	                                      'Company Name': company_name,
	                                      'Date Posted': date_posted,
	                                      'HTML': None,
	                                      'DescriptionBS4': None,
	                                      'Type': employment_type,
	                                      'Category': category,
	                                      'Valid_Until': valid_until},
	                                      ignore_index=True)
		except:
			print('')
			continue



	return dataframe



def generate_Pepsico_test():
	generate_Pepsico().to_csv(r'pepsico_data.csv', index = False)

#generate_Pepsico_test()





	
