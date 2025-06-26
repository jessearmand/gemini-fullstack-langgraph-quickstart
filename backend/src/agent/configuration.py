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
        passed_configurable = (
            config["configurable"] if config and "configurable" in config else {}
        )

        # Build the values for Configuration instantiation
        # Order of precedence:
        # 1. Values from passed_configurable (from RunnableConfig)
        # 2. Values from environment variables
        # 3. Pydantic defaults (applied during cls(**init_values) if not present)

        init_values: dict[str, Any] = {}

        # Iterate over all known model fields plus 'model_provider'
        # to ensure all possible configurations are checked.
        all_possible_keys = list(cls.model_fields.keys())
        if "model_provider" not in all_possible_keys: # Should be there due to Field definition
             all_possible_keys.append("model_provider")


        for key in all_possible_keys:
            if key in passed_configurable and passed_configurable[key] is not None:
                init_values[key] = passed_configurable[key]
            elif os.environ.get(key.upper()) is not None:
                init_values[key] = os.environ.get(key.upper())
            # If not in passed_configurable or env, it will either use Pydantic default
            # or be considered missing if no default and not optional.

        # The @model_validator (set_default_models_based_on_provider)
        # will run *before* field validation, using these init_values.
        # It expects 'model_provider' to be potentially present in init_values
        # or it will use its own default ("google") if 'model_provider' is not in init_values.
        # Then it sets other model defaults based on the resolved 'model_provider'.

        return cls(**init_values)
