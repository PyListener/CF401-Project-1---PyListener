from __future__ import unicode_literals

from pyramid.response import Response
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.httpexceptions import exception_response


from pylistener.security import check_credentials
from passlib.apps import custom_app_context as pwd_context
from pyramid.security import remember, forget

from pylistener.models import\
    User, AddressBook, Category, Attribute, UserAttributeLink

from pylistener.scripts.initializedb import\
    create_att_object, create_user_att_link_object, get_picture_binary

from twilio.rest import TwilioRestClient

import os
import sys
import shutil
import yagmail
import mimetypes
import json


HERE = os.path.dirname(os.path.realpath(__file__))


@view_config(route_name='home', renderer='../templates/home.jinja2')
def home_view(request):
    """Handle the home route."""
    if request.authenticated_userid:
        user = request.authenticated_userid
        contacts = request.dbsession.query(AddressBook).join(User.address_rel)\
            .filter(User.username == user).all()
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


@view_config(route_name='logout')
def logout_view(request):
    """Handle the logout route."""
    auth_head = forget(request)
    return HTTPFound(location=request.route_url("home"), headers=auth_head)


@view_config(
    route_name='manage',
    renderer='../templates/manage.jinja2',
    permission="manage")
def manage_view(request):
    """Manage user uploads."""
    if request.POST:
        try:
            if request.POST['contact']:
                handle_new_contact(request)
            return HTTPFound(location=request.route_url(
                'manage', id=request.matchdict["id"]))
        except KeyError:
            try:
                if request.POST['category']:
                    handle_new_category(request)
                return HTTPFound(location=request.route_url(
                    'manage', id=request.matchdict["id"]))
            except KeyError:
                if request.POST['attribute']:
                    handle_new_attribute(request)
                return HTTPFound(location=request.route_url(
                    'manage', id=request.matchdict["id"]))

    user = request.dbsession.query(User).filter(User.username == request.authenticated_userid)\
        .first().id
    categories = request.dbsession.query(Category).all()
    joined = request.dbsession.query(Attribute.id, Attribute.label, Attribute.picture, UserAttributeLink.user_id) \
        .join(UserAttributeLink, UserAttributeLink.attr_id == Attribute.id)
    attributes = joined.filter(UserAttributeLink.user_id == user).all()
    contacts = request.dbsession.query(AddressBook).filter(AddressBook.user == user)
    return {"categories": categories, "attributes": set(attributes), "contacts": contacts}


@view_config(route_name='register', renderer='../templates/register.jinja2')
def register_view(request):
    """Handle the register route."""
    if request.POST:
        input_file = request.POST['contact_img'].file
        input_type = mimetypes.guess_type(request.POST['contact_img'].filename)[0]
        if input_type[:5] != 'image':
            message = "Please try again with an image file."
            request.session.flash(message)
            return {}
        else:
            username = request.POST["contact_name"]
            password = request.POST["password"]
            sub_user = request.POST["sub_user"]
            new_user = User(
                username=username,
                password=pwd_context.hash(password),
                sub_user=sub_user
            )
        request.dbsession.add(new_user)
        add_new_contact(request, input_file, input_type, username)
        initialize_new_user(username, request)
        auth_head = remember(request, username)
        return HTTPFound(
            location=request.route_url('manage', id=new_user.username),
            headers=auth_head)
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
            user = request.dbsession.query(User)\
                .filter(User.username == request.authenticated_userid).first().id

            joined = request.dbsession.query(Attribute.id, Attribute.label, Attribute.picture, Attribute.cat_id, UserAttributeLink.priority, UserAttributeLink.user_id) \
                .join(UserAttributeLink, UserAttributeLink.attr_id == Attribute.id)

            attributes = joined.filter(UserAttributeLink.user_id == user)\
                .filter(Attribute.cat_id == request.matchdict["cat_id"])\
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

    string = "{0}, {1} {2}".format(contact.name, category.desc, attribute.desc)

    if request.POST:
        try:
            if request.POST['email']:
                send_email(contact, content)
                return HTTPFound(location=request.route_url('home'))
        except KeyError:
            if request.POST['sms']:
                send_sms(contact, content)
                return HTTPFound(location=request.route_url('home'))
    return {"content": string}


@view_config(route_name='picture')
def picture_handler(request):
    """Serve pictures from database binaries."""
    if request.matchdict["db_id"] == "add":
        picture_data = request.dbsession.query(AddressBook).get(request.matchdict['pic_id'])
    elif request.matchdict["db_id"] == "cat":
        picture_data = request.dbsession.query(Category).get(request.matchdict['pic_id'])
    elif request.matchdict["db_id"] == "att":
        picture_data = request.dbsession.query(Attribute).get(request.matchdict['pic_id'])

    mime_type = picture_data.pic_mime
    if sys.version_info[0] < 3:
        mime_type = mime_type.encode('utf-8')

    return Response(content_type=mime_type, body=picture_data.picture)


