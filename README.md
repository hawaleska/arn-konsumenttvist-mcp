# ARN Konsumenttvist MCP

MCP server for searching and analyzing decisions from the Swedish National Board for Consumer Disputes (Allmänna reklamationsnämnden, ARN).

ARN Konsumenttvist MCP gives AI assistants access to Swedish consumer-dispute decision data through the Model Context Protocol (MCP).

## What it can do

- Search ARN decisions
- Retrieve individual decisions
- Search for companies
- Read company-related decisions
- Search and read decisions in a combined operation
- Find similar ARN cases
- Work with consumer-dispute information through AI assistants

## MCP tools

- `arn_create_subscription`
- `arn_cancel_subscription`
- `arn_search`
- `arn_get_decision`
- `arn_search_and_read`
- `arn_search_company`
- `arn_search_company_and_read`
- `arn_similar_cases`

## Access and pricing

New users receive 10 free searches.

After the free searches have been used, an active subscription is required.

- Monthly: 59 SEK/month
- Annual: 590 SEK/year

Payments and subscriptions are handled through PayPal.

## MCP access

ARN Konsumenttvist MCP uses the Model Context Protocol with Streamable HTTP.

Authentication is required.

The public service endpoint will be published separately.

## Example use cases

- "Has ARN previously handled cases like this?"
- "Find ARN decisions involving this company."
- "Show similar consumer disputes."
- "What did ARN decide in this case?"
- "Find Swedish ARN cases concerning this type of consumer problem."

## Intended users

- Consumers
- AI assistants
- Developers building AI applications
- Legal and consumer-information tools
- Researchers
- Businesses analyzing consumer disputes

## Technology

- Model Context Protocol (MCP)
- Streamable HTTP
- Python
- SQLite
- PayPal subscription billing

## Status

ARN Konsumenttvist MCP is an actively developed commercial MCP service.

## Copyright

© 2026 Kim Hawaleska. All rights reserved.

ARN Konsumenttvist MCP, including its source code, software architecture, tool implementations, documentation and related materials, is proprietary software unless otherwise stated.

The ARN Konsumenttvist MCP service is provided commercially.

Unauthorized copying, redistribution, resale, modification or commercial use of the software is not permitted without prior written permission.

The underlying ARN decision data is not claimed as proprietary by this project. This project does not claim ownership of decisions issued by Allmänna reklamationsnämnden (ARN).

## Disclaimer

ARN Konsumenttvist MCP is an information and search service.

The service does not provide legal advice and should not be considered a substitute for professional legal advice.

Information retrieved through the service should be independently verified before being relied upon for legal, financial or other important decisions.

## Contact

hawaleska@gmail.com
