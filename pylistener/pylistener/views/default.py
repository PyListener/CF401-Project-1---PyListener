from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound


from pylistener.security import check_credentials
from pyramid.security import remember, forget
from pylistener.models import User, AddressBook, Categories, Attributes



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
    if request.POST:
        query = request.dbsession.query(User)
        username = request.POST["username"]
        password = request.POST["password"]
        real_password = None
        for user in query.all():
            if user.username == username:
                real_password = user.hashed_password
                break
        if real_password:
            if check_credentials(password, real_password):
                auth_head = remember(request, username)
            return HTTPFound(
                location=request.route_url("home"),
                headers=auth_head
            )

    return {}


@view_config(route_name='logout', permission="manage")
def logout_view(request):
    '''Handle the logout route.'''
    auth_head = forget(request)
    return HTTPFound(location=request.route_url("home"), headers=auth_head)


@view_config(route_name='manage', renderer='../templates/manage.jinja2')
def manage_view(request):
    '''Handle the manage route.'''
    pass


@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    '''Handle the register route.'''
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        new_user = User(
            username=username,
            hashed_password=password.pwd_context.hash(password),
            email=email
        )
        request.dbsession.add(new_user)
        return HTTPFound(location=request.route_url('manage', id=new_user.username))
    return {}


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
