import os
import requests
import sys
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileWriter, PdfFileReader

# Function to append pages from one PDF into another
def append_pdf(input_pdf, output_pdf):
	for page_num in range(input_pdf.getNumPages()):
		output_pdf.addPage(input_pdf.getPage(page_num))

# Base URL for Wiley's online library
baseurl = "http://onlinelibrary.wiley.com"

# Get the URL from command line argument
url = sys.argv[1]

# Check if the provided URL is valid
if url.startswith("http"):
	# Initialize PDF writer for the output
	output = PdfFileWriter()

	# Send a GET request to the provided URL
	response = requests.get(url)

	# Parse the returned HTML using BeautifulSoup
	parsed = BeautifulSoup(response.content, "lxml")

	# Find all citation elements and the product title in the parsed HTML
	toc = parsed.find_all(class_="citation")
	title = parsed.find(id="productTitle")
	title_text = ''.join(title.findAll(text=True))

	print(f"You are downloading {title_text}")

	# For each citation element, find the standard PDF link
	for counter, item in enumerate(toc):
		pdf = item.find(class_="standardPdfLink")
		pdflink = pdf.get('href')

		# If the link is relative, append the base URL
		if not pdflink.startswith("http"):
			pdflink = baseurl + pdflink

		# Retry up to 10 times to download and process the PDF
		for attempt in range(10):
			try:
				# Get the page with the actual PDF link
				response = requests.get(pdflink)

				# Parse the returned HTML and find the PDF document element
				response_parsed = BeautifulSoup(response.content, "lxml")
				pdftl = response_parsed.find(id="pdfDocument")
				pdftlink = pdftl.get('src')

				# Download the PDF
				pdffile = requests.get(pdftlink)

				# Save the downloaded PDF to a temporary file
				with open(f"{title_text}{counter}.pdf", 'wb') as file_seg:
					file_seg.write(pdffile.content)

				# Append the temporary PDF to the output PDF
				append_pdf(PdfFileReader(open(f"{title_text}{counter}.pdf", "rb")), output)

				# Delete the temporary PDF
				os.remove(f"{title_text}{counter}.pdf")

				print(f"Finished Processing : {pdftlink}")

				# Successfully downloaded and processed PDF, so break from retry loop
				break
			except Exception as e:
				print(f"Failed to get resource on attempt {attempt + 1}/10 due to error: {e}")
				if attempt == 9:
					print("Couldn't Connect to get resources. Exiting")
					sys.exit(1)

	# Save the combined PDF to a file
	with open(f"{title_text}.pdf", "wb") as combined_pdf:
		output.write(combined_pdf)
else:
	print("This is not a valid URL")
