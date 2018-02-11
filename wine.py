#!/usr/bin/env python

# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START imports]
import os
import urllib

from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search

import jinja2
import webapp2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)
# [END imports]

DEFAULT_WINE_NAME = 'ChenZeyuGuest'


# We set a parent key on the 'Greetings' to ensure that they are all
# in the same entity group. Queries across the single entity group
# will be consistent. However, the write rate should be limited to
# ~1/second.

def wine_key(wine_cate=DEFAULT_WINE_NAME):
    """Constructs a Datastore key for a Wine entity.

    We use wine_cate as the key.
    """
    return ndb.Key('WineCategory', wine_cate)

class wine(ndb.Model):
    """A main model for representing an individual Wine entry."""
    country = ndb.StringProperty(indexed = True)
    region = ndb.StringProperty(indexed = True)
    variety = ndb.StringProperty(indexed = True)
    name = ndb.StringProperty(indexed = True)
    year = ndb.StringProperty(indexed = True)
    date = ndb.DateTimeProperty(auto_now_add = True)


# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render())
# [END main_page]

# Wine
class Wine(webapp2.RequestHandler):
    def get(self):
        cate = self.request.get('WineCategory')

        if cate == '':
            wine_query = wine.query().order(-wine.date)
        else:
            wine_query = wine.query(ancestor = wine_key(cate)).order(-wine.date)

        wines = wine_query.fetch(10)
        wine_values = {
            'wines': wines,
            'cate': cate
        }
        template = JINJA_ENVIRONMENT.get_template('wine.html')
        self.response.write(template.render(wine_values))

    def post(self):
        cate = self.request.get('bt');

        query_params = {'WineCategory': cate}
        self.redirect('/wine?' + urllib.urlencode(query_params))


        #self.response.write("Hello!")

# Add Wine
class Enter(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('enter.html')
        self.response.write(template.render())
    def post(self):
        cate = self.request.get('WineCategory', 'Red')
        new_wine = wine(parent = wine_key(cate))
        new_wine.country = self.request.get('country')
        new_wine.region = self.request.get('region')
        new_wine.variety = self.request.get('variety')
        new_wine.name = self.request.get('name')
        new_wine.year = self.request.get('year')
        new_wine.put()
        query_params = {'WineCategory': cate}
        self.redirect('/wine?' + urllib.urlencode(query_params))

class Search(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render())
    def post(self):
        warn1 = 0
        warn2 = 0
        wines = ''


        cate = self.request.get('WineCategory', 'Red').lower()
        country = self.request.get('country').lower()
        region = self.request.get('region').lower()
        variety = self.request.get('variety').lower()
        name = self.request.get('name').lower()
        year = self.request.get('year').lower()
        print cate != ' ' and country != ' ' and region != ' ' and variety != ' ' and name != ' ' and year != ' '
        print cate !=' '
        if cate == '' and country == '' and region == '' and variety ==  '' and name == '' and year == '' :
            warn1 = 1
        ############Search##################
        wine_query = wine.query()
        if cate != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.key.parent().id()
                if cate in items.lower():
                    wine_query = wine.query(ancestor = wine_key(wine_tmp.key.parent().id()))

        if country != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.country
                if country in items.lower():
                    wine_query = wine_query.filter(wine.country == wine_tmp.country)
        if region != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.region
                if region in items.lower():
                    wine_query = wine_query.filter(wine.region == wine_tmp.region)
        if variety != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.variety
                if variety in items.lower():
                    wine_query = wine_query.filter(wine.variety == wine_tmp.variety)
        if name != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.name
                if region in items.lower():
                    wine_query = wine_query.filter(wine.name == wine_tmp.name)
        if year != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.year
                if year in items.lower():
                    wine_query = wine_query.filter(wine.year == wine_tmp.year)

        if warn1 != 1:
            if len(wine_query.fetch(10)) != 0:
                wines = wine_query.fetch(10)
            else:
                warn2 = 1

        wine_values = {
            'wines': wines,
            'warn1': warn1,
            'warn2': warn2,
        }
        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(wine_values))

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/wine', Wine),
    ('/enterinfo', Enter),
    ('/search', Search)
], debug=True)
# [END app]
