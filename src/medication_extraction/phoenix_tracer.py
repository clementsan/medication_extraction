"""Phoenix tracer for LLM observability"""

from phoenix.otel import register
# from openinference.instrumentation.mistralai import MistralAIInstrumentor

from . import utils


# Phoenix tracer
tracer_provider = register(
    project_name="medication-extraction",  # Optional: Specify a project name
    endpoint=utils.retrieve_api("PHOENIX_COLLECTOR_ENDPOINT") + "v1/traces",
    auto_instrument=True,  # Automatically instrument if dependencies are available
)
# Turn on instrumentation for MistralAI
# MistralAIInstrumentor().instrument(tracer_provider=tracer_provider)
tracer = tracer_provider.get_tracer(__name__)
