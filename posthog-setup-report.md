# PostHog post-wizard report

The wizard has completed a deep integration of PostHog analytics into the Apex Motors Kenya Flask application. The Python SDK is initialised globally via the `Posthog()` constructor, a session-based `distinct_id` is generated for anonymous visitors, and a generic exception handler captures all unhandled server errors into PostHog. Ten events are tracked across the full visitor and admin journey — from browsing the inventory to submitting an inquiry, clicking WhatsApp, and managing listings in the admin panel. The PostHog JS snippet is embedded in `base.html` for client-side tracking, and environment variables are managed via `.env`.

## Events

| Event name | Description | File |
|---|---|---|
| `car_detail_viewed` | A visitor views a specific car listing detail page. | `app.py` |
| `inventory_searched` | A visitor applies filters or sorts the inventory listing. | `app.py` |
| `inquiry_submitted` | A visitor submits an inquiry form (test drive, financing, or general). | `app.py` |
| `admin_logged_in` | The admin successfully logs into the admin dashboard. | `app.py` |
| `car_listing_added` | The admin adds a new car listing to the inventory. | `app.py` |
| `car_listing_marked_sold` | The admin marks a car listing as sold via the edit form. | `app.py` |
| `car_listing_deleted` | The admin deletes a car listing from the inventory. | `app.py` |
| `whatsapp_clicked` | A visitor clicks a WhatsApp button to contact the dealership. | `templates/car_detail.html` |
| `financing_calculator_used` | A visitor interacts with the financing calculator sliders. | `templates/car_detail.html` |
| `home_search_submitted` | A visitor submits the quick-search form on the homepage. | `templates/index.html` |

## Next steps

We've built some insights and a dashboard to monitor key user behavior:

- [Analytics basics (wizard) — Dashboard](https://eu.posthog.com/project/209367/dashboard/772729)
- [Inquiry submissions over time](https://eu.posthog.com/project/209367/insights/QAWkabYP)
- [Car view → Inquiry conversion funnel](https://eu.posthog.com/project/209367/insights/8aVWtOdb)
- [Inquiries by type](https://eu.posthog.com/project/209367/insights/sX8b1YFW)
- [WhatsApp clicks vs Inquiry submissions](https://eu.posthog.com/project/209367/insights/mUDEMxDM)
- [Inventory searches and car detail views](https://eu.posthog.com/project/209367/insights/38GuWOJI)

## Verify before merging

- [ ] Run a full production build (the wizard only verified the files it touched) and fix any lint or type errors introduced by the generated code.
- [ ] Run the test suite — call sites that were rewritten or instrumented may need updated mocks or fixtures.
- [ ] Add `POSTHOG_PROJECT_TOKEN` and `POSTHOG_HOST` to `.env.example` and any bootstrap/onboarding scripts so collaborators know what to set.

### Agent skill

We've left an agent skill folder in your project at `.claude/skills/integration-flask/`. You can use this context for further agent development when using Claude Code. This will help ensure the model provides the most up-to-date approaches for integrating PostHog.
