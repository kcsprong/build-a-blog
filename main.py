#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
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
#
import webapp2
import os
import cgi
import jinja2
import re

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)


class Handler(webapp2.RequestHandler):
    def write(self,*a,**kw):
        self.response.out.write(*a,**kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))


class Blogs(db.Model):
    title = db.StringProperty(required = True)
    blogpost = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)



class Blog(Handler):
    def render_front(self, title='', blogpost='', error=''):
        blogs=db.GqlQuery('SELECT * FROM Blogs ORDER BY created DESC LIMIT 5')
        self.render('main_blog.html', title=title, blogpost=blogpost, error=error, blogs=blogs)

    def get(self):
        self.render_front()

class NewPost(Handler):
    def render_front(self, title='', blogpost='', error=''):
        self.render('new_posts.html', title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get('title')
        blogpost = self.request.get('blogpost')

        if title and blogpost:
            b = Blogs(title = title, blogpost = blogpost)
            b.put()
            self.redirect('/blog/%s' %str(b.key().id()))

        else:
            error = 'Please include both a title and blog post'
            self.render_front(title, blogpost, error)

class MainPage(Handler):
    def render_front(self, title='', blogpost='', error=''):
        self.render('base.html', title=title, blogpost=blogpost, error=error)

    def get(self):
        self.render_front()

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        blog = Blogs.get_by_id(int(id))

        if blog:
            self.response.write('<h2>' + blog.title + '</h2><br><br><p>' + blog.blogpost + '</p>')
        else:
            self.response.write('Not a valid blog ID')


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/blog', Blog),
    ('/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
