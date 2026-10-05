# analysis_agent.py
## Its job is to receive the user's question and call the business analysis system.

from business_analysis import generate_business_analysis


def analysis_agent(question):

    # --------------------------------------------------
    # Run the existing business analysis engine
    # --------------------------------------------------

    analysis_results = generate_business_analysis()

    # --------------------------------------------------
    # Return structured results
    # --------------------------------------------------

    return {
        "question": question,
        "status": "success",
        "analysis": analysis_results
    }


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    question = "Give me an overall business analysis."

    result = analysis_agent(question)

    print("\nANALYSIS AGENT")
    print("=" * 50)

    print("\nQuestion:")
    print(result["question"])

    print("\nStatus:")
    print(result["status"])

    print("\nTotal Revenue:")
    print(
        result["analysis"]["kpis"]["total_revenue"]
    )

    print("\nTotal Orders:")
    print(
        result["analysis"]["kpis"]["total_orders"]
    )

    print("\nRevenue Trend:")
    print(
        result["analysis"]["insights"]["revenue_trend"]
    )

    print("\nRevenue Growth:")
    print(
        f"{result['analysis']['insights']['revenue_growth_percentage']:.2f}%"
    )

    print("\nTop Category:")
    print(
        result["analysis"]["insights"]["top_category"]
    )

    print("\nForecast Validation MAE:")
    print(
        f"{result['analysis']['forecast']['validation_mae']:.2f} BRL"
    )