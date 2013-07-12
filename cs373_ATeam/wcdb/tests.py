"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from minixsv import pyxsval
from genxmlif import GenXmlIfError
from models import Crisis, Person, Org, list_add, Li, Common
from loadModels import validate
import xml.etree.ElementTree as ET
from django.test.client import Client
from views import passwordValidate


#xsd = open('wcdb/WorldCrises.xsd.xml', 'r')
#psvi = pyxsval.parseAndValidate("wcdb/temp.xml", "wcdb/WorldCrises.xsd.xml",
#	xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)

class ModelsCrisisTest(TestCase):

#--------------------------------------------#
#-----Unit Tests for functions from models.py
#--------------------------------------------#

	#---------------------------------------#
	#-----test_list_add

	def test_list_add(self):
	    """
	    Tests the list_add functionality of adding information to a model object's lists
	    """
	    temp   = Crisis()
	    person = "random_person"
	    list_add(temp.people, person)
	    self.assertEqual(temp.people[0], "random_person")

	def test_list_add1(self):
	    """
	    Tests the list_add functionality of adding information to a model object's lists
	    """
	    temp          = Crisis()
	    organization0 = "random_org0"
	    organization1 = "random_org1"
	    list_add(temp.organizations, organization0)
	    list_add(temp.organizations, organization1)
	    self.assertEqual(temp.organizations[0], "random_org0")
	    self.assertEqual(temp.organizations[1], "random_org1")

	def test_list_add2(self):
		"""
		Tests the list_add functionality of adding information to a model object's lists
		"""
		temp          = Person()
		organization0 = "random_org0"
		organization1 = "random_org1"
		list_add(temp.organizations, organization0)
		list_add(temp.organizations, organization1)
		self.assertEqual(temp.organizations[0], "random_org0")
		self.assertEqual(temp.organizations[1], "random_org1")

	def test_list_add3(self):
	    """
	    Tests the list_add functionality of adding information to a model object's lists
	    """
	    temp   = Org()
	    person = "random_person"
	    list_add(temp.people, person)
	    self.assertEqual(temp.people[0], "random_person")


	#---------------------------------------#
	#-----test_li_populate

	def test_li_populate0(self):
		temp      = ET.Element('li')
		temp.set("href", "href_stuff")
		temp.text = "randomfloatingtext"
		temp_li   = Li()
		temp_li.populate(temp)
		self.assertEqual(temp_li.href, "href_stuff")

	def test_li_populate1(self):
		temp      = ET.Element('li')
		#print type(temp)
		temp.set("href", "href_stuff")
		temp.set("embed", "embed_stuff")
		temp.set("text", "text_stuff")
		temp.text = "randomfloatingtext"
		temp_li   = Li()
		temp_li.populate(temp)
		self.assertEqual(temp_li.href, "href_stuff")
		self.assertEqual(temp_li.embed, "embed_stuff")
		self.assertEqual(temp_li.text, "text_stuff")
		self.assertEqual(temp_li.floating_text, "randomfloatingtext")

	def test_li_populate2(self):
		temp      = ET.Element('li')
		temp.text = "randomfloatingtext"
		temp_li   = Li()
		self.assertEqual(temp_li.text, None)
		#self.assertEqual(temp_li.text, "randomfloatingtext")


	#---------------------------------------#
	#-----test_common_populate

	def test_common_populate0(self):
		temp_com = Common()
		xml_string = '<Common><Citations><li>The Hindustan Times</li></Citations><ExternalLinks><li href="http://en.wikipedia.org/wiki/2013_North_India_floods">Wikipedia</li></ExternalLinks><Images><li embed="http://timesofindia.indiatimes.com/photo/15357310.cms" /></Images><Videos><li embed="//www.youtube.com/embed/qV3s7Sa6B6w" /></Videos><Maps><li embed="https://www.google.com/maps?sll=30.08236989592049,79.31189246107706&amp;sspn=3.2522150867582833,7.2072687770004205&amp;t=m&amp;q=uttarakhand&amp;dg=opt&amp;ie=UTF8&amp;hq=&amp;hnear=Uttarakhand,+India&amp;ll=30.066753,79.0193&amp;spn=2.77128,5.07019&amp;z=8&amp;output=embed" /></Maps><Feeds><li embed="[WHATEVER A FEED URL LOOKS LIKE]" /></Feeds><Summary>Lorem ipsum...</Summary></Common>'
		root = ET.fromstring(xml_string)
		temp_com.populate(root)

		self.assertEqual(temp_com.citations[0].floating_text, "The Hindustan Times")
		self.assertEqual(temp_com.external_links[0].href, "http://en.wikipedia.org/wiki/2013_North_India_floods")
		self.assertEqual(temp_com.images[0].embed, "http://timesofindia.indiatimes.com/photo/15357310.cms")
		self.assertEqual(temp_com.videos[0].embed, "//www.youtube.com/embed/qV3s7Sa6B6w")
		#self.assertEqual(temp_com.maps[0].href, "https://www.google.com/maps?sll=30.08236989592049,79.31189246107706&amp;sspn=3.2522150867582833,7.2072687770004205&amp;t=m&amp;q=uttarakhand&amp;dg=opt&amp;ie=UTF8&amp;hq=&amp;hnear=Uttarakhand,+India&amp;ll=30.066753,79.0193&amp;spn=2.77128,5.07019&amp;z=8&amp;output=embed")
		self.assertEqual(temp_com.feeds[0].embed, "[WHATEVER A FEED URL LOOKS LIKE]")
		self.assertEqual(temp_com.videos[0].embed, "//www.youtube.com/embed/qV3s7Sa6B6w")

	def test_common_populate1(self):
		temp_com = Common()
		xml_string = '<Common><Citations><li>Random Citation</li></Citations><ExternalLinks><li href="http://en.wikipedia.org/wiki/2013_North_India_floods">Wikipedia</li></ExternalLinks><Images><li embed="http://timesofindia.indiatimes.com/photo/15357310.cms" /></Images><Summary>Random Summary</Summary></Common>'
		root = ET.fromstring(xml_string)
		temp_com.populate(root)

		self.assertEqual(temp_com.citations[0].floating_text, "Random Citation")
		self.assertEqual(temp_com.external_links[0].href, "http://en.wikipedia.org/wiki/2013_North_India_floods")
		self.assertEqual(temp_com.images[0].embed, "http://timesofindia.indiatimes.com/photo/15357310.cms")
		#self.assertEqual(temp_com.videos[0], "Random Summary")
	
	def test_common_populate2(self):
		temp_com = Common()
		xml_string = "<Common><Citations><li>Random Citation</li></Citations><Summary>Random Summary</Summary></Common>"
		root = ET.fromstring(xml_string)
		temp_com.populate(root)

		self.assertEqual(temp_com.citations[0].floating_text, "Random Citation")
		#self.assertEqual(temp_com.videos[0], "Random Summary")




