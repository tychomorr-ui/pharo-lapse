# PHARO-LAPSE DIMENSION 9 RECEIPT
## IETF Internet-Draft candidate

**Date:** 11 October 2026
**Status:** **PENDING_PUBLICATION** — local RFCXML and plaintext candidate prepared and validated; no Datatracker submission, author-email confirmation, acceptance, or public listing was performed.

## Delivered

- `ietf/draft-morris-pharo-lapse-00.xml` — RFCXML v3 source for a local pre-submission candidate named `draft-morris-pharo-lapse-00`.
- `ietf/draft-morris-pharo-lapse-00.txt` — plaintext rendering generated directly from that XML with `xml2rfc 3.34.1`.
- This receipt — the local evidence, source-metadata record, status boundaries, and submission procedure.

The candidate covers the complete local **v1.1.0** specification: identity and pins; canonical JSON; Ed25519 signatures; origin and current CIDs; direct compatibility with v1.0; acks and forwarding records; durable queues, retry, deduplication, and crash recovery; phase/lapse discipline; bounded, loop-free deterministic routing; the peer registry extension; recipient processing; reproducible receipts; test requirements; historical gate mapping; security considerations; and implementation constraints.

It is deliberately marked as a **local pre-submission candidate**. Its RFCXML `ipr` attribute is `none`, rather than an unapproved IETF Trust IPR selection, and the generated text therefore does not claim that an Internet-Draft has been submitted. An authorized contributor must make the IPR decision and supply a verified author contact before an actual submission.

## Public source metadata checked

