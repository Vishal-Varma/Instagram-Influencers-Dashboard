import pandas as pd
import numpy as np
import plotly.express as px 
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import streamlit as st 

color_scheme = px.colors.sequential.Magenta

st.set_page_config(layout = "centered", page_title = "Top Instagrams Influencers Dashboard")

st.title("Top Instagrams Influencers Dashboard")

@st.cache_data
def load_data():
    return pd.read_csv("./top_insta_influencers_data.csv")

data = load_data()
data.dropna(inplace = True)

def preprocess(value):
    value = value.strip().lower()
    if value.endswith("%"):
        return float(value[:-1]) / 100
    elif value.endswith("k"):
        return float(value[:-1]) * 1e3
    elif value.endswith("m"):
        return float(value[:-1]) * 1e6
    elif value.endswith("b"):
        return float(value[:-1]) * 1e9
    else:
        return float(value)
    
for col in ["posts", "followers", "avg_likes", "60_day_eng_rate", "new_post_avg_like", "total_likes"]:
    data[col] = data[col].apply(preprocess)
    
data["engagement_rate"] = (data["avg_likes"] / data["followers"]) * 100
data["growth_rate"] = (data["new_post_avg_like"] - data["avg_likes"]) / data["avg_likes"] * 100
data["like_follower_ratio"] = data["total_likes"] / data["followers"]

tab1, tab2, tab3, tab4 = st.tabs(["Overview of Influencer Performance", "Engagement and Influence Metrics", "Country-Specific Insights", "Engagement Trends"])

st.sidebar.header("Filters")
countries = st.sidebar.multiselect(
    "Select Country:",
    options = sorted(data["country"].unique()),
    default = ["India"]
)
influencers = st.sidebar.multiselect(
    "Select Country:",
    options = sorted(data[data["country"].isin(countries)]["channel_info"].unique()),
    default = sorted(data[data["country"].isin(countries)]["channel_info"].unique())
)

data = data[data["country"].isin(countries)]
data = data[data["channel_info"].isin(influencers)]

with tab1:
    fig = make_subplots(
        rows = 1, 
        cols = 3,
        specs=[[{"type" : "indicator"}, {"type" : "indicator"}, {"type" : "indicator"}]]
    )
    fig.add_trace(
        go.Indicator(
            mode = "number",
            value = data["total_likes"].sum(),
            title = {
                "text" : "Total Likes",
                "font" : {
                    "size" : 20
                }
            },
            number = {
                "valueformat" : ".2s",
                "font" : {
                    "size" : 20
                }
            },
            domain = {
                "row" : 0,
                "column" : 0
            }
        ), row = 1, col = 1
    )
    fig.add_trace(
        go.Indicator(
            mode = "number",
            value = data["engagement_rate"].mean(),
            title = {
                "text" : "Avg Engagement Rate",
                "font" : {
                    "size" : 20
                }
            },
            number = {
                "valueformat" : ".2s",
                "font" : {
                    "size" : 20
                }
            },
            domain = {
                "row" : 0,
                "column" : 1
            }
        ), row = 1, col = 2
    )
    fig.add_trace(
        go.Indicator(
            mode = "number",
            value = data["followers"].sum(),
            title = {
                "text" : "Total Followers",
                "font" : {
                    "size" : 20
                }
            },
            number = {
                "valueformat" : ".2s",
                "font" : {
                    "size" : 20
                }
            },
            domain = {
                "row" : 0,
                "column" : 2
            }
        ), row = 1, col = 3
    )
    fig.update_layout(
        height = 160
    )
    st.plotly_chart(fig)
    
    top_10_inf = data.sort_values(["influence_score", "rank"], ascending = [False, True]).head(10)
    fig = px.bar(
        data_frame = top_10_inf,
        x = "channel_info",
        y = "influence_score", 
        color = "influence_score",
        color_continuous_scale = color_scheme,
        text_auto = True
    )
    fig.update_layout(
        title = {
            "text" : "Top 10 Instagram Influencers"
        },
        xaxis = {
            "title" : "Instagram Channel"
        },
        yaxis = {
            "title" : "Influence Score"
        }
    )
    fig.update_traces(
        hovertemplate = "<b>Channel : </b>%{x}<br>" + "<b>Influence Score : </b>%{y}<br>"
    )
    fig.update_coloraxes(
        showscale = False
    )
    st.plotly_chart(fig)
    
    country_avg_er = data.groupby("country")["engagement_rate"].mean().reset_index()
    fig = px.choropleth(
        data_frame = country_avg_er, 
        locations = "country",
        locationmode = "country names",
        color = "engagement_rate",
        color_continuous_scale = color_scheme
    )
    fig.update_layout(
        title = {
            "text" : "Country-wise Average Engagement Rate"
        },
        geo = {
            "showframe" : False,
            "projection_type" : "natural earth"
        },
    )
    fig.update_traces(
        hovertemplate = "<b>Country : </b>%{location}<br>" + "<b>Engagement Rate : </b>%{z:.2f}%<br>"
    )
    fig.update_coloraxes(
        showscale = False
    )
    st.plotly_chart(fig)
    
with tab2:
    fig = px.histogram(
        data["avg_likes"],
        color_discrete_sequence = color_scheme
    )
    fig.update_layout(
        title = "Distribution of Average Likes",
        xaxis = dict(title = "Average Likes"),
        yaxis = dict(title = "Frequency")
    )
    fig.update_legends(
        visible = False
    )
    fig.update_traces(
        hovertemplate = "<b>Average Likes : </b>%{x}<br>" + "<b>Frequency : </b>%{y}"
    )
    st.plotly_chart(fig)
    
    fig = px.scatter(
        data_frame = data,
        x = "followers",
        y = "avg_likes",
        size = "influence_score",
        color = "followers",
        color_continuous_scale = color_scheme
    )
    fig.update_layout(
        title = "Followers vs Average Likes",
        xaxis = {
            "title" : "Followers"
        },
        yaxis = {
            "title" : "Avegare Likes"
        }
    )
    fig.update_coloraxes(
        showscale = False
    )
    fig.update_traces(
        hovertemplate = "<b>Followers : </b>%{x}<br>" + "<b>Average Likes : </b>%{y}<br>" 
    )
    st.plotly_chart(fig)
    
with tab3:
    country_avg_is = data.groupby("country")["influence_score"].mean().round(2).reset_index().sort_values("influence_score", ascending = False)
    fig = px.bar(
        data_frame = country_avg_is,
        x = "country",
        y = "influence_score", 
        color = "influence_score",
        color_continuous_scale = color_scheme,
        text_auto = True
    )
    fig.update_layout(
        title = {
            "text" : "Country-wise Average Influence Score"
        },
        xaxis = {
            "title" : "Country"
        },
        yaxis = {
            "title" : "Influence Score"
        }
    )
    fig.update_traces(
        hovertemplate = "<b>Country : </b>%{x}<br>" + "<b>Influence Score : </b>%{y}<br>"
    )
    fig.update_coloraxes(
        showscale = False
    )
    st.plotly_chart(fig)
    
    country_avg_lfr = data.groupby("country")["like_follower_ratio"].mean().round(2).reset_index().sort_values("like_follower_ratio", ascending = False)
    fig = px.scatter(
        data_frame = data,
        x = "country",
        y = "like_follower_ratio",
        color = "like_follower_ratio",
        size = "like_follower_ratio",
        color_continuous_scale = color_scheme
    )
    fig.update_layout(
        title = {
            "text" : "Country-wise Likes-to-Followers Ratio"
        },
        xaxis = {
            "title" : "Country"
        },
        yaxis = {
            "title" : "Likes-to-Followers Ratio"
        }
    )
    fig.update_traces(
        hovertemplate = "<b>Country : </b>%{x}<br>" + "<b>Likes-to-Followers Ratio : </b>%{y}<br>"
    )
    fig.update_coloraxes(
        showscale = False
    )
    st.plotly_chart(fig)
    
with tab4:
    fig = px.density_heatmap(
        data_frame = data,
        x = "rank",
        y = "country",
        z = "60_day_eng_rate",
        histfunc = "avg",
        color_continuous_scale = color_scheme,
        text_auto = True
    )
    fig.update_layout(
        title = "60-Day Engagement Rate by Rank and Country",
        xaxis = dict(title = "Rank"),
        yaxis = dict(title = "Country"),
        height = 600
    )
    fig.update_traces(
        hovertemplate = "<b>Country : </b>%{y}<br>" + "<b>Rank : </b>%{x}"
    )
    fig.update_coloraxes(
        showscale = False
    )
    st.plotly_chart(fig)