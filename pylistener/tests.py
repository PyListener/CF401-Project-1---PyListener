"""Test for Pylistener."""


import pytest
import transaction

from pyramid import testing

from pylistener.models import User, AddressBook, Category, Attribute, UserAttributeLink, get_tm_session
from pylistener.models.meta import Base
from passlib.apps import custom_app_context as pwd_context



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
        'sqlalchemy.url': 'postgres://maellevance:password@localhost:5432/test_pylistener'}
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
    """New user get added to the database."""
    new_user = User(username="test", password="test")
    db_session.add(new_user)
    query = db_session.query(User).all()
    assert len(query) == 1


def test_new_user_username(db_session):
    """New user has correct data."""
    new_user = User(username="test", password="test")
    db_session.add(new_user)
    user = db_session.query(User).filter(User.id == 1).first()
    assert user.username == "test"


def test_new_contact_is_added(db_session):
    """New contact gets added to correct table."""
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
    result = register_view(dummy_request)
    assert isinstance(result, HTTPFound)


def test_manage_view(dummy_request):
    """Test that you can see the manage view."""
    from .views.default import manage_view
    result = manage_view(dummy_request)
    assert result == {'categories': []}


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
    cat_object = create_cat_object("a", "b", "c")
    assert isinstance(cat_object, Category)


def test_create_att_object():
    """Test create_att_object returns an Attribute model."""
    from .scripts.initializedb import create_att_object
    att_object = create_att_object("a", "b", "c", "d")
    assert isinstance(att_object, Attribute)


def test_create_user_object():
    """Test create_user_object returns a User model."""
    from .scripts.initializedb import create_user_object
    user_object = create_user_object("test", "test")
    assert isinstance(user_object, User)


def test_create_address_object():
    """Test create_address_object returns an AddressBook model."""
    from .scripts.initializedb import create_address_object
    address_object = create_address_object("a", "b", "c", "d", "e")
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


# # Tests security # #








# def test_delete_view_removes_an_item(db_session, dummy_request, add_models):
#     """Delete view removes an item."""
#     from .views.default import delete_view
#     expense = db_session.query(Expense).get(2)
#     dummy_request.matchdict["id"] = expense.id
#     delete_view(dummy_request)
#     assert expense not in db_session.query(Expense).all()


# def test_delete_view_redirects(dummy_request, add_models):
#     """When logging out you get redirected to the home page."""
#     from .views.default import delete_view
#     from pyramid.httpexceptions import HTTPFound
#     dummy_request.matchdict["id"] = 2
#     result = delete_view(dummy_request)
#     assert isinstance(result, HTTPFound)


# def test_api_list_contains_list_of_dicts(dummy_request, add_models):
#     """When using the list view for the API, get back dictionaries."""
#     from .views.default import api_list_view
#     result = api_list_view(dummy_request)
#     assert isinstance(result[0], dict)


# def test_api_list_contains_all_expenses(dummy_request, add_models):
#     """When using the list view for the API, get back dictionaries."""
#     from .views.default import api_list_view
#     result = api_list_view(dummy_request)
#     expense_dicts = [expense.to_json() for expense in EXPENSES]
#     for item in expense_dicts:
#         assert item in result

# # ======== FUNCTIONAL TESTS ===========


# @pytest.fixture(scope="session")
# def testapp(request):
#     """Create an instance of webtests TestApp for testing routes.

#     With the alchemy scaffold we need to add to our test application the
#     setting for a database to be used for the models.
#     We have to then set up the database by starting a database session.
#     Finally we have to create all of the necessary tables that our app
#     normally uses to function.

#     The scope of the fixture is function-level, so every test will get a new
#     test application.
#     """
#     from webtest import TestApp
#     from expense_tracker import main

#     app = main({}, **{"sqlalchemy.url": 'postgres:///test_expenses'})
#     testapp = TestApp(app)

#     SessionFactory = app.registry["dbsession_factory"]
#     engine = SessionFactory().bind
#     Base.metadata.create_all(bind=engine)

#     def tearDown():
#         Base.metadata.drop_all(bind=engine)

#     request.addfinalizer(tearDown)

#     return testapp


# @pytest.fixture(scope="session")
# def fill_the_db(testapp):
#     """Fill the database with some model instances and return the session.

#     Start a database session with the transaction manager and add all of the
#     expenses. This will be done anew for every test.
#     """

#     SessionFactory = testapp.app.registry["dbsession_factory"]
#     with transaction.manager:
#         dbsession = get_tm_session(SessionFactory, transaction.manager)
#         dbsession.add_all(new_expenses)

#     return dbsession


