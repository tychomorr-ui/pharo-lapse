# Emergency Communications Pilot Package
## PHARO-LAPSE — Fire / Wildland / All-Hazards Use

**Package version:** 1.0
**Package status:** **PENDING — operator-fillable; not an authorization, award, contract, deployment record, or results report**
**Prepared for:** `[AGENCY LEGAL NAME — OPERATOR TO COMPLETE]`
**Prepared date:** `[DATE — OPERATOR TO COMPLETE]`
**Pilot window:** `[START DATE]` through `[END DATE]` (proposed 90-day window; operator to confirm)
**Agency pilot owner:** `[NAME / TITLE — OPERATOR TO COMPLETE]`
**PHARO-LAPSE project contact:** `[NAME / ORGANIZATION / EMAIL / PHONE — OPERATOR TO COMPLETE]`

---

## 1. Purpose and package boundary

This package provides a proposed, operator-fillable structure for a limited emergency-communications pilot using the PHARO-LAPSE protocol. It is intended to help an authorized agency decide whether to evaluate store-and-forward, signed message delivery when ordinary connectivity is intermittent or unavailable.

PHARO-LAPSE is specified as a store-and-forward messaging protocol that uses durable queues, signed envelopes, pinned peer identities, acknowledgement handling, and recipient-side duplicate suppression. It is designed to operate above an available IP carrier or local overlay; it does **not** itself provide a radio carrier, public-safety dispatch service, continuous connectivity, confidentiality, real-time delivery, or emergency response authority.

> **No live pilot is represented by this package.** No agency has been named, contacted, enrolled, awarded, contracted, or deployed through this document. No operational message, test, telemetry, receipt, or outcome is claimed.

### 1.1 Proposed pilot scope — complete before release

| Field | Operator entry / decision |
|---|---|
| Agency legal name | `[PENDING — OPERATOR TO COMPLETE]` |
| Unit / jurisdiction / incident context | `[PENDING — OPERATOR TO COMPLETE]` |
| Authorized pilot purpose | `[PENDING — OPERATOR TO COMPLETE]` |
| Included use cases | `[PENDING — OPERATOR TO COMPLETE]` |
| Explicit exclusions | `[PENDING — OPERATOR TO COMPLETE]` |
| Pilot start and end dates | `[PENDING — OPERATOR TO COMPLETE]` |
| Number and type of devices | `[PENDING — OPERATOR TO COMPLETE]` |
| Approved transport / overlay | `[PENDING — OPERATOR TO COMPLETE]` |
| Pilot location(s) | `[PENDING — OPERATOR TO COMPLETE]` |
| Data classification and records schedule | `[PENDING — AGENCY REVIEW REQUIRED]` |
| Safety officer / incident-command coordination | `[PENDING — AGENCY ASSIGNMENT REQUIRED]` |
| Go / no-go authority | `[PENDING — AGENCY ASSIGNMENT REQUIRED]` |

### 1.2 Pilot guardrails

- The agency retains command authority, dispatch authority, safety authority, and all decisions about operational use.
- PHARO-LAPSE **MUST NOT** be represented as a replacement for 911, dispatch, radio, satellite, cellular, or any agency-required primary or backup communications path unless the agency separately authorizes that use in writing.
- Pilot messages **MUST NOT** be relied on for time-critical life-safety action until the agency's authorized go/no-go authority has approved the applicable use case.
- The pilot begins only after the pre-deployment checklist is complete, required approvals are documented, and a designated operator records a go decision.
- The agency may pause or stop the pilot at any time. A stop decision takes precedence over pilot success targets.
- This package does not grant access to facilities, systems, networks, records, personal information, or controlled information.

---

## 2. Fillable letter of intent

> **Send only after completion and signature by an authorized agency representative.** This template expresses an interest in evaluating a pilot; it is not a purchase order, contract, grant award, authorization to operate, security approval, or commitment to procure.

**[AGENCY LETTERHEAD, IF USED]**

`[DATE]`

`[RECIPIENT NAME / ORGANIZATION]`
`[RECIPIENT ADDRESS OR EMAIL]`

**Subject: Non-binding letter of intent — PHARO-LAPSE emergency communications pilot evaluation**

To whom it may concern:

`[AGENCY LEGAL NAME]` is considering a limited evaluation of PHARO-LAPSE for the following proposed purpose: `[DESCRIBE PROPOSED PILOT PURPOSE AND USE CASE]`.

