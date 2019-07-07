from django.test import TestCase
from django.test import Client

import plotr.models

import dataimport
import json
import plotrviz
import re

class ImportCSVTestCase(TestCase):

	def test_model_inserted(self):		
		WINE_FIELDCOUNT = 7
		WINE_VALUECOUNT = 25
		WINE_CSVPATH = 'plotr/testdata/wine.csv'
		WINE_TABPATH = 'plotr/testdata/wine.txt'

		for p in (WINE_CSVPATH, WINE_TABPATH):
			print
			if p == WINE_CSVPATH:
				print "[*] Begin Testing insertion of data from csv"
				new_data_wine = dataimport.fix_data(dataimport.readcsv(p))
			else:
				print "[*] Begin Testing insertion of data from tab-delimited text"
				new_data_wine = dataimport.fix_data(dataimport.readcsv(p, delim='\t'))
			warnings = new_data_wine['warnings']	
			modelInsert = dataimport.create_model(new_data_wine, "Wine")
			print "[+] INFO: data_id: %s " % modelInsert.data_id			
			self.assertEqual(len(modelInsert.fields.all()), WINE_FIELDCOUNT)
			print "[+] OK  : field count correct"
			for f in  modelInsert.fields.all():
				self.assertEqual(len(f.values.all()), WINE_VALUECOUNT)
			print "[+] OK  : value count correct"
			self.assertEqual(len(warnings), 0)
			print "[+] OK  : No warnings on clean file"
			print "[*] End of Test"

	def test_low_quality_data(self):
		POOR_QUALITY_CSV = 'plotr/testdata/poordata.csv'
		new_data_low_quality = dataimport.fix_data( dataimport.readcsv(POOR_QUALITY_CSV) )
		warnings =  new_data_low_quality['warnings']
		modelLowQual = dataimport.create_model(new_data_low_quality, "Something About Fruits")
		print 
		print "[*] Begin Testing insertion of data from poorly formatted csv"
		print "[+] INFO: data_id: %s " % modelLowQual.data_id
		correct_headers = ["Potato", "Field2", "Bananas", "Orange", "AppleSauce", "Potato1", "Field7"]
		actual_headers = []
		for f in  modelLowQual.fields.all():
			actual_headers.append(f.fieldName)
		#print correct_headers, actual_headers
		self.assertEqual(len(actual_headers), len(correct_headers))
		print "[+] OK  : field count correct"		
		difference = set(correct_headers) - set(actual_headers)
		self.assertEqual(len(difference), 0)
		print "[+] OK  : Actual Headers == Correct Headers"		
		self.assertEqual(len(warnings), 6)
		correct_warnings = ["Renamed field 2: '' to 'Field2'", "Renamed field 3: 'Banana's' to 'Bananas'", 
							"Renamed field 4: 'Orange!' to 'Orange'", "Renamed field 5: 'Apple Sauce' to 'AppleSauce'",
							"Renamed field 6: 'Potato' to 'Potato1'","Renamed field 7: '' to 'Field7'"]
		self.assertEqual(sorted(warnings), correct_warnings)		
		print "[*] End of Testing insertion of data from csv"

	def test_wrong_file_types(self):
		POOR_QUALITY_CSV = 'plotr/testdata/png.csv'
		print
		print "[*] Begin Testing insertion of data from wrong file type"
		new_data_low_quality = dataimport.fix_data( dataimport.readcsv(POOR_QUALITY_CSV) )
		warnings =  new_data_low_quality['warnings']
		self.assertEqual(warnings, ['Invalid File Detected'])
		print "[+] OK  : PNG content rejected"	
		POOR_QUALITY_CSV = 'plotr/testdata/markdown.csv'
		new_data_low_quality = dataimport.fix_data( dataimport.readcsv(POOR_QUALITY_CSV) )		
		self.assertEqual(new_data_low_quality['warnings'], ['Invalid File Detected'])
		print "[+] OK  : Markdown content rejected"			
		print "[*] End of Testing insertion of data from wrong file type"




