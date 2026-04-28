import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="GHG Emissions Dashboard",
    page_icon="🌍",
    layout="wide"
)

@st.cache_data
def load_data():
    df = pd.read_csv("ghg_emissions_cleaned.csv")
    return df

df = load_data()

st.title("🌍 Greenhouse Gas Emissions by Sector Dashboard")
st.write(
    "This interactive dashboard analyses greenhouse gas emissions across European countries, "
    "years, and sectors using data from the European Environment Agency."
)

# Sidebar filters
st.sidebar.header("Filter Options")

countries = sorted(df["Country"].dropna().unique())
selected_countries = st.sidebar.multiselect(
    "Select countries:",
    countries,
    default=["Germany", "France", "Italy"] if all(c in countries for c in ["Germany", "France", "Italy"]) else countries[:3]
)

years = sorted(df["year"].dropna().unique())
year_range = st.sidebar.slider(
    "Select year range:",
    int(min(years)),
    int(max(years)),
    (int(min(years)), int(max(years)))
)

sectors = sorted(df["sector"].dropna().unique())
selected_sectors = st.sidebar.multiselect(
    "Select sectors:",
    sectors,
    default=sectors[:5]
)

filtered_df = df[
    (df["Country"].isin(selected_countries)) &
    (df["year"].between(year_range[0], year_range[1])) &
    (df["sector"].isin(selected_sectors))
]

st.subheader("Key Performance Indicators")

col1, col2, col3, col4 = st.columns(4)

total_emissions = filtered_df["emissions_gg_co2e"].sum()
avg_emissions = filtered_df["emissions_gg_co2e"].mean()
highest_country = (
    filtered_df.groupby("Country")["emissions_gg_co2e"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)
highest_sector = (
    filtered_df.groupby("sector")["emissions_gg_co2e"].sum().idxmax()
    if not filtered_df.empty else "N/A"
)

col1.metric("Total Emissions", f"{total_emissions:,.0f} Gg CO₂e")
col2.metric("Average Emissions", f"{avg_emissions:,.0f} Gg CO₂e")
col3.metric("Highest Country", highest_country)
col4.metric("Highest Sector", highest_sector[:30] + "..." if len(highest_sector) > 30 else highest_sector)

st.divider()

if filtered_df.empty:
    st.warning("No data available for the selected filters. Please change your selection.")
else:
    st.subheader("Emissions Trend Over Time")
    trend_df = filtered_df.groupby(["year", "Country"], as_index=False)["emissions_gg_co2e"].sum()

    fig_trend = px.line(
        trend_df,
        x="year",
        y="emissions_gg_co2e",
        color="Country",
        markers=True,
        title="Greenhouse Gas Emissions Trend by Country",
        labels={
            "year": "Year",
            "emissions_gg_co2e": "Emissions (Gg CO₂ equivalent)"
        }
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    colA, colB = st.columns(2)

    with colA:
        st.subheader("Emissions by Sector")
        sector_df = filtered_df.groupby("sector", as_index=False)["emissions_gg_co2e"].sum()
        sector_df = sector_df.sort_values("emissions_gg_co2e", ascending=False).head(15)

        fig_sector = px.bar(
            sector_df,
            x="emissions_gg_co2e",
            y="sector",
            orientation="h",
            title="Top Emitting Sectors",
            labels={
                "sector": "Sector",
                "emissions_gg_co2e": "Emissions (Gg CO₂ equivalent)"
            }
        )
        st.plotly_chart(fig_sector, use_container_width=True)

    with colB:
        st.subheader("Country Comparison")
        country_df = filtered_df.groupby("Country", as_index=False)["emissions_gg_co2e"].sum()
        country_df = country_df.sort_values("emissions_gg_co2e", ascending=False)

        fig_country = px.bar(
            country_df,
            x="Country",
            y="emissions_gg_co2e",
            title="Total Emissions by Country",
            labels={
                "Country": "Country",
                "emissions_gg_co2e": "Emissions (Gg CO₂ equivalent)"
            }
        )
        st.plotly_chart(fig_country, use_container_width=True)

    st.subheader("Sector Contribution")
    pie_df = filtered_df.groupby("sector", as_index=False)["emissions_gg_co2e"].sum()
    pie_df = pie_df.sort_values("emissions_gg_co2e", ascending=False).head(10)

    fig_pie = px.pie(
        pie_df,
        names="sector",
        values="emissions_gg_co2e",
        title="Share of Emissions by Sector"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("Data Preview")
    st.dataframe(filtered_df.head(100), use_container_width=True)

    st.subheader("Dashboard Insights")
    st.write(
        "The dashboard shows how greenhouse gas emissions vary across countries, sectors, and years. "
        "The sector comparison helps identify the main contributors to emissions, while the trend chart "
        "shows whether emissions have increased or decreased over time. This allows users to explore "
        "where sustainability action may be most needed."
    )
    st.subheader("Insights")

st.write(
    "The dashboard shows that emissions vary significantly across sectors and countries. "
    "Energy-related sectors tend to contribute the highest emissions, while some countries "
    "show a decreasing trend over time, indicating improvements in sustainability policies."
)