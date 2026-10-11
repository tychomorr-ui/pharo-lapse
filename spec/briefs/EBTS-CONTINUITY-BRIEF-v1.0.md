# EBTS Continuity Brief

**Version:** 1.0
**Dimension:** 6 — EBTS continuity
**Status:** **PENDING integration; regulatory-mandate claim BLOCKED**
**Date:** 11 October 2026

## Continuity problem

SNAP benefits are delivered through Electronic Benefit Transfer (EBT) cards. A disruption, fraudulent transaction, or prolonged inability to recover an account can prevent a household from purchasing food. GAO reported more than $320 million in reported stolen SNAP benefits and found that USDA had not comprehensively assessed State prevention measures. [1] USDA describes skimming as copying EBT-card information at an ATM or retailer reader, followed by card cloning and fraudulent purchases. [2]

This brief considers a narrow candidate role for the PHARO-LAPSE/NEXINUS pattern: a **continuity-evidence channel** for non-benefit-authorizing operational messages between approved parties. It is not an EBT authorization network, payment processor, consumer portal, benefits ledger, or EBT-contractor replacement. No SNAP data connection, State/retailer/processor interface, deployment, pilot, live test, or operational result exists for this Dimension.

## Public regulatory context

The current public baseline includes **7 CFR § 274.8**, which requires a separate EBT security component in the State agency's Automated Data Processing security program and periodic EBT risk analyses, including vulnerability to theft. [3] The candidate pattern below does not demonstrate compliance with that rule.

The named **Enhanced Cybersecurity for SNAP Act of 2026** is verifiable: Congress.gov lists **S. 3949** and **H.R. 7658** under that title, but both are **Introduced**, not enacted. [4] [5] **Regulatory-mandate claim — BLOCKED.** The introduced Senate text is a proposal, not current law, final regulation, or an implemented Federal requirement. If enacted, it would direct cybersecurity and digital-service rules covering such items as chip cards, interfaces and transaction alerts, fraud reporting, online-transaction security, and replacement-card timing. [6] The bill's NIST PIN/password reference is not a control mapping for this repository; NIST guidance must be applied to the actual authentication architecture. [7]

## Technical fit: a bounded continuity-evidence pattern

The fit is **message continuity and evidence integrity**, not payment authorization. Historical receipts describe local-overlay transport; an Ed25519-signed message and acknowledgement; a durable sender queue that survives restart; and a receiver inbox that returns a cached acknowledgement for a duplicate identifier. Subject to owner approval, those ideas could support incident handoffs, processor-status notices, or recovery-workflow evidence.

The channel would remain outside the cardholder payment path. A minimal envelope could contain a non-sensitive event reference, identities, message ID, payload hash, timestamp, retry state, and acknowledgement reference. It must not copy household data, card data, PINs, authentication secrets, or full transaction data simply for continuity. The proposed properties do not establish end-to-end exactly-once EBT business processing, availability, recovery objectives, capacity, geographic resilience, cryptographic validation, or security authorization.

NIST frames cyber resiliency as anticipating, withstanding, recovering from, and adapting to adverse conditions; its constructs are engineering guidance, not certification. [8] Contingency planning is likewise an operational planning activity. [9]

## Integration path and decision gates

1. **Authorize and bound the use case.** A State or processor owner would select a non-payment message and exclude benefit authorization, balance changes, card issuance, and adjudication.
2. **Set controls.** The owner would approve data classification, source/destination systems, identity and key custody, encryption/signing, retention, audit, and incident handling. This is **PENDING**: no owner, authorization, identity, key material, or EBT environment is available.
3. **Specify and test.** An approved adapter would emit a minimal event reference; the receiver would authenticate, validate, deduplicate, and acknowledge it. Use approved synthetic data in a non-production environment to test loss, retry, restart, malformed messages, key rotation, duplication, and recovery. No such test occurred.
4. **Assess the implementation.** A qualified authority—not this brief—would map the implemented service to 7 CFR § 274.8, applicable agency and State requirements, processor commitments, privacy obligations, and any future rules. A compliance determination is **BLOCKED** without scope, implementation, and authorized assessment.

