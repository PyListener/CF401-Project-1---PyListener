"""Tests for Pylistener."""


import pytest
import transaction

from pyramid import testing

from pylistener.models import User, AddressBook, Category, Attribute, UserAttributeLink, get_tm_session
from pylistener.models.meta import Base
from passlib.apps import custom_app_context as pwd_context

TEST_DB = 'postgres://hotsauce@localhost:5432/test_pylistener'


@pytest.fixture(scope="session")
def configuration(request):
    """Set up a Configurator instance.

    This Configurator instance sets up a pointer to the location of the
        database.
    It also includes the models from your app's model package.
    Finally it tears everything down, including the in-memory SQLite database.

    This configuration will persist for the entire duration of your PyTest run.
    """
    settings = {
        'sqlalchemy.url': TEST_DB}
    config = testing.setUp(settings=settings)
    config.include('pylistener.models')
    config.include('pylistener.routes')

    def teardown():
        testing.tearDown()

    request.addfinalizer(teardown)
    return config


@pytest.fixture
def db_session(configuration, request):
    """Create a session for interacting with the test database.

    This uses the dbsession_factory on the configurator instance to create a
    new database session. It binds that session to the available engine
    and returns a new session for every call of the dummy_request object.
    """
    SessionFactory = configuration.registry['dbsession_factory']
    session = SessionFactory()
    engine = session.bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    def teardown():
        session.transaction.rollback()
        Base.metadata.drop_all(engine)

    request.addfinalizer(teardown)
    return session


@pytest.fixture
def dummy_request(db_session):
    """Instantiate a fake HTTP Request, complete with a database session.

    This is a function-level fixture, so every new request will have a
    new database session.
    """
    return testing.DummyRequest(dbsession=db_session)


@pytest.fixture
def test_user(db_session):
    """Instantiate a test user account."""
    new_user = User(username="test", password=pwd_context.hash("test"))
    db_session.add(new_user)


# # ======== UNIT TESTS ==========
def test_user_table_empty(db_session):
    """Test user table is initially empty."""
    query = db_session.query(User).all()
    assert not len(query)


def test_addresses_table_empty(db_session):
    """Test addresses table is initially empty."""
    query = db_session.query(AddressBook).all()
    assert not len(query)


def test_category_table_empty(db_session):
    """Test category table is initially empty."""
    query = db_session.query(Category).all()
    assert not len(query)


def test_attribute_table_empty(db_session):
    """Test attribute table is initially empty."""
    query = db_session.query(AddressBook).all()
    assert not len(query)


def test_new_user_is_added(db_session):
    """Test new user gets added to the database."""
    new_user = User(username="test", password="test")
    db_session.add(new_user)
    query = db_session.query(User).all()
    assert len(query) == 1


def test_new_user_username(db_session):
    """Test new user has correct data."""
    new_user = User(username="test", password="test")
    db_session.add(new_user)
    user = db_session.query(User).filter(User.id == 1).first()
    assert user.username == "test"


def test_new_contact_is_added(db_session):
    """Test new contact gets added to correct table."""
    new_contact = AddressBook(
        name="test_name",
        phone="test_phone",
        email="test_email"
    )
    db_session.add(new_contact)
    query = db_session.query(AddressBook).all()
    assert len(query) == 1


def test_new_contact_data(db_session):
    """Test new contact has correct data."""
    new_contact = AddressBook(
        name="test_name",
        phone="test_phone",
        email="test_email"
    )
    db_session.add(new_contact)
    contact = db_session.query(AddressBook).all()
    assert contact[0].name == "test_name"
    assert contact[0].phone == "test_phone"
    assert contact[0].email == "test_email"


def test_new_category_is_added(db_session):
    """Test new category is added to database."""
    new_cat = Category(
        label="test_label",
        desc="test_desc"
    )
    db_session.add(new_cat)
    query = db_session.query(Category).all()
    assert len(query) == 1


def test_new_category_data(db_session):
    """Test new category has correct data."""
    new_cat = Category(
        label="test_label",
        desc="test_desc"
    )
    db_session.add(new_cat)
    category = db_session.query(Category).all()
    assert category[0].label == "test_label"
    assert category[0].desc == "test_desc"


def test_new_attribute_is_added(db_session):
    """Test new attribute is added to database."""
    new_att = Attribute(
        label="test_label",
        desc="test_desc"
    )
    db_session.add(new_att)
    query = db_session.query(Attribute).all()
    assert len(query) == 1


