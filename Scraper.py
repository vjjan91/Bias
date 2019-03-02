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
'''Counter generates a dictionary from the abstract data, providing frequencies of occurences'''
from collections import Counter
'''Importing the CSV library here to dump the dictionary for further analysis and error checking if required. Will edit it out later.'''
import csv
'''This library is imported to check if we can feasibly introduce delays into the processor loop to reduce instances of the remote server, shutting the connection while scrapping extraordinarily large datasets.'''
import time
'''Fragmenting code into different scripts. Some functions are to be used across the different sub-parts as well. Hence, shifted some of the functions to the new script.'''
from common_functions import pre_processing, arguments_parser,  status_logger

def url_reader(url, status_logger_name):
	'''This keyword is supplied to the URL and is hence used for souping.
	Encountered an error where some links would not open due to HTTP.error
	This is added here to try and ping the page. If it returns false the loop ignores it and
	moves on to the next PII number'''
	try:
		page=urlopen(url)
		page_status(page, status_logger_name)
		return page
	except (UnboundLocalError, urllib.error.HTTPError):
		pass

def results_determiner(url, status_logger_name):
	'''This function determines the number of results that a particular keywords returns
	once it looks up the keyword on link.springer.com
	The function returns all the possible links containing results and then provides the total number of results
	returned by a particular keyword, or combination of keywords.'''
	first_page_to_scrape = urlopen(url)
	first_page_to_scrape_soup = BeautifulSoup(first_page_to_scrape, 'html.parser')
	number_of_results = first_page_to_scrape_soup.find('h1', {'id':'number-of-search-results-and-search-terms'}).find('strong').text
	results_determiner_status_key = "Total number of results obtained: "+number_of_results
	status_logger(status_logger_name, results_determiner_status_key)

def url_generator(start_url, query_string, status_logger_name):
	'''This function is written to scrape all possible webpages of a given topic
	The search for the URLs truncates when determiner variable doesn't return a positive value'''
	url_generator_start_status_key = start_url+" "+"start_url has been received"
	status_logger(status_logger_name, url_generator_start_status_key)
	'''Initiallizing a list here in order to contain the URLs. Even if a URL does not return valid results,
	it is popped later on from the list.'''
	urls_to_scrape=[]
	counter = 0
	total_url = start_url+str(counter)+"?facet-content-type=""Article""&query="+query_string
	initial_url_status_key = total_url+" "+"has been obtained"
	status_logger(status_logger_name, initial_url_status_key)
	urls_to_scrape.append(total_url)
	test_soup = BeautifulSoup(urlopen(total_url), 'html.parser')
	determiner = test_soup.find('a', {'class':'title'})
	'''This while loop continuously pings and checks for new webpages, then stores them for scraping'''
	while(determiner):
		counter = counter+1
		total_url = start_url+str(counter)+"?facet-content-type=""Article""&query="+query_string
		url_generator_while_status_key=total_url+" "+"has been obtained"
		status_logger(status_logger_name, url_generator_while_status_key)
		soup = BeautifulSoup(urlopen(total_url), 'html.parser')
		determiner = soup.find('a', {'class':'title'})
		urls_to_scrape.append(total_url)
	urls_to_scrape.pop(len(urls_to_scrape)-1)
	#print(urls_to_scrape)
	url_generator_stop_status_key = "URLs have been obtained"
	return urls_to_scrape

def page_status(page, status_logger_name):
	'''Prints the page status. Will be used whenever a new webpage is picked for scraping.'''
	page_status_key = "Page status:"+" "+str(page.status)
	status_logger(status_logger_name, page_status_key)

def page_souper(page, status_logger_name):
	'''Function soups the webpage elements and provided the tags for search.
	Note: Appropriate encoding has to be picked up beenfore souping'''
	page_souper_start_status_key = "Souping page"
	status_logger(status_logger_name, page_souper_start_status_key)
	page_soup = BeautifulSoup(page, 'html.parser')
	page_souper_stop_status_key = "Souped page"
	status_logger(status_logger_name, page_souper_stop_status_key)
	return page_soup