class unloadModelsCrisisTest(TestCase):

#---------------------------------------------------#
#-----Unit Tests for functions from unloadModels.py
#---------------------------------------------------#

	#---------------------------------------#
	#-----test_clean_xml (paranoid clean for things that are not li objects)
	
	def test_clean_xml0(self):
		dirt = "happy&go&lucky&&&go&happy"
		dirt_to_clean = clean_xml(dirt)
		standard_clean = "happy&amp;go&amp;lucky&amp;&amp;&amp;go&amp;happy"
		self.assertEqual(dirt_to_clean, standard_clean)
	
	#---------------------------------------#
	#-----test_export_crisis

	def test_export_crisis(self):
		xml_string = "<WC><Crisis ID=\"CRI_random\" Name=\"random\"><People><Person ID=\"PER_random\" /></People><Organizations><Org ID=\"ORG_random\" /></Organizations><Kind>random</Kind><Date>2011-01-25</Date><Time>09:00:00+05:30</Time><Locations><li>random</li></Locations><HumanImpact><li>random</li></HumanImpact><EconomicImpact><li>random</li></EconomicImpact><ResourcesNeeded><li>random</li></ResourcesNeeded><WaysToHelp><li> href=\"http://random\"</li><li>random</li></WaysToHelp><Common><Citations><li> href= random</li></Citations><ExternalLinks><li> href=\"http:random.html\"</li></ExternalLinks><Images><li> embed=\"http:random.jpg\"</li></Images><Summary>random</Summary></Common></Crisis></WC>"
		crisis_list1 = []
		root1 = ET.fromstring(xml_string)
		populate_crisis(root1, crisis_list1)
		print ""
		print "HELLLLLLLLLOOOOOOOOO"
		print "test_populate_crisis : ", crisis_list1
		print len(crisis_list1[0].people)
		for person in crisis_list1[0].people :
			print person
		crisis_xml = export_crisis(crisis_list1[0])
		check_string = xml_string [4:-5]

		print crisis_xml

		# self.assertEqual(check_string, crisis_xml)


	#---------------------------------------#
	#-----test_export_person

	def test_export_person(self):
		person_string = "<WC><Person ID=\"PER_HMUBAR\" Name=\"Hosni Mubarak\"><Crises><Crisis ID=\"CRI_UEGYPT\" /></Crises><Organizations><Org ID=\"ORG_MUSBRO\" /><Org ID=\"ORG_EGYGOV\" /></Organizations><Kind>Politician</Kind><Location>Egypt</Location><Common></Common></Person></WC>"
		person_list = []
		root = ET.fromstring(person_string)
		populate_person(root, person_list)
		person_xml = export_person(person_list[0])
		check_string = person_string [4:-5]

		self.assertEqual(check_string, person_xml)

	#---------------------------------------#
	#-----test_export_organization

	def test_export_org(self):
		org_string = "<WC><Organization ID=\"ORG_MUSBRO\" Name=\"The Muslim Brotherhood\"><Crises><Crisis ID=\"CRI_UEGYPT\" /></Crises><People><Person ID=\"PER_ELBARA\" /><Person ID=\"PER_HMUBAR\" /><Person ID=\"PER_RLAKAH\" /><Person ID=\"PER_MMORSI\" /></People><Kind>Islamic Movement</Kind><Location>Egypt</Location><Common></Common></Organization></WC>"
		org_list = []
		root8 = ET.fromstring(org_string)
		populate_org(root8, org_list)
		org_xml = export_organization(org_list[0])
		check_string = org_string [4:-5]

		self.assertEqual(check_string, org_xml)


	#---------------------------------------#
	#-----test_receive_import


