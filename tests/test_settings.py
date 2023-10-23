INSTALLED_APPS = [  
    'django.contrib.contenttypes',  
    'django.contrib.auth',  
    'tests',  
]  
  
DATABASES = {  
    'default': {  
        'ENGINE': 'django.db.backends.sqlite3',  
        'NAME': ':memory:',  
    }  
}  
  
SECRET_KEY = 'testkey'  

USE_TZ = True
