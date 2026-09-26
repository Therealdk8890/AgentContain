import json

from agentcontain import cli
from agentcontain.engine import admit, evidence_envelope
from agentcontain.policy import Policy


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
        "run", "--policy", "production", "--agent-id", "agent-1",
        "--capability", "network", "--egress", "api.example", "--contain", "--json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["execution"]["agent_id"] == "agent-1"
    assert payload["execution"]["policy_id"] == "production"
    assert payload["verification"]["status"] == "verified"
    assert payload["enforcement"]["complete"] is True


def test_cli_writes_evidence_file(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: FakeEngine())
    output = tmp_path / "evidence.json"

    assert cli.main([
        "run", "--policy", "production", "--agent-id", "agent-1",
        "--contain", "--evidence-output", str(output),
    ]) == 0

    document = json.loads(output.read_text(encoding="utf-8"))
    assert document["schema_version"] == "agentcontain.evidence/v1"
    assert document["execution"]["agent_id"] == "agent-1"
    assert document["verification"]["status"] == "verified"
    assert "Evidence:" in capsys.readouterr().out


def test_evidence_envelope_binds_identity_and_report() -> None:
    class Engine:
        pass

    admission = admit(Policy("production"), agent_id="agent-1", engine=Engine())
    envelope = evidence_envelope(
        admission,
        report=FakeReport(),
    )
    assert envelope.execution["execution_id"] == admission.identity.execution_id
    assert envelope.verification["status"] == "verified"
    assert envelope.proof["claims"] == list(FakeReport.stages)


def test_cli_returns_nonzero_when_engine_cannot_be_loaded(monkeypatch, capsys) -> None:
    def fail(_agent_id):
        raise RuntimeError("engine unavailable")

    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: fail(agent_id))

    assert cli.main(["run", "--policy", "production"]) == 1
    assert "engine unavailable" in capsys.readouterr().err
