# Coverage Freshness R0

This directory defines the source authority and publication freshness contract for My-TW-Coverage.

## Authority

- TWSE OpenAPI / MOPS are PRIMARY for TWSE listings, disclosures, monthly revenue, and filed financial statements.
- TPEx is PRIMARY for OTC market truth. The R0 registry deliberately marks the TPEx machine adapter as pending rather than pretending yfinance is official.
- yfinance is SECONDARY only. It may support operational snapshots, but it must not silently override a PRIMARY source.

## Commands

Audit current report freshness:

```bash
python scripts/freshness.py
python scripts/freshness.py Pilot_Reports/Semiconductors/2330_台積電.md --claim supply_chain_claim
```

Discover only tickers affected by recent official events:

```bash
python scripts/event_census.py --since 2026-10-01
python scripts/event_census.py --since 2026-10-01 --output /tmp/tw-census.json
```

The census is read-only and fail-closed. If a required source cannot be checked, `complete=false` and the process exits non-zero. A zero-event census is only trustworthy when all required census sources were checked successfully.

## R0 boundary

R0 does not bulk-rewrite 1,700+ reports. It produces an affected-ticker set and deterministic actions such as `refresh_financials` or `revalidate_supply_chain`. The next layer may invoke existing targeted updaters only for those tickers.

The publication gate is claim-scoped: a supply-chain article must have fresh supply-chain evidence; a valuation claim must have fresh valuation evidence. Existing legacy reports with no verification marker intentionally evaluate as `UNKNOWN` rather than being assumed current.
