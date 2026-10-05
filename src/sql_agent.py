
# sql_agent.py
# SQL Agent: Convert business questions into SQL queries


import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate

from database import engine


# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


# --------------------------------------------------
# Connect to database
# --------------------------------------------------

db = SQLDatabase(engine)


# --------------------------------------------------
# Create LLM
# --------------------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)


# --------------------------------------------------
# SQL Generation Prompt
# --------------------------------------------------

sql_prompt = PromptTemplate(
    input_variables=["question", "schema"],
    template="""
You are a SQL analyst for an e-commerce business.

Convert the user's business question into a PostgreSQL SQL query.

Database schema:
{schema}

Business metric definitions:
- Product revenue = SUM(order_items.price)
- Total payment value = SUM(payments.payment_value)
- Total orders = COUNT(DISTINCT orders.order_id)
- Total customers = COUNT(DISTINCT customers.customer_unique_id)
- Average order value = product revenue / total orders

Metric usage rules:
- If the user asks for "revenue", use Product Revenue.
- Product Revenue must be calculated using order_items.price.
- Use payments.payment_value only when the user explicitly asks for payment value.
- Use the metric definitions above whenever the question matches one of them.

Category rules:
- When the user asks about product categories, use the category_translation table whenever possible.
- product_category_name in products contains the original Portuguese category name.
- category_translation.product_category_name maps to products.product_category_name.
- category_translation.product_category_name_english contains the English category name.
- When displaying a product category, prefer category_translation.product_category_name_english.
- Use a LEFT JOIN so categories without a translation are not lost.
- When grouping by category, group by the English category expression.
- If an English translation is unavailable, fall back to products.product_category_name.

SQL rules:
- Use only tables and columns provided in the database schema.
- Generate only one PostgreSQL SELECT query.
- Do not explain the SQL.
- Do not use markdown.
- Do not invent tables or columns.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE, or other data-changing queries.

User question:
{question}
"""
)


# --------------------------------------------------
# SQL Correction Prompt
# --------------------------------------------------

sql_correction_prompt = PromptTemplate(
    input_variables=[
        "question",
        "schema",
        "sql_query",
        "error_message"
    ],
    template="""
You are a PostgreSQL SQL correction agent.

The following SQL query was generated for a business question,
but PostgreSQL returned an error.

Business question:
{question}

Database schema:
{schema}

Generated SQL:
{sql_query}

PostgreSQL error:
{error_message}

Correct the SQL query using the database schema.

Rules:
- Return only one PostgreSQL SELECT query.
- Do not explain the correction.
- Do not use markdown.
- Use only tables and columns provided in the schema.
- Do not generate INSERT, UPDATE, DELETE, DROP, ALTER, TRUNCATE, CREATE,
  or any other data-changing query.
- Preserve the original business intent.
- Fix the SQL based on the PostgreSQL error.

Return only the corrected SQL query.
"""
)


# --------------------------------------------------
# Clean generated SQL
# --------------------------------------------------

def clean_sql(sql_query):

    sql_query = sql_query.strip()

    # Remove markdown code fences if the LLM
    # accidentally returns them.

    if sql_query.startswith("```sql"):

        sql_query = sql_query[
            len("```sql"):
        ]

    elif sql_query.startswith("```"):

        sql_query = sql_query[
            len("```"):
        ]

    if sql_query.endswith("```"):

        sql_query = sql_query[
            :-len("```")
        ]

    return sql_query.strip()


# --------------------------------------------------
# Generate SQL
# --------------------------------------------------

def generate_sql(question):

    try:

        schema = db.get_table_info()

        prompt = sql_prompt.format(
            question=question,
            schema=schema
        )

        response = llm.invoke(prompt)

        sql_query = clean_sql(
            response.content
        )

        if not sql_query:

            return {
                "status": "error",
                "message": (
                    "The SQL Agent generated "
                    "an empty query."
                )
            }

        return {
            "status": "success",
            "sql_query": sql_query
        }

    except Exception as e:

        return {
            "status": "error",
            "message": (
                "SQL generation failed: "
                f"{str(e)}"
            )
        }


# --------------------------------------------------
# Validate SQL
# --------------------------------------------------

def validate_sql(sql_query):

    cleaned_sql = sql_query.strip()

    if not cleaned_sql:

        return {
            "status": "error",
            "message": "SQL query is empty."
        }

    # --------------------------------------------------
    # Remove trailing semicolon for validation
    # --------------------------------------------------

    sql_without_semicolon = (
        cleaned_sql.rstrip(";").strip()
    )

    # --------------------------------------------------
    # Only one SQL statement is allowed
    # --------------------------------------------------

    if ";" in sql_without_semicolon:

        return {
            "status": "error",
            "message": (
                "Multiple SQL statements "
                "are not allowed."
            )
        }

    # --------------------------------------------------
    # Only SELECT queries are allowed
    # --------------------------------------------------

    if not sql_without_semicolon.lower().startswith(
        "select"
    ):

        return {
            "status": "error",
            "message": (
                "Only SELECT queries are allowed."
            )
        }

    return {
        "status": "success"
    }


