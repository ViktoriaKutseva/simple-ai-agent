import os
import runpy
import types


class DummyCompletionResult:
    def __init__(self, content: str):
        self.choices = [types.SimpleNamespace(message=types.SimpleNamespace(content=content))]


class FakeCompletions:
    def __init__(self, response_content: str):
        self.response_content = response_content
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return DummyCompletionResult(self.response_content)


class FakeOpenAIClient:
    instances = []

    def __init__(self, **kwargs):
        self.init_kwargs = kwargs
        self.completions = FakeCompletions(response_content="mocked-response")
        self.chat = types.SimpleNamespace(completions=self.completions)
        FakeOpenAIClient.instances.append(self)


def test_settings_reads_api_key_from_env(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "test-key")

    import importlib
    import settings

    importlib.reload(settings)

    assert settings.settings.openrouter_api_key == "test-key"


def test_main_script_builds_openai_request(monkeypatch, capsys):
    FakeOpenAIClient.instances.clear()
    fake_openai_module = types.SimpleNamespace(OpenAI=FakeOpenAIClient)
    monkeypatch.setitem(os.sys.modules, "openai", fake_openai_module)

    import settings

    monkeypatch.setattr(settings.settings, "openrouter_api_key", "main-key")

    runpy.run_module("main", run_name="__main__")

    assert len(FakeOpenAIClient.instances) == 1
    client = FakeOpenAIClient.instances[0]

    assert client.init_kwargs == {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": "main-key",
    }

    assert len(client.completions.calls) == 1
    request = client.completions.calls[0]
    assert request["model"] == "z-ai/glm-4.5-air:free"
    assert request["messages"][0]["content"] == "What is the meaning of life?"

    out = capsys.readouterr().out
    assert "mocked-response" in out
