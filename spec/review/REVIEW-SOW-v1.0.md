# Pharo-Lapse External Review — Statement of Work

**Document ID:** `REVIEW-SOW-v1.0`
**Version:** 1.0
**Prepared:** 11 October 2026
**Status:** **DRAFT PACKAGE — NOT SENT; NO REVIEWER ENGAGED**
**Protocol baseline:** `PHARO-LAPSE-v1.1.0`
**Review type:** Independent design, implementation, and test-coverage review

---

## 1. Purpose and current status

This document defines a repeatable scope for an independent reviewer to assess the **Pharo-Lapse** protocol materials and the repository implementation artifacts. It is a request-for-review template, **not** a contract, purchase order, submission, engagement letter, security attestation, or review result.

No person or organization has been contacted, selected, retained, or represented as willing to perform this work. No review has occurred under this SOW. Any review remains **PENDING** until a reviewer independently agrees to scope, terms, access method, and disclosure process.

The review is intended to identify defects, ambiguities, missing evidence, and material implementation/specification gaps. A reviewer is not asked to certify the protocol as secure, fit for a particular use, compliant with law, or ready for deployment.

## 2. Review objectives

The reviewer should produce an evidence-based assessment in these eight areas:

1. **Cryptographic correctness**
2. **Protocol conformance**
3. **Test coverage and testability**
4. **Error handling and failure behavior**
5. **Injection and parser/command/data surface**
6. **Implementation-to-specification gaps**
7. **Security assumptions and residual risk**
8. **Documentation clarity and reproducibility**

Findings should distinguish among: (a) a confirmed defect with a minimal reproduction or precise reasoning, (b) a specification ambiguity, (c) a missing test or missing evidence, and (d) a recommendation. The reviewer must not convert an unverified historical receipt into a current live result.

## 3. Candidate review materials

The package may include the following repository paths at a mutually agreed revision:

| Material | Intended review use | Status / limitation |
|---|---|---|
| `spec/PHARO-LAPSE-v1.1.0.md` | Normative v1.1 protocol rules, wire format, security and test requirements | Specification declares live v1.1 gate re-run pending an executable harness and two-device overlay. |
| `spec/PHARO-LAPSE-v1.0.0.md` | Historical compatibility baseline | Its historical claims are not a fresh v1.1 run. |
| `spec/ARCHANGEL-INTEGRATION-v0.2.md` | Design context for intended multi-hop integration | Design document; not an implemented integration. |
| `reference/nexinus_queue.py` | Queue and direct-delivery reference behavior | Does not by itself establish v1.1 conformance. |
| `reference/phone_inbox_dedup.py` | Recipient/dedup reference behavior | Review revision and runtime assumptions before relying on it. |
| `reference/NEXINUS-WG-SIGNED-PROBE.py` | Diagnostic signed-message probe | Its own header says it uses separate test keys and a JSON format of its own; it is not the Pharo-Lapse CID serializer. |
| `cryptochrome/` and `tests/test_cryptochrome.py` | Optional deterministic sensor/heading module and unit tests | Not evidence of a live multi-device delivery. |
| `tests/GATE-3-RECEIPT-WANLESS.md` through `tests/GATE-6-RECEIPT-EXACTLY-ONCE.md` | Historical v1.0 evidence context | Receipts are historical records, not executable v1.1 tests. |

The author should provide a repository commit identifier, a clean checkout or archive, interpreter/dependency versions, and the exact command set used for any reproduction. If that material is absent, reproducibility is **PENDING** rather than assumed.

## 4. In-scope technical review

### 4.1 Cryptographic correctness

Review the design and implementation for consistency with the normative requirements, including:

- Ed25519 key generation, signing, verification, public-key pin handling, and rejection of invalid or unpinned identities;
- canonical JSON requirements: Unicode-code-point key order, no insignificant whitespace, UTF-8 bytes, array ordering, and rejection of duplicate object keys before canonicalization;
- origin signing-domain field inclusion/exclusion and the separate roles of origin signature, `origin_cid`, current `cid`, and forwarding-record signatures;
- CIDv1/dag-json/sha2-256 construction and whether the actual encoder and verifier use exactly the required byte domain;
- base64 decoding and malformed-signature/key handling;
- phase-anchor construction and binding of `phase`, `lapse`, and `phase_anchor`;
- ack validation, including pinned-recipient verification, `acked_msg_id`, `acked_origin_cid`, and route binding; and
- key-storage claims versus the actual runtime boundary. Hardware-backed-key behavior must be treated as **unverified** unless the reviewer receives credible, reproducible platform evidence.

