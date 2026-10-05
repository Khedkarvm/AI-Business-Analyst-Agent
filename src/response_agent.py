import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from business_insights import format_category_name

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


# --------------------------------------------------
# Response Prompt
# --------------------------------------------------

response_prompt = PromptTemplate(
    input_variables=["question", "agent_result"],
    template="""
You are the final response layer of an AI Business Analyst.

Answer the user's question using only the information in the agent result.

General rules:
- Do not invent facts or values.
- Do not perform new calculations.
- Do not change the meaning of any result.
- Answer the question directly and concisely.
- All monetary values in this business system are in BRL.
- Always display monetary values as: 1,234.56 BRL.
- Never use $, USD, €, £, or other currency symbols.
- Format large counts with commas, e.g. 99,441.
- Convert technical database names into readable text when the meaning
  is clear, such as replacing underscores with spaces.
- Preserve percentages and dates correctly.
- Use Markdown when useful.
- Mention the source if one is provided.
- Do not mention internal agents, Python, DataFrames, or implementation details.
- Do not give recommendations unless they are explicitly present
  in the agent result.

IMPORTANT RULE FOR OVERALL BUSINESS PERFORMANCE QUESTIONS:

If the agent result contains a "summary" section and the user is asking
for overall business performance, use the summary section for the main answer.

Do NOT reproduce:
- the full monthly_revenue data
- the full forecast values
- the full anomaly records

Instead, provide a concise business summary containing:

1. Total revenue
2. Total orders
3. Average order value
4. Recent 3-month revenue change
5. Top revenue category and its revenue
6. Forecast validation MAE
7. Data-quality information if available

If forecast start/end dates are available, mention the forecast period.

Use a format similar to:

## Overall Business Performance

- **Revenue:** 13,591,643.70 BRL
- **Orders:** 98,666
- **Average Order Value:** 137.75 BRL
- **Recent 3-month revenue change:** -12.13%
- **Top revenue category:** Health & Beauty — 1,258,681.34 BRL
- **Forecast validation MAE:** 69,385.65 BRL

**Data quality:** 3 months have fewer than 100 orders, and
November 2016 has no recorded data.

Then provide only a short factual interpretation using information
already present in the agent result.

Do not create additional conclusions or recommendations.

For SQL questions:
- Answer only what the user asked.
- Do not include unrelated KPI information.

For RAG/business-policy questions:
- Answer directly from the retrieved information.
- Include the source when available.

User question:
{question}

Agent result:
{agent_result}

Provide the final business answer.
"""
)


# --------------------------------------------------
# Format SQL Result
# --------------------------------------------------

def format_sql_result(agent_result):

    if not isinstance(agent_result, dict):
        return agent_result

    result = agent_result.get("result")

    if not isinstance(result, dict):
        return agent_result

    rows = result.get("rows")
    columns = result.get("columns", [])

    if not rows:
        return agent_result

    formatted_result = agent_result.copy()
    formatted_result["result"] = result.copy()

    formatted_rows = []

    for row in rows:

        formatted_row = []

        for column, value in zip(columns, row):

            column_name = column.lower()

            # Count / number columns
            if (
                isinstance(value, (int, float))
                and (
                    "count" in column_name
                    or "orders" in column_name
                    or "customers" in column_name
                )
            ):
                formatted_row.append(
                    f"{int(value):,}"
                )

            # Category names
            elif (
                isinstance(value, str)
                and "category" in column_name
            ):
                formatted_row.append(
                    format_category_name(value)
                )

            # Other numeric values
            elif isinstance(value, float):
                formatted_row.append(
                    f"{value:,.2f}"
                )

            elif isinstance(value, int):
                formatted_row.append(
                    f"{value:,}"
                )

            else:
                formatted_row.append(value)

        formatted_rows.append(formatted_row)

    formatted_result["result"]["rows"] = formatted_rows

    return formatted_result


# --------------------------------------------------
# Response Agent
# --------------------------------------------------

def response_agent(question, agent_result):

    formatted_result = format_sql_result(
        agent_result
    )

    prompt = response_prompt.format(
        question=question,
        agent_result=formatted_result
    )

    response = llm.invoke(prompt)

    return response.content.strip()


# --------------------------------------------------
# Run directly for testing
# --------------------------------------------------

if __name__ == "__main__":

    question = "What is the total revenue?"

    agent_result = {
        "sql_query": (
            "SELECT SUM(price) AS total_revenue "
            "FROM order_items;"
        ),
        "result": {
            "status": "success",
            "columns": ["total_revenue"],
            "rows": [[13591643.7]]
        }
    }

    answer = response_agent(
        question,
        agent_result
    )

    print("\nRESPONSE AGENT")
    print("=" * 50)

    print("\nQuestion:")
    print(question)

    print("\nFinal Answer:")
    print(answer)