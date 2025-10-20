import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------
# Page Setup
# -------------------------------------
st.set_page_config(page_title="Placement Analysis Dashboard", layout="wide")
st.title("🎓 Executive Placement Analysis Dashboard")

df = pd.read_csv("indian_student_placement_data.csv")
df.columns = df.columns.str.strip()
df["Placement Date"] = pd.to_datetime(df["Placement Date"], errors="coerce")

# st.dataframe(df.head())

# -------------------------------------
# Sidebar Filters
# -------------------------------------
st.sidebar.header("🔍 Filters")

branch_list = sorted(df["Branch"].dropna().unique())
year_list = sorted(df["Graduation Year"].dropna().unique())
company_list = sorted(df["Company"].dropna().unique())

branches = st.sidebar.multiselect("Select Branch(es)", options=branch_list, default=branch_list)
years = st.sidebar.multiselect("Select Graduation Year(s)", options=year_list, default=year_list)
company = st.sidebar.selectbox("Select Company (Searchable)", options=["All"] + company_list)

filtered_df = df.copy()
filtered_df = filtered_df[filtered_df["Branch"].isin(branches)]
filtered_df = filtered_df[filtered_df["Graduation Year"].isin(years)]
if company != "All":
    filtered_df = filtered_df[filtered_df["Company"] == company]

st.sidebar.write(f"📦 Showing **{len(filtered_df)}** records after filters.")

# -------------------------------------
# KPI Metrics
# -------------------------------------
st.subheader("📊 Key Placement Metrics")
col1, col2, col3, col4 = st.columns(4)

total_placements = len(filtered_df)
avg_salary = filtered_df["Salary (INR)"].mean()
top_company = filtered_df["Company"].value_counts().idxmax() if not filtered_df.empty else "N/A"
top_branch = filtered_df["Branch"].value_counts().idxmax() if not filtered_df.empty else "N/A"

col1.metric("👩‍🎓 Total Placements", total_placements)
col2.metric("💰 Average Salary (INR)", f"{avg_salary:,.0f}" if not pd.isna(avg_salary) else "N/A")
col3.metric("🏢 Top Recruiter", top_company)
col4.metric("🏫 Top Branch", top_branch)



# -------------------------------------
# Tabs
# -------------------------------------
overview, tab1, tab2, tab3, tab4, tab5, tab6,tab7 = st.tabs([
    "🏠 Overview",
    "📘 Academic Trends",
    "🏢 Company Insights",
    "💰 Salary Analysis",
    "📍 Location Insights",
    "🧩 Multi-Factor Analysis",
    "🕒 Placement Timeline",
    "💼 Job Roles Analysis"
])

