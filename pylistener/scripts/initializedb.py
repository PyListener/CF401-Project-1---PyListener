import os
import sys
import transaction
import json

from pyramid.paster import (
    get_appsettings,
    setup_logging,
    )

from pyramid.scripts.common import parse_vars

from pylistener.models.meta import Base
from pylistener.models import (
    get_engine,
    get_session_factory,
    get_tm_session,
    )
from pylistener.models import User, AddressBook, Attribute, Category, UserAttributeLink
from passlib.apps import custom_app_context as pwd_context


def usage(argv):
    cmd = os.path.basename(argv[0])
    print('usage: %s <config_uri> [var=value]\n'
          '(example: "%s development.ini")' % (cmd, cmd))
    sys.exit(1)


def main(argv=sys.argv):
    if len(argv) < 2:
        usage(argv)
    config_uri = argv[1]
    options = parse_vars(argv[2:])
    setup_logging(config_uri)
    settings = get_appsettings(config_uri, options=options)
    settings["sqlalchemy.url"] = os.environ["DATABASE_URL"]
    engine = get_engine(settings)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session_factory = get_session_factory(engine)

    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, 'data.json')) as data:
        json_data = data.read()
        j_data = json.loads(json_data)

    with open(os.path.join(here, 'contacts.json')) as contacts:
        test_contacts = contacts.read()
        j_test_contacts = json.loads(test_contacts)

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        test_user = User(username="testted", password=pwd_context.hash("password"))
        test_user2 = User(username="Nurse Jackie", password=pwd_context.hash("password1234"))
        dbsession.add(test_user)
        dbsession.add(test_user2)

        u_id = dbsession.query(User).first().id
        u_id2 = dbsession.query(User).filter(User.username == "Nurse Jackie").id
        for i in range(3):
            add_row = AddressBook(
                name=j_test_contacts[i]["name"],
                phone=j_test_contacts[i]["phone"],
                email=j_test_contacts[i]["email"],
                user=u_id,
                picture=get_picture_binary(os.path.join(here, j_test_contacts[i]["picture"]))
            )
            add_row2 = AddressBook(
                name=j_test_contacts[i + 3]["name"],
                phone=j_test_contacts[i + 3]["phone"],
                email=j_test_contacts[i + 3]["email"],
                user=u_id2,
                picture=get_picture_binary(os.path.join(here, j_test_contacts[i + 3]["picture"]))
            )
            dbsession.add(add_row)
            dbsession.add(add_row2)

        for category in j_data:
            cat_row = Category(
                label=category["label"],
                desc=category["desc"],
                picture=get_picture_binary(os.path.join(here, category["picture"]))
            )
            dbsession.add(cat_row)
            cat_id_query = dbsession.query(Category)
            cat_id = cat_id_query.filter(Category.label == category["label"]).first()
            for attribute in category["attributes"]:
                attr_row = Attribute(
                    label=attribute["label"],
                    desc=attribute["desc"],
                    cat_id=int(cat_id.id),
                    picture=get_picture_binary(os.path.join(here, attribute["picture"]))
                )
                dbsession.add(attr_row)

                attr_id = dbsession.query(Attribute).filter(Attribute.label == attribute["label"]).first().id

                link_row = UserAttributeLink(
                    user_id=u_id,
                    attr_id=attr_id
                )
                link_row2 = UserAttributeLink(
                    user_id=u_id2,
                    attr_id=attr_id
                )
                dbsession.add(link_row)
                dbsession.add(link_row2)


def get_picture_binary(path):
    """Open an image to save binary data."""
    with open(path, "rb") as pic_data:
        return pic_data.read()