def test_new_attribute_data(db_session):
    """Test new attribute has correct data."""
    new_att = Attribute(
        label="test_label",
        desc="test_desc"
    )
    db_session.add(new_att)
    att = db_session.query(Attribute).all()
    assert att[0].label == "test_label"
    assert att[0].desc == "test_desc"


def test_login_view_bad_credentials(dummy_request):
    """Test that when given bad credentials login doesn't happen."""
    from .views.default import login_view
    dummy_request.POST["username"] = "testme"
    dummy_request.POST["password"] = "badpassword"
    result = login_view(dummy_request)
    assert result == {}


def test_login_view_get_request(dummy_request):
    """Test that you can see the login view."""
    from .views.default import login_view
    result = login_view(dummy_request)
    assert result == {}


def test_login_view_good_credentials(dummy_request, test_user):
    """Test that when given good credentials login can be successful."""
    from .views.default import login_view
    from pyramid.httpexceptions import HTTPFound
    dummy_request.POST["username"] = "test"
    dummy_request.POST["password"] = "test"
    result = login_view(dummy_request)
    assert isinstance(result, HTTPFound)


def test_logout_view_redirects(dummy_request):
    """When logging out you get redirected to the home page."""
    from .views.default import logout_view
    from pyramid.httpexceptions import HTTPFound
    result = logout_view(dummy_request)
    assert isinstance(result, HTTPFound)


def test_register_view(dummy_request):
    """Test that you can see the register view."""
    from .views.default import register_view
    result = register_view(dummy_request)
    assert result == {}


def test_register_view_redirects(dummy_request):
    """Test that when you register you are redirected."""
    from .views.default import register_view
    from pyramid.httpexceptions import HTTPFound
    dummy_request.POST["username"] = "test"
    dummy_request.POST["password"] = "test"
    dummy_request.POST["sub_user"] = "test"
    result = register_view(dummy_request)
    assert isinstance(result, HTTPFound)


def test_not_found_view(dummy_request):
    """Test not found view."""
    from .views.notfound import notfound_view
    result = notfound_view(dummy_request)
    assert result == {}


def test_home_view(dummy_request):
    """Test home view."""
    from .views.default import home_view
    result = home_view(dummy_request)
    assert result == {}


def test_categories_view():
    """Test category view."""
    from .views.default import categories_view
    with pytest.raises(Exception):
        categories_view(dummy_request)


def test_attributes_view():
    """Test attributes view."""
    from .views.default import attributes_view
    with pytest.raises(Exception):
        attributes_view(dummy_request)


# # Unit test for initialize_db  # #
def test_create_cat_object():
    """Test create_cat_object returns a Category model."""
    from .scripts.initializedb import create_cat_object
    cat_object = create_cat_object("a", "b", "c", "c")
    assert isinstance(cat_object, Category)


def test_create_att_object():
    """Test create_att_object returns an Attribute model."""
    from .scripts.initializedb import create_att_object
    att_object = create_att_object("a", "b", "c", "d", "c")
    assert isinstance(att_object, Attribute)


def test_create_user_object():
    """Test create_user_object returns a User model."""
    from .scripts.initializedb import create_user_object
    user_object = create_user_object("test", "test", "test")
    assert isinstance(user_object, User)


def test_create_address_object():
    """Test create_address_object returns an AddressBook model."""
    from .scripts.initializedb import create_address_object
    address_object = create_address_object("a", "b", "c", "d", "e", "f")
    assert isinstance(address_object, AddressBook)


def test_create_user_att_link_object():
    """Test create_user_att_link_object returns a UserAttributeLink model."""
    from .scripts.initializedb import create_user_att_link_object
    user_att_link_object = create_user_att_link_object("user", "attribute")
    assert isinstance(user_att_link_object, UserAttributeLink)


def test_get_picture_binary():
    """Test get_picture_binary returns a bytes class."""
    from .scripts.initializedb import get_picture_binary
    import os
    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, 'scripts/img_questions/how.jpg')
    rb = get_picture_binary(path)
    assert isinstance(rb, bytes)


def test_handle_new_picture():
    """Test handle new picture function returns a bytes class."""
    import os
    from .views.default import handle_new_picture
    here = os.path.abspath(os.path.dirname(__file__))
    path = os.path.join(here, 'scripts/img_questions/how.jpg')
    with open(path, 'rb') as ouput_file:
        new_picture = handle_new_picture("name", ouput_file)
    assert isinstance(new_picture, bytes)


# # ======== FUNCTIONAL TESTS ===========


