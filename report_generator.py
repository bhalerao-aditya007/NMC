"""
Report Generator for Red Flag Analysis
Generates comprehensive reports in multiple formats
"""

import pandas as pd
from datetime import datetime
from typing import Dict, Any
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ReportGenerator:
    """
    Generates comprehensive analysis reports
    """

    def __init__(self, output_dir: str | Path):
        self.report_data = None
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_report(
        self,
        analysis_results: Dict[str, Any],
        output_format: str = "excel",
    ) -> str:
        """
        Generate comprehensive report
        """
        self.report_data = analysis_results

        if output_format == "excel":
            return self._generate_excel_report()
        elif output_format == "html":
            return self._generate_html_report()
        elif output_format == "json":
            return self._generate_json_report()
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

    # ------------------------------------------------------------------
    # EXCEL
    # ------------------------------------------------------------------

    def _generate_excel_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"Red_Flag_Analysis_Report_{timestamp}.xlsx"

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

        logger.info("Excel report generated successfully")
        return str(output_file)

    # ------------------------------------------------------------------
    # DATAFRAMES
    # ------------------------------------------------------------------

    def _create_summary_dataframe(self) -> pd.DataFrame:
        summary = self.report_data.get("flag_summary", {})

        return pd.DataFrame(
            {
                "Metric": [
                    "Total Records Analyzed",
                    "Red Flagged Entries",
                    "Green Flagged Entries",
                    "High Severity Flags",
                    "Medium Severity Flags",
                    "Low Severity Flags",
                    "Analysis Date",
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
            rows.append(
                {
                    "Excel Row No.": entry["record_index"],
                    "Sr. No.": entry["sr_no"],
                    "Budget Item No.": entry["budget_item_no"],
                    "Name of Work": entry["name_of_work"],
                    "Number of Flags": len(entry["flags"]),
                    "Flag Types": ", ".join(f["flag_name"] for f in entry["flags"]),
                    "Severity": ", ".join(
                        f.get("severity", "N/A") for f in entry["flags"]
                    ),
                    "Issues Found": " | ".join(
                        f["description"] for f in entry["flags"]
                    ),
                }
            )
        return pd.DataFrame(rows)

    def _create_green_flag_dataframe(self) -> pd.DataFrame:
        rows = [
            {
                "Excel Row No.": e["record_index"],
                "Sr. No.": e["sr_no"],
                "Budget Item No.": e["budget_item_no"],
                "Name of Work": e["name_of_work"],
                "Status": "No Issues Found",
            }
            for e in self.report_data.get("green_flagged", [])
        ]
        return pd.DataFrame(rows)

    def _create_flag_summary_dataframe(self) -> pd.DataFrame:
        summary = self.report_data.get("flag_summary", {})
        by_flag_type = summary.get("by_flag_type", {})

        rows = [
            {
                "Flag Type": k,
                "Occurrences": v,
                "Percentage": round(
                    v / summary.get("total_red_flags", 1) * 100, 2
                ),
            }
            for k, v in by_flag_type.items()
        ]

        return (
            pd.DataFrame(rows)
            .sort_values("Occurrences", ascending=False)
            if rows
            else pd.DataFrame()
        )

    def _create_detailed_findings_dataframe(self) -> pd.DataFrame:
        rows = []
        for entry in self.report_data.get("red_flagged", []):
            for flag in entry["flags"]:
                base = {
                    "Excel Row No.": entry["record_index"],
                    "Budget Item No.": entry["budget_item_no"],
                    "Name of Work": entry["name_of_work"],
                    "Flag ID": flag["flag_id"],
                    "Flag Type": flag["flag_name"],
                    "Severity": flag.get("severity", "N/A"),
                    "Description": flag["description"],
                }
                for k, v in flag.get("details", {}).items():
                    base[k.replace("_", " ").title()] = v
                rows.append(base)

        return pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # HTML / JSON
    # ------------------------------------------------------------------

    def _generate_html_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"Red_Flag_Analysis_Report_{timestamp}.html"

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(self._create_html_content())

        return str(output_file)

    def _generate_json_report(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.output_dir / f"Red_Flag_Analysis_Report_{timestamp}.json"

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(
                self.report_data,
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        return str(output_file)
