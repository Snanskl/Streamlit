# DOCUMENTARY & BUG FIXED
<br>

## DAY 4
<br>

**BUG**: Problem with converting date column.<br>
    Today challenge is fixing the column that originally a date format from the database, but since I have extracted from other source, the format then automatically converted to object(string) type. Which for me mean that to be able to filter through the data, i must have convert the column in to its correct data type into date(YYYmmdd) and without time(!HHMM).<br><br>

At the beginning it seems to be working when i converted the date columns in the **Sales table** as following: <br>
df_sales['OrderDate'] = pd.to_datetime(df_sales['OrderDate']).dt.date <br>
df_sales['DueDate'] = pd.to_datetime(df_sales['DueDate']).dt.date <br>
df_sales['ShipDate'] = pd.to_datetime(df_sales['ShipDate']).dt.date <br><br>
-This code effectively converts 'OrderDate' to 'date' type, which dropping any time information and converting the column into a non-datetime format, which limits further datetime operations that can be performed with pandas datetime functionalities.<br><br>

### Bug code:<br>
But then when I tried to work with **SALES KPIs** with this exact code: <br>
**unique_month = df_sales['OrderDate'].dt.month_name().unique()**<br><br>

### The error:<br>
**AttributeError: Can only use .dt accessor with datetimelike values**
<br>
-The error is raised, since these columns has changed to date format(YYYmmdd) and not datetime(YYYmmdd HH:MM) which is why i can't access the dt. accessor from pandas to call method like '.month_name()'. It result in error beacuse '.dt' can only be used with datetimelike values ('datetime64[ns]') type in pandas, not with 'date' objects.
<br><br>

**SOLUTION**: Temporary converting datetime columns.
<br>
-Temporarily convert date column to datetime when performing operations that required datetime functionalities. <br>
temp_dates = pd.to_datetime(df_sales['OrderDate'])<br>
unique_month = temp_dates.dt.month_name().unique()<br>
unique_month.sort()<br>
Use the temporary converted dates for grouping<br>
monthly_sales = df_sales.groupby(temp_dates.dt.month_name())['TotalDue'].sum()<br>



