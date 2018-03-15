#!/usr/bin/env python
# [START imports]
import os
import urllib
import random
import time

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

DEFAULT_WINE_CAT = 'red'
## charlist
CHAR = [chr(i) for i in xrange(ord('A'), ord('Z')+1)] \
                    + [chr(i) for i in xrange(ord('a'), ord('z')+1)] \
                    + [chr(i) for i in xrange(ord('0'), ord('9')+1)]

def wine_key(wine_cate=DEFAULT_WINE_CAT):
    """Constructs a Datastore key for a Wine entity."""
    return ndb.Key('WineCategory', wine_cate.lower())
def user_key(user):
    return ndb.Key('User', user)

class wine(ndb.Model):
    """A main model for representing an individual Wine entry."""
    id = ndb.StringProperty(indexed = True)
    country = ndb.StringProperty(indexed = True)
    region = ndb.StringProperty(indexed = True)
    variety = ndb.StringProperty(indexed = True)
    name = ndb.StringProperty(indexed = True)
    year = ndb.StringProperty(indexed = True)
    price = ndb.FloatProperty(indexed = True)
    date = ndb.DateTimeProperty(auto_now_add = True)


class cart_entry(ndb.Model):
    wine_id = ndb.StringProperty(indexed = True)
    wine_num = ndb.IntegerProperty(indexed = True)
    date = ndb.DateTimeProperty(auto_now_add = True)


class history_entry(ndb.Model):
    user_id = ndb.StringProperty(indexed = True)
    wine_id = ndb.StringProperty(indexed = True)
    wine_num = ndb.IntegerProperty(indexed = True)
    date = ndb.DateTimeProperty(auto_now_add = True)

# [START main_page]
class MainPage(webapp2.RequestHandler):

    def get(self):
        template = JINJA_ENVIRONMENT.get_template('index.html')

        cookie_id = self.request.cookies.get('key')  # if first time, then generate an cookie_id
        if cookie_id == None:
            cookie_id = str(random.randint(1000000000, 9999999999))

        user = users.get_current_user()
        if user:
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/')
            url_linktext = 'Login'

        template_values = {
            'user': user,
            'cookie_id': cookie_id,
            'url': url,
            'url_linktext': url_linktext
        }

        template = JINJA_ENVIRONMENT.get_template('index.html')
        self.response.write(template.render(template_values))
        self.response.headers.add_header('Set-Cookie', 'key=%s' % str(cookie_id))


# [END main_page]

# Wine Library
class Wine(webapp2.RequestHandler):
    def get(self):
        cate = self.request.get('WineCategory').lower()

        if cate == '':
            wine_query = wine.query().order(-wine.date)
        else:
            wine_query = wine.query(ancestor = wine_key(cate)).order(-wine.date)

        ##user
        user = users.get_current_user()
        if user:
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/')
            url_linktext = 'Login'

        wines = wine_query.fetch(50)
        wine_values = {
            'user': user,
            'wines': wines,
            'cate': cate,
            'url': url,
            'url_linktext': url_linktext
        }
        template = JINJA_ENVIRONMENT.get_template('wine.html')
        self.response.write(template.render(wine_values))

    def post(self):
        cate = self.request.get('bt').lower();

        query_params = {'WineCategory': cate}
        self.redirect('/wine?' + urllib.urlencode(query_params))


# Add Wine
class Enter(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('enter.html')
        ##user
        user = users.get_current_user()
        if user:
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/')
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }

        self.response.write(template.render(template_values))

    def post(self):
        cate = self.request.get('WineCategory', 'red')
        new_wine = wine(parent = wine_key(cate.lower()))
        # generate wine unique id
        new_wine.id = ''
        for i in xrange(20):
            new_wine.id += CHAR[random.randint(0, len(CHAR) - 1)]
        new_wine.country = self.request.get('country')
        new_wine.region = self.request.get('region')
        new_wine.variety = self.request.get('variety')
        new_wine.name = self.request.get('name')
        new_wine.year = self.request.get('year')
        new_wine.price = float(self.request.get('price'))
        new_wine.put()
        query_params = {'WineCategory': cate.lower()}
        self.redirect('/wine?' + urllib.urlencode(query_params))

