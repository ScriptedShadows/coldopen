"""Pydantic schemas for ColdOpen's dossier payload.

The whole dossier is generated in a single structured-output call, so every
field the frontend renders is described here. Keep descriptions prescriptive —
they are the prompt for each field.
"""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class PainPoint(BaseModel):
    title: str = Field(description="Short name of the business pain, 3-6 words")
    detail: str = Field(
        description="One sentence on why this likely hurts this specific company, grounded in what the website says"
    )


class CompanyProfile(BaseModel):
    name: str = Field(description="Company name as they brand themselves")
    domain: str = Field(description="Bare domain, e.g. acme.com")
    tagline: str = Field(description="Their positioning in one line, paraphrased")
    industry: str = Field(description="Primary industry, 2-4 words")
    summary: str = Field(
        description="2-3 sentences: what they sell, to whom, and how they position it"
    )
    buyer_persona: str = Field(
        description="The most likely economic buyer for a B2B SaaS pitch at this company, e.g. 'VP of Customer Operations'"
    )
    brand_color: str = Field(
        description="Hex color that plausibly matches their brand, e.g. #0a5c4a. Infer from industry/positioning if unknown. Must be dark enough to carry white text."
    )
    tone: str = Field(description="Their brand voice in 3-5 words")
    terminology: list[str] = Field(
        description="5-7 words/phrases this company uses for its own world (their customers, units of work, metrics). Used to re-skin the demo."
    )
    pain_points: list[PainPoint] = Field(description="Exactly 3 pain points")


class KPI(BaseModel):
    label: str = Field(description="Metric name in the prospect's own terminology")
    value: str = Field(description="Plausible current value, formatted, e.g. '4,382' or '92.4%'")
    delta: str = Field(description="Change vs last period, e.g. '+12.5%'")
    good: bool = Field(description="Whether the delta is a good thing")


class TrendPoint(BaseModel):
    label: str = Field(description="Short x-axis label, e.g. 'Jan'")
    value: float = Field(description="Y value; series should look organic, not linear")


class TableRow(BaseModel):
    cells: list[str] = Field(description="One cell per column, plausible for this industry")


class Insight(BaseModel):
    kind: Literal["win", "risk", "watch"]
    title: str = Field(description="Short insight headline")
    body: str = Field(description="One sentence tying the insight to a pain point")


class DemoConfig(BaseModel):
    """Config that skins Meridian, the fictional SaaS product, for this prospect."""

    workspace_name: str = Field(description="e.g. 'Acme Operations' — company name + plausible team")
    demo_slug: str = Field(description="URL-safe slug for the fake demo URL, e.g. 'acme'")
    nav_items: list[str] = Field(description="Exactly 5 nav labels using the prospect's terminology; first is 'Overview'")
    kpis: list[KPI] = Field(description="Exactly 4 KPIs")
    trend_title: str = Field(description="Title for the main trend chart, in their terminology")
    trend: list[TrendPoint] = Field(description="Exactly 12 monthly points, organic shape with a clear story")
    table_title: str = Field(description="Title for the records table")
    table_columns: list[str] = Field(description="Exactly 4 column headers")
    table_rows: list[TableRow] = Field(description="Exactly 5 rows of plausible records")
    insights: list[Insight] = Field(description="Exactly 3 insights, each tied to a pain point")
    talk_track: list[str] = Field(
        description="Exactly 4 beats the SE says out loud while screen-sharing this demo, in order: (1) orient them in their own world, (2) narrate the trend story, (3) drill into one record/signal tied to a pain point, (4) land the so-what. Each beat 1-2 spoken sentences, conversational, no jargon."
    )

    # Structured-output grammars can't enforce list lengths, and the model
    # occasionally over-delivers — trim to the layout's capacity.
    @field_validator("kpis")
    @classmethod
    def _cap_kpis(cls, v: list[KPI]) -> list[KPI]:
        return v[:4]

    @field_validator("nav_items")
    @classmethod
    def _cap_nav(cls, v: list[str]) -> list[str]:
        return v[:5]

    @field_validator("insights")
    @classmethod
    def _cap_insights(cls, v: list[Insight]) -> list[Insight]:
        return v[:3]


class SalesThesis(BaseModel):
    """The strategic spine of the dossier — generated first, then fed to both the
    demo builder and the brief writer so they cannot contradict each other."""

    positioning: str = Field(
        description="1-2 sentences: how Meridian should be positioned for THIS prospect specifically"
    )
    demo_world: str = Field(
        description="What world Exhibit A must depict — whose data, which team's view, which entities. If the prospect sells software/analytics/dashboards themselves, this MUST be their internal business operations (accounts, deployments, pipeline, renewals), never a clone of their own product."
    )
    never_do: str = Field(
        description="The single biggest trap to avoid when pitching this company, one sentence"
    )


class BriefQuestion(BaseModel):
    topic: str = Field(description="Discovery area, 2-3 words")
    question: str = Field(description="The open question, phrased as a consultant would ask it")
    why: str = Field(description="What the answer reveals, one sentence")


class DiscoveryBrief(BaseModel):
    snapshot: str = Field(description="3-4 sentence pre-call read on the account")
    hypotheses: list[str] = Field(description="Exactly 3 testable hypotheses about their pain")
    questions: list[BriefQuestion] = Field(description="Exactly 5 discovery questions")
    landmines: list[str] = Field(description="2-3 things NOT to say or assume on the call")
    competitive_angle: str = Field(description="One paragraph: how to position against the status quo they likely use")


class RoiLine(BaseModel):
    label: str = Field(description="Value driver name")
    assumption: str = Field(
        description="The conservative assumption behind the number. MUST contain explicit quantities (headcount, hours/week, loaded cost, ARR, or a percentage) that arithmetically support the annual value — never vague phrases like 'a modest fraction' or 'a conservative share'."
    )
    annual_value: str = Field(description="Formatted annual value, e.g. '$140K'")


class RoiSheet(BaseModel):
    headline: str = Field(description="One-line value statement with a total annual number")
    lines: list[RoiLine] = Field(description="Exactly 3 value drivers")
    payback: str = Field(description="Payback estimate, e.g. 'Under 4 months'")
    cost_of_inaction: str = Field(description="One sentence on what waiting a year costs")
    disclaimer: str = Field(description="One honest line that these are directional estimates to validate together")


# The dossier is generated in two stages: a strategist pass (profile + thesis),
# whose output steers two parallel builder passes (demo, brief + ROI). One schema
# for the whole dossier would also exceed the API's compiled-grammar size limit.
class ProfilePacket(BaseModel):
    company: CompanyProfile
    thesis: SalesThesis


class BriefAndRoi(BaseModel):
    brief: DiscoveryBrief
    roi: RoiSheet


class Dossier(BaseModel):
    company: CompanyProfile
    thesis: SalesThesis
    demo: DemoConfig
    brief: DiscoveryBrief
    roi: RoiSheet


class GenerateRequest(BaseModel):
    url: str


class GenerateResponse(BaseModel):
    dossier: Dossier
    scraped_title: str | None = None
    generated_in_seconds: float
