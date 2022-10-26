from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

import random

# Kafka Broker/Cluster Details
KAFKA_TOPIC_NAME_CONS = "transmessage"
KAFKA_BOOTSTRAP_SERVERS_CONS = '34.70.106.130:9092'

# Cassandra Cluster Details
cassandra_connection_host = "34.70.106.130"
cassandra_connection_port = "9042"
cassandra_keyspace_name = "trans_ks"
cassandra_table_name = "trans_message_detail_tbl"

# MongoDB Cluster Details
mongodb_host_name = "34.70.106.130"
mongodb_port_no = "27017"
mongodb_user_name = "admin"
mongodb_password = "admin"
mongodb_database_name = "trans_db"
mongodb_collection_name = "trans_message_detail_agg_tbl"

def save_to_cassandra_table(current_df, epoc_id):
    print("Inside save_to_cassandra_table function")
    print("Printing epoc_id: ")
    print(epoc_id)

    current_df \
    .write \
    .format("org.apache.spark.sql.cassandra") \
    .mode("append") \
    .option("spark.cassandra.connection.host", cassandra_connection_host) \
    .option("spark.cassandra.connection.port", cassandra_connection_port) \
    .option("keyspace", cassandra_keyspace_name) \
    .option("table", cassandra_table_name) \
    .save()
    print("Exit out of save_to_cassandra_table function")

'''def save_to_mongodb_collection(current_df, epoc_id):
    print("Inside save_to_mongodb_collection function")
    print("Printing epoc_id: ")
    print(epoc_id)

    

    print("Exit out of save_to_mongodb_collection function") '''

