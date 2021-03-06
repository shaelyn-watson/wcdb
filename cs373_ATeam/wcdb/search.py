# from models import *
from getDbModel import *
from django.db.models import Q
import re


def search(query) :
	"""
	Searches the databse for the search query

	@type query:  string
	@param query: the search query, sent in by the user
	@rtype:       list
	@return:      list of Crises, People, and Orgs, sorted by how much of the query their page information matches.
	"""
	query       =    query.upper()
	searchTerms =    query.split()
	numTerms    = len(searchTerms)
	result      =               []

	#exact matching case
	exactCrises = searchCrisis([query])
	exactPeople = searchPerson([query])
	exactOrgs   =    searchOrg([query])
	exactLis    =     searchLi([query])

	for item in exactCrises :
		match = Match(item.crisis_ID, numTerms + 1)
		result.append(match)

	for item in exactPeople :
		match = Match(item.person_ID, numTerms + 1)
		result.append(match)

	for item in exactOrgs :
		match = Match(item.org_ID, numTerms + 1)
		result.append(match)

	for item in exactLis :
		repeat = False
		for resultItem in result :
			if resultItem.idref == item.model_id :
				repeat = True
				break
		if repeat == False :
			match = Match(item.model_id, numTerms + 1)
			#print item.model_id
			result.append(match)

	#or case
	orCrises = searchCrisis(searchTerms).difference(exactCrises)
	orPeople = searchPerson(searchTerms).difference(exactPeople)
	orOrgs   =      searchOrg(searchTerms).difference(exactOrgs)
	orLis    =        searchLi(searchTerms).difference(exactLis)
	
	orCrises = removeExactLis(exactLis, orCrises)
	orPeople =  removeExactLis(exactLis, orPeople)
	orOrgs   = removeExactLis(exactLis, orOrgs)

	for li in searchLi(searchTerms).difference(exactLis) :
		repeat = False
		for resultItem in result :
			if li.model_id == resultItem.idref :
				orLis.remove(li)


	matchFound = {}
	# initializing lists of booleans for each ID
	initMatchFound(numTerms, matchFound, orCrises, orPeople, orOrgs, orLis)
	#populating the dictionary
	populateMatchFound(searchTerms, numTerms, matchFound, orCrises, orPeople, orOrgs, orLis)

	#print matchFound

	sortedCounts = []
	for i in xrange(numTerms) :
		sortedCounts.append([])

	for idref in matchFound:
		count = 0
		for boolean in matchFound[idref]:
			if boolean:
				count += 1
		match = Match(idref, count)
		sortedCounts[count - 1].append(match)

	# print "BEFORE ADDING ORS"
	# for res in result :
	# 	print res.id
	for index in reversed(xrange(numTerms)) :
		for match in sortedCounts[index] :
			result.append(match)
	#print result
	# print "\nAFTER ADDING ORS"
	# for res in result :
	# 	print res.id
	
	getContext(result, matchFound, [query], 1)
	if numTerms > 1:
		getContext(result, matchFound, searchTerms, numTerms)
	# 	for context in match.contexts:
	# 		print "begin: ", context.begin 
	# 		print "bold: ", context.bold 
	# 		print "end: ", context.end
	return result

def searchCrisis(searchTerms) :
	"""
	Searches through database for Crisis objects containing any of the terms in the list.

	@type  searchTerms: list
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@rtype:             set
	@return:            a set of Crisis objects, whose pages' information contains matches terms 
	                    in searchTerms
	"""
	modelSet = set()
	for term in searchTerms :
		modelSet = modelSet.union(Crisis.objects.filter(Q(crisis_ID__iregex = term) | Q(name__iregex = term) | Q(kind__iregex = term) | Q(date__iregex = term) | Q(time__iregex = term) | Q(common_summary__iregex = term)))
	return modelSet