| Source | Verified metadata / use in candidate |
|---|---|
| [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119.html) | Scott Bradner, *Key words for use in RFCs to Indicate Requirement Levels*, BCP 14 / RFC 2119, March 1997. Normative requirements-language reference. |
| [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html) | Simon Josefsson and Ilari Liusvaara, *Edwards-Curve Digital Signature Algorithm (EdDSA)*, RFC 8032, January 2017. Normative Ed25519 reference. |
| [RFC 7748](https://www.rfc-editor.org/rfc/rfc7748.html) | Adam Langley, Mike Hamburg, and Sean Turner, *Elliptic Curves for Security*, RFC 7748, January 2016. Informative Curve25519 transport context. |
| [WireGuard protocol](https://www.wireguard.com/protocol/) and [technical paper](https://www.wireguard.com/papers/wireguard.pdf) | Official protocol page documents Curve25519/Noise_IK and UDP; the candidate cites Jason A. Donenfeld, *WireGuard: Next Generation Kernel Network Tunnel*, NDSS 2017, as in the v1.1.0 source specification. |
| [OpenTimestamps](https://opentimestamps.org/) | Official site describes independently verifiable timestamp proofs and Bitcoin support. The candidate makes OTS an external, optional provenance mechanism rather than a delivery-validity condition. |
| [CID specification](https://github.com/multiformats/cid) | Public multiformats source describes CIDv1 as a self-describing content-addressed identifier. It supports the v1.1.0 CIDv1/dag-json/sha2-256 terminology. |
| [IETF submission guidance](https://authors.ietf.org/en/submitting-your-internet-draft) | Confirms RFCXML v3 is preferred, plaintext can accompany it, and non-authenticated authors must verify by email before posting. The public submission endpoint is [Datatracker Submit](https://datatracker.ietf.org/submit/). |

A direct public lookup for `draft-morris-pharo-lapse` did not yield a verified Datatracker document. No Datatracker URL is claimed for this candidate.

## Local validation performed

The XML was parsed as well-formed XML, with root `rfc`, `version="3"`, and `docName="draft-morris-pharo-lapse-00"`. The RFCXML v3 formatter completed its preptool run and generated the required text artifact successfully:

```text
xml2rfc --verbose --v3 --text \
  --out ietf/draft-morris-pharo-lapse-00.txt \
  ietf/draft-morris-pharo-lapse-00.xml

Completed preptool run
Created file ietf/draft-morris-pharo-lapse-00.txt
xml2rfc_status=0
```

`xml2rfc 3.34.1` produced a 784-line, 14-page plaintext rendering from the 311-line XML source. Static marker checks confirmed the plaintext includes `RFC 2119`, `RFC 8032`, `RFC 7748`, `WireGuard`, `OpenTimestamps`, `route_history`, `phase_anchor`, `MAX_HOPS_EXCEEDED`, `IANA Considerations`, and `Implementation and Publication Status`.

`idnits` was not installed in this sandbox, and a download attempt at the legacy `https://www.ietf.org/tools/idnits/idnits` location returned HTTP 404. No passing `idnits` result is claimed. The current IETF guidance still recommends an `idnits` check before a real submission; that check remains required after the responsible author selects IPR terms and adds verified contact metadata.

## Exact submission steps — not performed

1. An authorized Tyler Morris/Nexinus contributor must review the IETF Note Well, BCP 78 rights terms, and the current [submission guidance](https://authors.ietf.org/en/submitting-your-internet-draft). They must decide the applicable IPR declaration and provide a verified author email address. Do **not** infer or invent either value.
2. Update the local RFCXML only with the contributor-approved `ipr` value and verified author address. Regenerate the plaintext from that revised XML using `xml2rfc --v3 --text --out ietf/draft-morris-pharo-lapse-00.txt ietf/draft-morris-pharo-lapse-00.xml`.
3. Run the current `idnits` tool against the regenerated plaintext and resolve applicable nits. Also review the draft-name availability and the current submission window at [Datatracker Submit](https://datatracker.ietf.org/submit/).
4. Open <https://datatracker.ietf.org/submit/> in an authorized contributor's browser. Upload the standalone RFCXML v3 file as the authoritative submission; the matching plaintext may be supplied alongside it if desired. Do not upload an archive container.
5. Complete only the metadata, rights, and author assertions that the authorized contributor can truthfully make. Submit through Datatracker.
6. If the submitter is not logged in as a listed author, act on the Datatracker verification email. IETF guidance states that the draft is not accepted and posted until that requested email action is completed. A logged-in listed author can bypass that email step.
7. After acceptance, independently verify the actual Datatracker document page and record its exact URL, submission revision, and posting time. Only then may the draft be described as published or publicly listed.

## LIVE / PENDING / BLOCKED

| Item | State | Evidence / dependency |
|---|---|---|
| RFCXML v3 source candidate | **LIVE** | `ietf/draft-morris-pharo-lapse-00.xml` exists locally and `xml2rfc 3.34.1` completed its preptool run successfully. |
| Plaintext candidate | **LIVE** | `ietf/draft-morris-pharo-lapse-00.txt` was generated from the XML source, not manually transcribed. |
| Required public reference metadata | **LIVE** | The RFC Editor, WireGuard, OpenTimestamps, CID, and IETF guidance sources listed above were read and incorporated as references. |
| IETF Datatracker submission | **BLOCKED** | Requires an authorized contributor to choose IPR terms, provide a verified contact address, complete rights/author assertions, and operate the Datatracker submission flow. No upload was attempted. |
| Email confirmation | **PENDING** | Depends on a real submission by a non-authenticated/non-listed author; no email was sent or received. |
| Public Datatracker page / live publication | **BLOCKED** | No accepted submission and no real Datatracker URL was verified. |
| Fresh v1.1.0 executable gate results | **BLOCKED** | The v1.1.0 source says an executable harness and two-device overlay are required. Historical v1.0 receipts are not presented as current v1.1.0 runs. |
| Repository commit and authenticated push | **PENDING** | Requires review and repository authentication outside this task. |

## Boundary

This receipt proves local artifact creation and local static/RFCXML formatter validation only. It does **not** claim an IETF submission, Datatracker acceptance, live publication, email delivery or confirmation, implementation deployment, live mesh test, telemetry, contract, contact, or protocol result. Existing v1.0/v1.1 specifications, Gate 3–6 receipts, and Cryptochrometer code were not modified.
