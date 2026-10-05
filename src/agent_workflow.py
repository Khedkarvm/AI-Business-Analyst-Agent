from typing import TypedDict

from langgraph.graph import StateGraph, START, END

from output_formatter import format_analysis_output
from planner_agent import planner_agent
from sql_agent import sql_agent
from analysis_agent import analysis_agent
from rag_agent import rag_agent
from response_agent import response_agent

# --------------------------------------------------
# 1. Define workflow state
# --------------------------------------------------
class AgentState(TypedDict):
    question: str
    route: str
    result: object
    technical_details: object


# --------------------------------------------------
# 2. Planner node
# --------------------------------------------------

def planner_node(state: AgentState):

    question = state["question"]

    route = planner_agent(question)

    return {
        "route": route
    }


# --------------------------------------------------
# 3. SQL Agent node
# --------------------------------------------------

def sql_node(state: AgentState):

    question = state["question"]

    result = sql_agent(question)

    return {
        "result": result,
        "technical_details": result
    }


# --------------------------------------------------
# 4. Analysis Agent node
# --------------------------------------------------

def analysis_node(state: AgentState):
    question = state["question"]

    result = analysis_agent(question)

    formatted_result = format_analysis_output(result)

    return {"result": formatted_result}

# --------------------------------------------------
# 5. RAG Agent node
# --------------------------------------------------

def rag_node(state: AgentState):

    question = state["question"]

    result = rag_agent(question)

    return {
        "result":result
    }



# --------------------------------------------------
# Response node
# --------------------------------------------------

def response_node(state: AgentState):

    question = state["question"]
    agent_result = state["result"]

    final_answer = response_agent(
        question,
        agent_result
    )

    return {
        "result": final_answer
    }


# --------------------------------------------------
# 6. Routing function
# --------------------------------------------------

def route_agent(state: AgentState):

    route = state["route"]

    if route == "SQL_AGENT":
        return "sql"

    elif route == "ANALYSIS_AGENT":
        return "analysis"

    elif route == "RAG_AGENT":
        return "rag"

    else:
        return "rag"


# --------------------------------------------------
# 7. Build LangGraph
# --------------------------------------------------

workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("sql", sql_node)
workflow.add_node("analysis", analysis_node)
workflow.add_node("rag", rag_node)
workflow.add_node("response", response_node)

workflow.add_edge(START, "planner")

workflow.add_conditional_edges(
    "planner",
    route_agent,
    {
        "sql": "sql",
        "analysis": "analysis",
        "rag": "rag"
    }
)

workflow.add_edge("sql", "response")
workflow.add_edge("analysis", "response")
workflow.add_edge("rag", "response")
workflow.add_edge("response", END)

app = workflow.compile()


# --------------------------------------------------
# 8. Test workflow
# --------------------------------------------------

if __name__ == "__main__":

    questions = [
        "What is the total revenue?",
        "Analyze the overall business performance.",
        "How many days do customers have to request a return?"
    ]

    for question in questions:

        result = app.invoke({
            "question": question
        })

        print("\n" + "=" * 60)
        print("QUESTION:")
        print(question)

        print("\nROUTE:")
        print(result["route"])

        print("\nFINAL RESULT:")
        print(result["result"])