# --------------------------------------------------
# Run SQL
# --------------------------------------------------

def execute_sql(sql_query):

    validation_result = validate_sql(
        sql_query
    )

    if validation_result["status"] == "error":

        return validation_result

    try:

        # --------------------------------------------------
        # Execute SQL using SQLAlchemy
        # --------------------------------------------------

        with engine.connect() as connection:

            result = connection.exec_driver_sql(
                sql_query
            )

            rows = result.fetchall()

            columns = list(
                result.keys()
            )

        # --------------------------------------------------
        # Convert database values into
        # JSON-friendly values
        # --------------------------------------------------

        clean_rows = []

        for row in rows:

            clean_row = []

            for value in row:

                if hasattr(
                    value,
                    "as_integer_ratio"
                ):

                    value = float(value)

                clean_row.append(value)

            clean_rows.append(
                clean_row
            )

        return {
            "status": "success",
            "columns": columns,
            "rows": clean_rows
        }

    except Exception as e:

        return {
            "status": "error",
            "message": (
                "SQL execution failed: "
                f"{str(e)}"
            )
        }


# --------------------------------------------------
# Correct SQL after execution error
# --------------------------------------------------

def correct_sql(
    question,
    sql_query,
    error_message
):

    try:

        schema = db.get_table_info()

        prompt = sql_correction_prompt.format(
            question=question,
            schema=schema,
            sql_query=sql_query,
            error_message=error_message
        )

        response = llm.invoke(prompt)

        corrected_sql = clean_sql(
            response.content
        )

        if not corrected_sql:

            return {
                "status": "error",
                "message": (
                    "The SQL correction agent "
                    "generated an empty query."
                )
            }

        return {
            "status": "success",
            "sql_query": corrected_sql
        }

    except Exception as e:

        return {
            "status": "error",
            "message": (
                "SQL correction failed: "
                f"{str(e)}"
            )
        }


# --------------------------------------------------
# SQL Agent
# --------------------------------------------------

def sql_agent(question):

    # --------------------------------------------------
    # Step 1: Generate SQL
    # --------------------------------------------------

    generation_result = generate_sql(
        question
    )

    if generation_result["status"] == "error":

        return {
            "question": question,
            "sql_query": None,
            "result": generation_result
        }

    sql_query = generation_result[
        "sql_query"
    ]

    # --------------------------------------------------
    # Step 2: Validate generated SQL
    # --------------------------------------------------

    validation_result = validate_sql(
        sql_query
    )

    if validation_result["status"] == "error":

        return {
            "question": question,
            "sql_query": sql_query,
            "result": validation_result
        }

    # --------------------------------------------------
    # Step 3: Execute generated SQL
    # --------------------------------------------------

    execution_result = execute_sql(
        sql_query
    )

    # --------------------------------------------------
    # Step 4: If SQL fails, attempt ONE correction
    # --------------------------------------------------

    if execution_result["status"] == "error":

        error_message = execution_result[
            "message"
        ]

        correction_result = correct_sql(
            question=question,
            sql_query=sql_query,
            error_message=error_message
        )

        # --------------------------------------------------
        # Correction failed
        # --------------------------------------------------

        if correction_result["status"] == "error":

            return {
                "question": question,
                "sql_query": sql_query,
                "result": execution_result,
                "correction_attempted": True,
                "correction_result": correction_result
            }

        corrected_sql = correction_result[
            "sql_query"
        ]

        # --------------------------------------------------
        # Validate corrected SQL
        # --------------------------------------------------

        corrected_validation = validate_sql(
            corrected_sql
        )

        if corrected_validation["status"] == "error":

            return {
                "question": question,
                "sql_query": sql_query,
                "result": execution_result,
                "correction_attempted": True,
                "corrected_sql": corrected_sql,
                "correction_result":
                    corrected_validation
            }

        # --------------------------------------------------
        # Execute corrected SQL
        # --------------------------------------------------

        corrected_execution = execute_sql(
            corrected_sql
        )

        return {
            "question": question,
            "sql_query": corrected_sql,
            "original_sql": sql_query,
            "result": corrected_execution,
            "correction_attempted": True,
            "original_error": error_message
        }

    # --------------------------------------------------
    # Step 5: Original SQL succeeded
    # --------------------------------------------------

    return {
        "question": question,
        "sql_query": sql_query,
        "result": execution_result,
        "correction_attempted": False
    }


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    question = "What is the total revenue?"

    result = sql_agent(
        question
    )

    print("\nSQL AGENT")
    print("=" * 50)

    print("\nQuestion:")
    print(result["question"])

    print("\nGenerated SQL:")
    print(result["sql_query"])

    print("\nCorrection Attempted:")
    print(
        result.get(
            "correction_attempted",
            False
        )
    )

    print("\nResult:")
    print(result["result"])

