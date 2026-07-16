"""
Built-in templates for common prompt types.
"""

TEMPLATES = {
    'bug_report': """Bug Report
Summary:
{summary}

Environment:
- OS: {os}
- Version: {version}
- Browser: {browser}

Steps to Reproduce:
1. {step1}
2. {step2}
3. {step3}

Expected Behavior:
{expected}

Actual Behavior:
{actual}

Additional Context:
{context}""",

    'feature_request': """Feature Request
Title:
{title}

Problem Statement:
{problem}

Proposed Solution:
{solution}

Alternatives Considered:
{alternatives}

User Impact:
{impact}

Implementation Notes:
{notes}""",

    'meeting_notes': """Meeting Notes
Date: {date}
Attendees: {attendees}

Agenda:
{agenda}

Discussion Points:
{discussion}

Action Items:
{tasks}

Next Steps:
{next_steps}

Next Meeting: {next_meeting}""",

    'daily_standup': """Daily Standup - {date}
Yesterday:
{yesterday}

Today:
{today}

Blockers:
{blockers}

Notes:
{notes}""",

    'code_review': """Code Review
PR: {pr_link}
Author: {author}

Summary:
{summary}

Changes:
{changes}

Testing:
{testing}

Questions/Concerns:
{concerns}

Approval Status: {status}""",
}

TEMPLATE_NAMES = list(TEMPLATES.keys())