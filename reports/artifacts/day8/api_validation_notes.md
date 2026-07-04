# NovaPay API Validation Notes

The `/score` endpoint accepts one transaction at a time and validates the payload with Pydantic before any model inference runs.

## Implemented validation rules

- `transaction_id` and `customer_id` must be present and non-empty.
- `timestamp` must be parseable as a valid datetime.
- Monetary fields such as `amount_src`, `amount_usd`, and `fee` must be non-negative.
- `exchange_rate_src_to_dest` must be greater than zero.
- Risk scores such as `ip_risk_score`, `device_trust_score`, `risk_score_internal`, and `corridor_risk` must stay between 0 and 1.
- Count and velocity fields must be non-negative.
- `new_device` and `location_mismatch` must be booleans.
- Country, currency, channel, device, IP, and KYC fields must be non-empty strings.

## Important scope note

The API validates `ip_address`, country, currency, channel, and KYC fields as required non-empty strings. It does not enforce a fixed allow-list or validate IP address format. This keeps the API aligned with the training data and avoids rejecting categories that the model preprocessing can handle.

## Why these checks matter

These checks prevent invalid or malicious payloads from entering the model pipeline, reduce scoring errors, and improve trust in real-time fraud decisions.
