from crewai import Agent, Task, Crew
from utils.db_simulator import setup_sample_db, run_query
import os
import yaml
from dotenv import load_dotenv, find_dotenv
import crew_setup as cs
from crewai import Flow
from crewai.flow.flow import listen, start


# these expect to find a .env file at the directory above the lesson.                                                                                                                     # the format for that file is (without the comment)                                                                                                                                       #API_KEYNAME=AStringThatIsTheLongAPIKeyFromSomeService
def load_env():
    _ = load_dotenv(find_dotenv())

def get_openai_api_key():
    load_env()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    return openai_api_key

openai_api_key = get_openai_api_key()
os.environ["OPENAI_MODEL_NAME"] = 'gpt-3.5-turbo'

# Creating Crew
sql_generator_crew = Crew(
  agents=[cs.query_generator_agent],
  tasks=[cs.query_task],
  verbose=True
)

# Creating Crew
sql_reviewer_crew = Crew(
  agents=[cs.query_reviewer_agent],
  tasks=[cs.review_task],
  verbose=True
)

# Creating Crew
sql_compliance_crew = Crew(
  agents=[cs.compliance_checker_agent],
  tasks=[cs.compliance_task],
  verbose=True
)

if __name__ == "__main__":
    setup_sample_db()

    class SQLAssistantFlow(Flow):
        @start()
        def collect_prompt_user(self):
            user_prompt = "Show me the top 5 products by total revenue for April 2024"
            return user_prompt

        @listen(collect_prompt_user)
        def gen_raw_sql(self, user_prompt):
            output = sql_generator_crew.kickoff(inputs={"user_input": user_prompt})      
            print("Generated SQL:", output)
            # print("SQL Generator Output (dict):", output.__dict__)
            self.state["raw_sql"] = output.pydantic.sqlquery
            return output

        @listen(gen_raw_sql)
        def review_raw_sql(self, generate_sql):
            output2 = sql_reviewer_crew.kickoff(inputs={"sql_query": self.state["raw_sql"]})
            print("============ Review Results ============")
            print("Raw SQL:", self.state["raw_sql"])
            print("Reviewed SQL:", output2.pydantic.reviewed_sqlquery)
            self.state["reviewed_sql"] = output2.pydantic.reviewed_sqlquery
            return output2

        @listen(review_raw_sql)
        def compliance_check(self, reviewed_sql_output):
            output3 = sql_compliance_crew.kickoff(inputs={"reviewed_sqlquery": self.state["reviewed_sql"]})
            print("============ Compliance Results ============")
            print("Compliance Report:", output3.pydantic.report)
            self.state["compliance_report"] = output3.pydantic.report
            return output3

        # @listen(filter_leads)
        # def write_email(self, leads):
        #     scored_leads = [lead.to_dict() for lead in leads]
        #     emails = email_writing_crew.kickoff_for_each(scored_leads)
        #     return emails


    flow = SQLAssistantFlow()

    results = flow.kickoff()

    # Print final reviewed SQL and compliance report
    print("\n=== FINAL REVIEWED SQL ===")
    print(flow.state.get("reviewed_sql"))
    print("\n=== COMPLIANCE REPORT ===")
    print(flow.state.get("compliance_report"))

