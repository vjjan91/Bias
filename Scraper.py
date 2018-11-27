'''Hello! This is the third (UPDATE 1.0: Correction, IT IS THE FOURTH PROJECT!) project that I've started in two months.
Feels great to learn so many new concepts.
Here's to never stop learning.
The aim of the project is to measure (quantitatively) the disparity in the the publications
pertaining to the natural history and ecology of specific geographical regions.
This project is a collaboration between Vijay Ramesh, Department of Ecology, Evolution & Environmental Biology, Columbia University.
More info will be added here. Soon.
Sarthak J. Shetty
04/08/2018'''

'''Adding the libraries to be used here.'''

'''urllib2 has since lost support and urllib.request has replaced it. urlopen has been borrowed from there.'''
from urllib.request import urlopen
''''Importing urllib.error to handle errors in HTTP pinging.'''
import urllib.error
'''BeautifulSoup is used for souping.'''
from bs4 import BeautifulSoup
'''Fragmenting code into different scripts. Some functions are to be used across the different sub-parts as well.
Hence, shifted some of the functions to the new script.'''
from common_functions import pre_processing, arguments_parser,  status_logger

def url_reader(url, status_logger_name):
	'''This keyword is supplied to the URL and is hence used for souping.''' 
	'''Encountered an error where some links would not open due to HTTP.error
	This is added here to try and ping the page. If it returns false the loop ignores it and
	moves on to the next PII number'''
	try:
		page=urlopen(url)
		page_status(page, status_logger_name)
		return page
	except (UnboundLocalError, urllib.error.HTTPError):
		pass

def url_generator(start_url, query_string, status_logger_name):
	'''This function is written to scrape all possible webpages of a given topic
	The search for the URLs truncates when determiner doesn't return a positive value'''
	url_generator_start_status_key = start_url+" "+"start_url has been received"
	status_logger(status_logger_name, url_generator_start_status_key)
	urls_to_scrape=[]
	counter = 0
	total_url = start_url+str(counter)+"?query="+query_string
	initial_url_status_key = total_url+" "+"has been obtained"
	status_logger(status_logger_name, initial_url_status_key)
	urls_to_scrape.append(total_url)
	test_soup = BeautifulSoup(urlopen(total_url), 'html.parser')
	determiner = test_soup.find('a', {'class':'title'})
	'''This while loop continuously pings and checks for new webpages, then stores them for scraping'''
	while(determiner):
		counter = counter+1
		total_url = start_url+str(counter)+"?query="+query_string
		url_generator_while_status_key=total_url+" "+"has been obtained"
		status_logger(status_logger_name, url_generator_while_status_key)
		soup = BeautifulSoup(urlopen(total_url), 'html.parser')
		determiner = soup.find('a', {'class':'title'})
		urls_to_scrape.append(total_url)
	urls_to_scrape.pop(len(urls_to_scrape)-1)
	#print(urls_to_scrape)
	url_generator_stop_status_key = "URLs have been obtained"
	return urls_to_scrape

def abstract_id_database_writer(abstract_id_log_name, abstract_input_tag_id, site_url_index):
	abstract_id_writer_temp_index  = site_url_index
	'''This function writes the abtract ids to a .txt file for easy access and documentation.'''
	abstract_id_log = open((abstract_id_log_name+str(abstract_id_writer_temp_index+1)+'.txt'), 'a')
	abstract_id_log.write(abstract_input_tag_id)
	abstract_id_log.write('\n')
	abstract_id_log.close()

def abstract_database_writer(abstract_page_url, title, author, abstract, abstracts_log_name, status_logger_name):
	'''This function makes text files'''
	abstract_database_writer_start_status_key = "Writing"+" "+title+" "+"by"+" "+author+" "+"to disc"
	status_logger(status_logger_name, abstract_database_writer_start_status_key)
	abstracts_log = open(abstracts_log_name+'.txt', 'a')
	abstracts_log.write("Title:"+" "+title)
	abstracts_log.write('\n')
	abstracts_log.write("Author:"+" "+author)
	abstracts_log.write('\n')
	abstracts_log.write("URL:"+" "+abstract_page_url)
	abstracts_log.write('\n')
	abstracts_log.write("Abstract:"+" "+abstract)
	abstracts_log.write('\n'+'\n')
	abstracts_log.close()
	abstract_database_writer_stop_status_key = "Written"+" "+title+" "+"to disc"
	status_logger(status_logger_name, abstract_database_writer_stop_status_key)

def abstract_id_database_reader(abstract_id_log_name, site_url_index, status_logger_name):
	abstract_id_reader_temp_index = site_url_index
	'''This function has been explicitly written to access
	the abstracts database that the given prgram generates.'''
	abstract_id_database_reader_start_status_key = "Extracting Abstract IDs from disc"
	status_logger(status_logger_name, abstract_id_database_reader_start_status_key)

	lines_in_abstract_id_database=[line.rstrip('\n') for line in open(abstract_id_log_name+str(abstract_id_reader_temp_index+1)+'.txt')]

	abstract_id_database_reader_stop_status_key = "Extracted Abstract IDs from disc"
	status_logger(status_logger_name,abstract_id_database_reader_stop_status_key)

	return lines_in_abstract_id_database

def page_status(page, status_logger_name):
	'''Prints the page status. Will be used whenever a new webpage is picked for scraping.'''
	page_status_key = "Page status:"+" "+str(page.status)
	status_logger(status_logger_name, page_status_key)

