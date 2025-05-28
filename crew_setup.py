from crewai import Agent, Task, Crew
from pydantic import BaseModel, Field
from typing import List
import yaml


# Define file paths for YAML configurations
files = {
    'agents': 'config/agents.yaml',
    'tasks': 'config/tasks.yaml',
}

# Load configurations from YAML files
configs = {}
for config_type, file_path in files.items():
    with open(file_path, 'r') as file:
        configs[config_type] = yaml.safe_load(file)

# Assign loaded configurations to specific variables
agents_config = configs['agents']
tasks_config = configs['tasks']



class SQLQuery(BaseModel):
    sqlquery: str = Field(..., description="The raw sql query for the user input")

class ReviewedSQLQuery(BaseModel):
    reviewed_sqlquery: str = Field(..., description="The reviewed sql query for the raw sql query")

class ComplianceReport(BaseModel):
    report: str = Field(..., description="A markdown-formatted compliance report with a verdict and any flagged issues.")



# Creating Agents
query_generator_agent = Agent(
  config=agents_config['query_generator_agent']
)

query_reviewer_agent = Agent(
  config=agents_config['query_reviewer_agent']
)

compliance_checker_agent = Agent(
  config=agents_config['compliance_checker_agent']
)

# Creating Tasks
query_task = Task(
  config=tasks_config['query_task'],
  agent=query_generator_agent,
  output_pydantic=SQLQuery
)

review_task = Task(
  config=tasks_config['review_task'],
  agent=query_reviewer_agent,
  output_pydantic=ReviewedSQLQuery
)

compliance_task = Task(
  config=tasks_config['compliance_task'],
  agent=compliance_checker_agent,
  context=[review_task],
  output_pydantic=ComplianceReport
)

# Creating Crew objects for import
sql_generator_crew = Crew(
    agents=[query_generator_agent],
    tasks=[query_task],
    verbose=True
)

sql_reviewer_crew = Crew(
    agents=[query_reviewer_agent],
    tasks=[review_task],
    verbose=True
)

sql_compliance_crew = Crew(
    agents=[compliance_checker_agent],
    tasks=[compliance_task],
    verbose=True
)