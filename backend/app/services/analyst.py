"""Turn a scraped site into a full ColdOpen dossier.

Generation runs in two stages:

1. Strategist pass — company profile + a sales thesis (positioning, what world
   the demo must depict, the #1 trap to avoid).
2. Two builder passes run in parallel, both anchored to that thesis — one
   produces the tailored demo config, the other the discovery brief + value
   case. Because they share the strategist's conclusions, the demo and the
   brief cannot tell contradictory stories.

Every stage is an Anthropic structured-output call (`messages.parse`): the
model proposes, Pydantic validates. (A single schema for the whole dossier
would exceed the API's compiled-grammar size limit anyway.)
"""

from concurrent.futures import ThreadPoolExecutor

import anthropic
from pydantic import BaseModel

from ..schemas import BriefAndRoi, DemoConfig, Dossier, ProfilePacket
from .scraper import ScrapedSite

MODEL = "claude-opus-4-8"

SYSTEM = """You are ColdOpen, a pre-sales research engine used by solutions engineers.

You are given raw scraped content from a prospect company's website. You produce part of
a pre-first-call dossier for an SE selling "Meridian" — a general-purpose B2B operations-
intelligence platform (dashboards, workflow tracking, alerting). Meridian is deliberately
generic: the craft is re-skinning it so the prospect sees THEIR world.

Rules:
- Ground every claim in the scraped content. Where you infer, infer conservatively
  from the industry — never invent specific facts about the company (funding, names,
  customer counts) that are not in the text.
- Use the prospect's own vocabulary everywhere: their word for customers, their units
  of work, their metrics.
- If the prospect itself sells software, analytics, or dashboards, Meridian must never
  be positioned as — or demoed as — a version of their own product. Sell to their
  INTERNAL operations instead (accounts, deployments, onboarding, renewals, support).
- Sample data must be plausible for a company of this apparent size and sector, with
  organic-looking numbers (no round-number sequences, no obviously fake names).
- ROI numbers are directional and conservative; the disclaimer must say so plainly.
- brand_color: prefer the site's declared theme color if it is dark enough to carry
  white text; otherwise pick a plausible dark brand hex for the sector."""

DEMO_RULES = """Consistency rules for the demo config — violations make the demo unusable:
- KPIs, the trend series, table rows, and insights describe ONE coherent dataset. An
  insight may never contradict a KPI delta (if a KPI improved 81%, no insight may say
  the same metric is worsening — scope any negative signal to a clearly different metric
  or entity, and reflect that entity in the table).
- The trend series tells a simple story a seller can narrate (e.g. seasonal dip then
  recovery), and at least one insight and one talk-track beat reference that story.
- Whether a falling trend is good or bad must match the domain (incidents falling = good).
- Never name any sample account, record, or entity "Meridian" — that is our product's name
  and reusing it in the data reads as a mistake.
- The demo depicts exactly the world specified in the sales thesis, nothing else."""


class AnalystError(Exception):
    pass


def _parse[T: BaseModel](
    client: anthropic.Anthropic, content: str, schema: type[T]
) -> T:
    try:
        response = client.messages.parse(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM,
            messages=[{"role": "user", "content": content}],
            output_format=schema,
        )
    except anthropic.AuthenticationError as exc:
        raise AnalystError(
            "Anthropic API key is missing or invalid. Set ANTHROPIC_API_KEY in backend/.env."
        ) from exc
    except anthropic.RateLimitError as exc:
        raise AnalystError("Rate limited by the Anthropic API — wait a moment and retry.") from exc
    except anthropic.APIStatusError as exc:
        raise AnalystError(f"Anthropic API error ({exc.status_code}): {exc.message}") from exc
    except anthropic.APIConnectionError as exc:
        raise AnalystError("Could not reach the Anthropic API — check your connection.") from exc

    parsed = response.parsed_output
    if parsed is None:
        raise AnalystError("The model returned output that did not match the dossier schema.")
    return parsed


def build_dossier(site: ScrapedSite) -> Dossier:
    client = anthropic.Anthropic()
    site_block = "=== SCRAPED SITE ===\n" + site.as_prompt_block()

    # Stage 1 — strategist: profile + sales thesis.
    packet = _parse(
        client,
        "Build the company profile and the sales thesis for this prospect. The thesis "
        "will be handed to the demo builder and the brief writer, so make it decisive.\n\n"
        + site_block,
        ProfilePacket,
    )

    context = (
        "=== COMPANY PROFILE (already established — stay consistent with it) ===\n"
        + packet.company.model_dump_json(indent=2)
        + "\n\n=== SALES THESIS (binding — everything you produce must follow it) ===\n"
        + packet.thesis.model_dump_json(indent=2)
        + "\n\n"
        + site_block
    )

    # Stage 2 — builders, in parallel, both anchored to the thesis.
    with ThreadPoolExecutor(max_workers=2) as pool:
        demo_future = pool.submit(
            _parse,
            client,
            "Build the tailored Meridian demo config for this prospect.\n\n"
            + DEMO_RULES
            + "\n\n"
            + context,
            DemoConfig,
        )
        brief_future = pool.submit(
            _parse,
            client,
            "Build the discovery brief and the conservative value case for this prospect, "
            "consistent with the sales thesis.\n\n" + context,
            BriefAndRoi,
        )
        demo = demo_future.result()
        brief_part = brief_future.result()

    return Dossier(
        company=packet.company,
        thesis=packet.thesis,
        demo=demo,
        brief=brief_part.brief,
        roi=brief_part.roi,
    )
