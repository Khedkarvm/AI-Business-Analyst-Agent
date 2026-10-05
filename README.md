# AI Business Analyst Agent

## Project Overview

AI Business Analyst Agent is an AI-powered business analytics system that allows users to ask business questions in natural language.

The system uses AI agents, PostgreSQL, Python analytics, forecasting, and Retrieval-Augmented Generation (RAG) to provide business insights and answers.

## Project Objective

The objective of this project is to build an AI Business Analyst that can:

- Answer business questions using SQL
- Calculate business KPIs
- Analyze revenue trends
- Analyze product categories
- Forecast future revenue
- Answer business policy questions using RAG
- Provide business-friendly answers through a Streamlit dashboard

## System Architecture

User Question
        ↓
Planner Agent
        ↓
 ┌──────┼────────┐
 ↓      ↓        ↓
SQL   Analysis   RAG
Agent  Agent     Agent
 ↓      ↓        ↓
PostgreSQL Python Business
          Analytics Documents
        ↓
Response Agent
        ↓
Streamlit Dashboard

## AI Agents

### Planner Agent

Determines which agent should handle the user's question.

### SQL Agent

Generates and executes SQL queries against the PostgreSQL database.

Example:

> What is the total revenue?

Result:

> 13,591,643.70 BRL

### Analysis Agent

Performs business analytics including:

- Revenue analysis
- Order analysis
- Average Order Value
- Revenue trends
- Product category analysis
- Data quality analysis
- Revenue forecasting

### RAG Agent

Answers questions from business documents such as:

- Return policy
- Shipping policy
- Business policy

Example:

> How many days do customers have to request a return?

Answer:

> Customers have 7 days from delivery to request a return.

### Response Agent

Converts technical agent results into clear, business-friendly responses.

## Technology Stack

- Python
- PostgreSQL
- SQLAlchemy
- Pandas
- LangChain
- LangGraph
- Groq LLM
- Prophet
- Sentence Transformers
- ChromaDB
- Streamlit
- Altair

## Dataset

The project uses the Brazilian E-Commerce Public Dataset by Olist.

The database contains information about:

- Orders
- Order Items
- Customers
- Products
- Sellers
- Payments
- Reviews
- Geolocation
- Product Categories

## Business KPIs

Current project results:

| KPI | Value |
|---|---:|
| Total Product Revenue | 13,591,643.70 BRL |
| Total Orders | 98,666 |
| Average Order Value | 137.75 BRL |
| Top Category | Health & Beauty |
| Top Category Revenue | 1,258,681.34 BRL |
| Revenue Contribution | 9.26% |

## Revenue Analysis

The system analyzes monthly revenue and compares recent valid months with previous valid months.

Current analysis shows:

- Revenue trend: Decreasing
- Recent 3-month revenue: 2,615,317.86 BRL
- Previous 3-month revenue: 2,976,378.87 BRL
- Revenue change: -12.13%

## Revenue Forecasting

The project uses Prophet for monthly revenue forecasting.

Forecast validation:

- MAE: 69,385.65 BRL

The system generates revenue forecasts for future months and displays them in the Streamlit dashboard.

## Data Quality

The system identifies months with fewer than 100 orders.

Currently detected:

- September 2016 — 3 orders
- December 2016 — 1 order
- September 2018 — 1 order

The historical dataset also contains a missing month:

- November 2016

These data-quality issues are highlighted before relying on trend or forecasting analysis.

## RAG System

The RAG system uses business documents stored in the `business_docs` folder.

Documents include:

- `return_policy.txt`
- `shipping_policy.txt`
- `business_policy.txt`

The system retrieves relevant information and provides answers with document sources.

## Streamlit Dashboard

The dashboard provides:

- Business KPI cards
- AI Business Analyst question interface
- Monthly revenue trend
- Revenue forecast
- Category analysis
- Data quality information
- Technical SQL output for SQL questions

## Example Questions

Users can ask questions such as:

```text
What is the total revenue?

What is the average order value?

Which product category generates the highest revenue?

Analyze the overall business performance.

How many days do customers have to request a return?

What is the refund policy?