Subject to the agency's applicable legal, procurement, security, safety, records, and operational approvals, the agency intends to evaluate a proposed pilot during `[PROPOSED START DATE]` through `[PROPOSED END DATE]` at `[PROPOSED LOCATION / JURISDICTION]`. The proposed pilot scope is limited to `[DEVICES / PARTICIPANTS / USE CASES]` and excludes `[EXCLUSIONS]`.

Before any operational use, the parties will document the approved scope, responsible roles, communication fallback procedures, data handling requirements, stop authority, evaluation measures, and closeout process. This letter does not authorize access to agency systems or data and does not authorize live deployment.

This letter is non-binding except to the extent that a subsequently executed written instrument expressly states otherwise. No contract, award, procurement action, deployment, or result is implied by this letter.

Sincerely,

| Agency authorization field | Operator entry |
|---|---|
| Authorized representative name | `[OPERATOR TO COMPLETE]` |
| Title | `[OPERATOR TO COMPLETE]` |
| Signature | `[OPERATOR TO COMPLETE]` |
| Date signed | `[OPERATOR TO COMPLETE]` |
| Agency reference / file number | `[OPERATOR TO COMPLETE, IF APPLICABLE]` |

**Acknowledgement of receipt (optional; not acceptance):**

| Recipient field | Operator entry |
|---|---|
| Recipient name / organization | `[OPERATOR TO COMPLETE]` |
| Signature or acknowledgement method | `[OPERATOR TO COMPLETE]` |
| Date | `[OPERATOR TO COMPLETE]` |

---

## 3. Deployment checklist

**Checklist status:** **PENDING.** Each item requires a dated entry, evidence reference, and responsible person before an operator marks it complete. A blank or unchecked item is not evidence of completion.

### 3.1 Authorization, scope, and safety

| # | Required item | Status (Complete / N/A / Blocked) | Owner | Date | Evidence / dependency |
|---|---|---|---|---|---|
| A1 | Agency legal name, pilot owner, go/no-go authority, and stop authority are documented. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency assignment required]` |
| A2 | Written pilot scope, exclusions, locations, dates, and participating roles are approved by the agency. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency approval required]` |
| A3 | Safety plan identifies the primary and fallback communications paths and confirms that PHARO-LAPSE is not the sole life-safety path unless separately authorized. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Safety / incident-command review required]` |
| A4 | Privacy, legal, procurement, records, information-security, and labor/union reviews required by the agency are identified and resolved or expressly waived by the authorized agency official. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency review required]` |
| A5 | Incident escalation, safety incident reporting, and pilot-stop procedures are communicated to all pilot participants. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Training / briefing record required]` |

### 3.2 Technical readiness

| # | Required item | Status (Complete / N/A / Blocked) | Owner | Date | Evidence / dependency |
|---|---|---|---|---|---|
| T1 | Device inventory, custody, power plan, charging plan, and physical-security plan are recorded. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Inventory required]` |
| T2 | The approved carrier or local overlay, peer addressing, ports, and network-change controls are documented. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Authorized network design required]` |
| T3 | Each pilot peer has a documented identity, public-key pin exchange method, key backup/revocation procedure, and owner. Private keys are not shared. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Key-management procedure required]` |
| T4 | Durable queue storage, available capacity, restart/recovery procedure, and device time/clock assumptions are documented. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Configuration review required]` |
| T5 | A controlled pre-pilot test plan defines test messages, expected acknowledgements, duplicate-handling observation, failure/recovery observation, acceptance thresholds, and who records evidence. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Approved test plan required; no test result is asserted here]` |
| T6 | The agency authorizes any connection to agency systems, logs, networks, or data. No connection is made merely because this package exists. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Written authorization required]` |

### 3.3 Operating readiness

| # | Required item | Status (Complete / N/A / Blocked) | Owner | Date | Evidence / dependency |
|---|---|---|---|---|---|
| O1 | Participants receive a role-based briefing on intended use, non-use, message priority, manual fallback, and stop authority. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Training record required]` |
| O2 | A message taxonomy is approved (for example: exercise, routine, priority, and prohibited content). | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency operational decision required]` |
| O3 | The agency-approved data handling, retention, access, export, and deletion/return procedure is attached or referenced. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency records/privacy decision required]` |
| O4 | Daily operational check, incident reporting channel, change-control log, and pilot observation log are assigned. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Operator assignment required]` |
| O5 | A pre-start go/no-go review occurs and the designated agency authority records its decision. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Go/no-go record required]` |

