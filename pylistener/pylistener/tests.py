# """A short testing suite for the expense tracker."""


# import pytest
# import transaction

# from pyramid import testing

# from pylistener.models import Expense, get_tm_session
# from pylistener.models.meta import Base


# @pytest.fixture(scope="session")
# def configuration(request):
#     """Set up a Configurator instance.

#     This Configurator instance sets up a pointer to the location of the
#         database.
#     It also includes the models from your app's model package.
#     Finally it tears everything down, including the in-memory SQLite database.

#     This configuration will persist for the entire duration of your PyTest run.
#     """
#     settings = {
#         'sqlalchemy.url': 'postgres:///test_expenses'}
#     config = testing.setUp(settings=settings)
#     config.include('pylistener.models')
#     config.include('pylistener.routes')

#     def teardown():
#         testing.tearDown()

#     request.addfinalizer(teardown)
#     return config


# @pytest.fixture
# def db_session(configuration, request):
#     """Create a session for interacting with the test database.

#     This uses the dbsession_factory on the configurator instance to create a
#     new database session. It binds that session to the available engine
#     and returns a new session for every call of the dummy_request object.
#     """
#     SessionFactory = configuration.registry['dbsession_factory']
#     session = SessionFactory()
#     engine = session.bind
#     Base.metadata.create_all(engine)

#     def teardown():
#         session.transaction.rollback()
#         Base.metadata.drop_all(engine)

#     request.addfinalizer(teardown)
#     return session


# @pytest.fixture
# def dummy_request(db_session):
#     """Instantiate a fake HTTP Request, complete with a database session.

#     This is a function-level fixture, so every new request will have a
#     new database session.
#     """
#     return testing.DummyRequest(dbsession=db_session)


# @pytest.fixture
# def add_models(dummy_request):
#     """Add a bunch of model instances to the database.

#     Every test that includes this fixture will add new random expenses.
#     """
#     dummy_request.dbsession.add_all(EXPENSES)


# @pytest.fixture
# def set_auth_credentials():
#     """Make a username/password combo for testing."""
#     import os
#     from passlib.apps import custom_app_context as pwd_context

#     os.environ["AUTH_USERNAME"] = "testme"
#     os.environ["AUTH_PASSWORD"] = pwd_context.hash("foobar")


# # ======== UNIT TESTS ==========

# def test_new_expenses_are_added(db_session):
#     """New expenses get added to the database."""
#     db_session.add_all(EXPENSES)
#     query = db_session.query(Expense).all()
#     assert len(query) == len(EXPENSES)


# def test_list_view_returns_empty_when_empty(dummy_request):
#     """Test that the list view returns no objects in the expenses iterable."""
#     from .views.default import list_view
#     result = list_view(dummy_request)
#     assert len(result["expenses"]) == 0


# def test_list_view_returns_objects_when_exist(dummy_request, add_models):
#     """Test that the list view does return objects when the DB is populated."""
#     from .views.default import list_view
#     result = list_view(dummy_request)
#     assert len(result["expenses"]) == 100


# def test_list_view_with_categories(dummy_request, add_models):
#     """Test that the list view does return objects when the DB is populated."""
#     from .views.default import list_view

#     dummy_request.method = "POST"
#     dummy_request.POST["category"] = "utilities"
#     result = list_view(dummy_request)
#     assert "utilities" in result.location


# def test_detail_view_contains_individual_expense_details(db_session, dummy_request, add_models):
#     """Test that the detail view actually returns individual expense info."""
#     from .views.default import detail_view
#     dummy_request.matchdict["id"] = 12
#     expense = db_session.query(Expense).get(12)
#     result = detail_view(dummy_request)
#     assert result["expense"] == expense


# def test_create_view_get_request_is_normal(dummy_request):
#     """The create view should return an empty dict."""
#     from .views.default import create_view
#     result = create_view(dummy_request)
#     assert result == {}


# def test_create_view_post_request_adds_new_db_item(db_session, dummy_request):
#     """Posting to the create view adds an item."""
#     from .views.default import create_view

#     dummy_request.method = "POST"
#     dummy_request.POST["item"] = "test item"
#     dummy_request.POST["amount"] = "1234.56"
#     dummy_request.POST["paid_to"] = "test recipient"
#     dummy_request.POST["category"] = "rent"
#     dummy_request.POST["description"] = "test description"
#     create_view(dummy_request)
#     new_expense = db_session.query(Expense).first()
#     latest = new_expense
#     assert latest.item == "test item"