## Compliance value and limits

If authorized and implemented, the pattern could provide reviewable evidence that a designated operational message was accepted, retried, acknowledged, or deduplicated. That can support an outage investigation or continuity exercise. Its value is **potential evidence support**, not automatic compliance.

It does not replace controls for card fraud, chip issuance, terminals, online merchants, authentication, fraud monitoring, accessibility, reporting, or benefit replacement. It cannot show compliance with 7 CFR § 274.8 or with the introduced Act.

**Current status list**

- **LIVE:** This brief and its static, cited description exist in the repository after validation.
- **PENDING:** Authorized use case; EBT owner; system/data boundary; interface agreement; key management; approved non-production environment; privacy and security review; integration; and controlled testing.
- **BLOCKED:** A claim that the Enhanced Cybersecurity for SNAP Act of 2026 currently mandates requirements; a claim of EBT/SNAP regulatory compliance; and any claim of a live EBT deployment, telemetry, processor relationship, retailer relationship, benefit result, or certification. Each requires facts and authority not available in this task.

## Appendix — historical Gate 3–6 receipt mapping

The following are **historical repository receipts dated 9 October 2026**. They are referenced as narrow engineering evidence only. This appendix does not modify them, rerun them, or relabel them as fresh `PHARO-LAPSE-1.1.0` results.


- **Gate 3 — `tests/GATE-3-RECEIPT-WANLESS.md`:** HTTP crossed a local WireGuard tunnel without public internet. It informs local encrypted-overlay feasibility only; it involved two nearby devices, not an EBT integration.
- **Gate 4 — `tests/GATE-4-RECEIPT-SIGNED-ACK.md`:** An Ed25519-signed envelope and acknowledgement had pinned-key verification. It informs a candidate evidence envelope only; it was a standalone probe, not browser CID or an EBT endpoint.
- **Gate 5 — `tests/GATE-5-RECEIPT-PHARO-GAP.md`:** A SQLite/WAL queue survived restart and later delivered after path restoration. It informs sender persistence and recovery, not deduplication, exactly-once semantics, or multihop.
- **Gate 6 — `tests/GATE-6-RECEIPT-EXACTLY-ONCE.md`:** A persistent inbox returned a cached acknowledgement for duplicate IDs. It informs candidate receiver idempotency, not EBT business processing or a v1.1.0 execution.

No receipt is evidence of SNAP data handling, payment authorization, card security, production availability, compliance, a live pilot, or a new test result.

## References

[1]: https://www.gao.gov/products/gao-25-107964 "GAO: USDA Should Comprehensively Assess Benefit Theft Prevention Measures States Are Implementing"

[2]: https://www.fna.usda.gov/snap/stolen-benefits "USDA Food and Nutrition Administration: Addressing Stolen SNAP Benefits"

[3]: https://www.ecfr.gov/current/title-7/subtitle-B/chapter-II/subchapter-C/part-274/section-274.8 "7 CFR § 274.8: Functional and Technical EBT System Requirements"

[4]: https://www.congress.gov/bill/119th-congress/senate-bill/3949 "Congress.gov: S. 3949, Enhanced Cybersecurity for SNAP Act of 2026"

[5]: https://www.congress.gov/bill/119th-congress/house-bill/7658 "Congress.gov: H.R. 7658, Enhanced Cybersecurity for SNAP Act of 2026"

[6]: https://www.congress.gov/119/bills/s3949/BILLS-119s3949is.htm "S. 3949 Introduced in Senate Text"

[7]: https://pages.nist.gov/800-63-4/sp800-63b.html "NIST SP 800-63B: Digital Identity Guidelines, Authentication and Authenticator Management"

[8]: https://csrc.nist.gov/pubs/sp/800/160/v2/r1/final "NIST SP 800-160 Volume 2 Revision 1: Developing Cyber-Resilient Systems"

[9]: https://csrc.nist.gov/pubs/sp/800/34/r1/upd1/final "NIST SP 800-34 Revision 1: Contingency Planning Guide for Federal Information Systems"
