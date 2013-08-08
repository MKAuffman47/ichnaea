import os

from unittest2 import TestCase
from webtest import TestApp

from ichnaea import main
from ichnaea.db import _Model
from ichnaea.db import Database

TRAVIS = bool(os.environ.get('TRAVIS', 'false') == 'true')

SQLURI = 'sqlite://'
UNIX_SOCKET = None


def _make_db(create=True, echo=False):
    return Database(SQLURI, unix_socket=UNIX_SOCKET, create=create, echo=echo)


def _make_app():
    wsgiapp = main({}, database=SQLURI, unix_socket=UNIX_SOCKET)
    return TestApp(wsgiapp)


class DBIsolation(object):

    def cleanup(self, db):
        engine = db.engine
        conn = engine.connect()
        trans = conn.begin()
        _Model.metadata.drop_all(engine)
        trans.commit()


class AppTestCase(TestCase, DBIsolation):

    def setUp(self):
        self.app = _make_app()
        self.db = self.app.app.registry.database
        self.db_session = self.db.session()

    def tearDown(self):
        self.db_session.close()
        self.cleanup(self.db)
        del self.db_session
        del self.db
        del self.app


class DBTestCase(TestCase, DBIsolation):

    def setUp(self):
        self.db = _make_db()
        self.db_session = self.db.session()

    def tearDown(self):
        self.db_session.close()
        self.cleanup(self.db)
        del self.db_session
        del self.db
