"""Email generation module for AI That Works episodes."""

from baml_client.types import EmailDraft

from .core import generate_email

__all__ = ["generate_email", "EmailDraft"]
