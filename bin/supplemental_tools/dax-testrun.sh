#!/usr/bin/env bash
#
# Test a new v3 processor yaml file. Test assessor is automatically named 
# "test-NNN" to avoid confusion and for easy cleanup.
#
# This script ties up the terminal while the job is running, so either use 
# tmux/screen or nohup <commandline> &> <logfile>
#
# Options:
#   [--basedir]   A subdir is created here to store all working files.
#                     Defaults to /nobackup/user/${USER}
#   [--delay]     How often in sec to check whether the job has finished.
#                     Defaults to 1800 (30min)
#   --project     XNAT project to test on
#   --session     XNAT session to test on
#   --procyaml    The v3 processor yaml file to test (overrides are not implemented)


# Defaults
basedir="/nobackup/user/${USER}"
delay=1800

# Command line args
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --basedir)   basedir="$2";   shift; shift ;;
        --project)   project="$2";   shift; shift ;;
        --session)   session="$2";   shift; shift ;;
        --procyaml)  procyaml="$2";  shift; shift ;;
        --delay)     delay="$2";     shift; shift ;;
        *) echo "Input ${1} not recognized"; shift ;;
    esac
done
if [ -z "${project}" -o -z "${session}" -o -z "${procyaml}" ]; then
    echo Usage:
    echo $(basename "${0}") [--basedir BASEDIR] [--delay DELAYSEC] --project PROJECT --session SESSION --procyaml proc.yaml
    exit 0
fi

# File and directory names
dstamp=$(date +%Y%m%d-%H%M%S)
tstamp=$(date +%H%M%S)
assessor=$(basename "${procyaml}" .yaml)
filetag="${project}-x-${session}-x-${assessor}-x-${dstamp}"
wkdir="${basedir}/${filetag}" && mkdir "${wkdir}"
yamlfile="test-${tstamp}-$(basename ${procyaml})"
setfile="${wkdir}/settings.yaml"
buildlog="${wkdir}/build.log"
launchlog="${wkdir}/launch.log"
updatelog="${wkdir}/update.log"
uploadlog="${wkdir}/upload.log"
resdir="${wkdir}/Spider_Upload_Dir" && mkdir -p "${resdir}"/{OUTLOG,PBS,PDF}

# Copy yaml file to wkdir and name as "test". v3 pulls assessor label from this filename
cp "${procyaml}" "${wkdir}/${yamlfile}"

# Create dax settings file
cat << EOF > "${setfile}"
---
processorlib: ${wkdir}
modulelib: /data/mcr/centos7/dax_modules
singularity_imagedir: /data/mcr/centos7/singularity
jobtemplate: /data/mcr/centos7/dax_templates/job_template_v3.txt
resdir: ${resdir}
attrs:
  job_rungroup: h_vuiis
  xnat_host: ${XNAT_HOST}
  skip_lastupdate: Y
yamlprocessors:
  - name: PROCESSOR
    filepath: ${yamlfile}
projects:
  - project: ${project}
    yamlprocessors: PROCESSOR
EOF

echo "Logging to ${wkdir}"

# Build
echo "Building"
dax build \
    --logfile "${buildlog}" \
    --project "${project}" \
    --sessions "${session}" \
    "${setfile}"

# FIXME Check for successful build or fail with useful info

# Launch
echo "Launching"
dax launch \
    --logfile "${launchlog}" \
    --project "${project}" \
    --sessions "${session}" \
    "${setfile}"

# Identify and track the job (check every $delay seconds)
jobid=$(grep "INFO - cluster - Submitted batch job" "${launchlog}" | cut -d ' ' -f 11)

if [ -z "${jobid}" ]; then
    echo "Job not launched"
    exit 1
else
    echo "Job ${jobid} launched"
fi

jobstate=
while [ "${jobstate}" != "completed" ]; do
    sleep "${delay}"
    jobstate=$(rtracejob ${jobid} |grep "State")
    jobstate=$(echo ${jobstate##*|})
    echo "Job ${jobid} state: ${jobstate}"
done

# FIXME show the assessor status (JOB_FAILED.txt, READY_TO_COMPLETE.txt, ...)

# FIXME If failed, report error lines in outlog

# Update/upload to get results to xnat
echo Updating
dax update \
    --logfile "${updatelog}" \
    --project "${project}" \
    --sessions "${session}" \
    "${setfile}"

echo "Uploading"
dax upload --project "${project}" --resdir "${resdir}"

# FIXME Can we make it easier to delete test assessors than via XNAT GUI?
