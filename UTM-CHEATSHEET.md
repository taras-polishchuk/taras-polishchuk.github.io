# UTM Cheatsheet

Коротка шпаргалка для швидкого копіювання UTM-лінків у CV, нотатки, LinkedIn, Telegram, GitHub і Upwork.

## Base URLs

| Version | URL | Use when |
| --- | --- | --- |
| Frontend | `https://taras-polishchuk.github.io/?ref=frontend` | Frontend roles, recruiters, generic web product outreach |
| Shopify | `https://taras-polishchuk.github.io/` | Shopify roles, agencies, Upwork Shopify clients |

## Naming Rules

| Field | Meaning | Example |
| --- | --- | --- |
| `utm_source` | Platform or source | `linkedin`, `telegram`, `upwork`, `cv`, `github` |
| `utm_medium` | Placement type | `profile`, `dm`, `proposal`, `pdf`, `readme` |
| `utm_campaign` | Goal of the traffic | `portfolio_profile`, `direct_outreach`, `job_application`, `resume_distribution`, `freelance_proposal` |
| `utm_content` | Specific context | `featured_link`, `anna_epam`, `shopify_theme_support` |

Use lowercase only. Prefer underscores instead of spaces.

## Ready Templates

| Channel | Recommended use | Ready URL |
| --- | --- | --- |
| LinkedIn profile | Featured link in profile | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=featured_link` |
| LinkedIn DM | Recruiter or hiring manager outreach | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=dm&utm_campaign=direct_outreach&utm_content=[recruiter_or_company]` |
| Telegram bio | Public profile link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=bio&utm_campaign=portfolio_profile&utm_content=public_profile` |
| Telegram DM | Personal outreach | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=dm&utm_campaign=direct_outreach&utm_content=[person_or_company]` |
| Upwork proposal | Shopify freelance proposal | `https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=proposal&utm_campaign=freelance_proposal&utm_content=[client_or_job_slug]` |
| Upwork follow-up | Message after proposal | `https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=message&utm_campaign=freelance_followup&utm_content=[client_or_job_slug]` |
| CV PDF | Frontend CV link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=[company_role]` |
| CV PDF Shopify | Shopify CV link | `https://taras-polishchuk.github.io/?utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=[company_role]` |
| GitHub profile | Profile README or bio | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=profile_readme` |
| GitHub repo README | Per-project README link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=readme&utm_campaign=portfolio_projects&utm_content=[repo_name]` |

## Safe Placeholder Examples

| Placeholder | Good examples |
| --- | --- |
| `[recruiter_or_company]` | `anna_epam`, `shopify_agency_hr` |
| `[person_or_company]` | `maria_recruiter`, `product_team_lead` |
| `[client_or_job_slug]` | `supplement_store_redesign`, `shopify_theme_support` |
| `[company_role]` | `stripe_frontend_dev`, `shopify_theme_dev` |
| `[repo_name]` | `shopify-dev-kb`, `quizpilot-waitlist` |

## Default Set

If you want the smallest possible set to reuse everywhere, keep these 5:

| Use case | URL |
| --- | --- |
| LinkedIn profile | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=featured_link` |
| Telegram outreach | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=dm&utm_campaign=direct_outreach&utm_content=[person_or_company]` |
| Upwork proposal | `https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=proposal&utm_campaign=freelance_proposal&utm_content=[client_or_job_slug]` |
| CV PDF | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=[company_role]` |
| GitHub profile | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=profile_readme` |

## My Production URLs

These are concrete links for your real channels. Keep the templates above for one-off outreach, but use the links below as your default production URLs.

| Channel | Where to use it | Final URL |
| --- | --- | --- |
| LinkedIn profile | Featured section or profile link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=featured_link` |
| LinkedIn DM | Default recruiter outreach | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=dm&utm_campaign=direct_outreach&utm_content=default_recruiter_outreach` |
| Telegram bio | Public Telegram profile or bio link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=bio&utm_campaign=portfolio_profile&utm_content=public_profile` |
| Telegram DM | Default personal outreach | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=dm&utm_campaign=direct_outreach&utm_content=default_direct_message` |
| Upwork proposal | Main Shopify proposal link | `https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=proposal&utm_campaign=freelance_proposal&utm_content=shopify_general_proposal` |
| Upwork follow-up | Follow-up after client reply | `https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=message&utm_campaign=freelance_followup&utm_content=shopify_general_followup` |
| CV PDF Frontend | Link inside general frontend CV | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=general_frontend_resume` |
| CV PDF Shopify | Link inside Shopify CV version | `https://taras-polishchuk.github.io/?utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=general_shopify_resume` |
| GitHub profile | Main GitHub profile / README link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=profile_readme` |
| GitHub repo README | Default project README link | `https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=readme&utm_campaign=portfolio_projects&utm_content=default_repo_readme` |

## Quick Copy Block

```text
LinkedIn profile:
https://taras-polishchuk.github.io/?ref=frontend&utm_source=linkedin&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=featured_link

Telegram bio:
https://taras-polishchuk.github.io/?ref=frontend&utm_source=telegram&utm_medium=bio&utm_campaign=portfolio_profile&utm_content=public_profile

Upwork proposal:
https://taras-polishchuk.github.io/?utm_source=upwork&utm_medium=proposal&utm_campaign=freelance_proposal&utm_content=shopify_general_proposal

CV PDF Frontend:
https://taras-polishchuk.github.io/?ref=frontend&utm_source=cv&utm_medium=pdf&utm_campaign=resume_distribution&utm_content=general_frontend_resume

GitHub profile:
https://taras-polishchuk.github.io/?ref=frontend&utm_source=github&utm_medium=profile&utm_campaign=portfolio_profile&utm_content=profile_readme
```