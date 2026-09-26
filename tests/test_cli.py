import json

from agentcontain import cli


class FakeReport:
    complete = True
    certified = True
    durable = True
    external_verified = True
    failures = ()


class FakeEngine:
    def contain(self):
        return FakeReport()


def test_cli_json_run(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id: FakeEngine())

    assert cli.main([
        "run",
        "--policy", "production",
        "--agent-id", "agent-1",
        "--capability", "network",
        "--egress", "api.example",
        "--contain",
        "--json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["agent_id"] == "agent-1"
    assert payload["policy_id"] == "production"
    assert payload["state"] == "contained"
    assert payload["events"][-1]["name"] == "containment_verified"
    assert payload["containment"]["certified"] is True


def test_cli_returns_nonzero_when_engine_cannot_be_loaded(monkeypatch, capsys) -> None:
    def fail(_agent_id):
        raise RuntimeError("engine unavailable")

    monkeypatch.setattr(cli, "build_agentcontainment_engine", fail)

    assert cli.main(["run", "--policy", "production"]) == 1
    assert "engine unavailable" in capsys.readouterr().err
