import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test Stability Engine", layout="wide")

st.title("📊 Advanced Test Stability Score Engine")
st.markdown("Upload TestCases and Defects files. System will compute stability automatically.")

st.markdown("---")

# Upload Section
st.header("📂 Upload Input Files")

testcase_file = st.file_uploader("Upload TestCases Excel", type=["xlsx"])
defect_file = st.file_uploader("Upload Defects Excel", type=["xlsx"])

analyze_button = st.button("🔍 Analyze Stability")

if analyze_button:

    if testcase_file is None or defect_file is None:
        st.warning("Please upload both TestCases and Defects Excel files.")
    else:

        # Read files
        tc_df = pd.read_excel(testcase_file)
        defect_df = pd.read_excel(defect_file)

        # --- EXECUTION CALCULATIONS ---
        execution_summary = tc_df.groupby("Module").agg(
            Total_Tests=("TestCaseID", "count"),
            Passed=("Status", lambda x: (x == "Pass").sum()),
            Failed=("Status", lambda x: (x == "Fail").sum())
        ).reset_index()

        # --- DEFECT CALCULATIONS ---
        defect_summary = defect_df.groupby("Module").agg(
            Total_Defects=("DefectID", "count"),
            Critical_Defects=("Severity", lambda x: (x == "Critical").sum()),
            Reopened_Defects=("Status", lambda x: (x == "Re-open").sum())
        ).reset_index()

        # Merge both
        merged_df = pd.merge(execution_summary, defect_summary, on="Module", how="left")

        merged_df = merged_df.fillna(0)

        # --- METRICS ---
        merged_df["Failure_Rate"] = merged_df["Failed"] / merged_df["Total_Tests"]
        merged_df["Defect_Density"] = merged_df["Total_Defects"] / merged_df["Total_Tests"]
        merged_df["Critical_Ratio"] = merged_df["Critical_Defects"] / merged_df["Total_Defects"].replace(0, 1)
        merged_df["Reopen_Rate"] = merged_df["Reopened_Defects"] / merged_df["Total_Defects"].replace(0, 1)

        # --- STABILITY SCORE ---
        merged_df["Stability_Score"] = (
            100
            - (merged_df["Failure_Rate"] * 40)
            - (merged_df["Defect_Density"] * 30)
            - (merged_df["Critical_Ratio"] * 20)
            - (merged_df["Reopen_Rate"] * 10)
        )

        # --- RISK CLASSIFICATION ---
        def classify(score):
            if score >= 80:
                return "🟢 Stable"
            elif score >= 60:
                return "🟡 Moderate Risk"
            else:
                return "🔴 High Risk"

        merged_df["Risk_Level"] = merged_df["Stability_Score"].apply(classify)

        overall_score = round(merged_df["Stability_Score"].mean(), 2)

        st.markdown("---")
        st.header("📈 Stability Dashboard")

        col1, col2 = st.columns(2)

        col1.metric("Overall Release Stability Score", f"{overall_score} / 100")

        if overall_score >= 80:
            col2.success("Release Risk Level: Stable")
        elif overall_score >= 60:
            col2.warning("Release Risk Level: Moderate")
        else:
            col2.error("Release Risk Level: High Risk")

        st.markdown("---")

        st.subheader("📋 Module Stability Breakdown")
        st.dataframe(
            merged_df[["Module", "Total_Tests", "Total_Defects", "Stability_Score", "Risk_Level"]]
            .sort_values(by="Stability_Score")
        )

        st.subheader("📊 Stability Score by Module")
        st.bar_chart(merged_df.set_index("Module")["Stability_Score"])

        st.subheader("🔥 Failure Rate by Module")
        st.bar_chart(merged_df.set_index("Module")["Failure_Rate"])