def abstract_word_extractor(abstract, abstract_title, abstract_year, permanent_word_sorter_list, trend_keywords, status_logger_name):
	'''This function creates the list that stores the text in the form of individual words
	against their year of appearence.'''
	abstract_word_sorter_start_status_key = "Adding:"+" "+abstract_title+" "+"to the archival list"
	status_logger(status_logger_name, abstract_word_sorter_start_status_key)
	'''This line of code converts the entire abstract into lower case'''
	abstract = abstract.lower()
	'''Converting the abstract into a list of words'''
	abstract_word_list = abstract.split()
	'''This line of code sorts the elements in the word list alphabetically. Working with dataframes is harden, hence
	we are curbing this issue by modifying the list rather.'''
	abstract_word_list.sort()
	'''If the word currently being looped in the abstract list matches the trend word being investigated for, the year it appears
	is appended to the permanent word sorter list'''
	for element in abstract_word_list:
		if(element==trend_keywords[0]):
			permanent_word_sorter_list.append(abstract_year[:4])

	abstract_word_sorter_end_status_key = "Added:"+" "+abstract_title+" "+"to the archival list"
	status_logger(status_logger_name, abstract_word_sorter_end_status_key)

def abstract_year_list_post_processor(permanent_word_sorter_list, status_logger_name):
	'''Because of this function we have a dictionary containing the frequency of occurrence of terms in specific years'''
	abstract_year_list_post_processor_start_status_key = "Post processing of permanent word sorter list has commenced"
	status_logger(status_logger_name, abstract_year_list_post_processor_start_status_key)

	starting_year = min(permanent_word_sorter_list)
	ending_year = max(permanent_word_sorter_list)

	abstract_year_dictionary = Counter(permanent_word_sorter_list)

	abstract_year_list_post_processor_end_status_key = "Post processing of permanent word sorter list has completed"
	status_logger(status_logger_name, abstract_year_list_post_processor_end_status_key)

	return abstract_year_dictionary, starting_year, ending_year

def abstract_year_dictionary_dumper(abstract_word_dictionary, abstracts_log_name, status_logger_name):
	'''This function saves the abstract word dumper to the disc for further inspection.
	The file is saved as a CSV bucket and then dumped.'''
	permanent_word_sorter_list_start_status_key = "Dumping the entire dictionary to the disc"
	status_logger(status_logger_name, permanent_word_sorter_list_start_status_key)
	with open(abstracts_log_name+"_"+"DICTIONARY.csv", 'w') as dictionary_to_csv:
		writer = csv.writer(dictionary_to_csv)
		for key, value in abstract_word_dictionary.items():
			year = key
			writer.writerow([year, value])
	
	permanent_word_sorter_list_end_status_key = "Dumped the entire dictionary to the disc"
	status_logger(status_logger_name, permanent_word_sorter_list_end_status_key)
		
def abstract_page_scraper(abstract_url, abstract_input_tag_id, abstracts_log_name, permanent_word_sorter_list, trend_keywords, site_url_index, status_logger_name):
	'''This function is written to scrape the actual abstract of the specific paper,
	 that is being referenced within the list of abstracts'''
	abstract_page_scraper_status_key="Abstract ID:"+" "+abstract_input_tag_id
	status_logger(status_logger_name, abstract_page_scraper_status_key)
	abstract_page_url = abstract_url+abstract_input_tag_id
	abstract_page = url_reader(abstract_page_url, status_logger_name)
	abstract_soup = page_souper(abstract_page, status_logger_name)
	title = title_scraper(abstract_soup, status_logger_name)
	abstract_date = abstract_date_scraper(title, abstract_soup, status_logger_name)

	'''Due to repeated attribute errors with respect to scraping the authors name, these failsafes had to be put in place.'''
	try:
		author = author_scraper(abstract_soup, status_logger_name)
	except AttributeError:
		author = "Author not available"

	'''Due to repeated attribute errors with respect to scraping the abstract, these failsafes had to be put in place.'''
	try:
		abstract = abstract_scraper(abstract_soup)
		abstract_word_extractor(abstract, title, abstract_date, permanent_word_sorter_list, trend_keywords, status_logger_name)
	except AttributeError:
		abstract = "Abstract not available"

	abstract_database_writer(abstract_page_url, title, author, abstract, abstracts_log_name, abstract_date, status_logger_name)
	analytical_abstract_database_writer(title, author, abstract, abstracts_log_name, status_logger_name)

