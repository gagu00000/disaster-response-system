"""
LLM Client Module
Interface to local Ollama LLM server.
Handles model selection, API calls, timeout management, connection testing,
and graceful degradation when unavailable.
Per Section 24.2-24.5.
"""
import time

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False


class LLMClient:
    """
    Client for communicating with the local Ollama LLM server.
    Falls back gracefully when Ollama is not available.
    """

    DEFAULT_MODEL = "mistral"
    FALLBACK_MODELS = ["llama3.2", "phi3"]
    DEFAULT_TEMPERATURE = 0.1
    DEFAULT_TIMEOUT = 30  # seconds

    def __init__(self, model: str = None):
        self.model = model or self.DEFAULT_MODEL
        self.is_connected = False
        self.connection_error = None

    def test_connection(self) -> bool:
        """Test if Ollama is running and the model is available."""
        if not OLLAMA_AVAILABLE:
            self.connection_error = "ollama Python package not installed"
            return False

        try:
            result = ollama.list()
            # Handle both old dict-style and new typed-object responses
            if hasattr(result, 'models'):
                models_list = result.models
                available = []
                for m in models_list:
                    name = getattr(m, 'model', '') or getattr(m, 'name', '') or ''
                    available.append(name.split(":")[0])
            else:
                models_list = result.get("models", [])
                available = [m.get("name", "").split(":")[0] for m in models_list]

            if self.model in available or any(self.model in m for m in available):
                self.is_connected = True
                return True

            # Try fallback models
            for fallback in self.FALLBACK_MODELS:
                if fallback in available or any(fallback in m for m in available):
                    self.model = fallback
                    self.is_connected = True
                    return True

            self.connection_error = f"Model '{self.model}' not found. Available: {available}"
            return False
        except Exception as e:
            self.connection_error = f"Cannot connect to Ollama: {str(e)}"
            return False

    def generate(self, prompt: str, max_tokens: int = 500,
                  temperature: float = None, system_prompt: str = None) -> str:
        """
        Generate text from the LLM.

        Args:
            prompt: the user/task prompt
            max_tokens: maximum response length
            temperature: sampling temperature (default 0.1)
            system_prompt: optional system-level instruction

        Returns:
            Generated text string
        """
        if not OLLAMA_AVAILABLE or not self.is_connected:
            raise ConnectionError("LLM not available")

        temp = temperature or self.DEFAULT_TEMPERATURE

        try:
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = ollama.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temp,
                    "num_predict": max_tokens,
                }
            )
            # Handle both dict and typed ChatResponse
            if hasattr(response, 'message'):
                msg = response.message
                return getattr(msg, 'content', '') or ''
            else:
                return response.get("message", {}).get("content", "")
        except Exception as e:
            raise ConnectionError(f"LLM generation failed: {str(e)}")

    def generate_with_timing(self, prompt: str, **kwargs) -> dict:
        """Generate text and return timing information."""
        start = time.time()
        try:
            text = self.generate(prompt, **kwargs)
            latency = time.time() - start
            return {"text": text, "latency": latency, "success": True, "error": None}
        except Exception as e:
            latency = time.time() - start
            return {"text": "", "latency": latency, "success": False, "error": str(e)}

    def warm_up(self):
        """Pre-warm the model by sending a simple test prompt."""
        try:
            self.generate("Hello. Respond with one word.", max_tokens=10)
        except Exception:
            pass

    def get_status(self) -> dict:
        """Get the current client status."""
        return {
            "model": self.model,
            "is_connected": self.is_connected,
            "ollama_installed": OLLAMA_AVAILABLE,
            "error": self.connection_error
        }
