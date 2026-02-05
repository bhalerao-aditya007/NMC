import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import json
import logging

logger = logging.getLogger(__name__)


class ReportGenerator:
    def __init__(self, output_dir: str | None = None):
        """
        output_dir:
        - If None → uses REPORT_OUTPUT_DIR env
        - If still None → defaults to /tmp/reports (Render-safe)
        """
        self.output_dir = (
            output_dir
            or os.environ.get("REPORT_OUTPUT_DIR")
            or "/tmp/reports"
        )

        os.makedirs(self.output_dir, exist_ok=True)
        self.report_data = None

        logger.info(f"Report output directory set to: {self.output_dir}")

    def generate_report(
        self,
        analysis_results: Dict[str, Any],
        output_format: str = "excel",
    ) -> str:
        self.report_data = analysis_results

        if output_format == "excel":
            return self._generate_excel_report()
        elif output_format == "html":
            return self._generate_html_report()
        elif output_format == "json":
            return self._generate_json_report()
        elif output_format == "pdf":
            return self._generate_pdf_report()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    # ------------------ EXCEL ------------------

    def _generate_excel_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir, f"Red_Flag_Analysis_Report_{timestamp}.xlsx"
        )

        logger.info(f"Generating Excel report: {output_file}")

        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            self._create_summary_dataframe().to_excel(
                writer, sheet_name="Summary", index=False
            )

            if self.report_data.get("red_flagged"):
                self._create_red_flag_dataframe().to_excel(
                    writer, sheet_name="Red Flagged Entries", index=False
                )

            if self.report_data.get("green_flagged"):
                self._create_green_flag_dataframe().to_excel(
                    writer, sheet_name="Green Flagged Entries", index=False
                )

            flag_summary_df = self._create_flag_summary_dataframe()
            if not flag_summary_df.empty:
                flag_summary_df.to_excel(
                    writer, sheet_name="Flag Type Summary", index=False
                )

            if self.report_data.get("red_flagged"):
                self._create_detailed_findings_dataframe().to_excel(
                    writer, sheet_name="Detailed Findings", index=False
                )

        return output_file

    # ------------------ DATAFRAMES ------------------

    def _create_summary_dataframe(self) -> pd.DataFrame:
        summary = self.report_data.get("flag_summary", {})
        return pd.DataFrame(
            {
                "Metric": [
                    "Total Records",
                    "Red Flagged",
                    "Green Flagged",
                    "High Severity",
                    "Medium Severity",
                    "Low Severity",
                    "Analysis Timestamp",
                ],
                "Value": [
                    self.report_data.get("total_records", 0),
                    len(self.report_data.get("red_flagged", [])),
                    len(self.report_data.get("green_flagged", [])),
                    summary.get("by_severity", {}).get("HIGH", 0),
                    summary.get("by_severity", {}).get("MEDIUM", 0),
                    summary.get("by_severity", {}).get("LOW", 0),
                    self.report_data.get("timestamp", "N/A"),
                ],
            }
        )

    def _create_red_flag_dataframe(self) -> pd.DataFrame:
        rows = []

        for entry in self.report_data.get("red_flagged", []):
            for flag in entry["flags"]:
                row = {
                "Excel Row No": entry["record_index"],
                "Sr No": entry["sr_no"],
                "Budget Item No": entry["budget_item_no"],
                "Name of Work": entry["name_of_work"],
                "Flag Type": flag["flag_name"],
                "Severity": flag.get("severity", "N/A"),
                "Reason": flag["description"]
                }

                for k, v in flag.get("details", {}).items():
                    row[k.replace("_", " ").title()] = v

                rows.append(row)

        return pd.DataFrame(rows)


    def _create_green_flag_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(
            [
                {
                    "Excel Row": e["record_index"],
                    "Sr No": e["sr_no"],
                    "Budget Item": e["budget_item_no"],
                    "Work Name": e["name_of_work"],
                    "Status": "No Issues Found",
                }
                for e in self.report_data.get("green_flagged", [])
            ]
        )

    def _create_flag_summary_dataframe(self) -> pd.DataFrame:
        summary = self.report_data.get("flag_summary", {})
        rows = [
            {
                "Flag Type": k,
                "Occurrences": v,
                "Percentage": round(
                    v / summary.get("total_red_flags", 1) * 100, 2
                ),
            }
            for k, v in summary.get("by_flag_type", {}).items()
        ]
        return pd.DataFrame(rows).sort_values("Occurrences", ascending=False)

    def _create_detailed_findings_dataframe(self) -> pd.DataFrame:
        rows = []
        for entry in self.report_data.get("red_flagged", []):
            for flag in entry["flags"]:
                row = {
                    "Excel Row": entry["record_index"],
                    "Budget Item": entry["budget_item_no"],
                    "Work Name": entry["name_of_work"],
                    "Flag ID": flag["flag_id"],
                    "Flag Name": flag["flag_name"],
                    "Severity": flag.get("severity", "N/A"),
                    "Description": flag["description"],
                }
                row.update(flag.get("details", {}))
                rows.append(row)
        return pd.DataFrame(rows)

    # ------------------ HTML / JSON ------------------

    def _generate_html_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir, f"Red_Flag_Analysis_Report_{timestamp}.html"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self._create_html_content())

        return output_file

    def _generate_json_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir, f"Red_Flag_Analysis_Report_{timestamp}.json"
        )

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.report_data, f, indent=2, ensure_ascii=False, default=str)

        return output_file

    # ------------------ PDF ------------------

    def _generate_pdf_report(self) -> str:
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError as exc:
            raise ValueError(
                "PDF generation requires the 'reportlab' package."
            ) from exc

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(
            self.output_dir, f"Red_Flag_Analysis_Report_{timestamp}.pdf"
        )

        styles = getSampleStyleSheet()
        story = [
            Paragraph("PWD Red Flag Analysis Report", styles["Title"]),
            Paragraph(
                f"Generated: {self.report_data.get('timestamp', 'N/A')}",
                styles["Normal"],
            ),
            Spacer(1, 12),
        ]

        summary = self.report_data.get("flag_summary", {})
        summary_data = [
            ["Metric", "Value"],
            ["Total Records", self.report_data.get("total_records", 0)],
            ["Red Flagged", len(self.report_data.get("red_flagged", []))],
            ["Green Flagged", len(self.report_data.get("green_flagged", []))],
            ["High Severity", summary.get("by_severity", {}).get("HIGH", 0)],
            ["Medium Severity", summary.get("by_severity", {}).get("MEDIUM", 0)],
            ["Low Severity", summary.get("by_severity", {}).get("LOW", 0)],
        ]

        summary_table = Table(summary_data, hAlign="LEFT")
        summary_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFB399")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333333")),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ]
            )
        )
        story.extend([summary_table, Spacer(1, 16)])

        red_flag_rows = [
            ["Excel Row", "Work Name", "Flag", "Severity", "Reason"]
        ]
        for entry in self.report_data.get("red_flagged", []):
            for flag in entry.get("flags", []):
                red_flag_rows.append(
                    [
                        entry.get("record_index", ""),
                        entry.get("name_of_work", "")[:50],
                        flag.get("flag_name", ""),
                        flag.get("severity", "N/A"),
                        flag.get("description", "")[:80],
                    ]
                )

        if len(red_flag_rows) > 1:
            story.append(Paragraph("Red Flag Details", styles["Heading2"]))
            red_flag_table = Table(red_flag_rows, hAlign="LEFT", colWidths=[60, 150, 110, 70, 160])
            red_flag_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFE5D9")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#333333")),
                        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DDDDDD")),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.extend([red_flag_table, Spacer(1, 12)])
        else:
            story.append(Paragraph("No red flags detected.", styles["Normal"]))

        doc = SimpleDocTemplate(output_file, pagesize=A4)
        doc.build(story)

        return output_file

    def _create_html_content(self) -> str:
        red = len(self.report_data.get("red_flagged", []))
        green = len(self.report_data.get("green_flagged", []))
        total = self.report_data.get("total_records", 0)

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Red Flag Analysis Report</title>
            <style>
                body {{ font-family: Arial; padding: 20px; }}
                h1 {{ color: #d32f2f; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; }}
                th {{ background: #f5f5f5; }}
            </style>
        </head>
        <body>
            <h1>🚩 Red Flag Analysis Report</h1>
            <p><b>Total Records:</b> {total}</p>
            <p><b>Red Flagged:</b> {red}</p>
            <p><b>Green Flagged:</b> {green}</p>
            <p><b>Generated:</b> {self.report_data.get("timestamp", "N/A")}</p>
        </body>
        </html>
        """
