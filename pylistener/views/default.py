from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from pyramid.httpexceptions import HTTPFound


from pylistener.security import check_credentials
from passlib.apps import custom_app_context as pwd_context
from pyramid.security import remember, forget
from pylistener.models import User, AddressBook, Category, Attribute

import os
import shutil


HERE = os.path.dirname(os.path.realpath(__file__))


@view_config(route_name='home', renderer='../templates/home.jinja2')
def home_view(request):
    if request.authenticated_userid:
        user = request.authenticated_userid
        contacts = request.dbsession.query(AddressBook).join(User.address_rel).filter(User.username == user).all()
        return {"contacts": contacts}
    return {}


@view_config(route_name='login', renderer='../templates/login.jinja2')
def login_view(request):
    """Authenticate the user."""
    if request.POST:
        query = request.dbsession.query(User)
        username = request.POST["username"]
        password = request.POST["password"]
        user = query.filter(User.username == username).first()
        real_password = user.password
        if check_credentials(password, real_password):
            auth_head = remember(request, username)
            return HTTPFound(
                location=request.route_url("manage", id=username),
                headers=auth_head
            )
    return {}


@view_config(route_name='logout', permission="manage")
def logout_view(request):
    """Handle the logout route."""
    auth_head = forget(request)
    return HTTPFound(location=request.route_url("home"), headers=auth_head)


@view_config(route_name='manage', renderer='../templates/manage.jinja2')
def manage_view(request):
    """Manage user uploads."""
    if request.POST:
        if request.POST['contact']:
            name = request.POST["contact_name"]
            phone = request.POST["contact_phone"]
            email = request.POST["contact_phone"]
            input_file = request.POST['contact_picture'].file
            temp_file_path = '/'.join([HERE, name])
            temp_file_path += '~'
            input_file.seek(0)
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)
            with open(temp_file_path, 'rb') as f:
                blob = f.read()
                picture = blob
            os.remove(temp_file_path)
            user = request.matchdict["id"]
            user_id = request.dbsession.query(User).filter(User.username == user).first()

            new_contact = AddressBook(
                name=name,
                phone=phone,
                email=email,
                picture=picture,
                user=user_id.id)
            request.dbsession.add(new_contact)

        elif request.POST['category']:
            label = request.POST["cat_label"]
            cat_desc = request.POST["cat_desc"]
            input_file = request.POST['contact_picture'].file
            temp_file_path = '/'.join([HERE, name])
            temp_file_path += '~'
            input_file.seek(0)
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)
            with open(temp_file_path, 'rb') as f:
                blob = f.read()
                picture = blob
            os.remove(temp_file_path)
            new_cat = Category(
                label=label,
                desc=cat_desc,
                picture=picture
            )
            request.dbsession.add(new_cat)
        elif request.POST['attribute']:
            label = request.POST["attr_label"]
            desc = request.POST["attr_descr"]
            category = request.POST["attr_cat"]
            input_file = request.POST['contact_picture'].file
            temp_file_path = '/'.join([HERE, name])
            temp_file_path += '~'
            input_file.seek(0)
            with open(temp_file_path, 'wb') as output_file:
                shutil.copyfileobj(input_file, output_file)
            with open(temp_file_path, 'rb') as f:
                blob = f.read()
                picture = blob
            os.remove(temp_file_path)
            category_query = request.dbsession.query(Category)
            category_id = category_query.filter(category.label == category).first()
            new_attr = Attribute(
                label=label,
                desc=desc,
                picture=picture,
                cat_id=category_id.id,
            )
            request.dbsession.add(new_attr)
    query = request.dbsession.query(Category)
    categories = query.all()
    return {"categories": categories}


@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    """Handle the register route."""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        new_user = User(
            username=username,
            password=pwd_context.hash(password),
        )
        request.dbsession.add(new_user)
        return HTTPFound(location=request.route_url('manage', id=new_user.username))
    return {}


@view_config(route_name='category', renderer='../templates/main.jinja2')
def categories_view(request):
    """Handle the categories route."""
    pass


@view_config(route_name='attribute', renderer='../templates/main.jinja2')
def attributes_view(request):
    """Handle the attributes route."""
    pass


@view_config(route_name='display', renderer='../templates/display.jinja2')
def display_view(request):
    """Handle the display route."""
    pass


@view_config(route_name='picture')
def picture_handler(request):
    """Serve pictures from database binaries."""
    if request.matchdict["db_id"] == "add":
        picture_data = request.dbsession.query(AddressBook).get(request.matchdict['pic_id']).picture
    return Response(content_type="image/jpg", body=picture_data)




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