class ExportTypeTestCase(TestCase):	
	data = None
	modelInsert = None
	dataBlank = None
	modelBlank = None
	
	def setUp(self):
		WINE_CSVPATH = 'plotr/testdata/wine.csv'
		self.data = dataimport.fix_data(dataimport.readcsv(WINE_CSVPATH))
		self.modelInsert = dataimport.create_model(self.data, "Alabaster Plaster")
		WINE_CSVPATH = 'plotr/testdata/wine_with_blanks.csv'
		self.dataBlank = dataimport.fix_data(dataimport.readcsv(WINE_CSVPATH))
		self.modelBlank = dataimport.create_model(self.dataBlank, "Alabaster Plaster")
		
	def test_json(self):				
		CORRECT_JSON = """{"headers": ["Year", "Price", "WinterRain", "AGST", "HarvestRain", "Age", "FrancePop"], "data": [{"Age": 31, "AGST": 17.1167, "WinterRain": 600, "FrancePop": 43183.569, "HarvestRain": 160, "Year": 1952, "Price": 7.495}, {"Age": 30, "AGST": 16.7333, "WinterRain": 690, "FrancePop": 43495.03, "HarvestRain": 80, "Year": 1953, "Price": 8.0393}, {"Age": 28, "AGST": 17.15, "WinterRain": 502, "FrancePop": 44217.857, "HarvestRain": 130, "Year": 1955, "Price": 7.6858}, {"Age": 26, "AGST": 16.1333, "WinterRain": 420, "FrancePop": 45152.252, "HarvestRain": 110, "Year": 1957, "Price": 6.9845}, {"Age": 25, "AGST": 16.4167, "WinterRain": 582, "FrancePop": 45653.805, "HarvestRain": 187, "Year": 1958, "Price": 6.7772}, {"Age": 24, "AGST": 17.4833, "WinterRain": 485, "FrancePop": 46128.638, "HarvestRain": 187, "Year": 1959, "Price": 8.0757}, {"Age": 23, "AGST": 16.4167, "WinterRain": 763, "FrancePop": 46583.995, "HarvestRain": 290, "Year": 1960, "Price": 6.5188}, {"Age": 22, "AGST": 17.3333, "WinterRain": 830, "FrancePop": 47128.005, "HarvestRain": 38, "Year": 1961, "Price": 8.4937}, {"Age": 21, "AGST": 16.3, "WinterRain": 697, "FrancePop": 48088.673, "HarvestRain": 52, "Year": 1962, "Price": 7.388}, {"Age": 20, "AGST": 15.7167, "WinterRain": 608, "FrancePop": 48798.99, "HarvestRain": 155, "Year": 1963, "Price": 6.7127}, {"Age": 19, "AGST": 17.2667, "WinterRain": 402, "FrancePop": 49356.943, "HarvestRain": 96, "Year": 1964, "Price": 7.3094}, {"Age": 18, "AGST": 15.3667, "WinterRain": 602, "FrancePop": 49801.821, "HarvestRain": 267, "Year": 1965, "Price": 6.2518}, {"Age": 17, "AGST": 16.5333, "WinterRain": 819, "FrancePop": 50254.966, "HarvestRain": 86, "Year": 1966, "Price": 7.7443}, {"Age": 16, "AGST": 16.2333, "WinterRain": 714, "FrancePop": 50650.406, "HarvestRain": 118, "Year": 1967, "Price": 6.8398}, {"Age": 15, "AGST": 16.2, "WinterRain": 610, "FrancePop": 51034.413, "HarvestRain": 292, "Year": 1968, "Price": 6.2435}, {"Age": 14, "AGST": 16.55, "WinterRain": 575, "FrancePop": 51470.276, "HarvestRain": 244, "Year": 1969, "Price": 6.3459}, {"Age": 13, "AGST": 16.6667, "WinterRain": 622, "FrancePop": 51918.389, "HarvestRain": 89, "Year": 1970, "Price": 7.5883}, {"Age": 12, "AGST": 16.7667, "WinterRain": 551, "FrancePop": 52431.647, "HarvestRain": 112, "Year": 1971, "Price": 7.1934}, {"Age": 11, "AGST": 14.9833, "WinterRain": 536, "FrancePop": 52894.183, "HarvestRain": 158, "Year": 1972, "Price": 6.2049}, {"Age": 10, "AGST": 17.0667, "WinterRain": 376, "FrancePop": 53332.805, "HarvestRain": 123, "Year": 1973, "Price": 6.6367}, {"Age": 9, "AGST": 16.3, "WinterRain": 574, "FrancePop": 53689.61, "HarvestRain": 184, "Year": 1974, "Price": 6.2941}, {"Age": 8, "AGST": 16.95, "WinterRain": 572, "FrancePop": 53955.042, "HarvestRain": 171, "Year": 1975, "Price": 7.292}, {"Age": 7, "AGST": 17.65, "WinterRain": 418, "FrancePop": 54159.049, "HarvestRain": 247, "Year": 1976, "Price": 7.1211}, {"Age": 6, "AGST": 15.5833, "WinterRain": 821, "FrancePop": 54378.362, "HarvestRain": 87, "Year": 1977, "Price": 6.2587}, {"Age": 5, "AGST": 15.8167, "WinterRain": 763, "FrancePop": 54602.193, "HarvestRain": 51, "Year": 1978, "Price": 7.186}]}"""
		print
		print "[*] Begin Testing json output"
		print "[+] INFO: data_id: %s " % self.modelInsert.data_id	
		j = json.loads(self.modelInsert.to_json())
		k = json.loads(CORRECT_JSON)
		self.assertEqual(j['headers'], k['headers'])
		self.assertEqual(j['data'], k['data'])
		print "[+] OK  : Actual JSON == Correct JSON"			
		CORRECT_JSON_RAW = """{"fields": [{"values": ["1952", "1953", "1955", "1957", "1958", "1959", "1960", "1961", "1962", "1963", "1964", "1965", "1966", "1967", "1968", "1969", "1970", "1971", "1972", "1973", "1974", "1975", "1976", "1977", "1978"], "name": "Year"}, {"values": ["7.495", "8.0393", "7.6858", "6.9845", "6.7772", "8.0757", "6.5188", "8.4937", "7.388", "6.7127", "7.3094", "6.2518", "7.7443", "6.8398", "6.2435", "6.3459", "7.5883", "7.1934", "6.2049", "6.6367", "6.2941", "7.292", "7.1211", "6.2587", "7.186"], "name": "Price"}, {"values": ["600", "690", "502", "420", "582", "485", "763", "830", "697", "608", "402", "602", "819", "714", "610", "575", "622", "551", "536", "376", "574", "572", "418", "821", "763"], "name": "WinterRain"}, {"values": ["17.1167", "16.7333", "17.15", "16.1333", "16.4167", "17.4833", "16.4167", "17.3333", "16.3", "15.7167", "17.2667", "15.3667", "16.5333", "16.2333", "16.2", "16.55", "16.6667", "16.7667", "14.9833", "17.0667", "16.3", "16.95", "17.65", "15.5833", "15.8167"], "name": "AGST"}, {"values": ["160", "80", "130", "110", "187", "187", "290", "38", "52", "155", "96", "267", "86", "118", "292", "244", "89", "112", "158", "123", "184", "171", "247", "87", "51"], "name": "HarvestRain"}, {"values": ["31", "30", "28", "26", "25", "24", "23", "22", "21", "20", "19", "18", "17", "16", "15", "14", "13", "12", "11", "10", "9", "8", "7", "6", "5"], "name": "Age"}, {"values": ["43183.569", "43495.03", "44217.857", "45152.252", "45653.805", "46128.638", "46583.995", "47128.005", "48088.673", "48798.99", "49356.943", "49801.821", "50254.966", "50650.406", "51034.413", "51470.276", "51918.389", "52431.647", "52894.183", "53332.805", "53689.61", "53955.042", "54159.049", "54378.362", "54602.193"], "name": "FrancePop"}], "title": "Alabaster Plaster", "data_id": "S2zl6"}"""
		j = self.modelInsert.to_json_raw()
		j = re.sub(r"\"data_id\": \"[A-Za-z0-9]{5}\"", "\"data_id\": \"S2zl6\"", j)
		self.assertEqual(j, CORRECT_JSON_RAW)
		print "[+] OK  : Actual Raw JSON == Correct Raw JSON"
		print "[*] End of Testing json output"

	def test_as_list(self):		
		print
		print "[*] Begin Testing list output"
		f = self.modelInsert.fields.get(fieldName='Year')
		generatedList = f.as_list()
		correctList = [1952, 1953, 1955, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978]
		self.assertEqual(correctList, generatedList)
		print "[+] OK  : Converted numeric without blanks"		
		f = self.modelBlank.fields.get(fieldName='WinterRain')
		generatedList = f.as_list()
		correctList = [600,690,502,420,582,485,763,830,697,608,402,602,819,None,610,575,622,551,536,None,574,572,418,821,763]
		self.assertEqual(correctList, generatedList)
		print "[+] OK  : Converted numeric with blanks"
		f = self.modelBlank.fields.get(fieldName='HarvestRain')
		generatedList = f.as_list()
		correctList = [160,80,130,110,None,187,290,38,52,None,96,267,86,118,None,244,89,112,158,123,184,171,247,87,51]
		self.assertEqual(correctList, generatedList)
		print "[+] OK  : Converted numeric with non-numeric words and blanks"
		f = self.modelBlank.fields.get(fieldName='GrapeType')
		generatedList = f.as_list()
		correctList = ["Champagne","Champagne","Champagne","Merlot","Merlot","Merlot","Red","Red","Red","Red","Red","Red","Merlot","Merlot","White","White","White","White","White","Champagne","Potato","Potato","Potato","Potato","100"]
		self.assertEqual(correctList, generatedList)
		print "[+] OK  : Converted text field with some numeric values"
		print "[*] End of Testing list output"

	def test_stats(self):
		print
		print "[*] Begin Testing stats output"
		f = self.modelBlank.fields.get(fieldName='Year')
		correctStats = {
			'max'	: 	1978,
			'min'	:	1952,
			'mean'	:	1965.8,
			'NAs'	:	0,
			'median':	1966,
		}
		self.assertEqual(correctStats, f.get_stats())
		print "[+] OK  : Calculated numerical stats with no blanks/missing/etc"
		f = self.modelBlank.fields.get(fieldName='HarvestRain')
		correctStats = {
			'max'	: 	290,
			'min'	:	38,
			'mean'	:	140,
			'NAs'	:	3,
			'median':	120.5,
		}
		self.assertEqual(correctStats, f.get_stats())
		print "[+] OK  : Calculated numerical stats, with blanks and text values"
		f = self.modelBlank.fields.get(fieldName='GrapeType')
		correctStats = {
			'levels'	: ['Potato',
							'Merlot',
							'White',
							'Champagne',
							'100',
							'Red', ],
			'distinct'	: 6,
		}
		generatedStats = f.get_stats()
		self.assertEqual(correctStats, generatedStats)
		print "[+] OK  : Calculated text stats, with blanks and text values"
		print "[*] End of Testing stats output"

