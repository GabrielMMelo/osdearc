import datetime
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import DoubleType, TimestampType


sparkSession = SparkSession.builder.getOrCreate()


def main():
	df = sparkSession.read.options(delimiter=';', header=True).csv('s3a://lake/dev/01_raw/awl_bg_prices/')
	print(df.count())
	print('OK')

if __name__ == '__main__':
	main()
