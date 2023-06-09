# %% [markdown]
# #### Skill Ontology Creation
# 

# %% [markdown]
# ##### This is a use case which is coming up as a part of the HR use case scenarios
# ##### 1. For resume filtering based on the job description 
# ##### 2. Talent management and upskilling

# %%
import openai
import os
import requests
import os
import openai
openai.api_type = "azure"
openai.api_base = "https://{}.openai.azure.com/"
openai.api_version = "2023-05-15"
openai.api_key = " "


# %%
user_input = input("Enter your prompt: ")
#eg format for entering user input - skill name: JavaScript, domain : IT and skill area : Programming
# %%
response = openai.ChatCompletion.create(
  engine="gpt-4",
  messages = [{"role":"system","content":"Create a skills ontology for the \"skill name\",\"domain\" and \"skill area\" provided by the user in the format \n{\"name\": \"\", \"domain\": \"\", \"skill_area\": \"\", \"job_roles\": [], \"certifications\": [], \"tools\": [], \"related_skills\": []}\nThe number of roles, certifications, tools and related skills can vary, and can be a maximum of 10 each\n"},{"role":"user","content":f"{user_input}"}],
  temperature=0.5,
  max_tokens=800,
  top_p=0.95,
  frequency_penalty=0,
  presence_penalty=0,
  stop=None)



# %%
from pprint import pprint
pprint(response.choices[0].message['content'])

# %% [markdown]
# ### Examples of different skill, skill area and domain

# %%
#skill name: JavaScript, domain : IT and skill area : Programming
#skill name : Business Intelligence, domain : IT and skill area : AI
#skill name : Computer Aided Test Tool, domain : IT and skill area : Design skills
#skill name : DX Studio, domain : IT and skill area : Gaming 
#skill name : Adobe Photoshop, domain : IT and skill area : Design skills
#skill_name: Fund Administration, Domain: BFSI and skill area: Mutual Funds
#skill_name: Fund Accounting, Domain: BFSI and skill area: Mutual Funds
#skill_name: Fund Management, Domain: BFSI and skill area: Mutual Funds
#skill_name: Insurance Rating System, Domain: BFSI and skill area: Insurance


