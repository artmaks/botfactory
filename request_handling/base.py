# -*- coding: utf-8 -*-
import webapp2
import jinja2
from webapp2_extras import auth
from webapp2_extras import sessions
from webapp2_extras.appengine.auth import models

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(['templates']),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


def user_required(handler):
    """
        Decorator for checking if there's a user associated with the current session.
        Will also fail if there's no session present.
    """

    def check_login(self, *args, **kwargs):
        auth = self.auth
        if not auth.get_user_by_session():
            # If handler has no login_url specified invoke a 403 error
            try:
                self.redirect(self.auth_config['login_url'], abort=True)
            except (AttributeError, KeyError), e:
                self.abort(403)
        else:
            return handler(self, *args, **kwargs)

    return check_login


class BaseHandler(webapp2.RequestHandler):
    """
        BaseHandler for all requests
        Holds the auth and session properties so they are reachable for all requests
    """

    def dispatch(self):
        """
            Save the sessions for preservation across requests
        """
        try:
            response = super(BaseHandler, self).dispatch()
            if(response):
                self.response.write(response)
        finally:
            self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def user(self):
        user_dict = self.auth.get_user_by_session()
        if user_dict is None:
            return None
        return models.User.get_by_id(user_dict["user_id"]).auth_ids[0]

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()

    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    def render(self, template_name, template_values):
        template = JINJA_ENVIRONMENT.get_template(template_name)
        self.response.write(template.render(template_values))

    @webapp2.cached_property
    def auth_config(self):
        """
            Dict to hold urls for login/logout
        """
        return {
            'login_url': self.uri_for('login'),
            'logout_url': self.uri_for('logout')
        }