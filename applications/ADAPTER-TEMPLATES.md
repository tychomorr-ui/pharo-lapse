# Dimension 5 Product Adapter Templates

These four templates implement the repository's proposed adapter boundary. They do not claim to implement any existing PD Pro, Task Force Pro, Recovery, or IWA Sage API.

Each template supports:

```text
pharo-lapse-outbox --product-id <product> --mode offline-reference-demo --output <path>
```

The adapter reads an operator-supplied payload file and writes exactly:

```json
{
  "product_id": "<product>",
  "body": "<operator-supplied text>"
}
```

The body must be UTF-8 text between 1 and 4096 characters. If the required payload-file environment variable is missing, the adapter exits with `BLOCKED` and creates no output. It never generates a product event, user record, recipient peer ID, public key, message ID, receipt, or telemetry.

| Product | Template | Required payload variable |
|---|---|---|
| PD Pro | `pd-pro/adapter-template.py` | `PD_PRO_PAYLOAD_FILE` |
| Task Force Pro | `task-force-pro/adapter-template.py` | `TASK_FORCE_PRO_PAYLOAD_FILE` |
| Recovery | `recovery/adapter-template.py` | `RECOVERY_PAYLOAD_FILE` |
| IWA Sage | `iwa-sage/adapter-template.py` | `IWA_SAGE_PAYLOAD_FILE` |

## Replace only the product boundary

Implement `load_authorized_payload()` using the product's real, operator-approved API or event source. Preserve the output contract and length check. Do not add recipient selection, key generation, queue writes, or receipt creation to the adapter; those belong to the Pharo-Lapse integration and operator configuration.

## Example invocation with a real operator-owned payload file

```bash
export PD_PRO_PAYLOAD_FILE=/absolute/path/to/operator-approved/pd-pro-payload.txt
python3 applications/pd-pro/adapter-template.py \
  pharo-lapse-outbox \
  --product-id pd-pro \
  --mode offline-reference-demo \
  --output /absolute/path/to/pd-pro-adapter-output.json
```

The example deliberately uses a placeholder path rather than a fabricated payload. The command is not a live product demonstration until the operator supplies a real payload source and authorized recipient configuration.
