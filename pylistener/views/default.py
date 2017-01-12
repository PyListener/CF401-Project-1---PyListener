from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import exception_response


from pylistener.security import check_credentials
from passlib.apps import custom_app_context as pwd_context
from pyramid.security import remember, forget

from pylistener.models import User, AddressBook, Category, Attribute, UserAttributeLink
from pylistener.scripts.pytextbelt import Textbelt

import os
import shutil
import yagmail
import mimetypes


HERE = os.path.dirname(os.path.realpath(__file__))


@view_config(route_name='home', renderer='../templates/home.jinja2')
def home_view(request):
    """Handle the home route."""
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
        if user:
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
        try:
            if request.POST['contact']:
                input_file = request.POST['contact_img'].file
                input_type = mimetypes.guess_type(request.POST['contact_img'].filename)[0]
                if input_type[:5] == 'image':
                    handle_new_contact(request, input_file)
                    message = "New Contact Added."
                    request.session.flash(message)
                else:
                    message = "Please try again with an image file."
                    request.session.flash(message)
            return {}
        except KeyError:
            try:
                if request.POST['category']:
                    input_file = request.POST['cat_img'].file
                    input_type = mimetypes.guess_type(request.POST['cat_img'].filename)[0]
                if input_type[:5] == 'image':
                    handle_new_category(request, input_file)
                    message = "New Category Added. Don't forget Attributes!"
                    request.session.flash(message)
                else:
                    message = "Please try again with an image file."
                    request.session.flash(message)
                return {}
            except KeyError:
                if request.POST['attribute']:
                    input_file = request.POST['att_img'].file
                    input_type = mimetypes.guess_type(request.POST['attr_img'].filename)[0]
                if input_type[:5] == 'image':
                    handle_new_attribute(request, input_file)
                    message = "New Attribute Added."
                    request.session.flash(message)
                else:
                    message = "Please try again with an image file."
                    request.session.flash(message)
                return {}
    query = request.dbsession.query(Category)
    categories = query.all()
    return {"categories": categories}


@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    """Handle the register route."""
    if request.POST:
        username = request.POST["username"]
        password = request.POST["password"]
        sub_user = request.POST["sub_user"]
        new_user = User(
            username=username,
            password=pwd_context.hash(password),
            sub_user=sub_user
        )
        request.dbsession.add(new_user)
        return HTTPFound(location=request.route_url('manage', id=new_user.username))
    return {}


@view_config(
    route_name='category',
    renderer='../templates/categories.jinja2',
    permission="manage"
)
def categories_view(request):
    """Handle the categories route."""
    if request.authenticated_userid:
            categories = request.dbsession.query(Category).all()
            return {"categories": categories, "addr_id": request.matchdict["add_id"]}


@view_config(
    route_name='attribute',
    renderer='../templates/attributes.jinja2',
    permission="manage")
def attributes_view(request):
    """Handle the attributes route."""
    try:
        if request.authenticated_userid:
            attributes = request.dbsession.query(User.username, Attribute.id, Attribute.label, Attribute.desc, Attribute.picture, Attribute.cat_id, UserAttributeLink.priority) \
                .join(UserAttributeLink.attr_rel) \
                .filter(User.username == request.authenticated_userid) \
                .filter(Attribute.cat_id == request.matchdict["cat_id"]) \
                .order_by(UserAttributeLink.priority).all()
            return {"attributes": set(attributes), "addr_id": request.matchdict["add_id"], "category_id": request.matchdict["cat_id"]}
    except AttributeError:
        raise exception_response(403)


@view_config(
    route_name='display',
    renderer='../templates/display.jinja2',
    permission="manage")
def display_view(request):
    """Handle the display route."""
    user = request.dbsession.query(User).filter(User.username == request.authenticated_userid).first()
    contact_id = request.matchdict["add_id"]
    contact = request.dbsession.query(AddressBook).filter(AddressBook.id == contact_id).first()
    cat_id = request.matchdict["cat_id"]
    category = request.dbsession.query(Category).filter(Category.id == cat_id).first()
    att_id = request.matchdict["att_id"]
    attribute = request.dbsession.query(Attribute).filter(Attribute.id == att_id).first()
    content = "{0}, you have received a message from {1}. \n\t \"{2} {3}\"" \
        .format(contact.name, user.sub_user, category.desc, attribute.desc)
    if request.POST:
        try:
            if request.POST['email']:
                yag = yagmail.SMTP(os.environ['EMAIL'], os.environ['PASSWORD'])
                print(contact.email)
                yag.send("maellevance@gmail.com", 'An email from Pylistener', content)
                return HTTPFound(location=request.route_url('home'))
        except KeyError:
            if request.POST['sms']:
                Recipient = Textbelt.Recipient('2066817287', "us")
                print(contact.phone)
                Recipient.send(content)
                return HTTPFound(location=request.route_url('home'))
    return {"content": content}


@view_config(route_name='picture')
def picture_handler(request):
    """Serve pictures from database binaries."""
    if request.matchdict["db_id"] == "add":
        picture_data = request.dbsession.query(AddressBook).get(request.matchdict['pic_id'])
    elif request.matchdict["db_id"] == "cat":
        picture_data = request.dbsession.query(Category).get(request.matchdict['pic_id'])
    elif request.matchdict["db_id"] == "att":
        picture_data = request.dbsession.query(Attribute).get(request.matchdict['pic_id'])
    return Response(content_type=picture_data.pic_mime, body=picture_data.picture)


def handle_new_contact(request, input_file):
    """Add new contact to DB."""
    name = request.POST["contact_name"]
    phone = request.POST["contact_phone"]
    email = request.POST["contact_phone"]
    user = request.matchdict["id"]
    user_id = request.dbsession.query(User).filter(User.username == user).first()
    picture = handle_new_picture(name, input_file)
    new_contact = AddressBook(
        name=name,
        phone=phone,
        email=email,
        picture=picture,
        user=user_id.id)
    request.dbsession.add(new_contact)


def handle_new_category(request, input_file):
    """Add new category to DB."""
    label = request.POST["cat_label"]
    cat_desc = request.POST["cat_desc"]
    picture = handle_new_picture(label, input_file)
    new_cat = Category(
        label=label,
        desc=cat_desc,
        picture=picture
    )
    request.dbsession.add(new_cat)


def handle_new_attribute(request, input_file):
    """Add new attribute to DB."""
    label = request.POST["attr_label"]
    desc = request.POST["attr_desc"]
    category = request.POST["attr_cat"]
    input_file = request.POST['attr_img'].file
    picture = handle_new_picture(label, input_file)
    category_query = request.dbsession.query(Category)
    category_id = category_query.filter(Category.label == category).first()
    new_attr = Attribute(
        label=label,
        desc=desc,
        picture=picture,
        cat_id=category_id.id,
    )
    request.dbsession.add(new_attr)


def handle_new_picture(name, input_file):
    """Handle the picture upload and return a BLOB."""
    temp_file_path = '/'.join([HERE, name])
    temp_file_path += '~'
    input_file.seek(0)
    with open(temp_file_path, 'wb') as output_file:
        shutil.copyfileobj(input_file, output_file)
    with open(temp_file_path, 'rb') as f:
        blob = f.read()
        picture = blob
    os.remove(temp_file_path)
    return picture