def page_souper(page, status_logger_name):
	'''Function soups the webpage elements and provided the tags for search.
	Note: Appropriate encoding has to be picked up before souping'''
	page_souper_start_status_key = "Souping page"
	status_logger(status_logger_name, page_souper_start_status_key)
	page_soup = BeautifulSoup(page, 'html.parser')
	page_souper_stop_status_key = "Souped page"
	status_logger(status_logger_name, page_souper_stop_status_key)
	return page_soup

def abstract_page_scraper(abstract_url, abstract_input_tag_id, abstracts_log_name, status_logger_name):
	'''This function is written to scrape the actual abstract of the specific paper,
	 that is being referenced within the list of abstracts'''
	abstract_page_scraper_status_key="Abstract ID:"+" "+abstract_input_tag_id
	status_logger(status_logger_name, abstract_page_scraper_status_key)
	abstract_page_url = abstract_url+abstract_input_tag_id
	abstract_page = url_reader(abstract_page_url, status_logger_name)
	abstract_soup = page_souper(abstract_page, status_logger_name)
	title = title_scraper(abstract_soup)
	
	'''Due to repeated attribute errors, these failsafes had to be put in place'''
	try:
		author = author_scraper(abstract_soup)
	except AttributeError:
		author = "Author not available"
	try:
		abstract = abstract_scraper(abstract_soup)
	except AttributeError:
		abstract = "Abstract not available"
	
	abstract_database_writer(abstract_page_url, title, author, abstract, abstracts_log_name, status_logger_name)
	#print(abstract_soup_text)

def abstract_crawler(abstract_url, abstract_id_log_name, abstracts_log_name, site_url_index, status_logger_name):
	abstract_crawler_temp_index  = site_url_index
	'''This function crawls the page and access each and every abstract'''
	abstract_input_tag_ids = abstract_id_database_reader(abstract_id_log_name, abstract_crawler_temp_index, status_logger_name)
	for abstract_input_tag_id in abstract_input_tag_ids:
		try:
			abstract_crawler_accept_status_key="Abstract Number:"+" "+str((abstract_input_tag_ids.index(abstract_input_tag_id)+1)+abstract_crawler_temp_index*20)
			status_logger(status_logger_name, abstract_crawler_accept_status_key)
			abstract_page_scraper(abstract_url, abstract_input_tag_id, abstracts_log_name, status_logger_name)
		except TypeError:
			abstract_crawler_reject_status_key="Abstract Number:"+" "+str(abstract_input_tag_ids.index(abstract_input_tag_id)+1)+" "+"could not be processed"
			status_logger(status_logger_name, abstract_crawler_reject_status_key)
			pass

def abstract_scraper(abstract_soup):
	'''This function scrapes the abstract from the soup and returns to the page scraper'''
	abstract = str(abstract_soup.find('p', {'class':'Para'}).text.encode('utf-8'))[1:]
	return abstract

def author_scraper(abstract_soup):
	'''This function scrapes the author of the text, for easy navigation and search'''
	author = str(abstract_soup.find('span', {'class':'authors__name'}).text.encode('utf-8'))[1:]
	return author

def title_scraper(abstract_soup):
	'''This function scrapes the title of the text'''
	try:
		title = str(abstract_soup.find('h1',{'class':'ArticleTitle'}).text.encode('utf-8'))[1:]
	except AttributeError:
		title = str(abstract_soup.find('h1',{'class':'ChapterTitle'}).text.encode('utf-8'))[1:]
	return title

def abstract_id_scraper(abstract_id_log_name, page_soup, site_url_index, status_logger_name):
	'''This function helps in obtaining the PII number of the abstract.
	This number is then coupled with the dynamic URL and provides'''

	abstract_id_scraper_start_status_key="Scraping IDs"
	status_logger(status_logger_name, abstract_id_scraper_start_status_key)
	''''This statement collects all the input tags that have the abstract ids in them'''
	abstract_input_tags = page_soup.findAll('a', {'class':'title'})
	for abstract_input_tag in abstract_input_tags:
		abstract_input_tag_id=abstract_input_tag.get('href')
		abstract_id_database_writer(abstract_id_log_name, abstract_input_tag_id, site_url_index)

	abstract_id_scraper_stop_status_key="Scraped IDs"
	status_logger(status_logger_name, abstract_id_scraper_stop_status_key)

def processor(abstract_url, urls_to_scrape, abstract_id_log_name, abstracts_log_name, status_logger_name, keywords_to_search):
	''''Multiple page-cycling function to scrape multiple result pages'''
	print(len(urls_to_scrape))
	for site_url_index in range(0, len(urls_to_scrape)):
		'''Collects the web-page from the url for souping'''
		page_to_soup = url_reader(urls_to_scrape[site_url_index], status_logger_name)
		'''Souping the page for collection of data and tags'''
		page_soup = page_souper(page_to_soup, status_logger_name)
		'''Scrapping the page to extract all the abstract IDs'''
		abstract_id_scraper(abstract_id_log_name, page_soup, site_url_index, status_logger_name)
		'''Actually obtaining the abstracts after combining ID with the abstract_url'''
		abstract_crawler(abstract_url, abstract_id_log_name, abstracts_log_name, site_url_index, status_logger_name)

def scraper_main(abstract_id_log_name, abstracts_log_name, start_url, abstract_url, query_string, status_logger_name, keywords_to_search):
	''''This function contains all the functions and contains this entire script here, so that it can be imported later to the main function'''

	'''Provides the links for the URLs to be scraped by the scraper'''
	urls_to_scrape = url_generator(start_url, query_string, status_logger_name)
	'''Calling the processor() function here'''
	processor(abstract_url, urls_to_scrape, abstract_id_log_name, abstracts_log_name, status_logger_name, keywords_to_search)