def abstract_crawler(abstract_url, abstract_id_log_name, abstracts_log_name, permanent_word_sorter_list, trend_keywords, site_url_index, status_logger_name):
	abstract_crawler_temp_index  = site_url_index
	'''This function crawls the page and access each and every abstract'''
	abstract_input_tag_ids = abstract_id_database_reader(abstract_id_log_name, abstract_crawler_temp_index, status_logger_name)
	for abstract_input_tag_id in abstract_input_tag_ids:
		try:
			abstract_crawler_accept_status_key="Abstract Number:"+" "+str((abstract_input_tag_ids.index(abstract_input_tag_id)+1)+abstract_crawler_temp_index*20)
			status_logger(status_logger_name, abstract_crawler_accept_status_key)
			abstract_page_scraper(abstract_url, abstract_input_tag_id, abstracts_log_name, permanent_word_sorter_list, trend_keywords, site_url_index, status_logger_name)
			'''Introduces a 5 second delay between successive pings.'''
			delay_function(status_logger_name)
		except TypeError:
			abstract_crawler_reject_status_key="Abstract Number:"+" "+str(abstract_input_tag_ids.index(abstract_input_tag_id)+1)+" "+"could not be processed"
			status_logger(status_logger_name, abstract_crawler_reject_status_key)
			pass

def analytical_abstract_database_writer(title, author, abstract, abstracts_log_name, status_logger_name):
	'''This function will generate a secondary abstract file that will contain only the abstract.
	The  abstract file generated will be passed onto the Visualizer and Analyzer function, as opposed to the complete 
	abstract log file containing lot of garbage words in addition to the abstract text.'''
	analytical_abstract_database_writer_start_status_key = "Writing"+" "+title+" "+"by"+" "+author+" "+"to analytical abstracts file"
	status_logger(status_logger_name, analytical_abstract_database_writer_start_status_key)

	analytical_abstracts_txt_log = open(abstracts_log_name+'_'+'ANALYTICAL'+'.txt', 'a')
	analytical_abstracts_txt_log.write("Abstract:"+" "+abstract)
	analytical_abstracts_txt_log.write('\n'+'\n')
	analytical_abstracts_txt_log.close()

	analytical_abstract_database_writer_stop_status_key = "Written"+" "+title+" "+"to disc"
	status_logger(status_logger_name, analytical_abstract_database_writer_stop_status_key)

def abstract_database_writer(abstract_page_url, title, author, abstract, abstracts_log_name, abstract_date, status_logger_name):
	'''This function makes text files to contain the abstracts for future reference.
	It holds: 1) Title, 2) Author(s), 3) Abstract'''
	abstract_database_writer_start_status_key = "Writing"+" "+title+" "+"by"+" "+author+" "+"to disc"
	status_logger(status_logger_name, abstract_database_writer_start_status_key)
	abstracts_csv_log = open(abstracts_log_name+'.csv', 'a')
	abstracts_txt_log = open(abstracts_log_name+'.txt', 'a')
	abstracts_txt_log.write("Title:"+" "+title)
	abstracts_txt_log.write('\n')
	abstracts_txt_log.write("Author:"+" "+author)
	abstracts_txt_log.write('\n')
	abstracts_txt_log.write("Date:"+" "+abstract_date)
	abstracts_txt_log.write('\n')
	abstracts_txt_log.write("URL:"+" "+abstract_page_url)
	abstracts_txt_log.write('\n')
	abstracts_txt_log.write("Abstract:"+" "+abstract)
	abstracts_csv_log.write(abstract)
	abstracts_csv_log.write('\n')
	abstracts_txt_log.write('\n'+'\n')
	abstracts_txt_log.close()
	abstracts_csv_log.close()
	abstract_database_writer_stop_status_key = "Written"+" "+title+" "+"to disc"
	status_logger(status_logger_name, abstract_database_writer_stop_status_key)

