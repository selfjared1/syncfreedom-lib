Syncfreedom-lib
=================

This is the public repository for users of 
SyncFreedom.com to simplify their development. 
The point of this project is to help you 
develop accounting utilities using the same 
python-quickbooks library that's used in typical 
web development.  That library is well documented 
but is inaccessible to the layman without first 
creating a UI to collect auth codes.  SyncFreedom 
handles the authorization aspect of the development
allowing you to focus on your utility. 

My goal in creating this service is to make python 
more accessible to accountants.  I encourage accountants 
to use and adopt python as THE general purpose programing 
language for accountants. 

The main difference between your development with 
the python-quickbooks package and this package is 
the QuickBooks class.  Anytime you would normally 
use the QuickBooks class from the python-quickbooks 
package you would replace it with SyncFreedomQuickBooks 
class.  The SyncFreedomQuickBooks is also different 
because it takes the company_id (realm_id) and your 
SyncFreedom credentials as arguments.

For example:

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
    customers = Customer.all(qb=qb)

It is best practice to place your credentials in a 
config.ini file.  Here is an example of the text 
in config.ini file:

    [SYNCFREEDOM_CREDENTIALS]
    username = your_syncfreedom_username
    password = your_syncfreedom_password
    
    [ENVIRONMENT_INFO]
    environment=Production
    sync_freedom_url=https://syncfreedom.com


When your credentials are inside of the config.ini file 
you will access the credentials and use this package like 
the following:

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
    customers = Customer.all(qb=qb)
