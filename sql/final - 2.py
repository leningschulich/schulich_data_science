#!/usr/bin/env python
# coding: utf-8

# In[22]:


resource_id = '8a89caa9-511c-4568-af89-7f2174b4378c'
limit = 1500
offset = 0
api_url = 'https://data.ontario.ca/api/3/action/datastore_search?resource_id={}&limit={}&offset={}'.format(resource_id,limit,offset)

print(api_url)


# In[23]:


import pandas as pd
import sqlalchemy as sa
import requests #necessary to get request from API
from sqlalchemy import Column


# In[24]:


api_response = requests.get(api_url)


# In[25]:


api_response


# In[26]:


data = api_response.json()
# Parse the JSON response into a Python data structure
data


# In[27]:


data['result']['records']


# In[28]:


Research_cases = pd.DataFrame(data['result']['records'])
Research_cases


# In[29]:


Research_cases['report_date'] = pd.to_datetime(Research_cases['report_date'])
Research_cases['total_individuals_at_least_one'] = pd.to_numeric(Research_cases['total_individuals_partially_vaccinated'])
Research_cases['total_individuals_partially_vaccinated'] = pd.to_numeric(Research_cases['total_individuals_partially_vaccinated'])
Research_cases['total_individuals_fully_vaccinated'] = pd.to_numeric(Research_cases['total_individuals_fully_vaccinated'])
Research_cases['total_individuals_3doses'] = pd.to_numeric(Research_cases['total_individuals_3doses'])


# In[31]:


Research_cases['new_doses_unvaccinated'] = Research_cases['total_doses_administered'] - Research_cases['total_individuals_at_least_one']
Research_cases['new_doses_one_vaccine'] = Research_cases['total_individuals_at_least_one'] - Research_cases['total_individuals_fully_vaccinated'] 
Research_cases['new_doses_two_vaccines'] = Research_cases['total_individuals_fully_vaccinated'] - Research_cases['total_individuals_3doses']
Research_cases['new_doses_three_vaccines'] = Research_cases['total_individuals_3doses']
Research_cases['new_doses_unvaccinated'].fillna(0,inplace = True)
Research_cases['new_doses_one_vaccine'].fillna(0,inplace = True)
Research_cases['new_doses_two_vaccines'].fillna(0,inplace = True)
Research_cases['new_doses_three_vaccines'].fillna(0,inplace = True)
Research_cases['new_doses'] = Research_cases['total_doses_administered'].diff(1)


# In[32]:


relevant_columns = ['report_date','new_doses','new_doses_unvaccinated','new_doses_one_vaccine','new_doses_two_vaccines','new_doses_three_vaccines']


# In[33]:


Research_cases


# In[34]:


Research_cases[relevant_columns]


# In[35]:


clean_copy_df = Research_cases[relevant_columns]


# In[36]:


clean_copy_df


# In[37]:


db_secret = {
    'drivername' :'postgresql+psycopg2',
    'host' :'mmai5100postgres.canadacentral.cloudapp.azure.com',
    'port' :'5432',
    'username' :'lening',
    'password' :'2023!Schulich',
    'database' :'lening_db' #my own data server
}


# In[38]:


db_connection_url = sa.engine.URL.create(
    drivername = db_secret['drivername'],
    username   = db_secret['username'],
    password   = db_secret['password'],
    host       = db_secret['host'],
    port       = db_secret['port'],
    database   = db_secret['database'] 
)


# In[39]:


#create an engine
engine = sa.create_engine(db_connection_url)
with engine.connect() as connection:
    connection.execute('CREATE SCHEMA IF NOT EXISTS final_exam')
clean_copy_df.to_sql(
   name = 'covid',
   schema = 'final_exam',
    con= engine,
    if_exists = 'replace',
    index=False,
    method='multi',
    dtype= {
        'report_date' : sa.types.DATE,
        'new_doses' : sa.types.DECIMAL(10,0),
        'new_doses_unvaccinated': sa.types.DECIMAL(10,0),
        'new_doses_one_vaccine': sa.types.DECIMAL(10,0),
        'new_doses_two_vaccines': sa.types.DECIMAL(10,0),
        'new_doses_three_vaccines': sa.types.DECIMAL(10,0)
    }
)


# In[ ]:




