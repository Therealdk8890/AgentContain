# Contributing to WarrantKit

Thanks for contributing to WarrantKit.

WarrantKit is developed as an open-source project under the Apache License 2.0. The repository is intentionally structured so that the open foundation can be reviewed, reused, and integrated while the project maintains a clear record of provenance for contributions.

## Contribution requirements

Before submitting a contribution:

1. Make sure you have the right to submit the work.
2. Do not submit code, documentation, test fixtures, credentials, customer material, or other content that you are not authorized to license to the project.
3. Do not include third-party material unless its license and required notices are compatible with the project and you identify the source.
4. Do not include confidential or proprietary material belonging to an employer, customer, former employer, or another third party.
5. Keep security-sensitive changes narrowly scoped and describe the security boundary they affect.

By intentionally submitting a contribution for inclusion in this repository, you represent that you have the necessary rights to submit it and that you understand contributions to the project are made under the Apache License 2.0 as described in the repository's `LICENSE` file.

For contributions that require a separate contributor agreement, corporate agreement, or other written IP documentation, maintainers may require that documentation before accepting the contribution.

## Commit sign-off

Contributors are encouraged to use a DCO-style sign-off on commits:

```text
git commit -s
```

A sign-off indicates that the contributor is making the certification represented by the Developer Certificate of Origin for that commit. A sign-off is a provenance aid; it does not transfer copyright ownership or replace a separately required contributor agreement.

## Third-party code and dependencies

Identify third-party code and material when adding or substantially changing dependencies. Do not copy code from another project into WarrantKit without checking its license and attribution requirements.

When a dependency introduces additional license or attribution obligations, document them in the repository before release.

## Pull requests

Pull requests should:

- explain the security or product boundary being changed;
- include tests for security-relevant behavior where practical;
- avoid mixing unrelated refactors with security-critical changes;
- identify any new external dependency or generated artifact;
- preserve existing copyright and license notices.

Security vulnerabilities should be reported privately according to `SECURITY.md`, not through a public pull request.

## Maintainer review

WarrantKit maintainers may request additional provenance information for contributions affecting:

- authorization or policy semantics;
- runtime enforcement;
- evidence and verification;
- cryptographic material;
- external integrations;
- licensing or third-party notices.

The goal is simple: keep the technical history, security boundary, and provenance of the project easy to understand for users, contributors, and future maintainers.
