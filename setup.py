
from setuptools import setup, find_packages


requires = [
    'pyramid',
    'pyramid_jinja2',
    'pyramid_debugtoolbar',
    'pyramid_tm',
    'SQLAlchemy',
    'transaction',
    'zope.sqlalchemy',
    'waitress',
    'psycopg2',
    'passlib',
    'yagmail',
    'keyring',
    'requests'
]

tests_require = [
    'WebTest >= 1.3.1',  # py3 compat
    'pytest',  # includes virtualenv
    'pytest-cov',
]

setup(name='pylistener',
      version='0.0',
      description='''A simple tool designed to enable people with Apraxia
        to communicate.''',
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Pyramid",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Maelle Vance, Rick Valenzuela, Ted Callahan',
      author_email='',
      url='https://pylistener.herokuapp.com',
      keywords='web wsgi bfg pylons pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      extras_require={
          'testing': tests_require,
      },
      install_requires=requires,
      entry_points="""\
      [paste.app_factory]
      main = pylistener:main
      [console_scripts]
      initialize_db = pylistener.scripts.initializedb:main
      """,
      )
