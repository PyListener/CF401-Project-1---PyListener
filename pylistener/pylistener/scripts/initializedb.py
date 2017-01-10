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
from pylistener.models import User, AddressBook, Attribute, Category


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

    with transaction.manager:
        dbsession = get_tm_session(session_factory, transaction.manager)

        print(j_data)

