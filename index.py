import pandas as pd
import streamlit as st
import plotly.express as px

# Title
st.title("UTAS Graduates Analysis")

# Define the file path
FILE_PATH = "UTAS.xlsx"  # Update this path to your actual Excel file
df = pd.read_excel(FILE_PATH)

# Clean data
df.dropna(subset=["Academic Year"], inplace=True)

# Unique values for filters
academic_years = sorted(df["Academic Year"].dropna().unique().tolist())
specializations = sorted(df["Specialization"].dropna().unique().tolist())
branches = sorted(df["Branch"].dropna().unique().tolist())

# Sidebar - Styled Filters
st.sidebar.markdown("<h2 style='font-size:22px; color:#4CAF50;'>🔎 Filter Options</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.markdown("#### 🎓 Academic Years")
selected_years = st.sidebar.multiselect("Select Academic Years", academic_years, default=academic_years)

st.sidebar.markdown("#### 🧪 Specializations")
selected_specializations = st.sidebar.multiselect("Select Specializations", specializations, default=specializations)

st.sidebar.markdown("#### 🏫 Branches")
selected_branches = st.sidebar.multiselect("Select Branches", branches, default=branches)

# Apply filters
filtered_df = df[
    df["Academic Year"].isin(selected_years) &
    df["Specialization"].isin(selected_specializations) &
    df["Branch"].isin(selected_branches)
]

# Show filtered raw data
st.subheader("Filtered Raw Data")
st.write(filtered_df)

# Pivot table generator
def get_branch_specialization_table(df_filtered):
    specs = sorted(df_filtered["Specialization"].dropna().unique().tolist())
    columns = ["Branch / Specialization"] + specs + ["Total", "Year"]
    rows = []
    for branch in df_filtered["Branch"].dropna().unique():
        for year in df_filtered["Academic Year"].dropna().unique():
            row = [branch]
            total = 0
            for spec in specs:
                count = df_filtered[
                    (df_filtered["Branch"] == branch) &
                    (df_filtered["Specialization"] == spec) &
                    (df_filtered["Academic Year"] == year)
                ].shape[0]
                row.append(count)
                total += count
            row.append(total)
            row.append(year)
            rows.append(row)
    return pd.DataFrame(rows, columns=columns)

# Summary Table
st.subheader("Branch-Specialization-Year Summary")
summary_df = get_branch_specialization_table(filtered_df)
st.dataframe(summary_df)

# Download CSV
csv = summary_df.to_csv(index=False).encode("utf-8")
st.download_button("Download Summary as CSV", csv, "summary.csv", "text/csv")

# Charts Section
st.markdown("---")
st.subheader("📊 Visualizations")

# Bar Chart
with st.container():
    st.markdown("**Number of Students per Specialization**")
    spec_counts = filtered_df["Specialization"].value_counts().reset_index()
    spec_counts.columns = ["Specialization", "Count"]
    spec_counts = spec_counts.sort_values(by="Count", ascending=True)
    st.bar_chart(spec_counts.set_index("Specialization"))

# Area Chart
with st.container():
    st.markdown("**Enrollment Trends Over Academic Years**")
    trend_data = (
        filtered_df.groupby(["Academic Year", "Specialization"])
        .size()
        .reset_index(name="Count")
        .pivot(index="Academic Year", columns="Specialization", values="Count")
        .fillna(0)
    )
    st.area_chart(trend_data)

# Line Chart: Total graduates per year
with st.container():
    st.markdown("**📈 Total Graduates Per Year**")
    total_per_year = filtered_df.groupby("Academic Year").size().reset_index(name="Total Graduates")
    fig_line = px.line(total_per_year, x="Academic Year", y="Total Graduates", markers=True)
    st.plotly_chart(fig_line)

# Pie Chart
with st.container():
    st.markdown("**Distribution by Branch**")
    branch_counts = filtered_df["Branch"].value_counts().reset_index()
    branch_counts.columns = ["Branch", "Count"]
    fig_pie = px.pie(branch_counts, names="Branch", values="Count", title="Branch Distribution")
    st.plotly_chart(fig_pie)

# Insights Section
st.markdown("---")
st.markdown(
    """
    <h2 style="font-size: 24px;">Insights:</h2>
    <ol style="font-size: 18px;">
        <li><strong>Point 1:</strong> From the table, it is clear that there are some specializations which are only available in the <strong>Muscat branch</strong>, including:</li>
        <ul style="font-size: 18px; margin-left: 20px;">
            <li>Applied Science</li>
            <li>Fashion Design</li>
            <li>Pharmacy</li>
            <li>Photography</li>
        </ul>
        <li><strong>Point 2:</strong> The Total Number of graduates from 19/20 to 20/21 has increased, but it has decreased sharply after that.</li>
    </ol>
    """,
    unsafe_allow_html=True
)