# def test_create_view_post_request_adds_new_db_items(db_session, dummy_request):
#     """Posting to the create view twice adds another new item."""
#     from .views.default import create_view

#     dummy_request.method = "POST"
#     dummy_request.POST["item"] = "test item"
#     dummy_request.POST["amount"] = "1234.56"
#     dummy_request.POST["paid_to"] = "test recipient"
#     dummy_request.POST["category"] = "rent"
#     dummy_request.POST["description"] = "test description"
#     create_view(dummy_request)

#     dummy_request.method = "POST"
#     dummy_request.POST["item"] = "test item2"
#     dummy_request.POST["amount"] = "834.00"
#     dummy_request.POST["paid_to"] = "test recipient2"
#     dummy_request.POST["category"] = "food"
#     dummy_request.POST["description"] = "test description2"
#     create_view(dummy_request)

#     new_expenses = db_session.query(Expense).all()
#     latest = new_expenses[-1]
#     assert latest.item == "test item2"


# def test_edit_view_returns_expense_info(db_session, dummy_request, add_models):
#     """GET request to the edit view contains expense item info."""
#     from .views.default import edit_view
#     dummy_request.matchdict["id"] = 2
#     result = edit_view(dummy_request)
#     expense = db_session.query(Expense).get(2)
#     assert result["data"]["item"] == expense.item


# def test_edit_view_edits_expense_info(db_session, dummy_request, add_models):
#     """POST request to the edit view edits expense item info."""
#     from .views.default import edit_view
#     dummy_request.matchdict["id"] = 2
#     dummy_request.POST["item"] = "test item"
#     dummy_request.POST["amount"] = "1234.56"
#     dummy_request.POST["paid_to"] = "test recipient"
#     dummy_request.POST["category"] = "rent"
#     dummy_request.POST["description"] = "test description"
#     edit_view(dummy_request)
#     expense = db_session.query(Expense).get(2)
#     assert expense.item == "test item"


# def test_edit_view_redirects_after_edit(dummy_request, add_models):
#     """POST request redirects."""
#     from .views.default import edit_view
#     from pyramid.httpexceptions import HTTPFound
#     dummy_request.matchdict["id"] = 2
#     dummy_request.POST["item"] = "test item"
#     dummy_request.POST["amount"] = "1234.56"
#     dummy_request.POST["paid_to"] = "test recipient"
#     dummy_request.POST["category"] = "rent"
#     dummy_request.POST["description"] = "test description"
#     result = edit_view(dummy_request)
#     assert isinstance(result, HTTPFound)


# def test_category_view_shows_only_one_category(db_session, dummy_request, add_models):
#     """GET request only shows one category."""
#     from .views.default import category_view
#     dummy_request.matchdict["cat"] = "utilities"
#     result = category_view(dummy_request)
#     query = db_session.query(Expense).filter(Expense.category == "utilities")
#     expenses = query.all()
#     assert result["expenses"] == expenses


# def test_category_view_with_new_category(dummy_request, add_models):
#     """Test that the list view does return objects when the DB is populated."""
#     from .views.default import category_view
#     from pyramid.httpexceptions import HTTPFound
#     dummy_request.method = "POST"
#     dummy_request.matchdict["cat"] = "rent"
#     dummy_request.POST["category"] = "utilities"
#     result = category_view(dummy_request)
#     assert isinstance(result, HTTPFound)


# def test_login_view_get_request(dummy_request):
#     """Test that you can see the login view."""
#     from .views.default import login_view
#     result = login_view(dummy_request)
#     assert result == {}


# def test_login_view_good_credentials(dummy_request, set_auth_credentials):
#     """Test that when given good credentials login can be successful."""
#     from .views.default import login_view
#     from pyramid.httpexceptions import HTTPFound
#     dummy_request.POST["username"] = "testme"
#     dummy_request.POST["password"] = "foobar"
#     result = login_view(dummy_request)
#     assert isinstance(result, HTTPFound)


# def test_login_view_bad_credentials(dummy_request, set_auth_credentials):
#     """Test that when given bad credentials login doesn't happen."""
#     from .views.default import login_view
#     dummy_request.POST["username"] = "testme"
#     dummy_request.POST["password"] = "badpass"
#     result = login_view(dummy_request)
#     assert result == {}


# def test_logout_view_redirects(dummy_request):
#     """When logging out you get redirected to the home page."""
#     from .views.default import logout_view
#     from pyramid.httpexceptions import HTTPFound
#     result = logout_view(dummy_request)
#     assert isinstance(result, HTTPFound)


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
