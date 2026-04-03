import logging
from typing import (
    TYPE_CHECKING,
)

from opentelemetry import (
    trace,
)
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


if TYPE_CHECKING:
    from fastapi import FastAPI


logger = logging.getLogger(__name__)


def setup_tracing(
    app: FastAPI, engine, host: str = "http://jaeger", port: int = 4317, app_name: str = "divine"
) -> None:
    resource = Resource.create({SERVICE_NAME: app_name})

    provider = TracerProvider(resource=resource)
    exporter = OTLPSpanExporter(endpoint=f"{host}:{port}", insecure=True)
    provider.add_span_processor(BatchSpanProcessor(exporter))

    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine.sync_engine)