The review should explicitly identify where a reference artifact implements a diagnostic format or another protocol version rather than the v1.1 signing/CID domain.

### 4.2 Protocol conformance

Map each relevant `MUST` and `MUST NOT` in `spec/PHARO-LAPSE-v1.1.0.md` to one of: **implemented and evidenced**, **implemented but untested**, **specified only**, **not implemented**, **ambiguous**, or **not applicable**. At minimum, inspect:

- direct v1.0-compatible behavior when v1.1 extensions are absent;
- v1.1 extension presence/defaulting rules and unsupported-extension handling;
- envelope field validation, body limit, message type, recipient match, and canonical object parsing;
- origin and current CID verification at every appropriate endpoint;
- persistent final-recipient dedup by `msg_id` and transit dedup by (`msg_id`, `origin_cid`);
- monotonic lapse/replay checks and duplicate exception ordering;
- route-history origin, uniqueness, loop prevention, `max_hops` interpretation, and deterministic route selection;
- forwarding-record verification, atomic persistence, stable `origin_cid`, and changed current `cid` after a relay;
- queue state transitions, retry timing, TTL/attempt terminal behavior, crash recovery, and cached acknowledgments; and
- all specified failure classes, including `LOOP_DETECTED`, `MAX_HOPS_EXCEEDED`, `INVALID_ORIGIN`, `INVALID_FORWARDING_RECORD`, and `NO_ROUTE`.

A reviewer should call out any mismatch between v1.1 normative requirements and the available reference artifacts. Absence of a multi-hop implementation or executable v1.1 harness is a finding or coverage gap, not evidence of conformance.

### 4.3 Test coverage and testability

Assess whether executable tests exist, are independently runnable, and adequately exercise the v1.1 test requirements. The review should seek or recommend deterministic negative and boundary tests for:

1. v1.0-compatible direct delivery without extensions;
2. phase-anchor mismatch;
3. mutation of body, phase, lapse, and hop budget after origin signing;
4. one-relay forwarding with stable `origin_cid` and updated current `cid`;
5. invalid forwarding signatures;
6. repeated-peer route rejection;
7. hop-budget rejection, including off-by-one cases;
8. transit crash recovery without duplicate forwarding;
9. final-recipient duplicate delivery with a cached ack;
10. deterministic route selection and tie breaking;
11. `via_peer_ids` parsing and malformed registry handling; and
12. historical-gate-equivalent direct delivery under v1.1 semantics.

Test review should also consider malformed JSON, duplicate JSON keys, non-UTF-8 or problematic Unicode input, oversized bodies, invalid base64, invalid UUID/time/lapse values, empty and maximal route histories, concurrency/race behavior, interrupted writes, database errors, timeouts, unexpected HTTP responses, ack substitution, replay, and resource exhaustion.

**Evidence boundary:** Tests run solely by a reviewer in a local environment may establish only the stated local result. A live v1.1 gate result requires the evidence called for by the specification: commit hash, test command, environment, message IDs, CIDs, route history, and UTC timestamps. This SOW does not claim any such result exists.

### 4.4 Error handling and failure behavior

Review input rejection, state preservation, error classification, and safe recovery. In particular, determine whether invalid inputs can cause an accepted application action, unintended state mutation, data loss, duplicate forwarding, misleading success, or unsafe diagnostic disclosure.

Expected review questions include:

- Are parser, validation, cryptographic, network, storage, and timeout failures distinguishable where required?
- Does a failed validation happen before application processing and before durable mutation where the specification requires it?
- Are dedup lookups safe against adversarial `msg_id` values and do they return only a valid cached result?
- Are `inflight` recovery, expiry, retry counter, and terminal transitions atomic enough for the stated guarantee?
- Can a malformed or spoofed ack incorrectly mark an outbox entry `acked`?
- Does a relay preserve a pending item on `NO_ROUTE` and prevent a second forwarding action after interruption?
- Are exception messages, logs, and HTTP errors bounded and free of secret material?

The report should separate an observed behavior from an inference made by source inspection.

### 4.5 Injection and untrusted-input surface

Evaluate all inputs that may be attacker-controlled or operationally untrusted, including envelope JSON, ack JSON, forwarding records, peer registry values, peer IDs, route fields, timestamps, public keys, base64 signatures, HTTP headers/body framing, SQLite values, configuration/environment values, and any subprocess or filesystem paths.

At minimum, look for:

- JSON duplicate-key differentials, parser inconsistencies, recursive/deep documents, oversized arrays/strings, and canonicalization differentials;
- SQL injection or unsafe dynamic SQL; parameter binding alone should be verified in relevant paths;
- command injection through peer IDs, host/port values, environment variables, or subprocess arguments;
- SSRF, host/port validation gaps, unsafe redirects, unexpected URL schemes, and DNS/overlay identity confusion;
- path traversal, insecure file permissions, accidental private-key exposure, and unsafe temporary-file behavior;
- log injection, response splitting, error-oracle leakage, and excessive diagnostic output;
- denial-of-service paths: expensive verification before cheap filters, unbounded queue/database growth, retry amplification, connection exhaustion, and amplification via cached responses; and
- dependency and transport assumptions, including the explicit non-goal that protocol confidentiality is provided by the transport layer rather than by this envelope format.

A reviewer must not perform intrusive testing against systems, addresses, credentials, or people that have not been explicitly authorized in writing. Default review work is offline/local and non-destructive.

## 5. Out of scope unless separately authorized

The following are excluded from this SOW unless a later written authorization specifies an environment, time window, and safety controls:

- production, field, or live-network testing;
- contacting peers, organizations, faculty, vendors, or third parties;
- deployment, configuration changes, key rotation, or data migration;
- destructive testing, load testing, denial-of-service testing, social engineering, phishing, or physical testing;
- legal, regulatory, export-control, privacy, accessibility, procurement, insurance, or formal certification advice;
- claims about hardware-security-module protection without platform-specific evidence; and
- review of applications or infrastructure outside the supplied repository/revision.

## 6. Reviewer method and rules of engagement

1. Work from a named repository revision or supplied archive and record any local modifications.
2. Prefer static analysis and deterministic local tests first. Describe each command that materially supports a finding.
3. Do not use real private keys, production peer pins, personal data, or non-public endpoints. Use reviewer-generated or explicitly provided test material only.
4. Do not open listeners to the public internet or contact a remote endpoint unless separately authorized.
5. Preserve minimal reproductions; redact secrets from reports, logs, patches, and screenshots.
6. Rate findings using a stated severity rubric and include preconditions, impact, confidence, and remediation direction.
7. State limitations, unavailable dependencies, and unperformed test categories explicitly as **PENDING** or **BLOCKED** with their dependency.

## 7. Deliverables

A completed review, if independently accepted by a reviewer, should provide the following deliverables. These are requested outputs, not outputs already received.

| Deliverable | Minimum content |
|---|---|
| Review report | Scope, repository revision, reviewer method, limitations, summary, and a finding table. |
| Requirement traceability matrix | v1.1 requirement/rule, evidence inspected, status, gap, and recommended next action. |
| Finding records | Identifier, severity, affected path/version, preconditions, impact, evidence or minimal reproduction, confidence, remediation direction, and retest status. |
| Test-coverage assessment | Existing runnable tests, tests attempted, results actually observed, gaps, and recommended additions. |
| Injection-surface assessment | Inputs examined, trust boundary, mitigations observed, residual risk, and tests not performed. |
| Reproduction material | Non-secret commands, test vectors, or patch/diff sufficient to reproduce a reported defect where feasible. |
| Reviewer declaration | Conflicts/limitations, whether work was static-only or included authorized local execution, and an explicit statement that no unauthorized live activity was performed. |
| Close-out note | Open, accepted, disputed, deferred, and unverified findings; no blanket security certification. |

An optional patch is welcome but is neither required nor authority to merge, deploy, or change the protocol.

## 8. Acceptance criteria for the review deliverable

The author may accept a review deliverable when all of the following are present:

