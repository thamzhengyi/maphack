import urllib
import webapp2
import jinja2
import os
import datetime

from google.appengine.ext import ndb
from google.appengine.api import users

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + "/templates"))

# This part for the front page
class MainPage(webapp2.RequestHandler):
    # Handler for the front page.

    def get(self):
        template = jinja_environment.get_template('front.html')
        self.response.out.write(template.render())

class MainPageUser(webapp2.RequestHandler):
    # Front page for those logged in

    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            parent = ndb.Key('Persons', users.get_current_user().email())
            person = parent.get()

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
            }
            template = jinja_environment.get_template('frontuser.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class Persons(ndb.Model):
    display_name = ndb.StringProperty()
    bio = ndb.TextProperty()

class Inventories(ndb.Model):
    next_game = ndb.IntegerProperty()

class Playlists(ndb.Model):
    next_game = ndb.IntegerProperty()

class Games(ndb.Model):
    game_id = ndb.IntegerProperty()
    game_title = ndb.StringProperty()
    game_platform = ndb.StringProperty()
    image_link = ndb.StringProperty()
    description = ndb.TextProperty()
    date = ndb.DateTimeProperty(auto_now_add=True)

class Profile(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        if user:  # signed in already
            parent = ndb.Key('Persons', users.get_current_user().email())
            person = parent.get()

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'display_name': person.display_name,
                'bio': person.bio
            }
            template = jinja_environment.get_template('profile.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

class EditProfile(webapp2.RequestHandler):
    def show(self):
        user = users.get_current_user()
        if user:  # signed in already
            parent = ndb.Key('Persons', users.get_current_user().email())
            person = parent.get()

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'display_name': person.display_name,
                'bio': person.bio
            }
            template = jinja_environment.get_template('edit_profile.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

    def get(self):
            self.show()

    def post(self):
            parent = ndb.Key('Persons', users.get_current_user().email())
            person = parent.get()

            person.display_name = self.request.get('display_name')
            person.bio = self.request.get('bio')

            person.put()
            self.redirect('/profile')

class Inventory(webapp2.RequestHandler):
    """ Form for getting and displaying games in Inventory. """

    def show(self):
        # Displays the page. Used by both get and post
        user = users.get_current_user()
        if user:  # signed in already

            # Retrieve person
            parent_key = ndb.Key('Inventories', users.get_current_user().email())

            # Retrieve games
            query = ndb.gql("SELECT * "
                            "FROM Games "
                            "WHERE ANCESTOR IS :1 "
                            "ORDER BY date DESC",
                            parent_key)

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'games': query,
            }

            template = jinja_environment.get_template('inventory.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

    def get(self):
        self.show()

    def post(self):
        # Retrieve inventory
        parent = ndb.Key('Inventories', users.get_current_user().email())
        inventory = parent.get()
        if inventory == None:
            inventory = Inventories(id=users.get_current_user().email())
            inventory.next_game = 1

        game = Games(parent=parent, id=str(inventory.next_game))
        game.game_id = inventory.next_game

        game.game_title = self.request.get('game_title')
        game.game_platform = self.request.get('game_platform')
        game.image_link = self.request.get('image_link')
        game.description = self.request.get('description')

        # Only store an item if there is a game title and game platform
        if game.game_title.rstrip() != '' and game.game_platform.rstrip() != '':
            inventory.next_game += 1
            inventory.put()
            game.put()

        self.show()

class Playlist(webapp2.RequestHandler):
    """ Form for getting and displaying games in Playlist. """

    def show(self):
        # Displays the page. Used by both get and post
        user = users.get_current_user()
        if user:  # signed in already

            # Retrieve person
            parent_key = ndb.Key('Playlists', users.get_current_user().email())

            # Retrieve games
            query = ndb.gql("SELECT * "
                            "FROM Games "
                            "WHERE ANCESTOR IS :1 "
                            "ORDER BY date DESC",
                            parent_key)

            template_values = {
                'user_mail': users.get_current_user().email(),
                'logout': users.create_logout_url(self.request.host_url),
                'games': query,
            }

            template = jinja_environment.get_template('playlist.html')
            self.response.out.write(template.render(template_values))
        else:
            self.redirect(self.request.host_url)

    def get(self):
        self.show()

    def post(self):
        # Retrieve playlist
        parent = ndb.Key('Playlists', users.get_current_user().email())
        playlist = parent.get()
        if playlist == None:
            playlist = Playlists(id=users.get_current_user().email())
            playlist.next_game = 1

        game = Games(parent=parent, id=str(playlist.next_game))
        game.game_id  = playlist.next_game

        game.game_title = self.request.get('game_title')
        game.game_platform = self.request.get('game_platform')
        game.image_link = self.request.get('image_link')
        game.description = self.request.get('description')

        # Only store an item if there is a game title and game platform
        if game.game_title.rstrip() != '' and game.game_platform.rstrip() != '':
            playlist.next_game += 1
            playlist.put()
            game.put()

        self.show()

# For deleting a game from inventory
class DeleteFromInventory(webapp2.RequestHandler):
    # Delete game specified by user

    def post(self):
        game = ndb.Key('Inventories', users.get_current_user().email(), 'Games', self.request.get('game_id'))
        game.delete()
        self.redirect('/inventory')

# For deleting a game from playlist
class DeleteFromPlaylist(webapp2.RequestHandler):
    # Delete game specified by user

    def post(self):
        game = ndb.Key('Playlists', users.get_current_user().email(), 'Games', self.request.get('game_id'))
        game.delete()
        self.redirect('/playlist')

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/maphack', MainPageUser),
                               ('/inventory', Inventory),
                               ('/playlist', Playlist),
                               ('/inventory/deletegame', DeleteFromInventory),
                               ('/playlist/deletegame', DeleteFromPlaylist),
                               ('/profile', Profile),
                               ('/profile/edit', EditProfile)],
                              debug=True)