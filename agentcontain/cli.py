"""Small operator-facing AgentContain CLI."""

from __future__ import annotations

import argparse
import json
import sys

from .engine import admit, build_agentcontainment_engine, contain
from .policy import Policy


def _policy_from_args(args: argparse.Namespace) -> Policy:
    return Policy(
        policy_id=args.policy,
        capabilities=tuple(args.capability),
        allowed_egress=tuple(args.egress),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="agentcontain",
        description="Runtime enforcement and proof platform for autonomous AI agents.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    run = sub.add_parser("run", help="admit an execution and optionally contain it")
    run.add_argument("--policy", required=True, help="policy identifier")
    run.add_argument("--agent-id", default="agent", help="agent identity")
    run.add_argument("--capability", action="append", default=[], help="declared capability")
    run.add_argument("--egress", action="append", default=[], help="allowed egress target")
    run.add_argument(
        "--contain",
        action="store_true",
        help="invoke external containment immediately after admission",
    )
    run.add_argument(
        "--json",
        action="store_true",
        help="emit machine-readable execution state",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command == "run":
        policy = _policy_from_args(args)
        try:
            engine = build_agentcontainment_engine(args.agent_id)
            admission = admit(policy, agent_id=args.agent_id, engine=engine)
            report = None
            if args.contain:
                report = contain(admission)

            payload = {
                "execution_id": admission.identity.execution_id,
                "agent_id": admission.identity.agent_id,
                "policy_id": admission.identity.policy_id,
                "policy_digest": admission.identity.policy_digest,
                "epoch": admission.identity.epoch,
                "state": admission.machine.state.value,
                "events": [event.to_dict() for event in admission.machine.events.events],
            }
            if report is not None:
                payload["containment"] = {
                    "complete": report.complete,
                    "certified": getattr(report, "certified", False),
                    "durable": getattr(report, "durable", False),
                    "external_verified": getattr(report, "external_verified", False),
                    "failures": list(getattr(report, "failures", ())),
                }

            if args.json:
                print(json.dumps(payload, sort_keys=True, indent=2))
            else:
                print(f"AgentContain execution {payload['execution_id']}")
                print(f"  Agent:  {payload['agent_id']}")
                print(f"  Policy: {payload['policy_id']}")
                print(f"  Epoch:  {payload['epoch']}")
                print(f"  State:  {payload['state'].upper()}")
                for event in admission.machine.events.events:
                    print(f"  Event:  {event.name}")
                if report is not None:
                    status = "VERIFIED" if report.certified and report.durable else "DEGRADED"
                    print(f"  Containment: {status}")
            return 0
        except Exception as exc:
            print(f"agentcontain: {exc}", file=sys.stderr)
            return 1

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
