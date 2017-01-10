from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from ..models import User, AddressBook, Categories, Attributes


@view_config(route_name='home', renderer='../templates/main.jinja2')
def home_view(request):
    try:
        query = request.dbsession.query(MyModel)
        one = query.filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(db_err_msg, content_type='text/plain', status=500)
    return {'one': one, 'project': 'pylistener'}


@view_config(route_name='login', renderer='../templates/login.jinja2')
def login_view(request):
    '''Handle the login route.'''
    pass


@view_config(route_name='logout')
def logout_view(request):
    '''Handle the logout route.'''
    pass


@view_config(route_name='manage', renderer='../templates/manage.jinja2')
def manage_view(request):
    '''Handle the manage route.'''
    pass


@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    '''Handle the register route.'''
    pass


@view_config(route_name='categories', renderer='../templates/main.jinja2')
def categories_view(request):
    '''Handle the categories route.'''
    pass


@view_config(route_name='attributes', renderer='../templates/main.jinja2')
def attributes_view(request):
    '''Handle the attributes route.'''
    pass


@view_config(route_name='display', renderer='../templates/display.jinja2')
def display_view(request):
    '''Handle the display route.'''
    pass


db_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_pylistener_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