1. The reviewed revision or archive is uniquely identified.
2. The report states the actual methods used and the work not performed.
3. Every finding is actionable or explains why evidence is insufficient.
4. Material claims cite a path, requirement, test command, test vector, or reasoned analysis sufficient for another technical reader to evaluate them.
5. The requirement traceability matrix covers the eight objectives in Section 2, or marks an item **PENDING**/**BLOCKED** with its specific dependency.
6. Test results are labeled as local/static/live exactly as performed; historical receipts are not relabeled as new runs.
7. No report includes secrets, private keys, sensitive peer data, or unapproved personal information.
8. No acceptance is conditioned on a “no vulnerabilities found” conclusion, a positive security certification, deployment, or public endorsement.

Acceptance of a report means only that it meets this documentation package’s delivery criteria. It does not validate every conclusion and does not authorize disclosure, publication, code changes, payment, or further access.

## 9. Confidentiality, disclosure, and data boundary

This package does **not** itself create an NDA, legal duty of confidentiality, employment relationship, institutional authorization, payment obligation, or permission to disclose findings. Before sharing non-public materials, the author and reviewer must separately agree in writing on confidentiality, retention, ownership, disclosure coordination, and any compensation.

Until such agreement exists, provide only material the author is authorized to share. Do not provide private keys, production credentials, peer registries containing sensitive addresses, personally identifying information, customer data, unpublished vulnerability details, or access to live systems.

Default reporting boundary:

- The reviewer may report findings privately to the author through an agreed channel.
- Public disclosure timing, attribution, and wording require separate mutual agreement.
- Critical findings should be reported promptly through the agreed private channel, with enough sanitized detail to assess impact.
- If no secure reporting channel has been agreed, the external review is **PENDING**; do not transmit sensitive material.
- The reviewer retains independent judgment; the author retains all decisions about remediation and publication unless a separate agreement states otherwise.

## 10. Review variants

All variants use the common technical scope, boundaries, deliverables, and acceptance criteria above. The names below identify possible review paths only. They do not assert availability, interest, affiliation, authorization, expertise, or contact.

### Variant A — Respectech (Ukiah)

**Prospective audience:** Respectech (Ukiah), if an authorized representative independently elects to consider the request.

**Recommended emphasis:** Practical software/security review of cryptographic boundary, input validation, durable-state failure modes, and implementation/specification gaps. The author should request a written confirmation of the reviewer’s role, scope, availability, fee (if any), and conflict status before sharing any non-public materials.

**Package to share initially:** This SOW, public repository link or a read-only archive, and a specific revision identifier. Do not infer that a review, partnership, service offering, or endorsement exists.

**Variant-specific dependency:** **PENDING —** an authorized Respectech representative must independently agree to review scope, terms, secure-reporting channel, and confidentiality boundary.

### Variant B — Mendocino College CS faculty

**Prospective audience:** A Mendocino College computer-science faculty member, only if that individual independently elects to consider the request in a personal or institutionally authorized capacity.

**Recommended emphasis:** Educational peer review of protocol specification clarity, threat-model reasoning, reproducible test design, canonicalization pitfalls, and requirement traceability. The reviewer should state whether the work is personal, pedagogical, or institutionally authorized; no institutional endorsement should be implied.

**Package to share initially:** This SOW, public repository link or a read-only archive, a revision identifier, and a request for an independent technical critique rather than certification. Do not use student work, institutional systems, or non-public information without explicit authorization.

**Variant-specific dependency:** **PENDING —** an individual reviewer must voluntarily agree, disclose the appropriate capacity/conflicts, and establish any required institutional and confidentiality permissions.

### Variant C — Anonymous public reviewer

**Prospective audience:** An unidentified member of the public who independently chooses to inspect public materials.

**Recommended emphasis:** Public, reproducible review using only intentionally published artifacts. Encourage concrete issue reports, requirement citations, sanitized test vectors, and minimal reproductions. Anonymous feedback may be useful but should be independently verified before action.

**Package to share initially:** Only content deliberately made public, this SOW, a revision identifier, and a public issue/disclosure path that the author intentionally establishes. No private material, credentials, live endpoints, or personal data should be solicited or accepted through an insecure channel.

**Variant-specific dependency:** **PENDING —** the author must intentionally publish the selected material and establish a safe, monitored public reporting path. No anonymous review is claimed or expected.

## 11. Intake checklist before any review begins

| Check | Required disposition before sharing non-public material |
|---|---|
| Repository revision/archive identified | Required |
| Reviewer identity or permitted anonymous process understood | Required |
| Scope, authorization, and non-destructive method agreed | Required |
| Confidentiality/disclosure terms agreed if needed | Required |
| Secure reporting channel defined | Required for non-public or sensitive findings |
| Sensitive materials excluded or redacted | Required |
| Live test access explicitly authorized | Required only if live testing is proposed |
| Contact/engagement confirmation | **Not present in this package** |

## 12. Current package status

| Item | State | Specific dependency / evidence |
|---|---|---|
| Review SOW drafted | **PREPARED** | This document is available in the repository review package. |
| External reviewer selected or contacted | **PENDING** | Requires author-directed outreach; no contact was made for this package. |
| Respectech (Ukiah) review | **PENDING** | Requires independent agreement by an authorized representative. |
| Mendocino College CS faculty review | **PENDING** | Requires voluntary, appropriately authorized agreement by an individual faculty reviewer. |
| Anonymous public review | **PENDING** | Requires intentional publication and a safe public reporting path. |
| Confidentiality terms | **PENDING** | Requires a separate agreement if non-public material will be shared. |
| External review findings | **PENDING** | Requires an actual completed review and report. |
| Live v1.1 test evidence | **BLOCKED** | Requires executable v1.1 harness, authorized environment, and the specification-required live evidence; this SOW creates none. |

---

**End of REVIEW-SOW-v1.0**
