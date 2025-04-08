# Evaluating AI Agents with Pydantic AI & Logfire

This repository is a personal initiative to review and apply the concepts learned in the ["Evaluating AI Agents"](https://learn.deeplearning.ai/courses/evaluating-ai-agents/) course by [DeepLearning.AI](https://www.deeplearning.ai/). The key aspects of this project are:

* A didactic review of the course material, reimagined through the lens of [Pydantic AI](https://ai.pydantic.dev/) and [Logfire](https://pydantic.dev/logfire).

* A reimplementation of the labs using [Pydantic AI](https://ai.pydantic.dev/) and [Logfire](https://pydantic.dev/logfire), showcasing the potential of both libraries.

  

## Table of Contents

- [Labs](#labs)

	- [Lab 1: Building your agent](#lab-1-building-your-agent-go-to-lab-page)

	- [Lab 2: Tracing your agent](#lab-2-tracing-your-agent-go-to-lab-page)

	- [Lab 3: Adding router and skill evaluations](#lab-3-adding-router-and-skill-evaluations-go-to-lab-page)

	- [Lab 4: Adding trajectory evaluations](#lab-4-adding-trajectory-evaluations-go-to-lab-page)

	- [Lab 5: Adding structure to your evaluations](#lab-5-adding-structure-to-your-evaluations-go-to-lab-page)

  

## Labs

  

### Lab 1: Building your agent [(Go to lab page)](https://learn.deeplearning.ai/courses/evaluating-ai-agents/lesson/pag5y/lab-1:-building-your-agent)


Files:

- `lab_1/solution_from_course.py`: contains the original solution provided by the course for Lab 1.

- `lab_1/solution_with_pydantic.py`: re-imagine the lab to use Pydantic AI (no observability at this point)

  

Notes:

- The system prompt used by the router was updated slightly. A new sentence at the end was added to help models like `gemini-1.5-flash` to determine the appropriate tool to use.

- Loading the Parquet file into memory once at the start optimizes performance by reducing I/O overhead and resource consumption, which could be beneficial if the `lookup_sales_data` tool were to be called twice.

  

### Lab 2: Tracing your agent [(Go to lab page)](https://learn.deeplearning.ai/courses/evaluating-ai-agents/lesson/njjlv/lab-2:-tracing-your-agent)

Files:

- `lab_2/solution_from_course.py`: contains the original solution provided by the course for Lab 2.

- `lab_2/solution_with_logfire.py`: replace re-imagine the lab to use Pydantic AI (no observability at this point)

	Changes:
	
| Change | Phoenix | Logfire  |
|--|--|--|
|Configuration  | `PROJECT_NAME = "tracing-agent"`<br>`tracer_provider = register(`<br>`project_name=PROJECT_NAME,`<br>`endpoint=get_phoenix_endpoint() + "v1/traces"`<br>`)`<br>`tracer = tracer_provider.get_tracer(__name__)`  | `logfire.configure()` |
|Auto-Instrumentation for OpenAI  | `OpenAIInstrumentor().instrument(tracer_provider = tracer_provider)` | `logfire.instrument_openai(client)` |
| Span creation | `#decorators`<br>`@tracer.tool()`<br>`@tracer.chain()`<br><br>`#context manager`<br>`with  tracer.start_as_current_span("AgentRun") as span:` | `#decorators`<br>`@logfire.instrument("tool=lookup_sales_data", span_name="{tool=}")`<br>`@logfire.instrument("chain=handle_tool_calls", span_name="{chain=}")` <br><br>`#context manager`<br>`with @logfire.span("{agent=}", agent="AgentRun") as span:`|



Notes:

- Logfire is designed to be compatible with OpenTelemetry, ensuring seamless integration with any OpenTelemetry instrumentation package. Additionally, it simplifies the process of instrumenting calls to OpenAI with a single line of code.

- Logfire facilitates the implementation of manual instrumentation, providing a high degree of customization.

- Creating a span is straightforward using `with logfire.span(...)`, and any span or log created within that block becomes a child of that span. Structured data can also be attached to a span.

- The `@logfire.instrument` decorator enables the wrapping of entire functions within a span, streamlining the instrumentation process.

- Logfire does not allow modifications to the span kind attribute, which is set to `span` by default. As a result, when moving to Logfire, the `span_name` attribute acts as a replacement for the `kind` attribute, making it easier to query spans in the future.



### Lab 3: Adding router and skill evaluations [(Go to lab page)](https://learn.deeplearning.ai/courses/evaluating-ai-agents/lesson/yx7uz/lab-3:-adding-router-and-skill-evaluations)


### Lab 4: Adding trajectory evaluations [(Go to lab page)](https://learn.deeplearning.ai/courses/evaluating-ai-agents/lesson/an0wh/lab-4:-adding-trajectory-evaluations)


### Lab 5: Error Handling and Observability [(Go to lab page)](https://learn.deeplearning.ai/courses/evaluating-ai-agents/lesson/fob86/lab-5:-adding-structure-to-your-evaluations)

