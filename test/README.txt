Dax Integration Test README

Version 1.0 - 27/06/2014


This folder contains a set of tools that make it simpler to integration test DAX
installs. As of version 1.0 of this document, these tools can be used to test
DAX manually, without the need for most of the additional periphery that this
would require, such as work queues and so forth. Subsequently, it will become
part of a continuous integration / continuous delivery test suite.


Contents:

./job_template.txt
The template that invokes test_job_runner.py. This must be copied into
~/.dax_templates/job_template.txt


./test_job_runner.py
The test job runner. It is invoked by the command generated through
job_template.txt and in turn invokes the pipeline processor for the appropriate
pipeline


./processors/<processors for integration testing>
A series of processor yaml definitions to cover the various relationships that
can be created between scans and processor types with their corresponding
assessors

./pipelines/test_pipeline.py
Shared functionality for pipelines that is used by the different processor
pipelines to generate completed jobs and result artefacts

./pipelines/<exes for faking work>
Processor pipelines corresponding to the various test processors, that generate
outputs for the assessors when they are mock executed