@pytest.fixture
def testapp(request):
    """Create an instance of webtests TestApp for testing routes.

    With the alchemy scaffold we need to add to our test application the
    setting for a database to be used for the models.
    We have to then set up the database by starting a database session.
    Finally we have to create all of the necessary tables that our app
    normally uses to function.

    The scope of the fixture is function-level, so every test will get a new
    test application.
    """
    from webtest import TestApp
    from pyramid.config import Configurator

    def main(global_config, **settings):
        config = Configurator(settings=settings)
        config.include('pyramid_jinja2')
        config.include('.models')
        config.include('.routes')
        config.include('.security')
        config.scan()
        return config.make_wsgi_app()

    app = main({}, **{'sqlalchemy.url': TEST_DB})
    testapp = TestApp(app)

    SessionFactory = app.registry["dbsession_factory"]
    engine = SessionFactory().bind
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(bind=engine)

    return testapp


@pytest.fixture
def new_user(testapp):
    """Add a new user to the database."""
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        new_user = User(username="test", password=pwd_context.hash("test"))
        dbsession.add(new_user)


@pytest.fixture
def login_fixture(testapp, new_user):
    """Test that logging redirects."""
    resp = testapp.post('/login', params={'username': 'test', 'password': 'test'})
    headers = resp.headers
    return headers


@pytest.fixture
def fill_the_db(testapp, new_user):
    """Fill the database with a contact, category and attribute."""
    from .scripts.initializedb import get_picture_binary
    import os
    here = here = os.path.abspath(os.path.dirname(__file__))
    SessionFactory = testapp.app.registry["dbsession_factory"]
    with transaction.manager:
        dbsession = get_tm_session(SessionFactory, transaction.manager)
        picture = get_picture_binary(os.path.join(here, "placeholder.jpg"))
        new_user = AddressBook(
            name="user name",
            phone="user phone",
            email="user email",
            picture=picture,
            pic_mime="image/jpeg",
            user=1
        )
        dbsession.add(new_user)
        new_category = Category(
            label="category label",
            desc="desc",
            picture=picture,
            pic_mime="image/jpeg"
        )
        dbsession.add(new_category)
        new_attribute = Attribute(
            label="attribute label",
            desc="description label",
            picture=picture,
            cat_id=1,
            pic_mime="image/jpeg"
        )
        dbsession.add(new_attribute)


def test_login_page_has_form(testapp):
    """Test that the login route brings up the login template."""
    html = testapp.get('/login').html
    assert len(html.find_all('input'))


def test_category_view_not_logged_in(testapp):
    """Test category route without logging in returns 403 error."""
    from webtest.app import AppError
    with pytest.raises(AppError, message="403 Forbidden"):
        testapp.get('/category/1')


def test_category_view_logged_in(testapp, fill_the_db, login_fixture):
    """Test category view when logged in is accessible."""
    response = testapp.get('/category/1', params=login_fixture)
    assert response.status_code == 200


def test_404_view(testapp):
    """Test a non-registered route will raise a 404."""
    from webtest.app import AppError
    with pytest.raises(AppError, message="404 Not Found"):
        testapp.get('/raise404')


def test_home_view_authenticated(testapp, login_fixture):
    """Test home view is accessible authenticated."""
    response = testapp.get('/', params=login_fixture)
    assert response.status_code == 200


def test_home_authenticated_has_contacts(testapp, fill_the_db, login_fixture):
    """Test home views renders contacts when authenticated."""
    response = testapp.get('/', params=login_fixture).html
    assert len(response.find_all("img")) == 1


def test_attribute_view_authenticated(testapp, fill_the_db, login_fixture):
    """Test attribute view with full db and authenticated user."""
    response = testapp.get('/attribute/1/1', params=login_fixture)
    assert response.status_code == 200


# def test_attribute_authenticated_has_attributes(testapp, login_fixture, fill_the_db):
#     """Test attribute view renders attributes when authenticated."""
#     response = testapp.get('/attribute/1/1', params=login_fixture)
#     assert len(response.html.find_all("img")) == 1


def test_display_view_authenticated(testapp, fill_the_db, login_fixture):
    """Test display view is accessible authenticated."""
    response = testapp.get("/display/1/1/1", params=login_fixture)
    assert response.status_code == 200


def test_display_authenticated_has_string(testapp, fill_the_db, login_fixture):
    """Test display view renders the string when authenticated."""
    response = testapp.get("/display/1/1/1", params=login_fixture)
    assert len(response.html.find_all('h1')) == 1
