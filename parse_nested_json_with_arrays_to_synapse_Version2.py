from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, expr
from pyspark.sql.types import StructType, ArrayType
import pyodbc

# Step 1: Create SparkSession
spark = SparkSession.builder \
    .appName("Parse Nested JSON with Arrays and Structs - Azure Synapse Integration") \
    .getOrCreate()

# Step 2: Function to Fetch Table Schema from Azure Synapse
def get_table_schema_synapse(table_name, jdbc_url, db_user, db_password):
    """
    Fetch column names of a specific table in Azure Synapse.

    Args:
        table_name (str): Name of the table to retrieve the schema for.
        jdbc_url (str): JDBC URL to connect to the Azure Synapse.
        db_user (str): Azure Synapse username.
        db_password (str): Azure Synapse password.

    Returns:
        list: List of column names in the table schema.
    """
    connection = pyodbc.connect(
        f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={jdbc_url};UID={db_user};PWD={db_password};DATABASE=master"
    )
    cursor = connection.cursor()
    cursor.execute(f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table_name}'")
    columns = [row[0] for row in cursor.fetchall()]
    connection.close()
    return columns

# Step 3: Function to Write Root-Level Columns to the "Entity" Table
def write_root_to_entity_table_synapse(df, jdbc_url, db_user, db_password, schema_name, root_table_name):
    """
    Writes root-level columns to the 'Entity' table in Azure Synapse.

    Args:
        df (DataFrame): The root-level DataFrame.
        jdbc_url (str): JDBC URL to connect to Azure Synapse.
        db_user (str): Azure Synapse username.
        db_password (str): Azure Synapse password.
        schema_name (str): Schema name in Azure SQL Database.
        root_table_name (str): Name of the root-level table.

    Returns:
        None. Writes data to the database.
    """
    full_table_name = f"{schema_name}.{root_table_name}"
    
    # Get table schema from Synapse
    entity_columns = get_table_schema_synapse(root_table_name, jdbc_url, db_user, db_password)
    
    # Filter only valid columns
    valid_columns = [col_name for col_name in df.columns if col_name in entity_columns]
    entity_df = df.select(*valid_columns)

    # Write the root-level columns to the Entity table if valid
    if not entity_df.isEmpty():
        entity_df.show(truncate=50)  # Debugging
        entity_df.write \
            .format("com.databricks.spark.sqldw") \
            .option("url", jdbc_url) \
            .option("dbtable", full_table_name) \
            .option("forwardSparkAzureStorageCredentials", "true") \
            .option("user", db_user) \
            .option("password", db_password) \
            .mode("overwrite") \
            .save()
        print(f"Root-level data successfully written to table: {full_table_name}")

# Step 4: Function to Flatten and Write Nested JSON Data
def flatten_and_write_synapse(df, parent_prefix, jdbc_url, db_user, db_password, schema_name):
    """
    Recursively parses and writes nested JSON nodes to Azure Synapse tables.

    Args:
        df (DataFrame): DataFrame containing data to process.
        parent_prefix (str): Parent column prefix used for table naming.
        jdbc_url (str): JDBC URL to connect to Azure Synapse.
        db_user (str): Azure Synapse username.
        db_password (str): Azure Synapse password.
        schema_name (str): Schema name in Azure Synapse.

    Returns:
        None.
    """
    nested_structs = []
    flat_columns = []

    # Identify flat fields and nested structures
    for field in df.schema.fields:
        field_name = field.name
        field_type = field.dataType
        
        new_column_name = f"{parent_prefix}_{field_name}" if parent_prefix else field_name

        if isinstance(field_type, StructType):
            nested_structs.append((field_name, new_column_name))
        elif isinstance(field_type, ArrayType):
            # Process arrays by exploding and handling as rows
            df = df.withColumn(new_column_name, explode(col(field_name)))
            flat_columns.append(col(new_column_name))  # Flatten exploded elements
        else:
            flat_columns.append(col(field_name).alias(new_column_name))
    
    # Write flat columns to the Synapse SQL table
    flat_df = df.select(flat_columns) if flat_columns else None
    if flat_df and not flat_df.isEmpty():
        table_name = f"{schema_name}.{parent_prefix if parent_prefix else 'root'}"
        
        # Get the valid schema from Synapse table
        table_columns = get_table_schema_synapse(parent_prefix, jdbc_url, db_user, db_password)
        valid_columns = [col.alias for col in flat_columns if col.alias in table_columns]
        valid_flat_df = flat_df.select(*valid_columns)

        if not valid_flat_df.isEmpty():
            valid_flat_df.write \
                .format("com.databricks.spark.sqldw") \
                .option("url", jdbc_url) \
                .option("dbtable", table_name) \
                .option("forwardSparkAzureStorageCredentials", "true") \
                .option("user", db_user) \
                .option("password", db_password) \
                .mode("overwrite") \
                .save()
            print(f"Data written to Synapse table: {table_name}")

    # Recursively process nested structs
    for original_column, nested_prefix in nested_structs:
        nested_df = df.select(col(original_column + ".*"))
        flatten_and_write_synapse(nested_df, nested_prefix, jdbc_url, db_user, db_password, schema_name)


# Step 5: Configure Parameters (ADF or External Parameters)
dbutils.widgets.text("schema_name", "default_schema", "Schema Name")
dbutils.widgets.text("root_table", "Entity", "Root Table Name")
dbutils.widgets.text("container_name", "<container-name>", "Container Name")
dbutils.widgets.text("storage_account", "<storage-account-name>", "Storage Account Name")
dbutils.widgets.text("json_path", "path/to/json", "JSON File Path")
dbutils.widgets.text("synapse_jdbc_url", "", "Synapse JDBC URL")
dbutils.widgets.text("db_user", "<user>", "Database User")
dbutils.widgets.text("db_password", "<password>", "Database Password")

# Retrieve widget/parameter values
schema_name = dbutils.widgets.get("schema_name")
root_table_name = dbutils.widgets.get("root_table")
container_name = dbutils.widgets.get("container_name")
storage_account = dbutils.widgets.get("storage_account")
json_path = dbutils.widgets.get("json_path")
jdbc_url = dbutils.widgets.get("synapse_jdbc_url")
db_user = dbutils.widgets.get("db_user")
db_password = dbutils.widgets.get("db_password")

# Log the received parameters for debugging
print(f"Schema: {schema_name}, Root Table: {root_table_name}, Container: {container_name}, Storage Account: {storage_account}")
print(f"JSON Path: {json_path}, JDBC URL: {jdbc_url}")

# Step 6: Load JSON File
json_file_path = f"abfss://{container_name}@{storage_account}.dfs.core.windows.net/{json_path}"
json_df = spark.read.option("multiLine", True).json(json_file_path)

print("JSON Schema:")
json_df.printSchema()
json_df.show(5, truncate=50)

# Step 7: Write Data to Synapse
# Write root-level fields to root ("Entity") table
write_root_to_entity_table_synapse(json_df, jdbc_url, db_user, db_password, schema_name, root_table_name)

# Recursively parse nested JSON structure (arrays and structs) and write to Synapse
flatten_and_write_synapse(json_df, "", jdbc_url, db_user, db_password, schema_name)

# Cleanup
spark.stop()