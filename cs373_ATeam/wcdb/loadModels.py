import sys
from genxmlif import GenXmlIfError
from minixsv import pyxsval
from django.conf import settings
from models import Crisis, Person, Org, Li, Common, Relations, list_add
import xml.etree.ElementTree as ET

"""
File imports an xml file, sent in by the user from the website, and populates Django models
using the information from the file.
"""

def populate_models(tree) :
	"""
	Function expects an element tree as a parameter. Main function of the file that calls
	populate_crisis, populate_org, and populate_person. Returns a dictionary where the keys
	are the type of model and the values are lists of instances of the models populated by 
	this funciton.
	"""
	e_root = tree.getroot()

	for crisis in e_root.findall("Crisis"):
		populate_crisis(crisis)

	#populate Crisis models
	#crises = []
	#populate_crisis(e_root, crises)


	for person in e_root.findall("Person"):
			populate_person(person)
	#populate Person models
	#people = []
	#populate_person(e_root, people)

	for organization in e_root.findall("Organization"):
		populate_org(organization)
	#populate Org models
	#organizations    = []
	#populate_org(e_root, organizations)

	#filled_models = {'crises' : crises , 'organizations' : organizations, "people" : people}
	#return filled_models

def populate_li(root, modl_id, tag):
    for li in root.find(tag) or [] :
            temp_li = Li()
            temp_li.populate(li, modl_id, tag)
            temp_li.save()

def populate_crisis(root) :
	"""
	Function expects a node in an element tree and a list as parameters. Find instances of crisis
	in the tree and adds it to the list
	"""
	for crisis in root.findall("Crisis"):
		temp_crisis           =                 Crisis()
		temp_crisis.crisis_ID =         crisis.get("ID")
		temp_crisis.name      =       crisis.get("Name")
		if crisis.find("Kind") is not None :
			temp_crisis.kind      = crisis.find("Kind").text
		if crisis.find("Date") is not None :
			temp_crisis.date      = crisis.find("Date").text
		if crisis.find("Time") is not None :
			temp_crisis.time      = crisis.find("Time").text
		#populating people
		for person in crisis.iter("Person") or [] :
			temp_relations = Relations()
			temp_relations.populate(c_id = crisis.get("ID"), p_id = person.get("ID"))
			temp_relations.save()
		#populating organizations
		for org in crisis.iter("Org") or [] :
			temp_relations = Relations()
			temp_relations.populate(c_id = crisis.get("ID"), o_id = org.get("ID"))
			temp_relations.save()

		populate_li(crisis, crisis.get("ID"), "Locations")
		populate_li(crisis, crisis.get("ID"), "HumanImpact")
		populate_li(crisis, crisis.get("ID"), "EconomicImpact")
		populate_li(crisis, crisis.get("ID"), "ResourcesNeeded")
		populate_li(crisis, crisis.get("ID"), "WaysToHelp")

		# for location in crisis.find("Locations") or [] :
		# 	temp_li = Li()
		# 	temp_li.populate(location, crisis.get("ID"), "Locations")
		# 	list_add(temp_crisis.locations, temp_li)

		#populating common fields
		found_common = crisis.find('Common')
		if found_common is not None:
			temp_crisis.common.populate(found_common)



		#add populated crisis model to list
		temp_crisis.save()

def populate_person(root) :
	"""
	Function expects a node in an element tree and a list as parameters. Find instances of person
	in the tree and adds it to the list
	"""
	for person in root.findall("Person"):
		temp_person             =                     Person()
		temp_person.person_ID   =             person.get("ID")
		temp_person.name        =           person.get("Name")
		if person.find("Kind") is not None :
			temp_person.kind        =     person.find("Kind").text
		if person.find("Location") is not None :
			temp_person.location    = person.find("Location").text

		for crisis in person.iter("Crisis") :
			temp_relations = Relations()
			temp_relations.populate(c_id = crisis.get("ID"), p_id = person.get("ID"))
			temp_relations.save()

		for org in person.iter("Org") :
			temp_relations = Relations()
			temp_relations.populate(p_id = person.get("ID"), o_id = org.get("ID"))
			temp_relations.save()

		#populating common fields
		found_common = person.find('Common')
		if found_common is not None :
			temp_person.common.populate(found_common)

		temp_person.save()

def populate_org(root) :
	"""
	Function expects a node in an element tree and a list as parameters. Find instances of organization
	in the tree and adds it to the list
	"""
	for org in root.findall("Organization") :
		temp_org          =                     Org()
		temp_org.org_ID   =             org.get("ID")
		temp_org.name     =           org.get("Name")
		if org.find("Kind") is not None :
			temp_org.kind     =     org.find("Kind").text
		if org.find("Location") is not None :
			temp_org.location = org.find("Location").text

		for crisis in org.iter("Crisis") :
			temp_relations = Relations()
			temp_relations.populate(c_id = crisis.get("ID"), o_id = org.get("ID"))
			temp_relations.save()

		for person in org.iter("Person") :
			temp_relations = Relations()
			temp_relations.populate(p_id = person.get("ID"), o_id = org.get("ID"))
			temp_relations.save()

		populate_li(org, org.get("ID"), "History")
		populate_li(org, org.get("ID"), "ContactInfo")

		found_common = org.find('Common')
		if found_common is not None :
			temp_org.common.populate(found_common)

		list.append(temp_org)

def validate(file_in) :
	"""
	Function expects a file as a parameter. Checks if file is a valid xml file.
	Returns False if not, and an element tree built from the file if it is valid.
	"""
	name = str(file_in.name)
	if name[-4:] != ".xml" and name[-4:] != ".XML" :
		return False
	xsd = open('wcdb/WorldCrises.xsd.xml', 'r')
	xmlFile = open('wcdb/temp.xml', 'w')
	xmlFile.write(file_in.read())
	xmlFile = open('wcdb/temp.xml', 'r')
	try:
		psvi = pyxsval.parseAndValidate("wcdb/temp.xml",
			"wcdb/WorldCrises.xsd.xml", xmlIfClass=pyxsval.XMLIF_ELEMENTTREE)
		tree = psvi.getTree()
	except pyxsval.XsvalError, e:
		return 'Validation aborted. ' + e
	except GenXmlIfError, e:
		return 'Parsing aborted. ' + e
	except Exception as e:
		# catch all
		return 'Exception. ' + str(e)
	#handle invalid case
	return tree
