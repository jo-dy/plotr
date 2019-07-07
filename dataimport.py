"""
dataimport

This module contains methods for importing data from a variety of sources (csv for now, xlsx TODO)
and preparing that data.

"""
import copy
import csv
import models
import re
from uniqueid import generate_unique_id


def readcsv(filename, delim = ',', quote_character="\"", csv_dialect= None):
	"""
		readcsv(filename, ...)
		parameters:
		 * filename			path to csv file (required)
		 * delim 			delimiter, defaults to comma
		 * quote_character	field boundary quote character, defaults to double-quote
		 * csv_dialect		defaults to excel		
		returns a dictionary containing 4 elements:		
		{ 	'n'		 	: <integer>,			#  n - the number of fields
			'headers'	: <list of strings>,	#  headers - a list of the names of the headers
			'content'	: <list of lists>,		#  content - a list of lists of data values associated with each header, in the same order.
			'warnings'	: <list of strings>,	#  warnings - a list of warnings about the raw data i.e. column count mismatch, renamings, etc
		}
	"""
	try:
		csvfile = open(filename, 'rbU')
		if csv_dialect:
			csvRead = csv.reader(csvfile, dialect=csv_dialect, delimiter = delim, quotechar=quote_character)
		else:
			dialect = csv.Sniffer().sniff(csvfile.read(1024))
			csvfile.seek(0)
			csvRead = csv.reader(csvfile, dialect)
			#csv.reader(csvfile, delimiter = delim, quotechar=quote_character)
		headers = csvRead.next()
		content = []
		for row in csvRead:
			content.append(row)
		content = list(map(list, zip(*content)))  #zip is amazing, python is amazing	
		raw = { 	'n'		 : len(headers),
					'headers'	: headers,
					'content'	: content,
					'warnings'	: [],
				}
		return raw
	except csv.Error:
		return { 	'n'		 	: 0,
					'headers'	: [],
					'content'	: [],
					'warnings'	: ["Invalid File Detected"],
				}

def fix_data(imported):
	"""
		fix_data(imported)
		takes a dictionary of raw imported data in the following format:
		{ 	'n'		 	: <integer>,
			'headers'	: <list of strings>,
			'content'	: <list of lists>,
			'warnings'	: <list of strings>,
		}
		and returns a similarly structured dictionary, but with possibly altered contents
		
		Does a series of checks on the data:

		  * Modifies header names
		      * rename duplicates
		      * remove special characters ([^A-Za-z0-9_])
		      * rename blanks
		  * Column count check
		  * Row count check
		  * Adds warnings as appropriate to describe what it's done.
	"""

	if imported['n'] == 0:
		return imported	#Nothing to do
	fixed = copy.deepcopy(imported)	#make a copy
	
	#Fix special characters in field name and blanks
	new_headers = []
	for header in fixed['headers']:
		stripped = re.sub('[^A-Za-z0-9_]+', '', header)
		if stripped == '':
			stripped = "Field%d" % (len(new_headers) + 1)
		new_headers.append(stripped)
		if stripped != header:
			fixed['warnings'].append("Renamed field %d: '%s' to '%s'" % (len(new_headers), header, stripped) )
	fixed['headers'] = new_headers
	
	#Rename any duplicates
	alreadyEncountered = []
	for header in fixed['headers']:
		nHeader = header
		n = 1
		while nHeader in alreadyEncountered:
			nHeader = "%s%d" % ( header, n)
		alreadyEncountered.append(nHeader)
		if nHeader != header:
			fixed['warnings'].append("Renamed field %d: '%s' to '%s'" % (len(alreadyEncountered), header, nHeader))		
	fixed['headers'] = alreadyEncountered

	#Check content count, should be same as headers. 
	#  If not, add Fieldj, Fieldj+1, etc to end of headers
	while len(fixed['content']) > len(fixed['headers']):
		n = len(fixed['headers'] + 1)
		fixed['headers'].append("Field%d" % n)

	#Check # values in each field, append empty values where applicable
	col_lens = [len(x) for x in fixed['content']]
	most_column = max(col_lens)
	fewest_column = min(col_lens)
	if fewest_column < most_column:
		for col in fixed['content']:
			nAdded = 0
			while len(col) < most_column:
				col.append('')
				nAdded += 1
			if nAdded >0:
				fixed['warnings'].append("Added blank records to short column")
	return fixed	

def create_model(csvdata, dtitle):
	fieldNames = csvdata['headers']
	fieldValues = csvdata['content']
	nFields = csvdata['n']		
	if nFields == 0:
		return None
	d = models.Dataset()
	d.title = dtitle
	d.data_id = generate_unique_id()
	d.save()
	for n in range(nFields):
		f = models.DataFields()
		f.fieldName = fieldNames[n]
		f.save()
		for m in range(len(fieldValues[n])):
			v = models.DataValues()
			v.order = m
			v.value = fieldValues[n][m]
			v.save()
			f.values.add(v)		
		f.fieldType = f.infer_type()
		f.save()
		d.fields.add(f)
	d.save()
	return d


