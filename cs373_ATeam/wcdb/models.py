import os
os.environ["DJANGO_SETTINGS_MODULE"] = "cs373_ATeam.settings"
from django.db import models

"""
File containing definitions for our Django models and any relevant classes and function
"""
# Helper function for populate_li - takes in an embed string from Li objects of the "Maps" kind
# and returns the correct string for the embedded link
def make_map_embed_string(map_string) :
    if map_string is None :
        return ''

    if map_string[0:23] == "https://maps.google.com":
        if map_string[-5:] != "embed" :
            map_string = map_string + "&output=embed"
    elif map_string[0:17] == "http://google.org" and map_string [-13:] != "embedded=true":
        map_string = map_string + "?&embedded=true"
    elif map_string[0:25] == "http://www.bing.com/maps/" and map_string[0:31] != "http://www.bing.com/maps/embed/":
        map_string = "http://www.bing.com/maps/embed/" + map_string[25:]
    else :
        map_string = ''

    return map_string

# Helper function for populate_li - takes in an embed string from Li objects of the "Videos" kind
# and returns the correct string for the embedded link
def make_video_embed_string(video_string) :
    if video_string is None :
        return ''

    if (video_string[0:23] != "http://www.youtube.com/" or video_string[23:27] == "user") and video_string[0:18] != "//www.youtube.com/" :
            video_string = ''
    elif video_string[0:23] == "http://www.youtube.com/" and video_string[0:28] != "http://www.youtube.com/embed" :
        if video_string[23:54] == "watch?feature=player_detailpage" :
            video_string = "//www.youtube.com/embed/" + video_string[57:68]
        elif video_string[23:52] == "watch?feature=player_embedded":
            video_string = "//www.youtube.com/embed/" + video_string[55:66]
        elif video_string[23:28] == "watch" :
            video_string = "//www.youtube.com/embed/" + video_string[31:42]
        else:
            video_string = ''

    return video_string

def populate_li(root, modl_id, tag):
    """
    Function expects a root, model ID, and tag as parameters. Tag is used to look traverse 
    the root's tree and find the correct parameters to pass to Li's populate method.Once an 
    Li object is populated, the function saves it to the database
    """
    outer_node = root.find(tag)
    if outer_node is not None:
        for li in outer_node or [] :
            href = li.get("href")
            embed = li.get("embed")
            text = li.get("text")
            floating_text = li.text

            if href is None:
                href = ''
            if embed is None:
                embed = ''
            if text is None:
                text = ''
            if floating_text is None:
                floating_text = ''

            if tag == "Videos" :
                embed = make_video_embed_string(embed)

            if tag == "Maps" :
                embed = make_map_embed_string(li.get("embed"))

            li.embed = embed
            temp_li = Li()
            check = Li.objects.filter(model_id=modl_id, href=href,
                embed=embed, text=text, floating_text=floating_text, kind=tag)

            if len(check) == 0:
                if (tag == "Videos" or tag == "Maps") and embed == '':
                    pass
                else:
                    temp_li.populate(li, modl_id, tag)
                    temp_li.save()

class Li(models.Model) :
    """
    Class for the List tag in the unified xml schema. Contains a field for an href, embedded link, 
    and alt text. The floating_text attribute is to catch any text not in attributes.
    """
    # Attributes
    href          =  models.CharField(max_length=2000)
    embed         =  models.CharField(max_length=2000)
    text          =  models.CharField(max_length=2000)
    # Text between tags
    floating_text =  models.CharField(max_length=10000)

    model_id      =  models.CharField(max_length=200)
    kind          =  models.CharField(max_length=200)

    def populate(self, e_node, modl_id, item_type) :
        """
        Non-static method expects an element node, model id, and an Li type as parameters. Example 
        values for type: citations, videos, images, etc. Uses node to populate attributues of a Li 
        object.
        """
        if e_node.get("href") is not None:
            self.href          =  e_node.get("href")
        if e_node.get("embed") is not None:
            self.embed         =  e_node.embed
        if e_node.get("text") is not None:
            self.text          =  e_node.get("text")
        if e_node.text is not None:
            self.floating_text =         e_node.text
        self.model_id      =             modl_id
        self.kind          =           item_type

class Common() :
    """
    Class for the Common tag in the unified xml schema Contains a field for an href, embedded link, and alt text
    The floating_text attribute is to catch any text not in attributes.
    """

    def populate(self, e_node, modl_id) :
        """
        Non-static method expects an element node and model ID as a parameter.
        Uses node to populate attributues of a Common object
        """
        populate_li(e_node, modl_id, "Citations")
        populate_li(e_node, modl_id, "ExternalLinks")
        populate_li(e_node, modl_id, "Images")
        populate_li(e_node, modl_id, "Videos")
        populate_li(e_node, modl_id, "Maps")
        populate_li(e_node, modl_id, "Feeds")

class Relations(models.Model) :
    """
    Relation model maintaining relationships between Crisis, Person, and Org models
    """
    crisis_ID = models.CharField(max_length=200)
    person_ID = models.CharField(max_length=200)
    org_ID    = models.CharField(max_length=200)
    def populate(self, c_id = None, p_id = None, o_id = None) :
        """
        Non-static method expects a crisis ID, person ID, and organization ID as optional parameters.
        """
        if c_id is not None :
            self.crisis_ID = c_id
        if p_id is not None :
            self.person_ID = p_id
        if o_id is not None :
            self.org_ID = o_id

class Crisis(models.Model) :
    """
    Crisis Model
    """
    crisis_ID         = models.CharField(max_length=200, primary_key=True)
    name              = models.CharField(max_length=200)
    kind              = models.CharField(max_length=200)
    date              = models.CharField(max_length=200)
    time              = models.CharField(max_length=200)
    common_summary    = models.CharField(max_length=10000)
    def getID(self) :
        return self.crisis_ID


class Person(models.Model) :
    """
    Person Model
    """

    person_ID         = models.CharField(max_length=200, primary_key=True)
    name              = models.CharField(max_length=200)
    kind              = models.CharField(max_length=200)
    location          = models.CharField(max_length=200)
    common_summary    = models.CharField(max_length=10000)
    def getID(self) :
        return self.person_ID
        
    

class Org(models.Model) :
    """
    Organization Model
    """
    org_ID         = models.CharField(max_length=200, primary_key=True)
    name           = models.CharField(max_length=200)
    kind           = models.CharField(max_length=200)
    location       = models.CharField(max_length=200)
    common_summary = models.CharField(max_length=10000)
    def getID(self) :
        return self.org_ID




