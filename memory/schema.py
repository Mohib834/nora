from pydantic import BaseModel, Field


class Person(BaseModel):
    """A specific human that Nora serves or interacts with. Extract when a person's identity,
    role, background, or working style is mentioned. Prefer this over the generic Entity type
    for any named individual who is central to the conversation."""

    role: str | None = Field(None, description='Professional role or title of the person')
    timezone: str | None = Field(None, description='Timezone the person works in, e.g. IST, UTC+5:30')
    expertise_areas: str | None = Field(None, description='Domains or technologies the person is skilled in')
    working_style: str | None = Field(None, description='How the person prefers to work — e.g. async, direct communication, prefers planning before coding')


class Goal(BaseModel):
    """A specific outcome or objective the person is actively working toward. Extract when
    someone states an intention, ambition, or target result — not a task or project, but the
    desired end state. Examples: 'ship Nora by July', 'become financially independent'."""

    status: str | None = Field(None, description='Current state: active, completed, or abandoned')
    priority: str | None = Field(None, description='Importance level: high, medium, or low')
    deadline: str | None = Field(None, description='Target date or timeframe if mentioned')


class Project(BaseModel):
    """An active, named piece of work with a defined scope — a codebase, product, or initiative.
    Distinct from a Goal: a project is HOW work is done, a goal is WHY. Extract when a specific
    named project, repository, or product is discussed. Examples: 'arshi-pa', 'Screenforge'."""

    tech_stack: str | None = Field(None, description='Technologies, languages, or frameworks used in this project')
    status: str | None = Field(None, description='Current state: active, paused, or completed')


class Preference(BaseModel):
    """An explicit preference the person has stated about how they want things done. Extract
    when someone says 'I prefer', 'always use', 'never do', or corrects a default behavior.
    This is a separate entity because preferences change over time and must be tracked temporally.
    Examples: 'prefers Claude over GPT', 'always use axios not fetch'."""

    domain: str | None = Field(None, description='Area this preference applies to: tech, workflow, communication, or output style')
    context: str | None = Field(None, description='When or why this preference applies — the conditions under which it holds')


class CapabilityGap(BaseModel):
    """Something Nora was asked to do but could not fulfill. Extract when a request fails,
    is declined, or goes unanswered due to missing tools, integrations, or knowledge.
    This is a raw event — each occurrence is a separate episode."""

    failure_reason: str | None = Field(None, description='Why Nora could not fulfill the request — missing tool, no integration, out of scope, etc.')
    request_category: str | None = Field(None, description='Category of capability that was missing: communication, code execution, calendar, file management, search, etc.')


class CapabilityInsight(BaseModel):
    """A recurring pattern extracted from multiple CapabilityGap events. Extract when a theme
    of repeated failures points to a structural gap in what Nora can do. This is the signal that
    tells Nora what capability to build next. One insight may span many individual gaps."""

    category: str | None = Field(None, description='The capability cluster this insight belongs to: communication, scheduling, code execution, etc.')
    priority: str | None = Field(None, description='Urgency of building this capability based on how often the gap appears: high, medium, or low')
    suggested_capability: str | None = Field(None, description='Name or description of the capability that would close this gap')


class RunOutcome(BaseModel):
    """The outcome of a single request Nora processed — what was planned, what was executed,
    and whether it satisfied the request. Extract from reflect node episodes. This builds
    Nora's track record so she can reason about her own performance over time."""

    plan_summary: str | None = Field(None, description='Brief summary of what capabilities or tools Nora planned to use')
    satisfied: str | None = Field(None, description='Whether the request was fully satisfied: yes, partial, or no')
    failure_reason: str | None = Field(None, description='If not satisfied, why — what went wrong or what was missing')


ENTITY_TYPES: dict[str, type] = {
    'Person': Person,
    'Goal': Goal,
    'Project': Project,
    'Preference': Preference,
    'CapabilityGap': CapabilityGap,
    'CapabilityInsight': CapabilityInsight,
    'RunOutcome': RunOutcome,
}
