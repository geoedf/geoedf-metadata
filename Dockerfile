FROM continuumio/miniconda3

SHELL ["/bin/bash", "-c"]

USER root
RUN mkdir /code
WORKDIR /code
# Install RabbitMQ

# Install the required packages for the application
RUN apt-get update && \
    apt-get install -y --no-install-recommends rabbitmq-server && \
    pip install pika

# Enable the RabbitMQ Management plugin
RUN rabbitmq-plugins enable rabbitmq_management

# Create conda environment and install packages except hdfeos2
RUN conda create -n geoedf_metadata -y python=3.8 && \
    conda install -f -y -q --name geoedf_metadata -c conda-forge \
    netcdf4 requests pika gdal shapely pyproj pyhdf h5py qgis pyqt=5 oslo.concurrency && \
    conda clean -afy && \
    rm -rf /opt/conda/pkgs/*


ENV PATH /opt/conda/envs/geoedf_metadata/bin:$PATH
RUN pip install click globus_sdk globus_sdk_tokenstorage identify certifi ruamel.yaml

# Expose the RabbitMQ management interface
EXPOSE 5673

## Set up a user and queue for testing
#RUN rabbitmqctl add_user test_user test_pass && \
#    rabbitmqctl add_vhost test_vhost && \
#    rabbitmqctl set_permissions -p test_vhost test_user ".*" ".*" ".*"

#CMD ["rabbitmq-server"]
COPY . /code/
RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
