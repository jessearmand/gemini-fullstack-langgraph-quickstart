import os
from pydantic import BaseModel, Field, model_validator
from typing import Any, Optional

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    model_provider: str = Field(
        default="google",
        metadata={"description": "The provider of the language models (e.g., 'google', 'openai')."}
    )

    query_generator_model: str = Field(
        default="gemini-2.5-flash-lite-preview-06-17",
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: str = Field(
        default="gemini-2.5-flash",
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: str = Field(
        default="gemini-2.5-pro",
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    @model_validator(mode="before")
    def set_default_models_based_on_provider(cls, values: dict[str, Any]) -> dict[str, Any]:
        """Set default model names based on the model_provider."""
        model_provider = values.get("model_provider", "google")

        if model_provider == "openai":
            values.setdefault("query_generator_model", "gpt-4.1")
            values.setdefault("reflection_model", "o4-mini")
            values.setdefault("answer_model", "o3")
        elif model_provider == "google":
            values.setdefault("query_generator_model", "gemini-2.5-flash-lite-preview-06-17")
            values.setdefault("reflection_model", "gemini-2.5-flash")
            values.setdefault("answer_model", "gemini-2.5-pro")
        return values

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Get raw values from environment or config
        raw_values: dict[str, Any] = {
            # Allow model_provider to be set from env or config
            name: os.environ.get(name.upper()) or configurable.get(name)
            if name in cls.model_fields else configurable.get(name)
            for name in list(cls.model_fields.keys()) + ["model_provider"] # Ensure model_provider is checked
        }

        # Filter out None values before passing to model_validator
        # The validator will then apply defaults if specific models aren't provided
        filtered_values = {k: v for k, v in raw_values.items() if v is not None}

        return cls(**filtered_values)
