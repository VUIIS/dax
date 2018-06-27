Dax Integration Test README

Version 1.0 - 27/06/2014


This folder contains a set of tools that make it simpler to integration test DAX installs. As of version 1.0 of this document, these tools can be used to test DAX manually, without the need for most of the additional periphery that this would require, such as work queues and so forth. Subsequently, it will become part of a continuous integration / continuous delivery test suite.

Test Runner:
 * a test runner, named 'test_job_runner.py'
Processors:
 * A series of processor yaml definitions to cover the various relationships that can be created between processor types and their corresponding assessors
 * A series of spiders that are executed by the test runner to fake real work and generate outputs


Contents
./test_job_runner.py
./processors/<processors for integration testing>
./pipelines/test_pipeline.py
./pipelines/<exes for faking work>

