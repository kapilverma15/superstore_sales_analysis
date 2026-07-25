import streamlit as st
import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

# Page Configuration
st.set_page_config(page_title='Sales Analysis', page_icon=":bar_chart:", layout="wide")
st.title(" :bar_chart: Sample Superstore Analysis")
st.markdown('<style>div.block-container{padding-top:2rem;}</style>', unsafe_allow_html=True)

# Define Default File Path
DEFAULT_FILE_PATH = "Sample - Superstore.csv"

# File Uploader & Default Path Logic
fl = st.file_uploader(":file_folder: Upload a file", type=["csv", "txt", "xlsx", "xls"])

if fl is not None:
    filename = fl.name
    st.write(f"Uploaded File: **{filename}**")
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        else:
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        st.stop()
else:
    if os.path.exists(DEFAULT_FILE_PATH):
        df = pd.read_csv(DEFAULT_FILE_PATH, encoding="ISO-8859-1")
    else:
        st.error(f"❌ File nahi mili! Kripya file path check karein ya uploader se file upload karein:\n`{DEFAULT_FILE_PATH}`")
        st.stop()

# Date Conversion
df["Order Date"] = pd.to_datetime(df["Order Date"])

col1, col2 = st.columns(2)

# Getting min and max date
startDate = df["Order Date"].min()
endDate = df["Order Date"].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Date Filter Applied
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Sidebar Cascade Filters
st.sidebar.header("Choose your filter: ")

region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
filtered_df = df.copy()

if region:
    filtered_df = filtered_df[filtered_df["Region"].isin(region)]

state = st.sidebar.multiselect("Pick the State", filtered_df["State"].unique())
if state:
    filtered_df = filtered_df[filtered_df["State"].isin(state)]

city = st.sidebar.multiselect("Pick the City", filtered_df["City"].unique())
if city:
    filtered_df = filtered_df[filtered_df["City"].isin(city)]

# Category Wise Sales
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df, 
        x="Category", 
        y="Sales", 
        text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, width="stretch")

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, width="stretch")

cl1, cl2 = st.columns(2)
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv")

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv")

# Time Series Analysis (Fixed Period Data Type Bug)
st.subheader('Time Series Analysis')

# Convert Period to string explicitly to prevent PyArrow serialization errors
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M").astype(str)
linechart = filtered_df.groupby("month_year")["Sales"].sum().reset_index()

fig2 = px.line(
    linechart, 
    x="month_year", 
    y="Sales", 
    labels={"Sales": "Amount", "month_year": "Month-Year"}, 
    height=500, 
    template="gridon"
)
st.plotly_chart(fig2, width="stretch")

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# TreeMap Chart
st.subheader("Hierarchical view of Sales using TreeMap")
if not filtered_df.empty:
    fig3 = px.treemap(
        filtered_df, 
        path=["Region", "Category", "Sub-Category"], 
        values="Sales", 
        color="Sub-Category"
    )
    st.plotly_chart(fig3, width="stretch")

# Segment & Category Pie Charts
chart1, chart2 = st.columns(2)
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(textposition="inside")
    st.plotly_chart(fig, width="stretch")

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(textposition="inside")
    st.plotly_chart(fig, width="stretch")

# Summary Table & Pivot Table
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = filtered_df.iloc[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]] if not filtered_df.empty else pd.DataFrame()
    if not df_sample.empty:
        fig = ff.create_table(df_sample, colorscale="Cividis")
        st.plotly_chart(fig, width="stretch")

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month", aggfunc="sum")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Scatter Plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")
data1.update_layout(
    title=dict(text="Relationship between Sales and Profits using Scatter Plot.", font=dict(size=20)),
    xaxis=dict(title=dict(text="Sales", font=dict(size=19))),
    yaxis=dict(title=dict(text="Profit", font=dict(size=19)))
)
st.plotly_chart(data1, width="stretch")

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, :20].style.background_gradient(cmap="Oranges"))

