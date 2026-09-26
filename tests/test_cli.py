import json

from agentcontain import cli


class FakeReport:
    complete = True
    certified = True
    durable = True
    external_verified = True
    failures = ()
    stages = ("runtime_fenced", "enforcer:cgroup:verified")
    enforcement_latency_seconds = 0.25


class FakeEngine:
    def contain(self):
        return FakeReport()


def test_cli_json_run(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: FakeEngine())

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


def test_cli_writes_portable_evidence_file(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: FakeEngine())
    output = tmp_path / "evidence.json"

    assert cli.main([
        "run",
        "--policy", "production",
        "--agent-id", "agent-1",
        "--contain",
        "--evidence-output", str(output),
    ]) == 0

    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["schema_version"] == "agentcontain.evidence/v1"
    assert document["execution"]["agent_id"] == "agent-1"
    assert document["execution"]["policy_id"] == "production"
    assert document["verification"]["status"] == "observed"
    assert "Evidence:" in capsys.readouterr().out


def test_cli_returns_nonzero_when_engine_cannot_be_loaded(monkeypatch, capsys) -> None:
    def fail(_agent_id):
        raise RuntimeError("engine unavailable")

    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: fail(agent_id))

    assert cli.main(["run", "--policy", "production"]) == 1
    assert "engine unavailable" in capsys.readouterr().err
