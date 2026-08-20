from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet


def generate_report(
    contract_title,
    summary,
    risks,
    obligations,
    entities
):

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            "Legal Contract Analysis Report",
            styles["Title"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    story.append(
        Paragraph(
            f"<b>Contract:</b> {contract_title}",
            styles["Normal"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Contract Summary",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph(
            summary or "No summary available.",
            styles["BodyText"]
        )
    )

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # RISKS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Risk Analysis",
            styles["Heading2"]
        )
    )

    risk_rows = [
        [
            "Category",
            "Score",
            "Level",
            "Reason"
        ]
    ]

    for risk in risks:

        risk_rows.append([
            risk.get("category", ""),
            str(
                risk.get(
                    "risk_score",
                    ""
                )
            ),
            risk.get(
                "risk_level",
                ""
            ),
            risk.get(
                "reason",
                ""
            )
        ])

    if len(risk_rows) > 1:

        table = Table(
            risk_rows,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(table)

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # OBLIGATIONS
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Obligations and Deadlines",
            styles["Heading2"]
        )
    )

    obligation_rows = [
        [
            "Obligation",
            "Responsible Party",
            "Deadline",
            "Category"
        ]
    ]

    for item in obligations:

        obligation_rows.append([
            item.get(
                "obligation",
                ""
            ),
            item.get(
                "responsible_party",
                ""
            ),
            item.get(
                "deadline",
                ""
            ),
            item.get(
                "category",
                ""
            )
        ])

    if len(obligation_rows) > 1:

        table = Table(
            obligation_rows,
            repeatRows=1
        )

        table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(table)

    story.append(
        Spacer(1, 15)
    )

    # --------------------------------------------------------
    # ENTITIES
    # --------------------------------------------------------

    story.append(
        Paragraph(
            "Extracted Entities",
            styles["Heading2"]
        )
    )

    if isinstance(
        entities,
        dict
    ):

        for key, value in entities.items():

            story.append(
                Paragraph(
                    f"<b>{key}:</b> {value}",
                    styles["BodyText"]
                )
            )

            story.append(
                Spacer(1, 5)
            )

    document.build(
        story
    )

    buffer.seek(0)

    return buffer