class loadModelsCrisisTest(TestCase):

#------------------------------------------------#
#-----Unit Tests for functions from loadModels.py
#------------------------------------------------#

	#---------------------------------------#
	#-----test_validate

	def test_validate0(self):
		f = open('wcdb/xml0.xml')
		self.assertEqual(type(f), file)
		self.assert_(validate(f) != False)

	def test_validate1(self):
		f = open('wcdb/xml1.xml')
		self.assertEqual(type(f), file)
		self.assert_(type(validate(f)) == str)

	def test_validate2(self):
		f = open('wcdb/xml2.xm')
		self.assertEqual(type(f), file)
		self.assertEqual(validate(f), False)

	#---------------------------------------#
	#-----test_populate_models

	#---------------------------------------#
	#-----test_populate_crisis

	def test_populate_crisis0(self):
		xml_string = "<WC><Crisis ID=\"CRI_NOTFOREXPORT\" Name=\"NOTFOREXPORT\"><People><Person ID=\"PER_NOTFOREXPORT\" /></People><Organizations><Org ID=\"ORG_NOTFOREXPORT\" /></Organizations><Kind>NOTFOREXPORT</Kind><Date>2011-01-25</Date><Time>09:00:00+05:30</Time><Locations><li>random</li></Locations><HumanImpact><li>random</li></HumanImpact><EconomicImpact><li>random</li></EconomicImpact><ResourcesNeeded><li>random</li></ResourcesNeeded><WaysToHelp><li> href=\"http://random\"</li><li>random</li></WaysToHelp><Common><Citations><li> href= random</li></Citations><ExternalLinks><li> href=\"http:random.html\"</li></ExternalLinks><Images><li> embed=\"http:random.jpg\"</li></Images><Summary>random</Summary></Common></Crisis></WC>"
		crisis_list = []
		root = ET.fromstring(xml_string)
		populate_crisis(root, crisis_list)
		print len(crisis_list[0].people)
		for person in crisis_list[0].people :
			print person

		self.assert_(len(crisis_list) >= 1)

	def test_populate_crisis1(self):
		xml_string1 = "<WC><Crisis ID=\"CRI_kindofrandom\" Name=\"kindofrandom\"><People><Person ID=\"PER_kindofrandom\" /></People><Organizations><Org ID=\"ORG_kindofrandom\" /></Organizations><Kind>kindofrandom</Kind><Date>2011-01-25</Date><Time>09:00:00+05:30</Time><Locations><li>kindofrandom</li></Locations><HumanImpact><li>kindofrandom</li></HumanImpact><EconomicImpact><li>kindofrandom</li></EconomicImpact><ResourcesNeeded><li>kindofrandom</li></ResourcesNeeded><WaysToHelp><li> href=\"http://kindofrandom\"</li><li>random</li></WaysToHelp><Common><Citations><li> href= random</li></Citations><ExternalLinks><li> href=\"http:random.html\"</li></ExternalLinks><Images><li> embed=\"http:random.jpg\"</li></Images><Summary>random</Summary></Common></Crisis></WC>"
		crisis_list1 = []
		root1 = ET.fromstring(xml_string1)
		populate_crisis(root1, crisis_list1)

		self.assert_(len(crisis_list1) >= 1)




	#---------------------------------------#
	#-----test_populate_person

	#---------------------------------------#
	#-----test_populate_org

