import time

import interleave_test as it

from agentcontain import Policy
from agentcontain.engine import admit, contain, verify


class Report:
    complete = True
    certified = True
    durable = True
    epoch = 1


class GateEngine:
    def __init__(self, started):
        self.started = started
        self.last_report = None

    def contain(self):
        self.last_report = Report()
        self.started.set()
        # Yield to the controlled scheduler without parking on an OS primitive.
        time.sleep(0)
        return self.last_report


def test_containment_and_verification_are_atomic_across_epoch_change():
    @it.interleave(iterations=100, strategy="dfs", max_preemptions=2)
    def model():
        started = it.Event()
        engine = GateEngine(started)
        admission = admit(
            Policy("production"),
            agent_id="agent-1",
            engine=engine,
            runtime_id="runtime-1",
        )
        errors = []

        def do_contain():
            contain(admission)

        def do_verify():
            try:
                verify(admission)
            except Exception as exc:
                errors.append(exc)

        containment = it.spawn(do_contain, name="contain")
        started.wait()
        verification = it.spawn(do_verify, name="verify")
        containment.join()
        verification.join()

        assert not errors, errors
        assert admission.machine.state.value == "verified"
        assert admission.identity.epoch == 1

    model()