def searchPerson(searchTerms) :
	"""
	Searches through database for Person objects containing any of the terms in the list.

	@type  searchTerms: list
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@rtype:             set
	@return:            a set of Person objects, whose pages' information contains matches terms 
	                    in searchTerms
	"""
	modelSet = set()
	for term in searchTerms :
		modelSet = modelSet.union(Person.objects.filter(Q(person_ID__iregex = term) | Q(name__iregex = term) | Q(kind__iregex = term) | Q(location__iregex = term) | Q(common_summary__iregex = term)))
	return modelSet			

def searchOrg(searchTerms) :
	"""
	Searches through database for Org objects containing any of the terms in the list.

	@type  searchTerms: list of strings
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@rtype:       set
	@return:      a set of Org objects, whose pages' information contains matches terms 
	              in searchTerms
	"""
	modelSet = set()
	for term in searchTerms :
		modelSet = modelSet.union(Org.objects.filter(Q(org_ID__iregex = term) | Q(name__iregex = term) | Q(kind__iregex = term) | Q(location__iregex = term) | Q(common_summary__iregex = term)))
	return modelSet	

def searchLi(searchTerms) :
	"""
	Searches through database for Li objects containing any of the terms in the list.

	@type  searchTerms: list of strings
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@rtype:             set
	@return:            a set of Li objects, whose pages' information contains matches terms 
	                    in searchTerms
	"""
	modelSet = set()
	for term in searchTerms :
		modelSet = modelSet.union(Li.objects.filter(Q(floating_text__iregex = term)))
	return modelSet		

def initMatchFound(numTerms, matchFound, orCrises, orPeople, orOrgs, orLis) :
	"""
	Initializes a dictionary where the keys are model idrefs and the values are lists of 
	booleans. The indices of the lists correspond to a term in the search query. The value
	at the index is True if that model instance matches that term and False otherwise.

	@type  numTerms:   int
	@param numTerms:   length of list created by splitting the search query, sent in by the user, 
	                   by whitespace
	@type  matchFound: dictionary
	@param matchFound: dictionary defined in function description
	@type  orCrises:   set
	@param orCrises:   Crisis objects whose pages contain matched terms
	@type  orPeople:   set
	@param orPeople:   Person objects whose pages contain matched terms
	@type  orOrgs:     set
	@param orOrgs:     Org objects whose pages contain matched terms
	@type  orLis:      set
	@param orLis:      Li objects whose pages contain matched terms

	"""
	for crisis in orCrises:
		matchFound[crisis.crisis_ID] = [False] * numTerms

	for person in orPeople:
		matchFound[person.person_ID] = [False] * numTerms

	for org in orOrgs:
		matchFound[org.org_ID] = [False] * numTerms

	for li in orLis:
		matchFound[li.model_id] = [False] * numTerms

def populateMatchFound(searchTerms, numTerms, matchFound, orCrises, orPeople, orOrgs, orLis) :
	"""
	Sets the boolean values in the dictionary mentioned in initMatchFound().

	@type  searchTerms: list
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@type  numTerms:    int
	@param numTerms:    length of searchTerms
	@type  matchFound:  dictionary
	@param matchFound:  dictionary described in initMatchFound()
	@type  orCrises:    set
	@param orCrises:    Crisis objects whose pages contain matched terms
	@type  orPeople:    set
	@param orPeople:    Person objects whose pages contain matched terms
	@type  orOrgs:      set
	@param orOrgs:      Org objects whose pages contain matched terms
	@type  orLis:       set
	@param orLis:       Li objects whose pages contain matched terms
	@rtype:             N/A
	@return:            function does not return
	"""
	for crisis in orCrises:
		crisisDict = getCrisis(crisis.crisis_ID)
		crisisDict.pop('people')
		crisisDict.pop('organizations')
		crisisString = str(crisisDict).upper()
		count = 0
		for term in searchTerms:
			if term in crisisString:
				matchFound[crisis.crisis_ID][count] = True
			count += 1

	for person in orPeople:
		personDict = getPerson(person.person_ID)
		personDict.pop('crises')
		personDict.pop('organizations')
		personString = str(personDict).upper()
		count = 0
		for term in searchTerms:
			if term in personString:
				matchFound[person.person_ID][count] = True
			count += 1

	for org in orOrgs:
		orgDict = getOrg(org.org_ID)
		orgDict.pop('people')
		orgDict.pop('crises')
		orgString = str(orgDict).upper()
		count = 0
		for term in searchTerms:
			if term in orgString:
				matchFound[org.org_ID][count] = True
			count += 1

	for li in orLis:
		liString = str(getLi(li.model_id)).upper()
		count = 0
		for term in searchTerms:
			if term in liString:
				matchFound[li.model_id][count] = True
			count += 1