# ---------------------------
# OVERVIEW TAB
# ---------------------------
with overview:
    st.header("🏫 Placement Overview")

    # ---------------------------
    # 🤖 AI Insights
    # ---------------------------
    st.subheader("🤖 AI Insights & Highlights")

    if not filtered_df.empty:
        top_branch = filtered_df["Branch"].value_counts().idxmax()
        top_branch_count = filtered_df["Branch"].value_counts().max()

        top_company = filtered_df["Company"].value_counts().idxmax()
        top_company_count = filtered_df["Company"].value_counts().max()

        avg_salary = filtered_df["Salary (INR)"].mean()
        max_salary = filtered_df["Salary (INR)"].max()
        min_salary = filtered_df["Salary (INR)"].min()

        recent_year = filtered_df["Graduation Year"].max()
        yearwise_avg = (
            filtered_df.groupby("Graduation Year")["Salary (INR)"].mean().reset_index()
        )
        best_year = yearwise_avg.loc[yearwise_avg["Salary (INR)"].idxmax(), "Graduation Year"]

        # YoY trends
        yearwise = filtered_df.groupby("Graduation Year")["Name"].count().reset_index()
        if len(yearwise) > 1:
            yearwise = yearwise.sort_values("Graduation Year")
            change = ((yearwise["Name"].iloc[-1] - yearwise["Name"].iloc[-2]) / yearwise["Name"].iloc[-2]) * 100
            salary_change = ((yearwise_avg["Salary (INR)"].iloc[-1] - yearwise_avg["Salary (INR)"].iloc[-2]) /
                             yearwise_avg["Salary (INR)"].iloc[-2]) * 100
            trend_text = f"📈 Placements grew by **{change:.1f}%** and average salary changed by **{salary_change:.1f}%** year-over-year."
        else:
            trend_text = "📈 Not enough data for year-over-year comparison."

        insights = f"""
        💡 **Summary of Placements:**
        - **{top_branch}** branch recorded the highest placements with **{top_branch_count} students**.
        - **{top_company}** was the top recruiter, hiring **{top_company_count} candidates**.
        - The **average salary** offered was **₹{avg_salary:,.0f}**, ranging from **₹{min_salary:,.0f}** to **₹{max_salary:,.0f}**.
        - Graduates from **{best_year}** achieved the **highest average salary** overall.
        - The most recent graduating batch analyzed: **{recent_year}**.
        {trend_text}
        """

        st.markdown(insights)
    else:
        st.info("No data available to generate insights with the current filters.")

    # ---------------------------
    # Charts
    # ---------------------------
    colA, colB = st.columns(2)

    with colA:
        yearwise = (
            filtered_df.groupby("Graduation Year")["Name"]
            .count()
            .reset_index()
            .rename(columns={"Name": "Placements"})
            .sort_values("Graduation Year")
        )
        fig = px.line(yearwise, x="Graduation Year", y="Placements", markers=True,
                      title="🎓 Total Placements by Year")
        fig.update_traces(line_color="#0073e6", marker_color="#0073e6")
        st.plotly_chart(fig, use_container_width=True, key="overview_year")

    with colB:
        top_companies = filtered_df["Company"].value_counts().head(5).reset_index()
        top_companies.columns = ["Company", "Placements"]
        fig = px.bar(top_companies, x="Placements", y="Company", orientation="h",
                     color="Company", title="🏢 Top 5 Recruiting Companies")
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True, key="overview_companies")

    st.subheader("💸 Average Salary Trend")
    avg_salary_year = (
        filtered_df.groupby("Graduation Year")["Salary (INR)"]
        .mean()
        .reset_index()
        .sort_values("Graduation Year")
    )
    fig = px.area(avg_salary_year, x="Graduation Year", y="Salary (INR)",
                  color_discrete_sequence=["#2ca02c"], title="Average Salary Growth Over Years")
    st.plotly_chart(fig, use_container_width=True, key="overview_salary")

    st.subheader("📊 Placement Breakdown")
    col1, col2 = st.columns(2)

    with col1:
        branch_dist = filtered_df["Branch"].value_counts().reset_index()
        branch_dist.columns = ["Branch", "Count"]
        fig = px.pie(branch_dist, names="Branch", values="Count", title="Placements by Branch")
        st.plotly_chart(fig, use_container_width=True, key="overview_branch_pie")

    with col2:
        loc_dist = filtered_df["Location"].value_counts().head(8).reset_index()
        loc_dist.columns = ["Location", "Count"]
        fig = px.bar(loc_dist, x="Count", y="Location", color="Location", orientation="h",
                     title="Top Placement Locations")
        st.plotly_chart(fig, use_container_width=True, key="overview_location_bar")

# ---------------------------
# ACADEMIC TRENDS
# ---------------------------
with tab1:
    st.subheader("Placements per Branch")
    branch_counts = filtered_df["Branch"].value_counts().reset_index()
    branch_counts.columns = ["Branch", "Count"]
    fig = px.bar(branch_counts, x="Branch", y="Count", color="Branch", title="Placements by Branch")
    st.plotly_chart(fig, use_container_width=True, key="academic_branch")

    st.subheader("Placements per Graduation Year")
    year_counts = filtered_df["Graduation Year"].value_counts().sort_index().reset_index()
    year_counts.columns = ["Graduation Year", "Placements"]
    fig = px.line(year_counts, x="Graduation Year", y="Placements", markers=True,
                  title="Placements Over Years")
    st.plotly_chart(fig, use_container_width=True, key="academic_year")

# ---------------------------
# COMPANY INSIGHTS
# ---------------------------
with tab2:
    st.subheader("Top 10 Recruiting Companies")
    top_companies = filtered_df["Company"].value_counts().head(10).reset_index()
    top_companies.columns = ["Company", "Placements"]
    fig = px.bar(top_companies, x="Placements", y="Company", color="Company", orientation="h",
                 title="Top Recruiting Companies")
    st.plotly_chart(fig, use_container_width=True, key="company_top10")

    st.subheader("Job Role Distribution")
    job_roles = filtered_df["Job Role"].value_counts().head(10).reset_index()
    job_roles.columns = ["Job Role", "Count"]
    fig = px.pie(job_roles, names="Job Role", values="Count", title="Top Job Roles")
    st.plotly_chart(fig, use_container_width=True, key="company_roles")

