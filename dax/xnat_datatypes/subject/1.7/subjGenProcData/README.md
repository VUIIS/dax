# XNAT 1.7 Workshop Plugin #

This is the XNAT 1.7 Workshop Plugin. It provides examples of most of the primary tools
available for extending and customizing XNAT 1.7.

Information about the XNAT 1.7 Workshop can be found [on the XNAT wiki's Workshop 2016
space](https://wiki.xnat.org/display/XW2).

# Building #

To build the XNAT 1.7 workshop plugin:

1. If you haven't already, clone this repository and cd to the newly cloned folder.
1. Build the plugin: `./gradlew jar` (on Windows, you can use the batch file: `gradlew.bat jar`). This should build the plugin in the file **build/libs/xnat-workshop-plugin-1.0.0.jar** (the version may differ based on updates to the code).
1. Copy the plugin jar to your plugins folder: `cp build/libs/xnat-workshop-plugin-1.0.0.jar /data/xnat/home/plugins`

# Deploying #

Deploying your XNAT plugin just requires copying it to the **plugins** folder for your XNAT installation. The location of the **plugins** folder varies based on how and where you have installed your XNAT. If you are running a virtual machine created through the [XNAT Vagrant project](https://bitbucket/xnatdev/xnat-vagrant.git), you can copy the plugin to the appropriate configuration folder and then copy it within the VM from **/vagrant** to **/data/xnat/home/plugins**.

You can also set up a share for your Vagrant configuration that actually creates the VM's **plugins** folder as a share with your host machine. This allows you to deploy the plugin by copying it into the shared local folder, where it will then appear on the VM in the linked shared folder.

Once you've copied the plugin jar into your XNAT's **plugins** folder, you need to restart the Tomcat server. Your new plugin will be available as soon as the restart and initialization process is completed.