# Search
class Search(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIRONMENT.get_template('search.html')
        ##user
        user = users.get_current_user()
        if user:
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
        else:
            url = users.create_login_url('/')
            url_linktext = 'Login'
        template_values = {
            'user': user,
            'url': url,
            'url_linktext': url_linktext
        }
        self.response.write(template.render(template_values))
    def post(self):
        warn0 = 0  ## Check the library
        warn1 = 0  ## Check the input except WineCategory
        warn2 = 1  ## Check the results
        ## Each Tag Sign
        cate_warn = 1
        name_warn = 1
        region_warn = 1
        country_warn =1
        variety_warn = 1
        year_warn = 1

        wines = ''

        cate = self.request.get('WineCategory', 'Red').lower()
        country = self.request.get('country').lower()
        region = self.request.get('region').lower()
        variety = self.request.get('variety').lower()
        name = self.request.get('name').lower()
        year = self.request.get('year').lower()
        price = str(self.request.get('price'))

        if country == '' and region == '' and variety ==  '' and name == '' and year == '' and price == '':
            warn1 = 1
        ############Search##################
        wine_query = wine.query()
        if not wine_query.fetch():
            warn0 = 1

        if cate != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.key.parent().id().lower()

                cate_lower = cate.lower();
                if cate_lower in items:
                    wine_query = wine.query(ancestor = wine_key(wine_tmp.key.parent().id()))
                    cate_warn = 0
                    break
                else:
                    cate_warn = 1
        else:
            wine_query = wine.query(ancestor = wine_key('Red'))
            if wine_query.fetch():
                cate_warn = 0
            else:
                cate_warn = 1

        if name != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.name
                if name in items.lower():
                    wine_query = wine_query.filter(wine.name == wine_tmp.name)
                    name_warn = 0
                    break
                else:
                    name_warn = 1
        else:
            name_warn = 0

        if region != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.region
                if region in items.lower():
                    wine_query = wine_query.filter(wine.region == wine_tmp.region)
                    region_warn = 0
                    break
                else:
                    region_warn = 1
        else:
            region_warn = 0

        if country != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.country
                if country in items.lower():
                    wine_query = wine_query.filter(wine.country == wine_tmp.country)
                    country_warn = 0
                    break
                else:
                    country_warn = 1
        else:
            country_warn = 0

        if variety != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.variety
                if variety in items.lower():
                    wine_query = wine_query.filter(wine.variety == wine_tmp.variety)
                    variety_warn = 0
                    break
                else:
                    variety_warn = 1
        else:
            variety_warn = 0

        if year != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = wine_tmp.year
                if year in items.lower():
                    wine_query = wine_query.filter(wine.year == wine_tmp.year)
                    year_warn = 0
                    break
                else:
                    year_warn = 1
        else:
            year_warn = 0

        if price != '':
            wine_tmps = wine_query.fetch()
            for wine_tmp in wine_tmps:
                items = str(wine_tmp.price)
                if price in items:
                    wine_query = wine_query.filter(wine.price == wine_tmp.price)
                    price_warn = 0
                    break
                else:
                    price_warn = 1
        else:
            price_warn = 0


        if cate_warn == 1 or name_warn == 1 or country_warn == 1 or region_warn or variety_warn == 1 or year_warn == 1 or price_warn == 1:
            warn2 = 1
        else:
            wines = wine_query.fetch()
            warn2 = 0
        # print wines
        wine_values = {
            'wines': wines,
            'warn0': warn0,
            'warn1': warn1,
            'warn2': warn2,
        }

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(wine_values))

