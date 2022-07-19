# glideinWMS Virtual Machine Bootstrap 

 This repository provides the sources for a service which bootstraps a glideinWMS
 pilot and the resources to automate the building of a VM configured with the 
 bootstrap service.

## Bootstrap Service

 The bootstrap service source and rpm specs are located in the pilot services
 directory.  The bootstrap service currently only supports cloud providers that 
 provide an EC2 style meta-data service.  Plans are in the works to support
 hepix/OpenNebula style user data services.

 The expected user data is in the form:

```
[Base64 encoded blob]####[additional arguments]
```

 or just a plain text ini file.


 "####" was picked as a separator because it will never appear in the base64 
 encoded string and we will make it a rule that it won't appear in the any of the
 userdata, either the base64 encoded blob or the additional arguments.

 If a plain text ini file is sent as user data, then it is assumed that the VM is
 being started up in debug mode.  Essentially, the only option that matters in 
 this case is the disable_shutdown option.  This prevents the service from 
 shutting down the VM, allowing an admin or dev to ssh into the VM for debugging
 purposes.  An example ini file is listed below:

```ini
[glidein_startup]
args = blah
idtoken_file_name = credential_frontend.idtoken
webbase= na

[vm_properties]
max_lifetime = 43200
contextualization_type = EC2
disable_shutdown = True
```

## VM Building

An rpm src file is built using the spec file.
The VM is then built using packer, the base image ISO  and the src rpm.

There are orphan directories for boxgrinder and oz that contain configurations
for building the VM with these two tools.   Boxgrinder is not supported
and oz is nearly so.



