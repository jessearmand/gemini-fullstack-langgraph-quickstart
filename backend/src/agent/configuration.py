import os
import logging
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
        # config is the RunnableConfig object. It can behave like a dictionary.
        logging.debug(f"[DEBUG Configuration.from_runnable_config] Received full config object: {config}")

        # Source 1: config.get("configurable", {}) - the nested dictionary
        cfg_from_nested = config.get("configurable", {}) if config else {}
        logging.debug(f"[DEBUG Configuration.from_runnable_config] Content of config.get('configurable', {{}}): {cfg_from_nested}")

        # Source 2: Top-level keys of the config object itself.
        # langgraph-cli might place keys here if they are part of config_schema.
        cfg_from_top_level = {}
        if isinstance(config, dict): # RunnableConfig often acts as a dict
            for schema_key in list(cls.model_fields.keys()):
                if schema_key in config and config[schema_key] is not None:
                    cfg_from_top_level[schema_key] = config[schema_key]
        logging.debug(f"[DEBUG Configuration.from_runnable_config] Content from top-level of config object: {cfg_from_top_level}")

        init_values: dict[str, Any] = {}

        # Populate init_values, giving precedence:
        # 1. Nested config["configurable"] (cfg_from_nested)
        # 2. Top-level keys in config object (cfg_from_top_level)
        # 3. Environment variables
        # 4. Pydantic field defaults (applied during cls(**init_values) if not set by above)

        for key in list(cls.model_fields.keys()):
            val_from_nested = cfg_from_nested.get(key)
            val_from_top_level = cfg_from_top_level.get(key)
            val_from_env = os.environ.get(key.upper()) # For model_provider, specifically check MODEL_PROVIDER
            if key == "model_provider" and not val_from_env: # common to use MODEL_PROVIDER
                val_from_env = os.environ.get("MODEL_PROVIDER")


            if val_from_nested is not None:
                init_values[key] = val_from_nested
            elif val_from_top_level is not None:
                init_values[key] = val_from_top_level
            elif val_from_env is not None:
                init_values[key] = val_from_env

        logging.debug(f"[DEBUG Configuration.from_runnable_config] Final init_values for Pydantic: {init_values}")
        return cls(**init_values)
