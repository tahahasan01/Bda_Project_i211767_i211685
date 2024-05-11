from pyspark.sql import SparkSession
from pyspark.ml.recommendation import ALS
from pyspark.ml.evaluation import RegressionEvaluator

# Create SparkSession
spark = SparkSession.builder \
    .appName("MusicRecommendation") \
    .getOrCreate()

# Load data from MongoDB into Spark DataFrame
audio_features_df = spark.read \
    .format("mongo") \
    .option("uri", "mongodb://localhost:27017/music_recommendation.audio_features") \
    .load()

# Split the data into training and testing sets
(training_data, test_data) = audio_features_df.randomSplit([0.8, 0.2])

# Train ALS (Alternating Least Squares) recommendation model
als = ALS(maxIter=5, regParam=0.01, userCol="user_id", itemCol="track_id", ratingCol="play_count", coldStartStrategy="drop")
model = als.fit(training_data)

# Evaluate the model on the test data
predictions = model.transform(test_data)
evaluator = RegressionEvaluator(metricName="rmse", labelCol="play_count", predictionCol="prediction")
rmse = evaluator.evaluate(predictions)
print("Root Mean Squared Error (RMSE):", rmse)

# Optionally, perform hyperparameter tuning and cross-validation to optimize the model

# Stop SparkSession
spark.stop()
