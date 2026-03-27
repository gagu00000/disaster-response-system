"""
Response Formatter Module
Formats LLM outputs for clean dashboard display.
"""


class ResponseFormatter:
    """Structures LLM outputs for dashboard display."""

    @staticmethod
    def format_explanation(text: str, caveat: bool = False) -> str:
        """Format a decision explanation for display."""
        formatted = text.strip()

        # Add AI label
        label = "🤖 AI-Generated Explanation (based on system data)"
        if caveat:
            label += "\n⚠️ *Some details may be approximate*"

        return f"**{label}**\n\n{formatted}"

    @staticmethod
    def format_query_response(text: str) -> str:
        """Format a query response for display."""
        formatted = text.strip()
        return f"🤖 **AI Response:**\n\n{formatted}"

    @staticmethod
    def format_insight_report(text: str) -> str:
        """Format an insight report for display."""
        formatted = text.strip()
        header = "🤖 **AI-Generated Simulation Report** *(based on system data)*\n\n---\n\n"
        return header + formatted

    @staticmethod
    def format_scenario_narration(text: str) -> str:
        """Format a scenario narration for display."""
        return f"🤖 *{text.strip()}*"

    @staticmethod
    def truncate_if_needed(text: str, max_chars: int = 2000) -> str:
        """Truncate response if it exceeds maximum length."""
        if len(text) > max_chars:
            return text[:max_chars] + "\n\n*[Response truncated]*"
        return text