# ---------------------------
# SALARY ANALYSIS
# ---------------------------
with tab3:
    st.subheader("Salary Distribution (Histogram)")
    fig = px.histogram(filtered_df, x="Salary (INR)", nbins=20, color="Branch", marginal="box",
                       title="Salary Distribution by Branch")
    st.plotly_chart(fig, use_container_width=True, key="salary_hist")

    st.subheader("Average Salary by Branch")
    avg_salary_branch = filtered_df.groupby("Branch")["Salary (INR)"].mean().reset_index()
    fig = px.bar(avg_salary_branch, x="Salary (INR)", y="Branch", color="Branch",
                 orientation="h", title="Average Salary by Branch")
    st.plotly_chart(fig, use_container_width=True, key="salary_avg")

# ---------------------------
# LOCATION INSIGHTS
# ---------------------------
with tab4:
    st.subheader("Placements by Location")
    location_counts = filtered_df["Location"].value_counts().head(10).reset_index()
    location_counts.columns = ["Location", "Count"]
    fig = px.bar(location_counts, x="Count", y="Location", color="Location", orientation="h",
                 title="Top Placement Locations")
    st.plotly_chart(fig, use_container_width=True, key="location_top")

# ---------------------------
# MULTI-FACTOR ANALYSIS
# ---------------------------
with tab5:
    st.subheader("Average Salary Heatmap (Branch vs Company)")
    pivot = filtered_df.pivot_table(index="Branch", columns="Company", values="Salary (INR)", aggfunc="mean")
    fig = px.imshow(pivot, color_continuous_scale="YlGnBu", aspect="auto",
                    title="Average Salary Heatmap")
    st.plotly_chart(fig, use_container_width=True, key="heatmap")

    st.subheader("Salary vs Graduation Year (Colored by Branch)")
    fig = px.scatter(filtered_df, x="Graduation Year", y="Salary (INR)", color="Branch",
                     hover_data=["Company", "Job Role"], title="Salary vs Graduation Year")
    st.plotly_chart(fig, use_container_width=True, key="scatter_salary")

# ---------------------------
# PLACEMENT TIMELINE
# ---------------------------
with tab6:
    st.subheader("Placements Over Time")
    time_df = filtered_df.copy()
    time_df["Month"] = time_df["Placement Date"].dt.to_period("M").astype(str)
    time_counts = time_df["Month"].value_counts().sort_index().reset_index()
    time_counts.columns = ["Month", "Placements"]
    fig = px.line(time_counts, x="Month", y="Placements", markers=True,
                  title="Monthly Placement Trend")
    st.plotly_chart(fig, use_container_width=True, key="timeline")


# ======================================================
# 💼 JOB ROLES ANALYSIS
# ======================================================

with tab7:
    st.header("🧑‍💼 Job Roles Analysis")

    # --- Top Job Roles ---
    st.subheader("Job Roles by Number of Placements")
    job_counts = filtered_df["Job Role"].value_counts().head(10).reset_index()
    job_counts.columns = ["Job Role", "Placements"]
    fig = px.bar(
        job_counts,
        x="Placements",
        y="Job Role",
        color="Job Role",
        orientation="h",
        title="Top Job Roles",
    )
    st.plotly_chart(fig, use_container_width=True, key="roles_top")

    # --- Average Salary by Job Role ---
    st.subheader("Average Salary by Job Role")
    avg_salary_role = (
        filtered_df.groupby("Job Role")["Salary (INR)"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )
    fig = px.bar(
        avg_salary_role,
        x="Salary (INR)",
        y="Job Role",
        color="Job Role",
        orientation="h",
        title="Average Salary by Job Role",
    )
    st.plotly_chart(fig, use_container_width=True, key="roles_salary")

    # --- Job Role Distribution by Branch ---
    st.subheader("Job Role Distribution by Branch")
    fig = px.treemap(
        filtered_df,
        path=["Branch", "Job Role"],
        title="Branch-wise Job Role Distribution",
    )
    st.plotly_chart(fig, use_container_width=True, key="roles_treemap")

    # --- AI Insights & Highlights ---
    st.markdown("### 🤖 AI Insights & Highlights")
    if not filtered_df.empty:
        top_role = job_counts.iloc[0]["Job Role"]
        top_role_count = job_counts.iloc[0]["Placements"]
        high_salary_role = avg_salary_role.iloc[0]["Job Role"]
        high_salary_value = avg_salary_role.iloc[0]["Salary (INR)"]

        st.info(
            f"""
            - The most common job role is **{top_role}**, with **{top_role_count} placements**.
            - The highest average salary is for **{high_salary_role}**, around **₹{high_salary_value:,.0f}**.
            - Branches like **{filtered_df['Branch'].mode()[0]}** show the most job diversity.
            - Consider aligning training programs with top-paying and high-demand roles for better outcomes.
            """
        )
    else:
        st.warning("No data available for Job Role insights.")
