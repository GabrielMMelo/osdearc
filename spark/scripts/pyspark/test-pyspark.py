from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, TimestampType

sparkSession = SparkSession.builder.getOrCreate()


def main():
    df = sparkSession.read.parquet('s3a://lake/dev/01_raw/awl_bg_tracker_docker/')
    df.write.format("delta").mode("overwrite").save('s3a://lake/dev/02_trusted/test/')


if __name__ == '__main__':
    main()