class VisualizationTestCase(TestCase):
	data = None
	modelT = None

	def setUp(self):		
		WINE_CSVPATH = 'plotr/testdata/wine.csv'
		self.data = dataimport.fix_data(dataimport.readcsv(WINE_CSVPATH))
		self.modelT = dataimport.create_model(self.data, "Alabaster Plaster")	
		pass

	def test_histogram(self):		
		print
		print "[*] Begin testing Visualizations: histogram"
		print "[+] INFO: data_id: %s" % self.modelT.data_id
		v = plotrviz.create_viz(self.modelT.data_id, "histogram", "Price")		
		print "[+] INFO: Created visualization object."
		plotrviz.render_viz(v, '/tmp/')
		print "[+] OK: histogram has been rendered."		
		self.assertEqual(str(v), "%s-histogram-Price.png" % self.modelT.data_id)		
		print "[+] OK: str() returns correct file name."
		print "[*] End of Testing Visualizations: histogram"

	def test_scatterplot(self):
		print
		print "[*] Begin testing Visualizations: scatterplot"
		print "[+] INFO: data_id: %s" % self.modelT.data_id
		v = plotrviz.create_viz(self.modelT.data_id, "scatterplot", "Price+AGST")		
		print "[+] INFO: Created visualization object."
		plotrviz.render_viz(v, '/tmp/')
		print "[+] OK: scatterplot has been rendered."		
		self.assertEqual(str(v), "%s-scatterplot-Price+AGST.png" % self.modelT.data_id)		
		print "[+] OK: str() returns correct file name."
		print "[*] End of Testing Visualizations: scatterplot"

class WebViewTestCase(TestCase):
	data = None
	modelT = None

	def setUp(self):		
		WINE_CSVPATH = 'plotr/testdata/wine.csv'
		self.data = dataimport.fix_data(dataimport.readcsv(WINE_CSVPATH))
		self.modelT = dataimport.create_model(self.data, "Alabaster Plaster")	
		pass

	def test_histogram(self):
		print
		print "[*] Begin testing Web Views: histogram"
		print "[+] INFO: data_id: %s" % self.modelT.data_id
		c = Client()
		response = c.get('/%s/v/histogram/' % self.modelT.data_id)
		for field in self.modelT.fields.all():
			self.assertContains(response, field.fieldName)
		self.assertContains(response, "Select variable")
		self.assertNotContains(response, "Select variable 1")
		self.assertNotContains(response, "Select variable 2")
		print "[+] OK: Offers user correct variables, correct number of times."
		response = c.get('/%s/v/histogram/banana/' % self.modelT.data_id)		
		self.assertContains(response, "Unknown in variable specifier banana for")
		print "[+] OK: Does not try to render for incorrect variable specifier."		
		print "[*] End of testing Web Views: histogram"

	def test_scatterplot(self):
		print
		print "[*] Begin testing Web Views: scatterplot"
		print "[+] INFO: data_id: %s" % self.modelT.data_id
		c = Client()
		response = c.get('/%s/v/scatterplot/' % self.modelT.data_id)
		for field in self.modelT.fields.all():
			self.assertContains(response, field.fieldName)
		self.assertContains(response, "Select variable 1")
		self.assertContains(response, "Select variable 2")
		self.assertNotContains(response, "Select variable 3")
		print "[+] OK: Offers user correct variables, correct number of times."
		response = c.get('/%s/v/scatterplot/banana/' % self.modelT.data_id)		
		self.assertContains(response, "Unknown in variable specifier banana for")
		print "[*] End of testing Web Views: scatterplot"

	def test_tabular(self):
		print
		print "[*] Begin testing Web Views: tabular"
		print "[+] INFO: data_id: %s" % self.modelT.data_id
		c = Client()
		response = c.get('/%s/v/tabular/' % self.modelT.data_id)
		self.assertContains(response, "Unknown visualization")
		print "[+] OK: Error for wrong URL."
		response = c.get('/%s/tabular/' % self.modelT.data_id)		
		self.assertNotContains(response, "Unknown visualization")		
		print "[+] OK: No error for correct URL."
		print "[*] End of testing Web Views: tabular"