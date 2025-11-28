# Dockerfile for AWS Lambda - Route Optimizer API
# Uses official AWS Lambda Python 3.11 base image

FROM public.ecr.aws/lambda/python:3.11

# Set working directory to Lambda task root
WORKDIR ${LAMBDA_TASK_ROOT}

# Configure environment variables for Lambda
ENV JOBLIB_TEMP_FOLDER=/tmp
ENV JOBLIB_MULTIPROCESSING=0
ENV OMP_NUM_THREADS=1
ENV OPENBLAS_NUM_THREADS=1
ENV MKL_NUM_THREADS=1

# Copy requirements file
COPY requirements.txt ${LAMBDA_TASK_ROOT}/

# Install Python dependencies
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt --target ${LAMBDA_TASK_ROOT}

# Copy Lambda function code
COPY lambda_function_updated.py ${LAMBDA_TASK_ROOT}/lambda_function.py

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD ["lambda_function.lambda_handler"]