if __name__ == "__main__":
    print("Real-Time Data Pipeline Started ...")

    spark = SparkSession \
        .builder \
        .appName("Real-Time Data Pipeline Demo") \
        .master("local[*]") \
        .config("spark.jars", "file:///D://spark_dependency_jars//jsr166e-1.1.0.jar,file:///D://spark_dependency_jars//spark-cassandra-connector-2.4.0-s_2.11.jar,file:///D://work//development//spark_structured_streaming_kafka//spark-sql-kafka-0-10_2.11-2.4.0.jar,file:///D://work//development//spark_structured_streaming_kafka//kafka-clients-1.1.0.jar") \
        .config("spark.executor.extraClassPath", "file:///D://spark_dependency_jars//jsr166e-1.1.0.jar:file:///D://spark_dependency_jars//spark-cassandra-connector-2.4.0-s_2.11.jar:file:///D://work//development//spark_structured_streaming_kafka//spark-sql-kafka-0-10_2.11-2.4.0.jar:file:///D://work//development//spark_structured_streaming_kafka//kafka-clients-1.1.0.jar") \
        .config("spark.executor.extraLibrary", "file:///D://spark_dependency_jars//jsr166e-1.1.0.jar:file:///D://spark_dependency_jars//spark-cassandra-connector-2.4.0-s_2.11.jar:file:///D://work//development//spark_structured_streaming_kafka//spark-sql-kafka-0-10_2.11-2.4.0.jar:file:///D://work//development//spark_structured_streaming_kafka//kafka-clients-1.1.0.jar") \
        .config("spark.driver.extraClassPath", "file:///D://spark_dependency_jars//jsr166e-1.1.0.jar:file:///D://spark_dependency_jars//spark-cassandra-connector-2.4.0-s_2.11.jar:file:///D://work//development//spark_structured_streaming_kafka//spark-sql-kafka-0-10_2.11-2.4.0.jar:file:///D://work//development//spark_structured_streaming_kafka//kafka-clients-1.1.0.jar") \
        .getOrCreate()

    spark.sparkContext.setLogLevel("ERROR")

    # Construct a streaming DataFrame that reads from transmessage
    transaction_detail_df = spark \
        .readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS_CONS) \
        .option("subscribe", KAFKA_TOPIC_NAME_CONS) \
        .option("startingOffsets", "latest") \
        .load()

    print("Printing Schema of transaction_detail_df: ")
    transaction_detail_df.printSchema()

    # Code Block 4 Starts Here
    transaction_detail_schema = StructType([
      StructField("results", ArrayType(StructType([
        StructField("user", StructType([
          StructField("gender", StringType()),
          StructField("name", StructType([
            StructField("title", StringType()),
            StructField("first", StringType()),
            StructField("last", StringType())
          ])),
          StructField("location", StructType([
            StructField("street", StringType()),
            StructField("city", StringType()),
            StructField("state", StringType()),
            StructField("zip", IntegerType())
          ])),
          StructField("email", StringType()),
          StructField("username", StringType()),
          StructField("password", StringType()),
          StructField("salt", StringType()),
          StructField("md5", StringType()),
          StructField("sha1", StringType()),
          StructField("sha256", StringType()),
          StructField("registered", IntegerType()),
          StructField("dob", IntegerType()),
          StructField("phone", StringType()),
          StructField("cell", StringType()),
          StructField("PPS", StringType()),
          StructField("picture", StructType([
            StructField("large", StringType()),
            StructField("medium", StringType()),
            StructField("thumbnail", StringType())
          ]))
        ]))
      ]), True)),
      StructField("nationality", StringType()),
      StructField("seed", StringType()),
      StructField("version", StringType()),
      StructField("tran_detail", StructType([
        StructField("tran_card_type", ArrayType(StringType())),
        StructField("product_id", StringType()),
        StructField("tran_amount", DoubleType())
      ]))
    ])
    # Code Block 4 Ends Here

    transaction_detail_df_1 = transaction_detail_df.selectExpr("CAST(value AS STRING)")

    transaction_detail_df_2 = transaction_detail_df_1.select(from_json(col("value"), transaction_detail_schema).alias("message_detail"))

    transaction_detail_df_3 = transaction_detail_df_2.select("message_detail.*")

    print("Printing Schema of transaction_detail_df_3: ")
    transaction_detail_df_3.printSchema()

    transaction_detail_df_4 = transaction_detail_df_3.select(explode(col("results.user")).alias("user"),
                                                            col("nationality"),
                                                            col("seed"),
                                                            col("version"),
                                                            col("tran_detail.tran_card_type").alias("tran_card_type"),
                                                            col("tran_detail.product_id").alias("product_id"),
                                                            col("tran_detail.tran_amount").alias("tran_amount")
                                                            )

    transaction_detail_df_5 = transaction_detail_df_4.select(
      col("user.gender"),
      col("user.name.title"),
      col("user.name.first"),
      col("user.name.last"),
      col("user.location.street"),
      col("user.location.city"),
      col("user.location.state"),
      col("user.location.zip"),
      col("user.email"),
      col("user.username"),
      col("user.password"),
      col("user.salt"),
      col("user.md5"),
      col("user.sha1"),
      col("user.sha256"),
      col("user.registered"),
      col("user.dob"),
      col("user.phone"),
      col("user.cell"),
      col("user.PPS"),
      col("user.picture.large"),
      col("user.picture.medium"),
      col("user.picture.thumbnail"),
      col("nationality"),
      col("seed"),
      col("version"),
      col("tran_card_type"),
      col("product_id"),
      col("tran_amount")
    )

    def randomCardType(transaction_card_type_list):
        return random.choice(transaction_card_type_list)

    getRandomCardType = udf(lambda transaction_card_type_list: randomCardType(transaction_card_type_list), StringType())

    transaction_detail_df_6 = transaction_detail_df_5.select(
      col("gender"),
      col("title"),
      col("first").alias("first_name"),
      col("last").alias("last_name"),
      col("street"),
      col("city"),
      col("state"),
      col("zip"),
      col("email"),
      concat(col("username"), round(rand() * 1000, 0).cast(IntegerType())).alias("user_id"),
      col("password"),
      col("salt"),
      col("md5"),
      col("sha1"),
      col("sha256"),
      col("registered"),
      col("dob"),
      col("phone"),
      col("cell"),
      col("PPS"),
      col("large"),
      col("medium"),
      col("thumbnail"),
      col("nationality"),
      col("seed"),
      col("version"),
      getRandomCardType(col("tran_card_type")).alias("tran_card_type"),
      concat(col("product_id"), round(rand() * 100, 0).cast(IntegerType())).alias("product_id"),
      round(rand() * col("tran_amount"), 2).alias("tran_amount")
    )

    transaction_detail_df_7 = transaction_detail_df_6.withColumn("tran_date",
      from_unixtime(col("registered"), "yyyy-MM-dd HH:mm:ss"))

    # Write raw data into HDFS
    transaction_detail_df_7.writeStream \
      .trigger(processingTime='5 seconds') \
      .format("json") \
      .option("path", "/data/json/trans_detail_raw_data") \
      .option("checkpointLocation", "/data/checkpoint/trans_detail_raw_data") \
      .start()

    transaction_detail_df_8 = transaction_detail_df_7.select(
      col("user_id"),
      col("first_name"),
      col("last_name"),
      col("gender"),
      col("city"),
      col("state"),
      col("zip"),
      col("email"),
      col("nationality"),
      col("tran_card_type"),
      col("tran_date"),
      col("product_id"),
      col("tran_amount"))

    transaction_detail_df_8 \
    .writeStream \
    .trigger(processingTime='5 seconds') \
    .outputMode("update") \
    .foreachBatch(save_to_cassandra_table) \
    .start()

    # Write result dataframe into console for debugging purpose
    trans_detail_write_stream = transaction_detail_df_8 \
        .writeStream \
        .trigger(processingTime='5 seconds') \
        .outputMode("update") \
        .option("truncate", "false")\
        .format("console") \
        .start()

    trans_detail_write_stream.awaitTermination()

    print("Real-Time Data Pipeline Completed.")