# syncfreedom-lib
This is the public repository for users of <br/>
SyncFreedom.com to simplify their development. <br/>
The point of this project is to help you <br/>
develop accounting utilities using the same <br/>
python-quickbooks library that's used in typical <br/>
web development.  That library is well documented <br/>
but is inaccessible to the layman without first <br/>
creating a UI to collect auth codes.  SyncFreedom <br/>
handles the authorization aspect of the development<br/>
allowing you to focus on your utility. <br/>

My goal in creating this service is to make python <br/>
more accessible to accountants.  I encourage accountants <br/>
to use and adopt python as THE general purpose programing <br/>
language for accountants. 

The main difference between your development with <br/>
the python-quickbooks package and this package is <br/>
the QuickBooks class.  Anytime you would normally <br/>
use the QuickBooks class from the python-quickbooks <br/>
package you would replace it with SyncFreedomQuickBooks <br/>
class.  The SyncFreedomQuickBooks is also different <br/>
because it takes the company_id (realm_id) and your <br/>
SyncFreedom credentials as arguments.<br/>
<br/>
For example: <br/>
'
'
'
from syncfreedom.client import SyncFreedomQuickBooks
from quickbooks.objects.account import Account

credentials = {
    'username':'your_syncfreedom_username', 
    'password':'your_syncfreedom_password'
    }
qb = SyncFreedomQuickBooks(
    company_id=self.company_id, 
    credentials=credentials
    )
account = Account()
account.FullyQualifiedName = "test"
assert qb.isvalid_object_name(account.qbo_object_name)

'
'
'

It is best practice to place your credentials in a <br/>
config.ini file.  Here is an example of the text <br/>
in config.ini file:
'
'
'
[SYNCFREEDOM_CREDENTIALS]
username = your_syncfreedom_username
password = your_syncfreedom_password

[ENVIRONMENT_INFO]
environment=Production
sync_freedom_url=https://syncfreedom.com
'
'
'

When your credentials are inside of the config.ini file <br/>
you will access the credentials and use this package like <br/>
the following:<br/>
<br/>

'
'
'
from syncfreedom.client import SyncFreedomQuickBooks
from quickbooks.objects.account import Account
from configparser import ConfigParser

configur = ConfigParser()
configur.read(r"""C:\your_file_path_to_the_config_file\config.ini"""))

credentials = configur['SYNCFREEDOM_CREDENTIALS']

qb = SyncFreedomQuickBooks(
    company_id=self.company_id, 
    credentials=credentials
    )
account = Account()
account.FullyQualifiedName = "test"
assert qb.isvalid_object_name(account.qbo_object_name)

'
'
'