# @pytest.fixture
# def new_session(testapp):
#     """Return a session for inspecting the database."""
#     SessionFactory = testapp.app.registry["dbsession_factory"]
#     with transaction.manager:
#         dbsession = get_tm_session(SessionFactory, transaction.manager)
#     return dbsession


# def test_home_route_has_table(testapp):
#     """The home page has a table in the html."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("table")) == 1


# def test_home_route_has_table2(testapp):
#     """Without data the home page only has the header row in its table."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 1


# def test_detail_route_is_not_found(testapp):
#     """Without data there's no detail page."""
#     response = testapp.get('/expense/4', status=404)
#     assert response.status_code == 404

# # ========= WITH DATA IN THE DB ========


# def test_home_route_with_data_has_filled_table(testapp, fill_the_db):
#     """When there's data in the database, the home page has some rows."""
#     response = testapp.get('/', status=200)
#     html = response.html
#     assert len(html.find_all("tr")) == 101


# def test_login_route_can_be_seen(testapp):
#     """Can send a GET request to the login route and see three input fields."""
#     response = testapp.get("/login", status=200)
#     html = response.html
#     assert len(html.find_all("input")) == 3


# def test_detail_route_has_details(testapp, new_session):
#     """Can send a GET request to a detail route and see item info."""
#     response = testapp.get("/expense/4")
#     expense = new_session.query(Expense).get(4)
#     assert expense.item in response.text

# # ======== TESTING WITH SECURITY ==========


# def test_create_route_is_forbidden(testapp):
#     """Any old user trying to create a new expense sees the forbidden view."""
#     response = testapp.get("/new-expense")
#     assert "can't do that" in response.text


# def test_edit_route_is_forbidden(testapp):
#     """Any old user trying to create a new expense sees the forbidden view."""
#     response = testapp.get("/expense/4/edit")
#     assert "can't do that" in response.text


# def test_delete_route_is_forbidden(testapp):
#     """Any old user trying to delete an expense sees the forbidden view."""
#     response = testapp.get("/delete/4")
#     assert "can't do that" in response.text


# def test_login_with_bad_credentials(set_auth_credentials, testapp):
#     """Bad credentials remain unauthenticated."""
#     response = testapp.post("/login", params={
#         "username": "testme",
#         "password": "bad password"
#     })
#     response = testapp.get("/new-expense")
#     assert "can't do that" in response.text


# def test_login_with_no_credentials(set_auth_credentials, testapp):
#     """No credential login remains unauthenticated."""
#     response = testapp.post("/login", params={
#         "username": "",
#         "password": ""
#     })
#     response = testapp.get("/new-expense")
#     assert "can't do that" in response.text

# # ======== TESTING WITH SECURITY | APP IS AUTHENTICATED ==========


# def test_auth_app_can_see_create_route(set_auth_credentials, testapp):
#     """A logged-in user should be able to access the create view."""
#     response = testapp.post("/login", params={
#         "username": "testme",
#         "password": "foobar"
#     })
#     response = testapp.get("/new-expense")
#     assert response.status_code == 200


# def test_auth_app_can_create_expense(testapp):
#     """A logged-in user can post a new expense."""
#     response = testapp.get("/new-expense")
#     token = response.html.find("input", {"type": "hidden"}).attrs["value"]
#     testapp.post("/new-expense", params={
#         "csrf_token": token,
#         "item": "another item",
#         "amount": "2743.88",
#         "paid_to": "another person",
#         "category": "another thing",
#         "description": "another item"
#     })
#     response = testapp.get("/")
#     assert "another item" in response.text


# def test_auth_app_can_edit_expense(testapp):
#     """A logged-in user can edit an existing expense."""
#     response = testapp.get("/expense/4/edit")
#     token = response.html.find("input", {"type": "hidden"}).attrs["value"]
#     testapp.post("/expense/4/edit", params={
#         "csrf_token": token,
#         "item": "an edited expense",
#         "amount": "0.00",
#         "paid_to": "no one",
#         "category": "who cares",
#         "description": "it was edited"
#     })
#     response = testapp.get("/expense/4")
#     assert "an edited expense" in response.text


# def test_auth_app_can_delete_expense(testapp):
#     """A logged-in user can delete an existing expense."""
#     response = testapp.get("/delete/4")
#     response = testapp.get('/expense/4', status=404)
#     assert response.status_code == 404


# def test_logged_out_user_can_no_longer_create(testapp):
#     """A user that has logged out can't create expenses."""
#     testapp.get("/logout")
#     response = testapp.get("/new-expense")
#     assert "can't do that" in response.text
