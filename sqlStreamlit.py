import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
import pyodbc
import sqlalchemy as sa

#--------------------------------------------------CONNECT TO SERVER---------------------------------------------------------
server = "."
database = "AdventureWorks2019"

#cnxn is represent a database connection object created by 'pyodbc.connect()' function
#So it basically connects to the database
cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')

#Read the file from AdventureWorks2019 database with connection of cnxn
df = pd.read_sql_query("SELECT * FROM Production.Product", cnxn)

#We have successfully connected to the database and read the file

#------------------------------------------------SET UP STREAMLIT---------------------------------------------------------

#Set up the streamlit page
st.set_page_config(page_title="Dashbarods for AdventureWorks2019",
                   page_icon = ":moneybag:",
                   layout= "wide",
                   menu_items={'About': 'This is a dashboard for AdventureWorks2019 database. It shows the products and sales data.'})


#Set index to ProductID. inplace=True means that the changes will be made to the original dataframe
df.set_index('ProductID', inplace=True)

#We have successfully set up the streamlit page

#----------------------------------------------CLEAN UP THE PRODUCT TABLE---------------------------------------------------------

#Drop the 'MakeFlag', 'FinishedGoodsFlag', 'WeightUnitMeasureCode', 
#'ProductLine', 'Class', 'Style', 'ProductSubcategoryID', 'ProductModelID', 'rowguid', 'ModifiedDate', 'Dis' columns    
df.drop(columns=['MakeFlag', 'FinishedGoodsFlag', 'WeightUnitMeasureCode', 'ProductLine', 
                 'Class', 'Style', 'ProductSubcategoryID', 'ProductModelID', 'rowguid', 
                 'ModifiedDate', 'DiscontinuedDate', 'SizeUnitMeasureCode'], inplace=True)

#Clean up the 'sellStartDate', 'SellEndDate' column to just the date
df['SellStartDate'] = pd.to_datetime(df['SellStartDate'])
df['SellEndDate'] = pd.to_datetime(df['SellEndDate'])

#Split the 'StartDate' and 'SellEndDate' column into Year, Month and Day
df['SellStartYear'] = df['SellStartDate'].dt.year
df['SellStartMonth'] = df['SellStartDate'].dt.month
df['SellStartDay'] = df['SellStartDate'].dt.day

df['SellEndYear'] = df['SellEndDate'].dt.year
df['SellEndMonth'] = df['SellEndDate'].dt.month
df['SellEndDay'] = df['SellEndDate'].dt.day

df.drop(columns=['SellStartDate'], inplace=True)
df.drop(columns= ['SellEndDate'], inplace=True)

#--------------------------------------------------WIDGETS FOR PRODUCT---------------------------------------------------------
st.title("Cost of Products :moneybag:")
st.markdown("Here you can find products data from **Adventureworks2019** database.")

st.sidebar.header("Filtering Products")

product_color = st.sidebar.multiselect("Filter products by color: ", 
                                       options=df['Color'].unique())

product_size = st.sidebar.multiselect("Filter products size: ",
                                      options=df['Size'].unique())

products_year = st.sidebar.multiselect("Filter products by year: ",
                                       options=df['SellStartYear'].unique())

#Make a copy of the dataframe so that we can filter the data without affecting the original dataframe
df_selection = df.copy()

#Place a filter selection in the df_selection variable
if product_color:
    df_selection = df[df['Color'].isin(product_color)]
    
if product_size:
    df_selection = df[df['Size'].isin(product_size)]
    
if products_year:
    df_selection = df[df['SellStartYear'].isin(products_year)]
    

#Show the data in the website
st.dataframe(df_selection)

#--------------------------------------------------PRODUCTS KPI's---------------------------------------------------------
st.title("Products KPI's")
st.markdown("Here you can find the KPI's for the cost of products.")

#Since the data is all of object type, we need to convert it to float to be able to get the sum
total_cost = float(df_selection['StandardCost'].sum())
avergae_cost = float(df_selection['StandardCost'].mean())
max_cost = float(df_selection['StandardCost'].max())

