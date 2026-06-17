# SP Project — Field IDs

Use these IDs in `additional_fields` when calling `jira_create_issue` or `jira_update_issue`.
Verify or discover values dynamically with `jira_search_fields` + `jira_get_field_options`.

## Issue types

| Name | ID |
|---|---|
| Story | `10000` |
| Task | `10001` |
| Sub-task | `10002` |
| Bug | `10003` |
| Epic | `10004` |

## Priority

| Name | ID |
|---|---|
| P1 | `1` |
| P2 | `2` |
| P3 | `3` |
| P4 | `4` |

## Pod (`customfield_10988`)

| Name | ID |
|---|---|
| Audit | `13806` |
| Booking 99 | `11000` |
| DevOps | `13598` |
| Dynamic Insights | `13773` |
| Firefighting | `13600` |
| Integrations | `13599` |
| Placeholder Pod | `13740` |
| Profile & Search | `11001` |
| Reporting & Insights | `11002` |
| Skills | `13739` |
| Squirtle Squad | `13938` |

## Environment (`customfield_10598`)

| Name | ID |
|---|---|
| Master | `10328` |
| Integration | `10317` |
| UAT | `10261` |
| Production | `10260` |
| Preview Environments | `11252` |

## Requires Documentation (`customfield_10694`)

| Name | ID |
|---|---|
| New | `10600` |
| Change To Existing | `10601` |
| None Required | `11070` |

## Source / Category (`customfield_11021`)

| Name | ID |
|---|---|
| Product Roadmap | `11136` |
| Product Roadmap (Customer Driven) | `11138` |
| Product Roadmap (Unplanned) | `12155` |
| Tech Roadmap | `11141` |
| Technical Debt | `11140` |
| Development Task | `11143` |
| Customer Task | `11142` |
| Customer Specific Change (CR) | `11137` |
| Customer Specific Change (Unplanned) | `12156` |
| Product Gap | `11139` |
| Firefighting | `11536` |
| Regression (Existing) | `11499` |
| Regression (Quarterly Work) | `11744` |

## Fix Versions (`fixVersions`)

| Name | ID |
|---|---|
| 2026 Q1 Release | `10419` |
| 2026 Q2 Release | `10420` |
| 2026 Q3 Release | `10421` |
| 2026 Q4 Release | `10422` |
| 2027 Q1 Release | `10489` |
| 2027 Q2 Release | `10490` |
| 2027 Q3 Release | `10491` |
| 2027 Q4 Release | `10492` |

Pick the version matching the current quarter.
