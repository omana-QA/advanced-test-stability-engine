import streamlit as st
import pandas as pd

st.set_page_config(page_title="Test Stability Engine", layout="wide")

st.title("📊 Advanced Test Stability Score Engine")
st.markdown("Quantifying module stability using execution and defect intelligence.")

st.markdown("---")

# File Upload Section
st.header("📂 Upload Data Files")

execution_file = st.file_uploader("Upload Execution Excel", type=["xlsx"])
defect_file = st.file_uploader("Upload Defect Excel", type=["xlsx"])

analyze_button = st.button("🔍 Analyze Stability")

if analyze_button:

    if execution_file is None or defect_file is None:
        st.warning("Please upload both Execution and Defect Excel files.")
    else:

        execution_df = pd.read_excel(execution_file)
        defect_df = pd.read_excel(defect_file)

        merged_df = pd.merge(execution_df, defect_df, on="Module")

        # Calculations
        merged_df["Failure_Rate"] = merged_df["Failed"] / merged_df["Total_Tests"]
        merged_df["Defect_Density"] = merged_df["Total_Defects"] / merged_df["Total_Tests"]
        merged_df["Critical_Ratio"] = merged_df["Critical_Defects"] / merged_df["Total_Defects"]
        merged_df["Reopen_Rate"] = merged_df["Reopened_Defects"] / merged_df["Total_Defects"]

        merged_df = merged_df.fillna(0)

        merged_df["Stability_Score"] = (
            100
            - (merged_df["Failure_Rate"] * 40)
            - (merged_df["Defect_Density"] * 30)
            - (merged_df["Critical_Ratio"] * 20)
            - (merged_df["Reopen_Rate"] * 10)
        )

        # Risk Classification
        def classify(score):
            if score >= 80:
                return "🟢 Stable"
            elif score >= 60:
                return "🟡 Moderate Risk"
            else:
                return "🔴 High Risk"

        merged_df["Risk_Level"] = merged_df["Stability_Score"].apply(classify)

        # Overall Stability Score
        overall_score = round(merged_df["Stability_Score"].mean(), 2)

        st.markdown("---")
        st.header("📈 Stability Dashboard")

        # Display Overall Score
        col1, col2 = st.columns(2)

        col1.metric("Overall Release Stability Score", f"{overall_score} / 100")

        if overall_score >= 80:
            col2.success("Release Risk Level: Stable")
        elif overall_score >= 60:
            col2.warning("Release Risk Level: Moderate")
        else:
            col2.error("Release Risk Level: High Risk")

        st.markdown("---")

        # Module Table
        st.subheader("📋 Module Stability Breakdown")
        st.dataframe(
            merged_df[["Module", "Stability_Score", "Risk_Level"]]
            .sort_values(by="Stability_Score")
        )

        # Charts
        st.subheader("📊 Stability Score by Module")
        st.bar_chart(merged_df.set_index("Module")["Stability_Score"])

        st.subheader("🔥 Failure Rate Indicator")
        st.bar_chart(merged_df.set_index("Module")["Failure_Rate"])