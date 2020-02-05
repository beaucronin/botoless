# botoless
 A smaller view of boto3, intended for serverless application development

## Installation

```
pip install botoless
```

## Usage

Botoless makes a few assumptions about how it's being used that allow it to present a much simpler interface than boto3:

1. It assumes that you are building a serverless web app or microservice, so it concentrates on the AWS services and usage patterns that are most relevant to that scenario
2. It assumes that it is being used in the context of a Lambda function runtime; this means, for example, that boto3 will be available and that it will be invoked with the credentials of the AWS account under which that Lambda is deployed


