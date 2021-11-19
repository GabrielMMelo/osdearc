from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, TimestampType

spark = SparkSession.builder.getOrCreate()


def main():
    df = spark.read.format("parquet").load("s3a://lake-dev/01_bronze/awl_bg/")

    # remove airbyte columns
    df = df.drop(*[column for column in df.columns if "_airbyte" in column]).drop("_id")

    # clean `createdAt`
    df = df.withColumn('reference_date', F.to_timestamp(F.substring(F.col('createdAt'), 0, 19), "yyyy-MM-dd hh:mm:ss"))
    df = df.drop('createdAt')

    # clean `added_date`
    meses = {
        "janeiro": "01",
        "fevereiro": "02",
        "março": "03",
        "abril": "04",
        "maio": "05",
        "junho": "06",
        "julho": "07",
        "agosto": "08",
        "setembro": "09",
        "outubro": "10",
        "novembro": "11",
        "dezembro": "12"
    }
    df = df.withColumn('added_date_day', F.regexp_extract(F.col('added_date'), ".*?(\d{2})\ de\ (.*?)\ de\ (.*)", 1))
    df = df.withColumn('added_date_month', F.regexp_extract(F.col('added_date'), ".*?(\d{2})\ de\ (.*?)\ de\ (.*)", 2))
    df = df.replace(to_replace=meses, subset=['added_date_month'])
    df = df.withColumn('added_date_year', F.regexp_extract(F.col('added_date'), ".*?(\d{2})\ de\ (.*?)\ de\ (.*)", 3))
    df = df.withColumn('added_date', F.to_date(
        F.concat(F.col('added_date_year'), F.lit('-'), F.col('added_date_month'), F.lit('-'), F.col('added_date_day')),
        "yyyy-MM-dd"))
    df = df.drop('added_date_day', 'added_date_month', 'added_date_year')

    # clean `availability`
    df = df.withColumn('is_available', F.when(F.col('availability').isNull(), F.lit(True)).otherwise(False))
    df = df.withColumn('availability_date', F.when(F.col('is_available') == F.lit(0),
                                                   F.regexp_extract(F.col('availability'), "\ em\ (.*)\.", 1)))
    df = df.withColumn('availability_date_day', F.split(F.col('availability_date'), "\/", -1)[0])
    df = df.withColumn('availability_date_month', F.lower(F.split(F.col('availability_date'), "\/", -1)[1]))
    df = df.replace(to_replace=meses, subset=['availability_date_month'])
    df = df.withColumn('availability_date_year', F.split(F.col('availability_date'), "\/", -1)[2])
    df = df.withColumn('availability_date', F.to_date(
        F.concat(F.col('availability_date_year'), F.lit('-'), F.col('availability_date_month'), F.lit('-'),
                 F.col('availability_date_day')), "yyyy-MM-dd"))
    df = df.drop("availability", 'availability_date_day', 'availability_date_month', 'availability_date_year')

    # clean `review_stars`
    df = df.withColumn('review_stars_tmp', F.regexp_extract(F.col('review_stars'), "^(.{3}).*", 1).cast("double"))
    df = df.withColumn('review_stars',
                       F.when(F.col('review_stars_tmp').isNull(), F.lit(-1.0)).otherwise(F.col('review_stars_tmp')))
    df = df.drop('review_stars_tmp')

    # clean `sellers_price`
    df = df.withColumn('has_sellers', F.when(F.col('sellers_price').isNull(), False).otherwise(True))

    # clean `delivery_price`
    df = df.withColumn('has_delivery_tax', F.when(F.col('delivery_price').isNull(), False).otherwise(True))
    df = df.withColumnRenamed('delivery_price', 'delivery_tax_price')

    output_table_name = "awl_bg"
    df.write.format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .save('s3a://lake-dev/02_silver/{}/'.format(output_table_name))


if __name__ == '__main__':
    main()