@view_config(route_name='delete')
def delete_handler(request):
    """Handle deleting contacts and attributes from manage page."""
    user = request.authenticated_userid
    if request.text == "add":
        address = request.dbsession.query(AddressBook).get(request.matchdict["id"])
        request.dbsession.delete(address)
    elif request.text == "att":
        att_id = request.matchdict["id"]
        user_id = request.dbsession.query(User).filter(User.username == user).first().id
        attribute = request.dbsession.query(UserAttributeLink) \
            .filter(UserAttributeLink.user_id == user_id) \
            .filter(UserAttributeLink.attr_id == att_id).first()
        request.dbsession.delete(attribute)

    return HTTPFound(request.route_url("manage", id=user))


# -------  Helper functions ------- #

def send_email(contact, content):
    """Send email via yagmail SMTP api."""
    yag = yagmail.SMTP(os.environ['EMAIL'], os.environ['PASSWORD'])
    print(contact.email)
    yag.send(contact.email, 'An email from Pylistener', content)


def send_sms(contact, content):
    """Send sms via twilio api."""
    account_sid = os.environ["TWILIO_SID"]
    auth_token = os.environ["TWILIO_TOKEN"]
    twilio_number = os.environ["TWILIO_NUMBER"]
    client = TwilioRestClient(account_sid, auth_token)
    client.messages.create(
        to='+1' + contact.phone,
        from_=twilio_number,
        body=content
    )


def handle_new_contact(request):
    """Handler function for a new contact in manage view."""
    input_file = request.POST['contact_img'].file
    input_type = mimetypes.guess_type(request.POST['contact_img'].filename)[0]
    if input_type[:5] == 'image':
        user_id = request.matchdict["id"]
        add_new_contact(request, input_file, input_type, user_id)
        message = "New Contact Added."
        request.session.flash(message)
    else:
        message = "Please try again with an image file."
        request.session.flash(message)


def add_new_contact(request, input_file, input_type, username):
    """Add new contact to DB."""
    name = request.POST["contact_name"]
    phone = request.POST["contact_phone"]
    email = request.POST["contact_email"]
    user = username
    user_id = request.dbsession.query(User).filter(User.username == user).first()
    picture = handle_new_picture(name, input_file)
    new_contact = AddressBook(
        name=name,
        phone=phone,
        email=email,
        picture=picture,
        pic_mime=input_type,
        user=user_id.id)
    request.dbsession.add(new_contact)


def handle_new_category(request):
    """Handler function for new category in manage view."""
    input_file = request.POST['cat_img'].file
    input_type = mimetypes.guess_type(request.POST['cat_img'].filename)[0]
    if input_type[:5] == 'image':
        add_new_category(request, input_file, input_type)
        message = "New Category Added. Don't forget Attributes!"
        request.session.flash(message)
    else:
        message = "Please try again with an image file."
        request.session.flash(message)


def add_new_category(request, input_file, input_type):
    """Add new category to DB."""
    label = request.POST["cat_label"]
    cat_desc = request.POST["cat_desc"]
    picture = handle_new_picture(label, input_file)
    new_cat = Category(
        label=label,
        desc=cat_desc,
        picture=picture,
        pic_mime=input_type
    )
    request.dbsession.add(new_cat)


def handle_new_attribute(request):
    """Handler function for a new attribute in manage view."""
    input_file = request.POST['attr_img'].file
    input_type = mimetypes.guess_type(request.POST['attr_img'].filename)[0]
    if input_type[:5] == 'image':
        handle_new_attribute(request, input_file, input_type)
        message = "New Attribute Added."
        request.session.flash(message)
    else:
        message = "Please try again with an image file."
        request.session.flash(message)


def add_new_attribute(request, input_file, input_type):
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
        pic_mime=input_type,
        cat_id=category_id.id,
    )
    request.dbsession.add(new_attr)
    user_id = request.dbsession.query(User).filter_by(username=request.authenticated_userid).first().id
    attr_id = attr_id = request.dbsession.query(Attribute).filter_by(label=label).first().id
    new_attr_link = UserAttributeLink(
        user_id=user_id,
        attr_id=attr_id
    )
    request.dbsession.add(new_attr_link)


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


def initialize_new_user(username, request):
    """Initialize attribute set for new user."""
    u_id = request.dbsession.query(User)\
        .filter(User.username == username).first().id

    with open(os.path.join(HERE, '../scripts/data.json')) as data:
        json_data = data.read()
        j_data = json.loads(json_data)

    for cat in j_data:
        cat_id_query = request.dbsession.query(Category)
        cat_id = cat_id_query.filter(Category.label == cat["label"]).first()
        for attribute in cat["attributes"]:
            attr_row = create_att_object(
                attribute["label"],
                attribute["desc"],
                get_picture_binary(os.path.join(HERE, "../scripts/" + attribute["picture"])),
                attribute["pic_mime"],
                cat_id.id
            )
            request.dbsession.add(attr_row)
            attr_id = request.dbsession.query(Attribute).filter(Attribute.label == attribute["label"]).first().id

            link_row = create_user_att_link_object(u_id, attr_id)
            request.dbsession.add(link_row)
