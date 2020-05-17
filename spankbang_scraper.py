import requests
from bs4 import BeautifulSoup as bs
import concurrent.futures
import csv

class spankbang_scrapper:
	def __init__(self):
		self.MAX_WORKERS = 6


	def load_page(self, url):
		url = url
		page = requests.get(url)
		if (page.status_code == 200):
			self.soup = bs(page.text, features='lxml')
		else:
			print(page.status_code)

	def get_title(self):
		res = self.soup.findAll('h1')
		for r in res:
			return( str(r.contents[0]).strip())

	def get_video_quality(self):
		res = self.soup.findAll('div', {'class' : 'play_cover'})
		for r in res:
			res2 = r.findAll('span', {'class' : 'i-hd'})
			for r2 in res2:
				return(str(r2.string).strip())

	def get_view_count(self):
		res = self.soup.findAll('div', {'class' : 'play_cover'})
		for r in res:
			res2 = r.findAll('span', {'class' : 'i-plays'})
			for r2 in res2:
				return(str(r2.string).strip())

	def get_total_time(self):
		res = self.soup.findAll('div', {'class' : 'play_cover'})
		for r in res:
			res2 = r.findAll('span', {'class' : 'i-length'})
			for r2 in res2:
				return(str(r2.string).strip())
	
	def save_to_csv(self, terms, name = 'spankbang'):
		fname = f'{name}.csv'
		search_terms = terms.replace(' ', ',')
		self.url = f'https://spankbang.com/tag/{search_terms}/'
		csv_data = self.get_all_data()

		with open(fname, 'w', newline='', encoding= 'utf-8') as f:
			writer = csv.writer(f)
			headersf = ['title', 'total_time', 'vid_quality', 'view_ct', 'uploader_name', 'rating', 'video_tags', 'comment_ct', 'url']
			writer.writerow(headersf)
			for c in csv_data:
				writer.writerow(c)

	def create_data_list(self, url):
		self.load_page(f'https://www.spankbang.com{url}')
		data = []
		data.append(self.get_title()) # kind of annoying, but you have to html.unescape these later
		data.append(self.get_total_time())
		data.append(self.get_video_quality())
		data.append(self.get_view_count())
		data.append(self.get_uploader_name())
		data.append(self.get_rating())
		data.append(self.get_video_tags())
		data.append(self.get_comment_ct())
		data.append(f'https://www.spankbang.com{url}')
		return data

	def get_uploader_name(self):
		result = self.soup.findAll('li', {'class' : 'us'})	
		for r in result:
			result2 = r.findAll('a')
			for r2 in result2:
				uPos = str(r2['href']).find('t/')
				return(r2['href'][uPos+2:])
	
	def get_rating(self):
		result = self.soup.findAll('span', {'class' : 'rate'})	
		for r in result:
			return(str(r.string))


	def get_comment_ct(self):
		result = self.soup.findAll('section', {'class' : 'all_comments'})	
		for r in result:
			result2 = r.findAll('h2')
			for r2 in result2:
				startInd = r2.string.find('(')
				endInd = r2.string.find(')')
				return(str(r2.string)[startInd + 1:endInd])

			

	def get_video_tags(self):
		all_tags = ''
		result = self.soup.findAll('div', {'class' : 'ent'})
		for r in result:
			result2 = r.findAll('a')
			for r2 in result2:
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
		'''Given the first page of a url, return a list containing all hrefs'''
		l_urls = []	
		bFoundMax = False
		self.load_page(self.url)
		
		while(bFoundMax == False):
			new_url = 'replace'
			res = self.soup.findAll('div', {'class' : 'pagination'})
			for r in res:
				# get url of next page
				res2 = r.findAll('li', {'class' : 'next'})
				for r2 in res2:
					res3 = r2.findAll('a', href=True)
					for r3 in res3:
						new_url = r3['href']
						self.url = f'https://spankbang.com{new_url}'
				
				# get all urls on this page
				l_urls.extend(self.get_page_urls())
				if(new_url != 'replace'):
					self.load_page(self.url)
				#check if new page found
				res4 = r.select('li.disabled.next')
				if(len(res4) == 1):
					bFoundMax = True

		return l_urls


	def get_page_urls(self):
		'''Assuming a search page was loaded, this will get all video urls on that page'''
		l_urls = []
		res = self.soup.findAll('div', {'class' : 'results'})
	
		for r in res:
			res2 = r.findAll('a', {'class': 'thumb'})
			for r2 in res2:
				l_urls.append(str(r2['href']))
		return l_urls
		#print(l_urls)

	
svs = spankbang_scrapper()

url = 'https://spankbang.com/3mg2l/video/anri+okita+got+big+bouncy+tits'
#url = 'https://spankbang.com/tag/japanese,teen,schoolgirl/'
#url = 'https://spankbang.com/tag/japanese,teen,schoolgirl/2/?period=all'
#svs.load_page(url)
tags = 'japanese teen schoolgirl'
svs.save_to_csv(tags)

#terms = "anri okita"
#xvs.save_to_csv(terms)