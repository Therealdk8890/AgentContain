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

    def to_receipt(self, secret, *, execution_id, policy_id):
        return FakeReceipt(execution_id, policy_id, secret)


class FakeReceipt:
    def __init__(self, execution_id, policy_id, secret):
        self.payload = {"agent_id": execution_id, "policy_id": policy_id}
        self.signature = secret.hex()

    def to_dict(self):
        return {"payload": self.payload, "signature": self.signature}


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


def test_cli_reads_receipt_secret_from_environment(monkeypatch, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: FakeEngine())
    monkeypatch.setenv("AGENTCONTAIN_RECEIPT_SECRET", "test-secret")

    assert cli.main([
        "run",
        "--policy", "production",
        "--agent-id", "agent-1",
        "--contain",
        "--json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["receipt"]["payload"]["agent_id"] == "agent-1"
    assert payload["receipt"]["signature"]


def test_cli_reads_receipt_secret_from_file(monkeypatch, tmp_path, capsys) -> None:
    monkeypatch.setattr(cli, "build_agentcontainment_engine", lambda agent_id, **kwargs: FakeEngine())
    secret = tmp_path / "receipt.secret"
    secret.write_text("test-secret\\n", encoding="utf-8")

    assert cli.main([
        "run",
        "--policy", "production",
        "--agent-id", "agent-1",
        "--contain",
        "--receipt-secret-file", str(secret),
        "--json",
    ]) == 0

    payload = json.loads(capsys.readouterr().out)
    assert payload["receipt"]["payload"]["agent_id"] == "agent-1"
    assert payload["receipt"]["signature"]
