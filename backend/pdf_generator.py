from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_report(filepath, user, analysis):

    doc = SimpleDocTemplate(filepath)

    styles = getSampleStyleSheet()

    content = []

    # Cover Page

    content.append(
        Paragraph(
            "Eco-Opti Sustainability Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Generated For: {user.username}",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Email: {user.email}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Report Date: {analysis.created_at}",
            styles["Normal"]
        )
    )

    content.append(PageBreak())

    # Emission Summary

    content.append(
        Paragraph(
            "Emission Summary",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Total Emissions: {analysis.total_emissions} kg CO₂",
            styles["Heading2"]
        )
    )

    content.append(PageBreak())

    # Optimizer Section

    content.append(
        Paragraph(
            "Optimizer Recommendations",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            analysis.optimizer_output,
            styles["BodyText"]
        )
    )

    content.append(PageBreak())

    # Final Decision

    content.append(
        Paragraph(
            "Executive Decision",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            analysis.final_decision,
            styles["BodyText"]
        )
    )

    doc.build(content)