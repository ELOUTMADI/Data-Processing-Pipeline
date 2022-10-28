# About This project

You can find below the architecture that's been built : 

![Architecture](https://user-images.githubusercontent.com/47195793/198748185-2b761fb6-f96e-4d67-b2c5-5a86e1f9ed71.png)

# How this is working ? 
Well , We've created a VM on GCP and built an SSH with putty to make installation easy for us . We've installed CDH on this VM , so that we can manage easily different technologies that we are going to use Like Apache Hadoop , Spark and Nifi . 

Thanks to randomuser.me we were able to generate data in JSON format . We've connected Apache Nifi with this website and on each new refresh new data will be generated and ingested to Kafka Broker .

The Data has been consumed and processed in a batch fashioned and stored in Dataframe format towards MongoDb and raw data to Cassandra . Apache Hadoop has been used to store some Jar Files to be able to run the code in Cloudera . 

Once the Processed Data starts arriving to MongoDB , some Data Analysis will be immediately displayed on a real time Dashboard that's been implemented with Python Dash .

This is an overview of how this pipeline is working you can go ahead and test it out .