### 3.4 Closeout readiness (confirm before starting)

| # | Required item | Status (Complete / N/A / Blocked) | Owner | Date | Evidence / dependency |
|---|---|---|---|---|---|
| C1 | The agency approves the closeout date, data disposition method, device return/custody process, and final review audience. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Agency decision required]` |
| C2 | The pilot evidence register has a location, access owner, and retention period. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Records plan required]` |
| C3 | The exit criteria in Section 5 are reviewed with the agency stop authority and pilot owner. | `[PENDING]` | `[TBD]` | `[TBD]` | `[Acknowledgement required]` |

---

## 4. 90-day success criteria and measurement plan

**Status:** **PROPOSED — no pilot metrics, telemetry, tests, or outcomes exist in this package.** The agency must approve the final baselines, thresholds, sampling periods, and evidence access before Day 1. These criteria evaluate a pilot; they do not establish suitability for emergency dispatch or life-safety use.

### 4.1 Measurement rules

1. **Day 1** is the agency-recorded start of the authorized pilot, not the preparation date of this package.
2. Measurements must identify the use case, device set, approved observation window, test/operational classification, and any connectivity interruption or configuration change relevant to interpretation.
3. A message counts as delivered only under the agency-approved definition and only when the authorized evidence register records the applicable outcome. Do not infer delivery from a lack of complaint.
4. Any unavailable metric, missing log, or unresolved inconsistency is recorded as **PENDING** or **BLOCKED**, not treated as success.
5. Results must distinguish controlled exercises from operational communications. No controlled result may be presented as an operational outcome.

### 4.2 Proposed criteria

| ID | Proposed success criterion | Proposed target / acceptance condition | Evidence to collect | Final threshold / owner | Status now |
|---|---|---|---|---|---|
| S1 | Authorized pilot readiness | 100% of participating devices and roles are on the approved inventory, with completed pre-start go/no-go record. | Inventory, approval, training and go/no-go records. | `[TBD by agency]` | **PENDING** |
| S2 | Controlled message workflow | At least `[TBD]` agency-approved controlled message scenarios are executed across the planned roles and connectivity conditions. | Scenario sheets, timestamps, authorized observation notes, and evidence-register references. | `[TBD by agency]` | **PENDING** |
| S3 | Delivery and acknowledgement observation | For the controlled scenarios, the agency sets a target for messages that reach the approved acknowledgement state within the approved time window; exceptions are reconciled individually. | Approved message ledger, acknowledgement evidence, exception log, and methodology. | `[TBD by agency]` | **PENDING** |
| S4 | Duplicate-processing observation | No duplicate application processing is observed in the agency-approved duplicate/retry test cases, or every observed exception is documented, contained, and adjudicated. | Test procedure, observation record, issue register, and corrective-action record. | `[TBD by agency]` | **PENDING** |
| S5 | Recovery and continuity observation | The agency-approved restart, power-loss, or interrupted-carrier scenarios are performed only if safe and authorized; each result is recorded without assuming recovery. | Approved procedure, authorization, observation record, and exception log. | `[TBD by agency]` | **PENDING** |
| S6 | Operator usability and adherence | At least `[TBD]%` of designated participants complete the agency-approved briefing; feedback and deviations are recorded and reviewed. | Attendance/attestation, survey or debrief form, deviation log. | `[TBD by agency]` | **PENDING** |
| S7 | Data handling and records compliance | 100% of pilot records sampled by the agency conform to the approved access, retention, and disposition plan, or deviations are documented and resolved before closeout. | Access review, retention/disposition log, and remediation record. | `[TBD by agency]` | **PENDING** |
| S8 | Safety and governance | No unresolved safety, privacy, security, or governance stop condition remains at the final review. | Stop-condition register, incident records, approvals, and final review notes. | `[TBD by agency]` | **PENDING** |

### 4.3 Suggested 90-day cadence — proposed only

| Period | Proposed activity | Required decision / record |
|---|---|---|
| Before Day 1 | Complete Sections 1–3, approve measures, and conduct go/no-go review. | Agency authorization or **BLOCKED** status with dependency. |
| Days 1–30 | Onboard, perform only approved controlled scenarios, and record exceptions. | Weekly operator review; safety stop authority remains active. |
| Days 31–60 | Continue approved scenarios; review data handling, workflow adherence, and any change requests. | Midpoint review; agency decides continue, pause, narrow, or stop. |
| Days 61–90 | Complete final approved observations, reconcile exceptions, and prepare closeout materials. | Final review against approved criteria; no result is presumed. |
| After Day 90 | Execute exit/closeout procedures. | Agency disposition and any future decision are separate from this package. |

