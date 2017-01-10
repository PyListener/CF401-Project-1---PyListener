import os
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.security import Allow, Authenticated
from pyramid.session import SignedCookieSessionFactory

from passlib.apps import custom_app_context as pwd_context


class NewRoot(object):
    def __init__(self, request):
        self.request = request

    """TODO: create second level of authentication?"""
    __acl__ = [
        (Allow, Authenticated, 'guardian'),
    ]


def check_credentials(request):
    """Return True if correct username and password, else False."""
    pass


def includeme(config):
    """Pyramid security configuration."""
    auth_secret = os.environ.get("AUTH_SECRET", "potato")
    authn_policy = AuthTktAuthenticationPolicy(
        secret=auth_secret,
        hashalg="sha512"
    )
    authz_policy = ACLAuthorizationPolicy()
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(authz_policy)
    config.set_root_factory(NewRoot)
    # Session stuff for CSRF Protection
    session_secret = os.environ.get("SESSION_SECRET", "itsaseekrit")
    session_factory = SignedCookieSessionFactory(session_secret)
    config.set_session_factory(session_factory)
    config.set_default_csrf_options(require_csrf=True)
