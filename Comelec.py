import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Interactive Dashboard for Comelec", layout="wide")

@st.cache_data
def load_data():
    csv_path = "CLEANED_053025.csv"
    df = pd.read_csv(csv_path)

    numeric_cols = [
        "Number of Established Precincts",
        "Number of Clustered Precincts",
        "Number of Registered Voters",
        "Number of Voters Who Actually Voted"
    ]
    for col in numeric_cols:
        df[col] = df[col].astype(str).str.replace(",", "")
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    location_col = "Region/Province/City/Municipality/Legislative/Provincial District"
    df.rename(columns={location_col: "Location"}, inplace=True)

    # Normalize location for matching
    df["Normalized_Location"] = df["Location"].str.lower().str.strip().str.replace(" city", "").str.replace(" municipality", "").str.replace(" province", "")

    return df

df = load_data()

region_place_mapping = {
    "NCR": [
        "Manila", "Quezon City", "Caloocan", "Las Piñas", "Makati", "Malabon",
        "Mandaluyong", "Marikina", "Muntinlupa", "Navotas", "Parañaque",
        "Pasay", "Pasig", "San Juan", "Taguig", "Valenzuela"
    ],
    "REGION I - Ilocos Region": ["Ilocos Norte", "Ilocos Sur", "La Union", "Pangasinan"],
    "REGION II - Cagayan Valley": ["Cagayan", "Isabela", "Nueva Vizcaya", "Quirino"],
    "REGION III - Central Luzon": ["Aurora", "Bataan", "Bulacan", "Nueva Ecija", "Pampanga", "Tarlac", "Zambales"],
    "REGION IV-A - CALABARZON": ["Batangas", "Cavite", "Laguna", "Quezon", "Rizal"],
    "REGION IV-B - MIMAROPA": ["Marinduque", "Occidental Mindoro", "Oriental Mindoro", "Palawan", "Romblon"],
    "REGION V - Bicol Region": ["Albay", "Camarines Norte", "Camarines Sur", "Catanduanes", "Masbate", "Sorsogon"],
    "REGION VI - Western Visayas": ["Aklan", "Antique", "Capiz", "Guimaras", "Iloilo", "Negros Occidental"],
    "REGION VII - Central Visayas": ["Bohol", "Cebu", "Negros Oriental", "Siquijor"],
    "REGION VIII - Eastern Visayas": ["Biliran", "Eastern Samar", "Leyte", "Northern Samar", "Samar", "Southern Leyte"],
    "REGION IX - Zamboanga Peninsula": ["Zamboanga del Norte", "Zamboanga del Sur", "Zamboanga Sibugay"],
    "REGION X - Northern Mindanao": ["Bukidnon", "Camiguin", "Misamis Occidental", "Misamis Oriental"],
    "REGION XI - Davao Region": ["Davao de Oro", "Compostela Valley", "Davao del Norte", "Davao del Sur", "Davao Occidental", "Davao Oriental"],
    "REGION XII - SOCCSKSARGEN": ["Cotabato", "North Cotabato", "Sarangani", "South Cotabato", "Sultan Kudarat"],
    "REGION XIII - Caraga": ["Agusan del Norte", "Agusan del Sur", "Dinagat Islands", "Surigao del Norte", "Surigao del Sur"],
    "CAR - Cordillera Administrative Region": ["Abra", "Apayao", "Benguet", "Ifugao", "Kalinga", "Mountain Province"],
    "BARMM - Bangsamoro Autonomous Region in Muslim Mindanao": ["Basilan", "Lanao del Sur", "Maguindanao", "Sulu", "Tawi-Tawi"]
}

region_colors = {
    "NCR": "#FF6F61",
    "REGION I - Ilocos Region": "#6B5B95",
    "REGION II - Cagayan Valley": "#88B794",
    "REGION III - Central Luzon": "#98B4D4",
    "REGION IV-A - CALABARZON": "#CDBE78",
    "REGION IV-B - MIMAROPA": "#F4A261",
    "REGION V - Bicol Region": "#E76F51",
    "REGION VI - Western Visayas": "#2A9D8F",
    "REGION VII - Central Visayas": "#264653",
    "REGION VIII - Eastern Visayas": "#287271",
    "REGION IX - Zamboanga Peninsula": "#29B6F6",
    "REGION X - Northern Mindanao": "#FFA726",
    "REGION XI - Davao Region": "#EF5350",
    "REGION XII - SOCCSKSARGEN": "#EC407A",
    "REGION XIII - Caraga": "#AB47BC",
    "CAR - Cordillera Administrative Region": "#42A5F5",
    "BARMM - Bangsamoro Autonomous Region in Muslim Mindanao": "#66BB6A"
}

def normalize_name(name):
    if pd.isna(name):
        return ""
    name = str(name).lower().strip()
    name = name.replace(" city", "").replace(" municipality", "").replace(" province", "")
    return name

def find_best_match(target_place, df_data):
    normalized_target = normalize_name(target_place)
    direct_match = df_data[df_data["Normalized_Location"] == normalized_target]
    if not direct_match.empty:
        return direct_match
    partial_match = df_data[df_data["Normalized_Location"].str.contains(normalized_target, case=False, na=False)]
    if not partial_match.empty:
        return partial_match
    reverse_match = df_data[df_data["Location"].str.contains(target_place, case=False, na=False)]
    if not reverse_match.empty:
        return reverse_match
    return pd.DataFrame()

summary = []
province_region_map = {}

for region, places in region_place_mapping.items():
    for place in places:
        match = find_best_match(place, df)
        if not match.empty:
            reg_voters = match["Number of Registered Voters"].sum()
            act_voters = match["Number of Voters Who Actually Voted"].sum()
            turnout_rate = (act_voters / reg_voters * 100) if reg_voters > 0 else 0
            summary.append({
                "Region": region,
                "Province/City": place,
                "Registered_Voters": reg_voters,
                "Voters_Who_Voted": act_voters,
                "Turnout_Rate": round(turnout_rate, 2),
                "Established_Precincts": match["Number of Established Precincts"].sum(),
                "Clustered_Precincts": match["Number of Clustered Precincts"].sum()
            })
            province_region_map[place] = region

summary_df = pd.DataFrame(summary)
summary_df["Did_Not_Vote"] = summary_df["Registered_Voters"] - summary_df["Voters_Who_Voted"]

# Sidebar filters
st.sidebar.title("Filter Options")
selected_region = st.sidebar.selectbox("Select Region", ["All"] + list(region_place_mapping.keys()))

if selected_region == "All":
    province_options = list(province_region_map.keys())
else:
    province_options = [p for p, r in province_region_map.items() if r == selected_region]

selected_province = st.sidebar.selectbox("Select Province/City", [""] + province_options)

# Title
st.title("Interactive Dashboard - COMELEC 2022 National and Local Elections")

def compact_layout(fig, title):
    fig.update_layout(
        title=title,
        margin=dict(l=30, r=30, t=40, b=30),
        height=350,
        font=dict(size=12)
    )
    fig.update_xaxes(tickangle=45, tickfont=dict(size=10))
    fig.update_yaxes(tickfont=dict(size=10))
    return fig

if selected_region == "All":
    region_data = summary_df.groupby("Region")[["Registered_Voters", "Voters_Who_Voted", "Did_Not_Vote"]].sum().reset_index()
    fig_region = go.Figure()
    for _, row in region_data.iterrows():
        region = row["Region"]
        color = region_colors.get(region, "#95A5A6")
        fig_region.add_trace(go.Bar(x=[region], y=[row["Voters_Who_Voted"]],
                             name="Voted", marker_color=color,
                             text=f"{row['Voters_Who_Voted']:,}", textposition="inside"))
        fig_region.add_trace(go.Bar(x=[region], y=[row["Did_Not_Vote"]],
                             name="Did Not Vote", marker_color="#E8E8E8",
                             text=f"{row['Did_Not_Vote']:,}", textposition="inside"))
    fig_region.update_layout(barmode="stack", xaxis_title="Region", yaxis_title="Voters", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    fig_region = compact_layout(fig_region, "Voter Turnout by Region")
    st.plotly_chart(fig_region, use_container_width=True)

elif selected_region:
    region_data = summary_df[summary_df["Region"] == selected_region]
    if not region_data.empty:
        fig_province = go.Figure()
        color = region_colors.get(selected_region, "#2CA02C")
        for _, row in region_data.iterrows():
            place = row["Province/City"]
            fig_province.add_trace(go.Bar(x=[place], y=[row["Voters_Who_Voted"]],
                                 name="Voted", marker_color=color))
            fig_province.add_trace(go.Bar(x=[place], y=[row["Did_Not_Vote"]],
                                 name="Did Not Vote", marker_color="#E8E8E8"))
        fig_province.update_layout(barmode="stack", xaxis_title="Province/City", yaxis_title="Voters", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        fig_province = compact_layout(fig_province, f"Voter Turnout in {selected_region}")
        st.plotly_chart(fig_province, use_container_width=True)

if selected_province:
    data = summary_df[summary_df["Province/City"] == selected_province]
    if not data.empty:
        row = data.iloc[0]
        reg = row["Registered_Voters"]
        voted = row["Voters_Who_Voted"]
        non_voted = reg - voted
        turnout = row["Turnout_Rate"]
        region = row["Region"]
        base_color = region_colors.get(region, "#2CA02C")

        col1, col2 = st.columns(2)

        fig_donut = go.Figure(data=[go.Pie(
            labels=["Voted", "Did Not Vote"],
            values=[voted, non_voted],
            hole=0.4,
            marker=dict(colors=[base_color, "#E8E8E8"]),
            textinfo="percent+label",
            textposition="inside"
        )])
        fig_donut.update_layout(
            title=f"{selected_province} - Voter Participation",
            margin=dict(l=30, r=30, t=40, b=30),
            height=350,
            font=dict(size=12),
            annotations=[dict(text=f"{turnout:.1f}%<br>Turnout", x=0.5, y=0.5, font_size=20, showarrow=False)]
        )

        fig_bar = go.Figure(data=[go.Bar(
            y=["Voted", "Did Not Vote"],
            x=[voted, non_voted],
            orientation='h',
            marker=dict(color=[base_color, "#E8E8E8"]),
            text=[f"{v:,}" for v in [voted, non_voted]],
            textposition='auto'
        )])
        fig_bar.update_layout(
            title=f"{selected_province} - Voter Breakdown",
            xaxis_title="Count",
            margin=dict(l=30, r=30, t=40, b=30),
            height=350,
            font=dict(size=12)
        )

        col1.plotly_chart(fig_donut, use_container_width=True)
        col2.plotly_chart(fig_bar, use_container_width=True)

# Precinct comparison for region or province
if selected_region != "All" or selected_province:
    if selected_province:
        filter_loc = selected_province
    else:
        filter_loc = selected_region

    prec_df = df[df["Normalized_Location"].str.contains(normalize_name(filter_loc))]

    if not prec_df.empty:
        est_sum = prec_df["Number of Established Precincts"].sum()
        clus_sum = prec_df["Number of Clustered Precincts"].sum()

        fig_precinct = go.Figure(data=[
            go.Bar(name="Established Precincts", x=["Precincts"], y=[est_sum], marker_color="#4CAF50"),
            go.Bar(name="Clustered Precincts", x=["Precincts"], y=[clus_sum], marker_color="#F44336")
        ])
        fig_precinct.update_layout(
            barmode='group',
            title=f"Precincts in {filter_loc}",
            yaxis_title="Count",
            margin=dict(l=30, r=30, t=40, b=30),
            height=350,
            font=dict(size=12)
        )
        st.plotly_chart(fig_precinct, use_container_width=True)