# Cart
class Cart(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:
            login_sign = 1
            user = user.email()
            url = users.create_logout_url('/')
            url_linktext = 'Logout'
            cookie_id = self.request.cookies.get('key')
            # check if have temporary cart
            cart_temp = cart_entry.query(ancestor = user_key(cookie_id))
            if cart_temp:
                for entry in cart_temp:
                    new_entry = cart_entry(parent = user_key(user))
                    new_entry.wine_id = entry.wine_id
                    new_entry.wine_num = entry.wine_num
                    new_entry.put()
                    entry.key.delete()
        else:
            login_sign = 0
            user = self.request.cookies.get('key')
            url = users.create_login_url('/')
            url_linktext = 'Login'

        entry_query = cart_entry.query(ancestor = user_key(user)).order(-cart_entry.date)
        entries = entry_query.fetch()

        wines = []
        total = 0.00
        for entry in entries:
            wine_query = wine.query()
            wine_tmps = wine_query.filter(wine.id == entry.wine_id).fetch(1)
            if  wine_tmps:
                wine_tmp = wine_tmps.pop(0)
                # wine_tmp = make_pairs(entry.wine_num)
                wines.append((wine_tmp, entry.wine_num))
                total = total + wine_tmp.price*entry.wine_num


        template_values = {
            'user': user,
            'wines': wines,
            'total': total,
            'login_sign': login_sign,
            'url': url,
            'url_linktext': url_linktext
        }

        template = JINJA_ENVIRONMENT.get_template('cart.html')
        self.response.write(template.render(template_values))

## update items in the cart
    def post(self):
        #update
        user = users.get_current_user()
        if not user:
            user = self.request.cookies.get('key')
        else:
            user = user.email()

        id = self.request.get('id')
        num = int(self.request.get('num'))

        entry_query = cart_entry.query(ancestor = user_key(user))
        entries = entry_query.fetch()

        for entry in entries:
            if entry.wine_id == id:
                entry = entry.key.get()
                entry.wine_num = num
                entry.put()
                if num == 0:
                    self.redirect('/delete')

        self.redirect('/cart')

#addtocart
class addtocart(webapp2.RequestHandler):
    def post(self):
        id = self.request.get('id')
        num = int(self.request.get('num'))
        user = users.get_current_user()
        if not user:
            user = self.request.cookies.get('key')
        else:
            user = user.email()


        #check if in the cart
        entry_query = cart_entry.query(ancestor = user_key(user)).order(-cart_entry.date)
        entry = entry_query.filter(cart_entry.wine_id == id).fetch(1)

        if not entry:
            new_entry = cart_entry(parent = user_key(user))
            new_entry.wine_id = id
            new_entry.wine_num = num
            new_entry.put()
        else:
            entry = entry.pop(0).key.get()
            entry.wine_num = entry.wine_num + num
            entry.put()

        self.redirect('/wine')

#delete
class delete(webapp2.RequestHandler):
    def post(self):
        #update
        user = users.get_current_user()
        if not user:
            user = self.request.cookies.get('key')
        else:
            user = user.email()

        id = self.request.get('id')

        entry_query = cart_entry.query(ancestor = user_key(user))
        entries = entry_query.fetch()

        for entry in entries:
            if entry.wine_id == id:
                entry = entry.key.delete()

        self.redirect('/cart')

#check out
class checkout(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        cart_entries = cart_entry.query(ancestor = user_key(user.email()))
        if not cart_entries.fetch():
            self.redirect('/cart')
            return
        for entry in cart_entries:
            new_entry = history_entry(parent = user_key(user.email()))
            new_entry.user_id = user.email()
            new_entry.wine_id = entry.wine_id
            new_entry.wine_num = entry.wine_num
            new_entry.put()
            entry.key.delete()

        template_values = {
            'user': user
        }
        template = JINJA_ENVIRONMENT.get_template('thank.html')
        self.response.write(template.render(template_values))

# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/wine', Wine),
    ('/enterinfo', Enter),
    ('/search', Search),
    ('/cart', Cart),
    ('/addtocart', addtocart),
    ('/delete', delete),
    ('/checkout', checkout),
], debug=True)
# [END app]
