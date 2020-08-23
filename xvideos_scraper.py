import requests
from bs4 import BeautifulSoup as bs
import concurrent.futures
import csv

class xvideos_scraper:
	def __init__(self):
		self.MAX_WORKERS = 6
		print('Xvideos Scraper is running...')


	def load_page(self, url):
		url = url
		page = requests.get(url)
		if (page.status_code == 200):
			self.soup = bs(page.text, features='lxml')
		else:
			print(page.status_code)

	def get_title(self):
		res = self.soup.findAll('h2', {'class' : "page-title"})
		for r in res:
			return str(r.contents[0])

	def get_video_quality(self):
		res = self.soup.findAll('span', {'class' : 'video-hd-mark'})
		if(len(res) == 0):
			return '0p'
		else:
			for r in res:
				return str(r.string)

	def get_view_count(self):
		res = self.soup.findAll('strong')
		for r in res:
			return str(r.string.replace(',',''))

	def get_total_time(self):
		result = self.soup.findAll('span', {'class' : 'duration'})	
		for r in result:
			return str(r.string)
	
	def save_to_csv(self, terms, name = 'xvid'):
		fname = f'{name}.csv'
		search_terms = terms.replace(' ', '+')
		self.url = f'https://www.xvideos.com/?k={search_terms}'
		csv_data = self.get_all_data()

		with open(fname, 'w', newline='', encoding= 'utf-8') as f:
			writer = csv.writer(f)
			headersf = ['title', 'total_time', 'vid_quality', 'view_ct', 'uploader_name', 'upvotes', 'downvotes', 'video_tags', 'comment_ct', 'url']
			writer.writerow(headersf)
			for c in csv_data:
				writer.writerow(c)
		print('Scraping completed.')
	
	def create_data_list(self, url):
		self.load_page(f'https://www.xvideos.com{url}')
		data = []
		data.append(self.get_title()) # kind of annoying, but you have to html.unescape these later
		data.append(self.get_total_time())
		data.append(self.get_video_quality())
		data.append(self.get_view_count())
		data.append(self.get_uploader_name())
		data.append(self.get_upvotes())
		data.append(self.get_downvotes())
		data.append(self.get_video_tags())
		data.append(self.get_comment_ct())
		data.append(f'https://www.xvideos.com{url}')
		return data

	def get_uploader_name(self):
		result = self.soup.findAll('span', {'class' : 'name'})	
		for r in result:
			return ( str(r.string) )

	def get_upvotes(self):
		result = self.soup.findAll('a', {'class' : 'vote-action-good'})	
		for r in result:
			result2 = r.findAll('span', {'class' : 'rating-inbtn'})
			for r2 in result2:
				return(str(r2.string))

	def get_downvotes(self):
		result = self.soup.findAll('a', {'class' : 'vote-action-bad'})	
		for r in result:
			result2 = r.findAll('span', {'class' : 'rating-inbtn'})
			for r2 in result2:
				return(str(r2.string))

	def get_comment_ct(self):
		result = self.soup.findAll('span', {'class' : 'thread-node-children-count'})	
		for r in result:
			return(int(r.string))

	def get_video_tags(self):
		all_tags = ''
		result = self.soup.findAll('div', {'class' : 'video-tags-list'})	
		for r in result:
			result2 = r.findAll('li')
			for r2 in result2:
				pot_tag = str(r2.contents[0].get('href'))
				if(pot_tag[:2] == '/t'):
					all_tags += f'{str(r2.string)}|'
		return all_tags[:-1] 
		


	

	def get_all_data(self):
		l_urls = self.get_all_urls()

		csv_data = []
		with concurrent.futures.ThreadPoolExecutor(max_workers = self.MAX_WORKERS) as ex:
			results = [ex.submit(self.create_data_list, l) for l in l_urls]

			for k in concurrent.futures.as_completed(results):
				csv_data.append(k.result())
		return csv_data




	def get_all_urls(self):
		l_urls = []
		'''Given the first page of a url, return a list containing all hrefs'''
		page_no = 1 
		prev_page = 0
		bFoundMax = False
		prev_page = 0  
		
		while(bFoundMax == False):
			self.load_page(f'{self.url}+&p={prev_page}')


			# checks if we found the last page
			res = self.soup.findAll('a', {'class':'active'})
			for r in res:
				if len(r['class']) != 1: # there are some classes that use active that aren't page links, so we need this to skip those
					continue
				# the idea is that curr_page should never be prev_page unless repeats are occurring.
				curr_page = int(r.string)
				if(prev_page == curr_page):
					bFoundMax = True
				else:
					l_urls.extend(self.get_page_urls())
					page_no += 1
					prev_page += 1
				break
		return l_urls


	def get_page_urls(self):
		l_urls = []
		res = self.soup.findAll('div', {'class' : 'thumb'})
		for r in res:
			pot_hrefs = str(r.contents[0]['href'])
			if(pot_hrefs[:2] == '/v'):
				l_urls.append(pot_hrefs)
		return l_urls

