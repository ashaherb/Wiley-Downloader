import os
import urllib
import urllib2
import sys
from bs4 import BeautifulSoup as BS
from pyPdf import PdfFileWriter, PdfFileReader

def append_pdf(input,output):
	[output.addPage(input.getPage(page_num)) for page_num in range(input.numPages)]

baseurl = "http://onlinelibrary.wiley.com"

url = sys.argv[1]

if url.startswith("http"):
	output = PdfFileWriter()
	f = urllib.urlopen(url)
	myfile = f.read()
	parsed = BS(myfile,"lxml")
	toc = parsed.find_all(class_="citation")
	title = parsed.find(id="productTitle")
	title_text = ''.join(title.findAll(text=True))
	print("You are downloading " + title_text)
	for counter, item in enumerate(toc):
		pdf = item.find(class_="standardPdfLink")
		pdflink = pdf.get('href')

		if not pdflink.startswith("http"):
			pdflink = baseurl + pdflink

		try:
			response = urllib2.urlopen(pdflink)
			response_parsed = BS(response,"lxml")
			pdftl = response_parsed.find(id="pdfDocument")
			pdftlink = pdftl.get('src')
		except:
			print("Failed to get resource , Retrying (0/10)")
			flag = 0
			for i in range(10):
				response = urllib2.urlopen(pdflink)
				response_parsed = BS(response,"lxml")
				pdftl = response_parsed.find(id="pdfDocument")
				if pdftl is not None:
					flag = 1
					break
				print("Failed to get resource , Retrying ("+str(i)+"/10)")
			if flag == 0:
				print ("Couldn't Connect to get resources. Exiting")
				exit()
		pdftlink = pdftl.get('src')
		pdffile = urllib2.urlopen(pdftlink)

		file_seg = open(title_text + str(counter)+".pdf", 'wb')
		file_seg.write(pdffile.read())
		file_seg.close()

		append_pdf(PdfFileReader(file(title_text + str(counter)+".pdf","rb")),output)
		os.remove(title_text + str(counter)+".pdf")

		print ("Finished Processing : " + pdflink)

	output.write(file(title_text+ ".pdf","wb"))
else:
	print ("This is not a valid URL")

