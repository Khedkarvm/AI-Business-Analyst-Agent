import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate


# --------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# --------------------------------------------------
# 2. Create LLM
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


# --------------------------------------------------
# 3. Planner prompt
# --------------------------------------------------

planner_prompt = PromptTemplate(
    input_variables=["question"],
    template="""
You are the planner for an AI Business Analyst system.

Decide which agent should handle the user's question.

Available agents:

SQL_AGENT
- Use for questions requiring database data,
  calculations, totals, counts, filtering, grouping,
  or business metrics.

ANALYSIS_AGENT
- Use for overall business analysis,
  trends, KPIs, forecasting, anomalies,
  or performance analysis.

RAG_AGENT
- Use for questions about business policies,
  return policy, shipping policy,
  or information contained in business documents.

Return ONLY one of:

SQL_AGENT
ANALYSIS_AGENT
RAG_AGENT

User Question:
{question}
"""
)


# --------------------------------------------------
# 4. Planner function
# --------------------------------------------------

def planner_agent(question):

    prompt = planner_prompt.format(
        question=question
    )

    response = llm.invoke(prompt)

    decision = response.content.strip()

    return decision


# --------------------------------------------------
# 5. Test planner
# --------------------------------------------------

if __name__ == "__main__":

    questions = [
        "What is the total revenue?",
        "Analyze the overall business performance.",
        "How many days do customers have to request a return?"
    ]

    for question in questions:

        decision = planner_agent(question)

        print("\nQuestion:")
        print(question)

        print("Planner Decision:")
        print(decision)