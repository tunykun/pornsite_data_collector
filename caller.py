from xvideos_scraper import xvideos_scraper
from spankbang_scraper import spankbang_scraper

# example tag
# check the examples folder for the output of the scrapers
tags = "anri okita"

xvs = xvideos_scraper()
xvs.save_to_csv(tags)

svs = spankbang_scraper()
svs.save_to_csv(tags)