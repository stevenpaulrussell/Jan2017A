import os

# Following is generally True, and makes both Heroku and local testing safe.  But override this for specific needs
LOCAL_CONNECT = True if os.environ['DATAQUEDA_LOCAL_HOME_DIR'] else False


TABLE_MASTER_KEY = 'Build_files/master.xls'
VIEWS_KEY = 'Queries/sql_views.xls'
QUERIES_KEY = 'Queries/sql_queries.xls'

FILE_NOTES_KEY = 'Build_files/file_annotations.xls'
IMPORTS_KEY_PREFIX = 'Imports/'
TABLE_NAME_SEPARATOR = '_from_'


# Put the names, hosts, etc that are used for connecting to AWS and to databases here.
# Note that the secrets should be stored in environment variables, not here!

S3ACCESS = 'AKIAJ6LHTEGDGW4HAO2A'
S3REGION = 'us-west-2'
S3SECRET = os.environ['S3SECRET_tdd_dataqueda']
AWS_BUCKET = 'tdd-dataqueda'

DATAQUEDA_DATABASE = 'd1cipri3jdtha0'
DATAQUEDA_USER = 'cbetlnyahiyqzy'
DATAQUEDA_PASSWORD = os.environ['DATAQUEDA_tdd_PASSWORD']
DATAQUEDA_HOST = 'ec2-54-83-52-71.compute-1.amazonaws.com'
DATAQUEDA_URL = 'postgres://cbetlnyahiyqzy:QkjU5eC3K0YfmP1sUzTCAOVaNw@ec2-54-83-52-71.compute-1.amazonaws.com:5432/d1cipri3jdtha0'

LOCAL_DATABASENAME = 'tdd_dataqueda'


#
#  Utility definitions
#


class DBFormatException(Exception):
    """Base class for errors and not-implemented items in this database handler"""