---

## 5. Exit criteria and stop conditions

### 5.1 Immediate pause / stop triggers

The designated agency stop authority should pause or stop pilot activity when any of the following occurs, subject to agency policy:

- A life-safety, incident-command, or dispatch authority directs a stop.
- PHARO-LAPSE is being used outside the approved scope, including as an unapproved sole communications path.
- A suspected loss, exposure, misuse, or unauthorized access involving pilot data, identity material, device custody, or network access is identified.
- A material message-integrity, acknowledgement, duplicate-processing, queue, or recovery anomaly is observed and cannot be safely bounded.
- An approved device, software, peer identity, network, data classification, or use case changes without required change approval.
- Required oversight, privacy, security, records, safety, or procurement approval expires, is denied, or is withdrawn.
- A participant reports a safety concern requiring investigation.

**Stop record:** `[PENDING — assign location, owner, escalation path, and notification timeline before Day 1]`.

### 5.2 Exit / closeout criteria

| # | Exit criterion | Required closeout record | Status now |
|---|---|---|---|
| E1 | Pilot end date is reached, or agency stop authority ends the pilot earlier. | End/stop decision with date, authority, and reason. | **PENDING** |
| E2 | Agency determines whether any approved pilot activity must cease immediately; all applicable participants are notified. | Communication record and custody status. | **PENDING** |
| E3 | No new pilot messages are initiated after the recorded cutoff, except agency-authorized closeout actions. | Cutoff record and exception approvals. | **PENDING** |
| E4 | Devices, peer access, network credentials, and physical assets are returned, disabled, or retained only as agency-authorized. | Inventory/custody and access-revocation record. | **PENDING** |
| E5 | Pilot queues, logs, exports, and other records are retained, returned, securely deleted, or otherwise disposed of under the agency-approved schedule. | Data disposition certificate or records reference. | **PENDING** |
| E6 | Outstanding exceptions, incidents, and corrective actions are resolved, transferred to an agency owner, or explicitly accepted as open risk. | Issue register disposition. | **PENDING** |
| E7 | Final review distinguishes observed evidence, unobserved claims, limitations, and future recommendations. | Agency final-review record. | **PENDING** |
| E8 | Any continuation, expansion, procurement, or deployment decision is handled through a separate authorized process. | Separate decision record, if any. | **PENDING** |

> Completing the exit checklist does not certify system performance, operational suitability, procurement eligibility, or future deployment. It only documents the agency-approved disposition of the pilot.

---

## 6. Data handling summary

**Status:** **PENDING — agency privacy, security, legal, records, and operational review required before any data is processed.** This summary is a planning baseline, not a data-processing agreement, security authorization, or records-retention schedule.

### 6.1 Data minimization and allowed-data decision

- Collect and transmit only the minimum data the agency explicitly approves for the defined pilot use case.
- Until the agency authorizes otherwise in writing, exclude personally identifiable information, protected health information, criminal justice information, controlled unclassified information, credentials, precise location trails, sensitive operational plans, and any other regulated or agency-restricted data.
- Treat message bodies, message identifiers, timestamps, peer identifiers, acknowledgement metadata, queue state, routing/overlay information, logs, and diagnostic exports as potentially sensitive until the agency classifies them.
- Do not connect pilot devices to agency systems, ingest agency data, or export pilot data to third parties without written agency authorization.

### 6.2 Protocol and configuration considerations

PHARO-LAPSE specifies signed end-to-end envelopes, pinned peer identities, durable queues, acknowledgements, and recipient-side deduplication. It does **not** provide confidentiality by itself; the relevant protocol specification lists confidentiality as a transport-layer concern. Before use, the agency must document and approve the actual transport/overlay, encryption controls, key handling, device hardening, storage protection, access controls, update controls, and logging configuration.

No claim is made here that any pilot device has a hardware-backed key, encryption at rest, approved network overlay, security authorization, or agency system connection.

### 6.3 Proposed handling controls — agency to approve