#Declare 4 columns for each KPI in the website
col1, col2, col3 = st.columns(3)

#We assigned the logic to each columns with .2f to format the number to 2 decimal places since float 
# dont take decimal formatting as argument when we tried to convert it
with col1:
    st.subheader("Total cost")
    st.subheader(f"US ${total_cost:,.2f}")
with col2:
    st.subheader("Average cost")
    st.subheader(f"US ${avergae_cost:,.2f}")
with col3:
    st.subheader("Maximum cost")
    st.subheader(f"US ${max_cost:,.2f}")

#--------------------------------------------------PRODUCTS CHART---------------------------------------------------------


#------BAR CHART FOR THE TOTAL COST BY PRODUCT-------------------
#The reset_index() function is used to reset the index, which mean that we drop the indexing that we have in the dataframe
cost_by_product = df_selection.groupby('SellStartYear')['StandardCost'].sum().reset_index()

#Create a bar chart for the total cost by product
total_cost_bar_chart = px.bar(cost_by_product, 
                              x='StandardCost', 
                              y='SellStartYear',
                              title="Total Cost by Product",
                              labels={'StandardCost': 'Total Cost', 'SellStartYear': 'Year'},
                              orientation='h',
                              height=800)

#Show the bar chart in the website
st.plotly_chart(total_cost_bar_chart)


#------DONUT CHART FOR THE YEAR WITH THE HIGHEST COST-------------------
#We make a sum group by the Name column specified for StandardCost collumn
cost_by_products = df_selection.groupby('Name')['StandardCost'].sum().reset_index()

#We then find the top 3 products name with the highest cost
top_3_products = cost_by_products.sort_values(by='StandardCost', ascending=False).head(3)

#Making a donut chart for the year with the highest cost
max_cost_donut_chart = px.pie(top_3_products,
                              values= 'StandardCost',
                              names='Name',
                              title="top 3 products with the highest cost",
                              hole=0.5)

max_cost_donut_chart.update_traces(textposition='inside',textinfo='percent+label')
max_cost_donut_chart.update_layout(legend_title_text='Name')

st.plotly_chart(max_cost_donut_chart)

#------SCATTER PLOT FOR THE COST BY PRODUCT-------------------

#making a scatter plot and its layout
scatter_plot_chart = px.scatter(df_selection,
                                x='Name',
                                y='StandardCost',
                                color='SellStartYear',
                                size='StandardCost',
                                hover_name='Name',
                                title='Cost by Product',
                                labels={'SellStartYear': 'Year', 'StandardCost': 'Cost'},
                                height=800)

#the update_layout() function is used to update the layout of the scatter plot chart
scatter_plot_chart.update_layout(xaxis_title='Product Name', yaxis_title='Price ($)' ,)

st.plotly_chart(scatter_plot_chart)

st.divider()
#------------------------------------------------SET UP SALES STREAMLIT---------------------------------------------------------

st.title("Sales Dashboard :money_with_wings:")
st.markdown("This is the **Sales dashboard** where you can find information about the sales in the database.")


#------------------------------------------------CONNECT TO SALES.SALES SERVER---------------------------------------------------------
#Read the file from AdventureWorks2019 database with connection of cnxn
df_sales = pd.read_sql_query("SELECT * FROM Sales.SalesOrderHeader", cnxn)

df_sales.set_index('SalesOrderID', inplace=True)

#------------------------------------------------CLEAN UP THE SALES TABLE---------------------------------------------------------

#We will start with dropping all the unnessary columns. such as 
# 'ModifiedDate', 'rowguid', 'Comment', 'ShipMethodID', 'ShipToAddressID', 'BillToAddressID', 'SalesPersonID' and 'SalesOrderNumber'
df_sales.drop(['ModifiedDate', 'rowguid', 'Comment', 'ShipMethodID', 'ShipToAddressID', 'BillToAddressID', 'SalesPersonID', 'RevisionNumber', 'Status', 
               'SalesOrderNumber', 'PurchaseOrderNumber', 'CustomerID', 'CreditCardID', 'TerritoryID', 'CreditCardApprovalCode', 'CurrencyRateID'], axis=1 ,inplace=True)

