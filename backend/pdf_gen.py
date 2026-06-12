from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet


def generate_report(filename, analysis):

    doc = SimpleDocTemplate(filename)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Eco-Opti Sustainability Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Total Emissions: {analysis.total_emissions} kg CO₂",
            styles["Normal"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Optimizer Output:<br/>{analysis.optimizer_output}",
            styles["BodyText"]
        )
    )

    content.append(Spacer(1, 10))

    content.append(
        Paragraph(
            f"Final Decision:<br/>{analysis.final_decision}",
            styles["BodyText"]
        )
    )

    doc.build(content)