class viewsTest(TestCase):

#--------------------------------------------#
#-----Unit Tests for functions from views.py
#--------------------------------------------#

	#---------------------------------------#
	#-----test_indexView
	#---------------------------------------#

	def test_indexView(self):
		response = self.client.get("http://localhost:8000/")
		self.assertEqual(response.status_code, 200)

	#---------------------------------------#
	#-----test_crisisView
	#---------------------------------------#

	# tests that user can see our pages 

	def test_crisisView0(self):
		response = self.client.get("http://localhost:8000/crisis/1")
		self.assertEqual(response.status_code, 200)

	def test_crisisView1(self):
		response = self.client.get("http://localhost:8000/crisis/2")
		self.assertEqual(response.status_code, 200)

	def test_crisisView2(self):
		response = self.client.get("http://localhost:8000/crisis/3")
		self.assertEqual(response.status_code, 200)

	#---------------------------------------#
	#-----test_orgsView
	#---------------------------------------#


	def test_orgsView0(self):
		response = self.client.get("http://localhost:8000/orgs/1")
		self.assertEqual(response.status_code, 200)

	def test_orgsView1(self):
		response = self.client.get("http://localhost:8000/orgs/2")
		self.assertEqual(response.status_code, 200)

	def test_orgsView2(self):
		response = self.client.get("http://localhost:8000/orgs/3")
		self.assertEqual(response.status_code, 200)

	#---------------------------------------#
	#-----test_peopleView
	#---------------------------------------#

	def test_peopleView0(self):
		response = self.client.get("http://localhost:8000/people/1")
		self.assertEqual(response.status_code, 200)

	def test_peopleView1(self):
		response = self.client.get("http://localhost:8000/people/2")
		self.assertEqual(response.status_code, 200)

	def test_peopleView2(self):
		response = self.client.get("http://localhost:8000/people/3")
		self.assertEqual(response.status_code, 200)

	"""
	Creates an infinite loop!
	def test_unittestView(self):
		response = self.client.get("http://localhost:8000/unittests/")
		self.assertEqual(response.status_code, 200)
	"""

	#---------------------------------------#
	#-----test_importView
	#---------------------------------------#

	def test_importView1(self):
		response = self.client.get("http://localhost:8000/import/")
		self.assertEqual(response.status_code, 200)

	def test_importView2(self):
		c = Client()
		with open('wcdb/xml0.xml') as upload:
			response = self.client.post("http://localhost:8000/import/", {'password': "ateam", 'xmlvalue': upload}, follow = True)
        	self.assertEqual(response.status_code, 200) # Redirect on form success

	#---------------------------------------#
	#-----test_passwordValidate
	#---------------------------------------#

	def test_passwordValidate0(self):
		pw = "ateam"
		result = passwordValidate(pw)
		self.assert_(result)

	def test_passwordValidate1(self):
		pw = "someotherteam"
		result = passwordValidate(pw)
		self.assert_(not (result))

	#---------------------------------------#
	#-----test_exportView
	#---------------------------------------#

	def test_exportView(self):
		response = self.client.get("http://127.0.0.1:8000/export/")
		self.assertEqual(response.status_code, 200)