def abstract_id_database_reader(abstract_id_log_name, site_url_index, status_logger_name):
	'''This function has been explicitly written to access
	the abstracts database that the given prgram generates.'''
	abstract_id_reader_temp_index = site_url_index
	abstract_id_database_reader_start_status_key = "Extracting Abstract IDs from disc"
	status_logger(status_logger_name, abstract_id_database_reader_start_status_key)

	lines_in_abstract_id_database=[line.rstrip('\n') for line in open(abstract_id_log_name+str(abstract_id_reader_temp_index+1)+'.txt')]

	abstract_id_database_reader_stop_status_key = "Extracted Abstract IDs from disc"
	status_logger(status_logger_name, abstract_id_database_reader_stop_status_key)

	return lines_in_abstract_id_database

def abstract_id_database_writer(abstract_id_log_name, abstract_input_tag_id, site_url_index):
	'''This function writes the abtract ids to a .txt file for easy access and documentation.'''
	abstract_id_writer_temp_index  = site_url_index
	abstract_id_log = open((abstract_id_log_name+str(abstract_id_writer_temp_index+1)+'.txt'), 'a')
	abstract_id_log.write(abstract_input_tag_id)
	abstract_id_log.write('\n')
	abstract_id_log.close()

def abstract_date_scraper(title, abstract_soup, status_logger_name):
	'''This function scrapes the date associated with each of the abstracts.
	This function will play a crucial role in the functionality that we are trying to build into our project.'''
	date_scraper_entry_status_key = "Scraping date of the abstract titled:"+" "+title
	status_logger(status_logger_name, date_scraper_entry_status_key)
	try:
		abstract_date = abstract_soup.find('time').get('datetime')
		date_scraper_exit_status_key = title+" "+"was published on"+" "+abstract_date
	except AttributeError:
		abstract_date = "Date for abstract titled:"+" "+title+" "+"was not available"
		date_scraper_exit_status_key = abstract_date
		pass
	
	status_logger(status_logger_name, date_scraper_exit_status_key)
	return abstract_date

def abstract_scraper(abstract_soup):
	'''This function scrapes the abstract from the soup and returns to the page scraper'''
	try:
		abstract = str(abstract_soup.find('p', {'id':'Par1'}).text.encode('utf-8'))[1:]
	except AttributeError:
		abstract = str(abstract_soup.find('p', {'class':'Para'}).text.encode('utf-8'))[1:]
	return abstract

def author_scraper(abstract_soup, status_logger_name):
	'''This function scrapes the author of the text, for easy navigation and search'''
	author_scraper_start_status_key = "Scraping the author name"
	status_logger(status_logger_name, author_scraper_start_status_key)
	author = str(abstract_soup.find('span', {'class':'authors__name'}).text.encode('utf-8'))[1:]
	author_scraper_end_status_key = "Scraped the author name"
	status_logger(status_logger_name, author_scraper_end_status_key)
	return author