| Control area | Proposed minimum decision | Status |
|---|---|---|
| Data inventory | Identify each data element, classification, source, purpose, recipient, and whether it is permitted. | **PENDING — agency classification** |
| Access | Name authorized roles; use least privilege; record administrative access and changes. | **PENDING — agency access decision** |
| Identity and keys | Document peer identity ownership, pin exchange, key storage, rotation/revocation, recovery, and loss response. Never share private keys. | **PENDING — key-management approval** |
| In transit | Specify the approved transport/overlay and its encryption/authentication controls; validate only through agency-authorized testing. | **PENDING — network/security approval** |
| At rest | Specify protected storage, device lock, backup limits, queue/log location, and encryption requirements. | **PENDING — security approval** |
| Retention | Set retention by data type and record system; do not retain longer than authorized. | **PENDING — records schedule** |
| Sharing/export | Prohibit external sharing, cloud upload, or third-party processing unless the agency authorizes it in writing. | **PENDING — agency authorization** |
| Incident response | Define reporting channel, containment actions, notification decision-maker, and evidence preservation requirements. | **PENDING — incident plan** |
| Disposition | Define return, transfer, secure deletion, or archival method; record completion. | **PENDING — closeout plan** |

### 6.4 Data subject / records / legal considerations

The agency is responsible for determining applicable public-records, retention, privacy, security, labor, procurement, emergency-management, and other legal obligations. If the proposed pilot includes personnel, incident, patient, victim, juvenile, investigative, critical-infrastructure, or location information, the appropriate agency authority must determine whether it is permitted and under what controls. This package makes no legal compliance determination.

---

## 7. Contacts and escalation

**All contact fields are intentionally blank. No agency contact, project contact, emergency contact, award, or contractual relationship is asserted. Complete and verify these entries through an authorized channel before sending or operating the pilot.**

### 7.1 Agency contacts — operator-fillable

| Role | Name | Organization / unit | Email | Phone / radio | Status |
|---|---|---|---|---|---|
| Executive sponsor | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Pilot owner | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Incident-command liaison | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Safety / stop authority | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Communications / dispatch liaison | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Information security contact | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Privacy / records contact | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Legal / procurement contact | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |

### 7.2 Project-side contacts — operator-fillable

| Role | Name | Organization | Email | Phone | Status |
|---|---|---|---|---|---|
| Project sponsor | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Technical lead | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Security / key-management owner | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| Data-handling owner | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |
| 24-hour operational escalation route | `[OPERATOR TO COMPLETE]` | `[TBD]` | `[TBD]` | `[TBD]` | **PENDING** |

### 7.3 Escalation rule

During an active incident or any life-safety event, personnel must use agency-approved emergency and command channels. This package does not create an emergency contact number or dispatch channel. Record the agency-approved escalation order here before Day 1:

1. `[PENDING — PRIMARY AGENCY-APPROVED CHANNEL]`
2. `[PENDING — FALLBACK AGENCY-APPROVED CHANNEL]`
3. `[PENDING — SAFETY / STOP AUTHORITY]`
4. `[PENDING — PROJECT-SIDE TECHNICAL ESCALATION]`

---

## 8. Release check before sending

A project operator should not send this package as a completed proposal until all recipient-specific fields have been reviewed for accuracy and authorization.

| Check | Release status |
|---|---|
| Agency name and recipient information verified through an authorized source | `[PENDING]` |
| Date, scope, and requested action completed | `[PENDING]` |
| Agency contacts verified and authorized for inclusion | `[PENDING]` |
| No unapproved operational, legal, security, performance, deployment, award, contract, or results claims remain | `[PENDING]` |
| Authorized project representative approves external release | `[PENDING]` |

---

## Appendix A — Evidence register template

Use this register only after an agency authorizes the pilot. Entries should describe what was observed or collected, not what is assumed.

| Evidence ID | Date/time | Activity / scenario | Classification | Custodian | Location / reference | Integrity / access note | Result state |
|---|---|---|---|---|---|---|---|
| `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `PENDING / COMPLETE / BLOCKED` |

## Appendix B — Change-control template

| Change ID | Requested change | Reason | Risk / data / safety impact | Approver | Decision | Effective date | Status |
|---|---|---|---|---|---|---|---|
| `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `[TBD]` | `PENDING / APPROVED / REJECTED` |

---

**Document conclusion:** This is a planning package only. All agency-specific facts, contacts, authorizations, approvals, deployment decisions, observations, and outcomes remain **PENDING** until established by an authorized operator and recorded in the appropriate agency-controlled record.
