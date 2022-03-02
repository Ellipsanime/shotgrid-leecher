#!/usr/bin/env python
# coding: utf-8

# In[56]:


get_ipython().system('pip install pymongo matplotlib')


# In[57]:


import pandas as pd
from pymongo import MongoClient


# In[58]:


mongo = MongoClient("mongodb://127.0.0.1:27017")


# In[59]:


def _get_avalon_frame(col: str) -> pd.DataFrame:
    df = pd.DataFrame(list(mongo.avalon.get_collection(col).find({})))
    return df

def _get_shotgrid_frame(col: str) -> pd.DataFrame:
    df = pd.DataFrame(list(mongo.shotgrid_openpype.get_collection(col).find({})))
    return df

def _get_logs(project: str) -> pd.DataFrame:
    df = pd.DataFrame(list(mongo.shotgrid_schedule.get_collection("logs").find({})))
    return df[(df.project_name == project) & (df.batch_result == "Ok")]


# #### SMURFS

# In[60]:


_DB = "SMURFS"
df = _get_shotgrid_frame(_DB)
df[df.type != 'Task'].groupby("type").count().plot.pie(y='_id', figsize=(5, 5))


# In[61]:


df.groupby("type").count().sort_values(by='_id')['_id']


# In[62]:


_get_avalon_frame(_DB).groupby("type").count().sort_values(by='_id')['_id']


# In[63]:


(_get_logs(_DB).duration).describe()


# In[64]:


pd.Series({'find': 150.8882656097412, 'find_one': 0.18116521835327148})


# #### Badgers_and_Foxes_S02_DEV

# In[65]:


_DB = "Badgers_and_Foxes_S02_DEV"
df = _get_shotgrid_frame(_DB)
df[df.type != 'Task'].groupby("type").count().plot.pie(y='_id', figsize=(5, 5))


# In[66]:


df.groupby("type").count().sort_values(by='_id')['_id']


# In[67]:


_get_avalon_frame(_DB).groupby("type").count().sort_values(by='_id')['_id']


# In[68]:


(_get_logs(_DB).duration).describe()


# In[69]:


pd.Series({'find': 4.987752199172974, 'find_one': 0.17355012893676758})


# #### MARSUPILAMI_RND

# In[70]:


_DB = "MARSUPILAMI_RND"
df = _get_shotgrid_frame(_DB)
df[df.type != 'Task'].groupby("type").count().plot.pie(y='_id', figsize=(5, 5))


# In[71]:


df.groupby("type").count().sort_values(by='_id')['_id']


# In[72]:


_get_avalon_frame(_DB).groupby("type").count().sort_values(by='_id')['_id']


# In[73]:


(_get_logs(_DB).duration).describe()


# In[74]:


pd.Series({'find': 2.2503437995910645, 'find_one': 0.19319820404052734})


# #### Common

# ##### Shotgrid calls

# In[75]:


pd.Series({'find': 7, 'find_one': 1})