# Download Filtered Dataset
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Filtered_Data.csv", mime="text/csv")
    filename = fl.name
    st.write(f"Uploaded File: **{filename}**")
    try:
        if filename.endswith('.csv') or filename.endswith('.txt'):
            df = pd.read_csv(fl, encoding="ISO-8859-1")
        else:
            df = pd.read_excel(fl)
    except Exception as e:
        st.error(f"Error reading uploaded file: {e}")
        st.stop()
else:
    if os.path.exists(default_file_path):
        df = pd.read_csv(default_file_path, encoding="ISO-8859-1")
    else:
        st.error(f"❌ File nahi mili! Kripya file path check karein ya uploader se file upload karein:\n`{default_file_path}`")
        st.stop()

# Date Conversion
df["Order Date"] = pd.to_datetime(df["Order Date"])

col1, col2 = st.columns((2))

# Getting the min and max date 
startDate = pd.to_datetime(df["Order Date"]).min()
endDate = pd.to_datetime(df["Order Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", endDate))

# Date Filter Applied
df = df[(df["Order Date"] >= date1) & (df["Order Date"] <= date2)].copy()

# Sidebar Filters
st.sidebar.header("Choose your filter: ")

# Region
region = st.sidebar.multiselect("Pick your Region", df["Region"].unique())
if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

# State
state = st.sidebar.multiselect("Pick the State", df2["State"].unique())
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]

# City
city = st.sidebar.multiselect("Pick the City", df3["City"].unique())

# Filter data based on Region, State, and City
if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df = df3[df3["State"].isin(state) & df3["City"].isin(city)]
elif region and city:
    filtered_df = df3[df3["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)]

# Category Wise Sales
category_df = filtered_df.groupby(by=["Category"], as_index=False)["Sales"].sum()

with col1:
    st.subheader("Category wise Sales")
    fig = px.bar(
        category_df, 
        x="Category", 
        y="Sales", 
        text=['${:,.2f}'.format(x) for x in category_df["Sales"]],
        template="seaborn"
    )
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap="Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Category.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region_df.style.background_gradient(cmap="Oranges"))
        csv = region_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download Data", data=csv, file_name="Region.csv", mime="text/csv",
                           help='Click here to download the data as a CSV file')

# Time Series Analysis
filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analysis')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["Sales"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="Sales", labels={"Sales": "Amount", "month_year": "Month-Year"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')

# TreeMap Chart
st.subheader("Hierarchical view of Sales using TreeMap")
fig3 = px.treemap(
    filtered_df, 
    path=["Region", "Category", "Sub-Category"], 
    values="Sales", 
    hover_data=["Sales"],
    color="Sub-Category"
)
fig3.update_layout(width=800, height=650)
st.plotly_chart(fig3, use_container_width=True)

# Segment & Category Pie Charts
chart1, chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Segment", template="plotly_dark")
    fig.update_traces(textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

with chart2:
    st.subheader('Category wise Sales')
    fig = px.pie(filtered_df, values="Sales", names="Category", template="gridon")
    fig.update_traces(textposition="inside")
    st.plotly_chart(fig, use_container_width=True)

# Summary Table & Pivot Table
import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
    df_sample = df[0:5][["Region", "State", "City", "Category", "Sales", "Profit", "Quantity"]]
    fig = ff.create_table(df_sample, colorscale="Cividis")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("Month wise sub-Category Table")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_Year = pd.pivot_table(data=filtered_df, values="Sales", index=["Sub-Category"], columns="month")
    st.write(sub_category_Year.style.background_gradient(cmap="Blues"))

# Create a scatter plot
data1 = px.scatter(filtered_df, x="Sales", y="Profit", size="Quantity")

# Updated modern Plotly layout syntax
data1.update_layout(
    title=dict(
        text="Relationship between Sales and Profits using Scatter Plot.",
        font=dict(size=20)
    ),
    xaxis=dict(
        title=dict(
            text="Sales",
            font=dict(size=19)
        )
    ),
    yaxis=dict(
        title=dict(
            text="Profit",
            font=dict(size=19)
        )
    )
)

st.plotly_chart(data1, use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500, 1:20:2].style.background_gradient(cmap="Oranges"))

# Download Original Dataset
csv = df.to_csv(index=False).encode('utf-8')
st.download_button('Download Data', data=csv, file_name="Data.csv", mime="text/csv")