def getContext(result, matchFound, searchTerms, numTerms):
	"""
	Iterates through the sorted list of result (instances of the Match class) and
	retrieves the contexts for matched search terms.

	@type  result:      list
	@param result:      list of sorted instances of the Match class
	@type  matchFound:  dictionary
	@param matchFound:  dictionary described in initMatchFound()
	@type  searchTerms: list of strings
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@type  numTerms:    int
	@param numTerms:    length of searchTerms
	@rtype:             N/A
	@return:            function does not return
	"""
	#going through match instances in result
	for match in result :
		# iterate through model:
		modelDict = {}
		keyList = []
		#crisis_dict = {name : *, kind : *, date : *, time : *, people : [], organizations : [], Common : ?}
		if match.idref[0:3] == "CRI" :
			modelDict = getCrisis(match.idref)
			keyList = ['name', 'kind', 'date', 'time','common']

		#person_dict = {name : *, kind : *, location : *, crises : [], organizations : [], Common : ?}
		if match.idref[0:3] == "PER" :
			modelDict = getPerson(match.idref)
			keyList = ['name', 'kind', 'location', 'common']

		#org_dict = {name : *, kind : *, location : *, crises : [], organizations : [], Common : ?}
		if match.idref[0:3] == "ORG" :
			modelDict = getOrg(match.idref)
			keyList = ['name', 'kind', 'location', 'common']

		for index in xrange(numTerms) :
			#checks to see if this page has a match for this term
			if (match.count > numTerms) or (matchFound[match.idref][index] == False) :
				#only = 1 when an exact is passed in
				if numTerms == 1 :
					pass
				else:
					continue
				#continue
			for key in keyList :
				if key != 'common' :
					found = modelDict[key].upper().find(searchTerms[index])
					if found >= 0 :
						getContextFromModel(match, modelDict, searchTerms, index, key)
						break
				else :
					#common case is different, since it's a nested container
					found = modelDict['common']['Summary'].upper().find(searchTerms[index])
					#break
					if found >= 0 :
						getContextFromModel(match, modelDict['common'], searchTerms, index, 'Summary')
						break
			#none of the attributes found it so it must be in the Li attributes
			else : 
				liDict = getLi(match.idref)
				# print len(liDict['floating_text'])
				# print len(liDict['kind'])
				for liIndex in xrange(len(liDict['kind'])) :
					found = liDict['floating_text'][liIndex].upper().find(searchTerms[index])
					if found >= 0 :
						tempContext = Context()
						tempContext.begin = liDict['kind'][liIndex] + ': ...'
						if found > 0 :
							regex = re.search("[^ ]* *[^ ]* *[^ ]* *[^ ]* *[^ ]*", liDict['floating_text'][liIndex][found-1::-1]).group(0)
							tempContext.begin += regex[::-1]
						tempContext.bold  =  liDict['floating_text'][liIndex][found:(found + len(searchTerms[index]))]
						tempContext.end   += re.search("[^ ]* *[^ ]* *[^ ]* *[^ ]* *[^ ]*", liDict['floating_text'][liIndex][found + len(searchTerms[index]): found + 100]).group(0)
						match.contexts.append(tempContext)
						break
		# 		continue

		# iterate through Li:

def getExactContext(result, matchFound, query, numTerms):
	for match in result :
		if match.count > numTerms :
			modelDict = {}
			keyList = []
			#crisis_dict = {name : *, kind : *, date : *, time : *, people : [], organizations : [], Common : ?}
			if match.idref[0:3] == "CRI" :
				modelDict = getCrisis(match.idref)
				keyList = ['name', 'kind', 'date', 'time','common']

			#person_dict = {name : *, kind : *, location : *, crises : [], organizations : [], Common : ?}
			if match.idref[0:3] == "PER" :
				modelDict = getPerson(match.idref)
				keyList = ['name', 'kind', 'location', 'common']

			#org_dict = {name : *, kind : *, location : *, crises : [], organizations : [], Common : ?}
			if match.idref[0:3] == "PER" :
				modelDict = getPerson(match.idref)
				keyList = ['name', 'kind', 'location', 'common']

def getContextFromModel(match, modelDict, searchTerms, index, attribute) :
	"""
	Called by getContext(). Retrieves the context for some match instance from the model instance
	the match's idref attribute corresponds to.

	@type  match:       Match
	@param match:       instance of the Match class
	@type  modelDict:   dictionary
	@param modelDict:   dictionary produced by the functions of getDbModel.py
	@type  searchTerms: list
	@param searchTerms: the search query, sent in by the user, split by whitespace
	@type  index:       int
	@param index:       corresponds to the index in searchTerms
	@type  attribute:   string
	@param attribute:   corresponds to a key in the modelDict
	@rtype:             N/A
	@return:            function does not return
	"""
	found = modelDict[attribute].upper().find(searchTerms[index])
	tempContext = Context()
	tempContext.begin =  attribute.upper() + ': ...'
	if found > 0 :
		regex = re.search("[^ ]* *[^ ]* *[^ ]* *[^ ]* *[^ ]*", modelDict[attribute][found-1::-1]).group(0)
		tempContext.begin += regex[::-1]
	tempContext.bold  =  modelDict[attribute][found:(found + len(searchTerms[index]))]
	tempContext.end   += re.search("[^ ]* *[^ ]* *[^ ]* *[^ ]* *[^ ]*", modelDict[attribute][found + len(searchTerms[index]): found + 100]).group(0)
	match.contexts.append(tempContext)

def removeExactLis(exactLis, orSet) :
	"""
	Function created to deal with duplicate results. All Li instances really
	just map to some instance of Crisis, Person, or Org. This function accounts
	for this by removing Li objects whose corresponding model instance has already
	found matches.

	@type  exactLis: set
	@param exactLis: Li objects with found matches
	@type  orSet:    set
	@param orSet:    Crisis, Person, or Org objects with found matches
	@rtype:          set
	@return:         orSet with the overlap between matched Li objects removed
	"""
	tempSet = set()
	for li in exactLis :
		for model in orSet :
			if li.model_id == model.getID() :
				tempSet.add(model)
	return orSet.difference(tempSet)


class Match() :
	"""
	Class to help represent search results. 

	@type idref:    string
	@ivar idref:    idref uniquely identifying some crisis, person, or organization
	@type count:    int
	@ivar count:    number of terms in the search query matched by the model identified
	                by the idref
	@type contexts: list
	@ivar contexts: contexts for terms matched by the model identified by the idref
	"""
	def __init__(self, idref, count) :
		self.idref = idref 
		self.count = count
		self.contexts = []

class Context() :
	"""
	Class to help represent the contexts for matched terms in a search result.

	@type begin: string
	@ivar begin: up to five words before the matched term
	@type bold:  string
	@ivar bold:  the matched term, isolated so the front end can bold the term with minimal
	             effort
	@type end:   string
	@ivar end:   up to five words after the matched term
	"""
	def __init__(self) :
		self.begin = ''
		self.bold  = ''
		self.end   = ''