def title_scraper(abstract_soup, status_logger_name):
	'''This function scrapes the title of the text'''
	title_scraper_start_status_key = "Scraping the title of the abstract"
	status_logger(status_logger_name, title_scraper_start_status_key)
	try:
		title = str(abstract_soup.find('h1',{'class':'ArticleTitle'}).text.encode('utf-8'))[1:]
	except AttributeError:
		title = str(abstract_soup.find('h1',{'class':'ChapterTitle'}).text.encode('utf-8'))[1:]
	title_scraper_end_status_key = "Scraped the title of the abstract"
	status_logger(status_logger_name, title_scraper_end_status_key)
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

def word_sorter_list_generator(status_logger_name):
	word_sorter_list_generator_start_status_key = "Generating the permanent archival list"
	status_logger(status_logger_name, word_sorter_list_generator_start_status_key)
	'''This function generates the list that hold the Words and corresponding Years of the
	abstract data words before the actual recursion of scrapping data from the website begins.'''
	word_sorter_list = []

	word_sorter_list_generator_exit_status_key = "Generated the permanent archival list"
	status_logger(status_logger_name, word_sorter_list_generator_exit_status_key)
	return word_sorter_list

def delay_function(status_logger_name):
	'''Since the Springer servers are contstantly shutting down the remote connection, we introduce
	this function in the processor function in order to reduce the number of pings it delivers to the remote.'''
	delay_function_start_status_key = "Delaying remote server ping: 5 seconds"
	status_logger(status_logger_name, delay_function_start_status_key)

	time.sleep(8)

	delay_function_end_status_key = "Delayed remote server ping: 5 seconds"
	status_logger(status_logger_name, delay_function_end_status_key)

def processor(abstract_url, urls_to_scrape, abstract_id_log_name, abstracts_log_name, status_logger_name, trend_keywords, keywords_to_search):
	''''Multiple page-cycling function to scrape multiple result pages returned from Springer.
	print(len(urls_to_scrape))'''
	
	'''This list will hold all the words mentioned in all the abstracts. It will be later passed on to the
	visualizer code to generate the trends histogram.'''
	permanent_word_sorter_list = word_sorter_list_generator(status_logger_name)

	for site_url_index in range(0, len(urls_to_scrape)):

		if(site_url_index==0):
			results_determiner(urls_to_scrape[site_url_index], status_logger_name)
		'''Collects the web-page from the url for souping'''
		page_to_soup = url_reader(urls_to_scrape[site_url_index], status_logger_name)
		'''Souping the page for collection of data and tags'''
		page_soup = page_souper(page_to_soup, status_logger_name)
		'''Scrapping the page to extract all the abstract IDs'''
		abstract_id_scraper(abstract_id_log_name, page_soup, site_url_index, status_logger_name)
		'''Actually obtaining the abstracts after combining ID with the abstract_url'''
		abstract_crawler(abstract_url, abstract_id_log_name, abstracts_log_name, permanent_word_sorter_list, trend_keywords, site_url_index, status_logger_name)

	'''This line of code processes and generates a dictionary from the abstract data'''
	
	abstract_year_dictionary, starting_year, ending_year = abstract_year_list_post_processor(permanent_word_sorter_list, status_logger_name)

	return abstract_year_dictionary, starting_year, ending_year

def scraper_main(abstract_id_log_name, abstracts_log_name, start_url, abstract_url, query_string, trend_keywords, keywords_to_search, status_logger_name):
	''''This function contains all the functions and contains this entire script here, so that it can be imported later to the main function'''
	
	'''Provides the links for the URLs to be scraped by the scraper'''
	urls_to_scrape = url_generator(start_url, query_string, status_logger_name)
	'''Calling the processor() function here'''
	abstract_year_dictionary, starting_year, ending_year = processor(abstract_url, urls_to_scrape, abstract_id_log_name, abstracts_log_name, status_logger_name, trend_keywords, keywords_to_search)
	'''This function dumps the entire dictionary onto the disc for further analysis and inference.'''
	abstract_year_dictionary_dumper(abstract_year_dictionary, abstracts_log_name, status_logger_name)
	'''Returning the abstract word dictionary here'''
	return abstract_year_dictionary, starting_year, ending_year