#------------------------------------------------CONVERT DATATYPE FOR EACH COLUMNS---------------------------------------------------------
#Clean up the 'OrderDate', 'DueDate' and 'ShipDate' column to just the date
df_sales['OrderDate'] = pd.to_datetime(df_sales['OrderDate']).dt.date
df_sales['DueDate'] = pd.to_datetime(df_sales['DueDate']).dt.date
df_sales['ShipDate'] = pd.to_datetime(df_sales['ShipDate']).dt.date

#Convert each columns data type to the correct data type
df_sales['SubTotal'] = df_sales['SubTotal'].astype(float)
df_sales['TaxAmt'] = df_sales['TaxAmt'].astype(float)
df_sales['Freight'] = df_sales['Freight'].astype(float)
df_sales['TotalDue'] = df_sales['TotalDue'].astype(float)

#--------------------------------------------------WIDEGET FOR SALES----------------------------------------------------------------

st.sidebar.header('Filtering Sales')

unique_years = pd.to_datetime(df_sales['OrderDate']).dt.year.unique()
unique_years.sort()

#Filter the sales by year
#Earlier I have write this line like this ->multiselect('Filter order by year:', options=df_sales['OrderDate']).dt.year.unique()
#Which raised an error since we cannot apply .dt directly on to the list object, the .dt must be used with the pandas series that contained 
#the datetime object.
sales_per_year = st.sidebar.multiselect('Filter order by year:', 
                                        options=unique_years)

if sales_per_year:
    df_sales_filtered = df_sales[pd.to_datetime(df_sales['OrderDate']).dt.year.isin(sales_per_year)]
    st.dataframe(df_sales_filtered)

#--------------------------------------------------CHART FOR SALES----------------------------------------------------------------
#Showing the table first
st.dataframe(df_sales)

#---------------BAR CHART---------------------
#Count amount of Online and Offline orders
order_counts = df_sales['OnlineOrderFlag'].value_counts().reset_index()

#Count amount of Online and Offline orders and split it into two columns
#Rename the column to OrderType and the second column to Count
order_counts.columns= ['OrderType', 'Count'] 

#Making a bar chart showing amount of OnlineOrder and OfflineOrder
online_offline_barchart = px.bar(order_counts, 
                              x='OrderType', 
                              y='Count',
                              title="Online vs Offline Orders",
                              labels={'OrderType': 'Order Type', 'Count': 'Amount of Orders'},
                              orientation='v',
                              height=400)

#Displaying bar chart
st.plotly_chart(online_offline_barchart)

#--------------------------------------------------SALES KPI's---------------------------------------------------------
st.title("Sales KPI's")
st.markdown("Here you can find the KPI's for the sales.")

#Temporarily convert the OrderDate to datetime object for the calculation
temp_dates = pd.to_datetime(df_sales['OrderDate'])

#Make a month in OrderDate to be unique and sort it
unique_month = temp_dates.dt.month_name().unique()
unique_month.sort()

#Group the month by its name and sum the TotalDue
#idxmax is used to get the index of the maximum value in the series
monthly_sales = df_sales.groupby(temp_dates.dt.month_name())['TotalDue'].sum()
best_sales_month = monthly_sales.idxmax()
best_sales_amount = monthly_sales.max()

#idxmin find the index of the minimum value in the series
least_sales_month = monthly_sales.idxmin()
least_sales_amount = monthly_sales.min()


#declare two columns
col1, col2 = st.columns(2)

with col1:
    st.subheader('Best Sales Month')
    st.subheader(f"Month: {best_sales_month}")
    st.subheader(f"Amount: ${best_sales_amount:,.2f}")
with col2:
    st.subheader('Least Sales Amount')
    st.subheader(f"Month: {least_sales_month}")
    st.subheader(f"Amount: ${least_sales_amount:,.2f}")





