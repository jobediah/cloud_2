# [START imports]
import os
import urllib
import datetime

from google.appengine.api import users
from google.appengine.ext import ndb

import jinja2
import webapp2


JINJA_ENVIRONMENT = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
                                       extensions=['jinja2.ext.autoescape'],
                                       autoescape=True)
# [END imports]

class PetDB(ndb.Model):
    author = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(indexed=False)
    age = ndb.IntegerProperty(indexed=False)
    rabies = ndb.BooleanProperty(indexed=False)
    bordetella = ndb.BooleanProperty(indexed=False)
    date = ndb.DateProperty()


# [START main_page]
class MainPage(webapp2.RequestHandler):
    
    def get(self):
        
        # Checks for active Google account session
        user = users.get_current_user()
        
        if user:
            person = users.get_current_user().user_id()
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            person = ""
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        k = ndb.Key(PetDB, 'default_name')
        pet_query = PetDB.query(ancestor=k)
        pet_data = pet_query.fetch()
        template_values = {'foos':pet_data, 'user': person, 'url': url, 'url_linktext':url_linktext,}
        
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))

# [END main_page]



class Pets(webapp2.RequestHandler):
    
    def post(self):
        if users.get_current_user():
            person = users.get_current_user().user_id()
    
        k = ndb.Key(PetDB, 'default_name')
        pet = PetDB(parent=k)
        pet.author = person
        pet.name = self.request.get('name')
        pet.type = self.request.get('pets')
        pet.age = int(self.request.get('age'))
        if self.request.get('rabies'):
            pet.rabies = True
        else:
            pet.rabies = False
        if self.request.get('bordetella'):
            pet.bordetella = True
        else:
            pet.bordetella = False
        olddt = str(self.request.get('vdate'))
        self.response.write(olddt)
        if(olddt != ""):
            newdt = olddt.replace("-", "")
            dt = datetime.datetime.strptime(newdt, "%Y%m%d").date()
            pet.date = dt
        pet.put()
        
        self.redirect("/")


class Edit(webapp2.RequestHandler):
    def get(self):
        id = self.request.get('key')
        k = ndb.Key(PetDB, 'default_name')
        pet_query = PetDB.query(ancestor=k)
        pet_data = pet_query.fetch()
        for pet_info in pet_data:
            if pet_info.key.urlsafe() == id:
                self.response.write(pet_info)
                break
    
        template_values = {'name': pet_info.name, 'age': pet_info.age, 'type': pet_info.type,
                            'rabies': pet_info.rabies, 'bordetella': pet_info.bordetella,
                            'date': pet_info.date, 'key': self.request.get('key'),}
                        
        template = JINJA_ENVIRONMENT.get_template('entries.html')
        self.response.write(template.render(template_values))

class SaveChanges(webapp2.RequestHandler):
    def post(self):
        key = self.request.get('key')
        self.response.write(key)
        pet_key = ndb.Key(urlsafe=key)
        pet = pet_key.get()
        self.response.write(pet.name)
        pet.name = self.request.get('name')
        pet.type = self.request.get('pets')
        pet.age = int(self.request.get('age'))
        if self.request.get('rabies'):
            pet.rabies = True
        else:
            pet.rabies = False
        if self.request.get('bordetella'):
            pet.bordetella = True
        else:
            pet.bordetella = False

        olddt = str(self.request.get('vdate'))
        self.response.write(olddt)
        if(olddt != ""):
            newdt = olddt.replace("-", "")
            dt = datetime.datetime.strptime(newdt, "%Y%m%d").date()
            pet.date = dt
        pet.put()

        self.redirect("/")

app = webapp2.WSGIApplication([
                               ('/', MainPage),
                               ('/animals', Pets),
                               ('/edit', Edit),
                               ('/save', SaveChanges),
                               ], debug=True)