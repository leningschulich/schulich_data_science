#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import sqlalchemy as sa


# In[2]:


db_secret = {
    'drivername' :'postgresql+psycopg2',
    'host' :'mmai5100postgres.canadacentral.cloudapp.azure.com',
    'port' :'5432',
    'username' :'lening',
    'password' :'2023!Schulich',
    'database' :'mban_db'
}


# In[3]:


db_connection_url = sa.engine.URL.create(
    drivername = db_secret['drivername'],
    username   = db_secret['username'],
    password   = db_secret['password'],
    host       = db_secret['host'],
    port       = db_secret['port'],
    database   = db_secret['database'] 
)


# In[4]:


print(db_connection_url)


# In[5]:


#create an engine
engine = sa.create_engine(db_connection_url)


# In[6]:


# Read Data Using Pandas
with engine.connect() as connection:
    data = pd.read_sql(sql='SELECT * FROM dimensions.date_dimension;', con=connection)


# In[7]:


data


# In[8]:


db_secret = {
    'drivername' :'postgresql+psycopg2',
    'host' :'mmai5100postgres.canadacentral.cloudapp.azure.com',
    'port' :'5432',
    'username' :'lening',
    'password' :'2023!Schulich',
    'database' :'lening_db' #my own data server
}


# In[9]:


db_connection_url = sa.engine.URL.create(
    drivername = db_secret['drivername'],
    username   = db_secret['username'],
    password   = db_secret['password'],
    host       = db_secret['host'],
    port       = db_secret['port'],
    database   = db_secret['database'] 
)


# In[10]:


#create an engine
engine = sa.create_engine(db_connection_url)


# In[11]:


with engine.connect() as connection:
    connection.execute('CREATE SCHEMA IF NOT EXISTS final_exam')


# In[17]:


data.to_sql(
   name = 'date_dimension',
   schema = 'final_exam',
    con= engine,
    if_exists = 'replace',
    index=False,
    method='multi',
    dtype= {
        'sk_date' : sa.types.Integer,
        'date' : sa.types.String,
        'day_name': sa.types.String,
        'day_of_month': sa.types.DECIMAL(10,0),
        'day_of_year': sa.types.DECIMAL(10,0),
        'month': sa.types.DECIMAL(10,0),
        'month_name': sa.types.String,
        'year': sa.types.DECIMAL(10,0),
        'year_week' : sa.types.String,
        'week': sa.types.String,
        'running_week': sa.types.DECIMAL(10,0),
        'year_quarter' : sa.types.String,
        'quarter' : sa.types.String,
        'running_quarter': sa.types.DECIMAL(10,0)
    }
)


# In[ ]:




