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

        test_user = create_user_object("testted", "password", "Tedley Lamar")
        test_user2 = create_user_object("Nurse Jackie", "password1234", "Charlie")
        dbsession.add(test_user)
        dbsession.add(test_user2)

        u_id = dbsession.query(User).first().id
        u_id2 = dbsession.query(User).filter(User.username == "Nurse Jackie").first().id
        for i in range(3):
            add_row = create_address_object(
                j_test_contacts[i]["name"],
                j_test_contacts[i]["phone"],
                j_test_contacts[i]["email"],
                u_id,
                get_picture_binary(os.path.join(here, j_test_contacts[i]["picture"])),
                j_test_contacts[i]["pic_mime"]
            )
            add_row2 = create_address_object(
                j_test_contacts[i + 3]["name"],
                j_test_contacts[i + 3]["phone"],
                j_test_contacts[i + 3]["email"],
                u_id2,
                get_picture_binary(os.path.join(here, j_test_contacts[i + 3]["picture"])),
                j_test_contacts[i]["pic_mime"]
            )
            dbsession.add(add_row)
            dbsession.add(add_row2)

        for category in j_data:
            cat_row = create_cat_object(
                category["label"],
                category["desc"],
                get_picture_binary(os.path.join(here, category["picture"])),
                j_data[i]["pic_mime"]
            )
            dbsession.add(cat_row)
            cat_id_query = dbsession.query(Category)
            cat_id = cat_id_query.filter(Category.label == category["label"]).first()
            for attribute in category["attributes"]:
                attr_row = create_att_object(
                    attribute["label"],
                    attribute["desc"],
                    get_picture_binary(os.path.join(here, attribute["picture"])),
                    j_data[i]["pic_mime"],
                    cat_id.id
                )
                dbsession.add(attr_row)
                attr_id = dbsession.query(Attribute).filter(Attribute.label == attribute["label"]).first().id

                link_row = create_user_att_link_object(u_id, attr_id)
                link_row2 = create_user_att_link_object(u_id2, attr_id)
                dbsession.add(link_row)
                dbsession.add(link_row2)


def get_picture_binary(path):
    """Open an image to save binary data."""
    with open(path, "rb") as pic_data:
        return pic_data.read()


def create_cat_object(lbl, des, pic, pic_mime):
    """Return a Category object with necessary information."""
    return Category(
        label=lbl,
        desc=des,
        picture=pic,
        pic_mime=pic_mime,
    )


def create_att_object(lbl, des, pic, pic_mime, c_id):
    """Return an Attribute object with given information."""
    return Attribute(
        label=lbl,
        desc=des,
        picture=pic,
        pic_mime=pic_mime,
        cat_id=c_id
    )


def create_user_object(uname, psswd,sub_u):
    """Return a User object with given information."""
    return User(
        username=uname,
        password=pwd_context.hash(psswd),
        sub_user=sub_u
    )


def create_address_object(nme, phn, eml, u, pic, pic_mime):
    """Return an AddressBook object with given information."""
    return AddressBook(
        name=nme,
        phone=phn,
        email=eml,
        user=u,
        picture=pic,
        pic_mime=pic_mime,
    )


def create_user_att_link_object(u, att):
    """Return a UserAttributeLink object with given information."""
    return UserAttributeLink(
        user_id=u,
        attr_id=att
    )
