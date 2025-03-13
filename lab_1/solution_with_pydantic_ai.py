# /// script
# dependencies = [
#   "duckdb==1.1.3",
#   "pandas",
#   "pyarrow",
#   "pydantic-ai",
#   "email-validator"
# ]
# ///

# =============================
# importing necessary libraries
# =============================

import asyncio
import os
import random
from dataclasses import dataclass

import duckdb
import pandas as pd
from pydantic import BaseModel, Field
from pydantic_ai import Agent, ModelRetry, RunContext


# database lookup
TRANSACTION_DATA_FILE_PATH = (
    "./data/Store_Sales_Price_Elasticity_Promotions_Data.parquet"
)


# ==============================
# initialization
# ==============================


@dataclass
class SharedDependencies:
    table_name: str
    dataframe: pd.DataFrame


model = os.getenv("PYDANTIC_AI_MODEL", "google-gla:gemini-1.5-flash")


# ==================
# Defining the tools
# ==================


# -----------------------
# Tool 1: Database Lookup
# -----------------------


text2sql_agent = Agent(model, deps_type=SharedDependencies)


# code for step 2 of tool 1
@text2sql_agent.system_prompt
def text2sql_system_prompt(ctx: RunContext) -> str:
    return f"""
    Generate an SQL query based on a prompt. Do not reply with anything besides the SQL query.
    The prompt is: {ctx.prompt}

    The available columns are: {ctx.deps.dataframe.columns}
    The table name is: {ctx.deps.table_name}
    """


# code for tool 1
async def lookup_sales_data(ctx: RunContext[SharedDependencies]) -> str:
    """Look up data from Store Sales Price Elasticity Promotions dataset.

    Args:
        ctx: The context.
    """
    try:
        df = ctx.deps.dataframe
        # step 1: load dataframe into a duckdb table
        duckdb.sql(
            f"CREATE TABLE IF NOT EXISTS {ctx.deps.table_name} AS SELECT * FROM df"
        )

        # step 2: generate the SQL code
        result = await text2sql_agent.run(ctx.prompt, usage=ctx.usage, deps=ctx.deps)
        sql_query = result.data
        # clean response to make sure it only includes SQL code
        sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
        # step 3: execute the SQL query
        result = duckdb.sql(sql_query).df()
        return result.to_string()
    except Exception as e:
        raise ModelRetry(f"Error accessing data:: {e}")


# ---------------------
# Tool 2: Data Analysis
# ---------------------


class SuccessfulAnalysis(BaseModel):
    """Response when analysis could be generated successfully."""

    description: str = Field(description="analysis description")


class UnsuccessfulAnalysis(BaseModel):
    """Response when no analysis could be generated"""


# Implementation of AI-powered sales data analysis
analyzer_agent = Agent(model, result_type=SuccessfulAnalysis | UnsuccessfulAnalysis)


async def analyze_sales_data(ctx: RunContext[SharedDependencies], data: str) -> str:
    """Analyze sales data to extract insights.

    Args:
        ctx: The context.
        data: The lookup_sales_data tool's output.
    """
    prompt = f"""
    Analyze the following data: {data}
    Your job is to answer the following question: {ctx.prompt}
    """
    result = await analyzer_agent.run(prompt, usage=ctx.usage)
    return (
        result.data.description
        if isinstance(result.data, SuccessfulAnalysis)
        else "No analysis could be generated"
    )


# --------------------------
# Tool 3: Data Visualization
# --------------------------


# class defining the response format of step 1 of tool 3
class VisualizationConfig(BaseModel):
    chart_type: str = Field(..., description="Type of chart to generate")
    x_axis: str = Field(..., description="Name of the x-axis column")
    y_axis: str = Field(..., description="Name of the y-axis column")
    title: str = Field(..., description="Title of the chart")


# agent to generate char visualization configuration
chart_visualization_config_agent = Agent(model, result_type=VisualizationConfig)


# agent to create a chart based on the configuration
chart_creation_agent = Agent(model)


async def generate_visualization(
    ctx: RunContext[SharedDependencies], data: str, visualization_goal: str
) -> str:
    """Generate Python code to create data visualizations.

    Args:
        ctx: The context.
        data: The lookup_sales_data tool's output.
        visualization_goal: The goal of the visualization.
    """
    result = await chart_visualization_config_agent.run(
        f"""
    Generate a chart configuration based on this data: {data}
    The goal is to show: {visualization_goal}
    """,
        usage=ctx.usage,
    )
    config = result.data

    result = await chart_creation_agent.run(
        f"""
    Write python code to create a chart based on the following configuration and data.
    Only return the code, no other text.
    config: {config}
    data: {data}
    """,
        usage=ctx.usage,
    )
    code = result.data.replace("```python", "").replace("```", "").strip()
    return code


# ------------------------------------
# Defining the router and `its logic`?
# ------------------------------------


router_agent = Agent(
    model,
    deps_type=SharedDependencies,
    # Hint: The last sentence is crucial for models like gemini-1.5-flash to determine the appropriate tool to use.
    system_prompt=(
        "You are a helpful assistant that can answer questions about "
        "the Store Sales Price Elasticity Promotions dataset. "
        "Always use the `lookup_sales_data` tool first, so you can get data to reply any user request."
    ),
    tools=[lookup_sales_data, analyze_sales_data, generate_visualization],
)


# ----------
# Entrypoint
# ----------


async def main():
    # Hint: Loading the Parquet file into memory once at the start
    # optimizes performance by reducing I/O overhead and resource consumption,
    # especially when the lookup_sales_data tool is called multiple times.
    df = pd.read_parquet(TRANSACTION_DATA_FILE_PATH)

    deps = SharedDependencies(table_name="sales", dataframe=df)
    # The following questions were taken from a Jupyter Notebook from Lab 1
    questions = [
        "Show me all the sales for store 1320 on November 1st, 2021",
        "what trends do you see in this data",
        "Show me the code for graph of sales by store in Nov 2021, and tell me what trends you see.",
        "A bar chart of sales by product SKU. Put the product SKU on the x-axis and the sales on the y-axis.",
    ]
    choosen_question = random.choice(questions)  # select a question at random
    print(f"Question: {choosen_question}")
    print("Answer:")
    result = await router_agent.run(
        choosen_question,
        deps=deps,
    )
    print(result.data)


if __name__ == "__main__":
    asyncio.run(main())
