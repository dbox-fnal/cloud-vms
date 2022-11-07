# Define custom macros
%define is_fedora %(test -e /etc/fedora-release && echo 1 || echo 0)
# From http://fedoraproject.org/wiki/Packaging:Python
# Define python_sitelib
%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

Name:               glideinwms-vm
Version:            2
Release:            3.rc2%{?dist}

Summary:            The glideinWMS service that contextualizes a VM
Group:              System Environment/Daemons
License:            Fermitools Software Legal Information (Modified BSD License)
URL:                http://www.uscms.org/SoftwareComputing/Grid/WMS/glideinWMS/doc.v2/manual/
BuildRoot:          %{_tmppath}/%{name}-buildroot
BuildArchitectures: noarch

Source0:            glideinwms_pilot.tar.gz


%description
glideinWMS pilot launcher service

Sets up a service definition in init.d (glideinwms-pilot) that executes
pilot_launcher.  This script contextualizes a VM to become a glideinWMS worker 
node.  It is responsible for bootstrapping the pilot Condor StartD and shutting 
down the VM once the pilot exits.


###############################################################################
## Sub-Packages
###############################################################################
%package core
Summary:            The glideinWMS service that contextualizes a VM
# Make sure this package is installed *after* /etc/sudoers is created
Requires:           sudo
Requires(post):     /sbin/chkconfig
Requires(pre):      /usr/sbin/groupadd
Requires(pre):      /usr/sbin/useradd
Requires(pre):      /bin/chmod

Group:              System Environment/Daemons

%description core
glideinWMS pilot launcher service

Sets up a service definition in init.d (glideinwms-pilot) that executes
pilot_launcher.  This script contextualizes a VM to become a glideinWMS worker 
node.  It is responsible for bootstrapping the pilot Condor StartD and shutting 
down the VM once the pilot exits.


%package ec2
Summary:            The glideinWMS service that contextualizes a VM
Requires:           glideinwms-vm-core >= %{version}-%{release}
Group:              System Environment/Daemons

%description ec2
glideinWMS pilot launcher service

Configures the glideinmws-vm-core package to use the ec2 style of user data 
retrieval.


%package one
Summary:            The glideinWMS service that contextualizes a VM
Requires:           glideinwms-vm-core >= %{version}-%{release}
Group:              System Environment/Daemons

%description one
glideinWMS pilot launcher service

Configures the glideinmws-vm-core package to use the opennebula style of
user data retrieval.


#%package nimbus
#Summary:            The glideinWMS service that contextualizes a VM
#Requires:           glideinwms-vm-core >= %{version}-%{release}
#Group:              System Environment/Daemons

#%description nimbus
#glideinWMS pilot launcher service

#Configures the glideinmws-vm-core package to use the nimbus style of user data 
#retrieval.

%package gce
Summary:            The glideinWMS service that contextualizes a VM
Requires:           glideinwms-vm-core >= %{version}-%{release}
Group:              System Environment/Daemons

%description gce
glideinWMS pilot launcher service

Configures the glideinmws-vm-core package to use the gce style of user data 
retrieval. However, VM shutdown is DISABLED.


%prep
%setup -q -n glideinwms_pilot

%build
#make %{?_smp_mflags}

###############################################################################
## pre section(s)
###############################################################################
%pre core

# Make glidein_pilot group - We do this because we have encoutered at least one
# OS repo where useradd was configured such that it didn't automatically create
# a group for the user
getent group glidein_pilot >/dev/null || /usr/sbin/groupadd glidein_pilot

# get corresponding gid for the glidein_pilot group name
gid=$(getent group glidein_pilot | cut -d: -f3)

# Make glidein_pilot user
getent passwd glidein_pilot >/dev/null || /usr/sbin/useradd -m -d /home/glidein_pilot -g ${gid} -s /bin/bash glidein_pilot

# Add glidein_pilot to sudoers so that it can shutdown the VM without a password 
/bin/chmod +w /etc/sudoers
echo "Defaults:glidein_pilot !requiretty" >> /etc/sudoers
echo "glidein_pilot ALL= NOPASSWD: ALL" >> /etc/sudoers
/bin/chmod -w /etc/sudoers

# Note that the sudoers file needs to be modified such that requiretty is 
# commented out.  Don't want to modify a system security setting in this rpm
# will add this note to README

###############################################################################
## install section
###############################################################################
%install
[ ${RPM_BUILD_ROOT} != "/" ] && rm -rf ${RPM_BUILD_ROOT}

# For some reason the setup macro cd's into the glideinwms_pilot directory.
# We will move up one directory so that we can access all the source files
# without having to specify relative paths.
cd ..

# "install" the python site-packages directory
install -d $RPM_BUILD_ROOT%{python_sitelib}
# copy the glideinwms_pilot package to the python site-packages directory
cp -arp glideinwms_pilot $RPM_BUILD_ROOT%{python_sitelib}

# install the init.d
install -d  $RPM_BUILD_ROOT%{_initrddir}
install -m 0755 glideinwms-pilot $RPM_BUILD_ROOT%{_initrddir}/glideinwms-pilot

# install the "executable"
install -d $RPM_BUILD_ROOT%{_sbindir}
install -m 0755 pilot-launcher $RPM_BUILD_ROOT%{_sbindir}/pilot-launcher

# install the ini files
install -d  $RPM_BUILD_ROOT%{_sysconfdir}/glideinwms
#install -m 0755 glidein-pilot-nimbus.ini $RPM_BUILD_ROOT%{_sysconfdir}/glideinwms/glidein-pilot-nimbus.ini
install -m 0755 glidein-pilot-ec2.ini $RPM_BUILD_ROOT%{_sysconfdir}/glideinwms/glidein-pilot-ec2.ini
install -m 0755 glidein-pilot-one.ini $RPM_BUILD_ROOT%{_sysconfdir}/glideinwms/glidein-pilot-one.ini
install -m 0755 glidein-pilot-gce.ini $RPM_BUILD_ROOT%{_sysconfdir}/glideinwms/glidein-pilot-gce.ini

# install the PRE and POST script dirs
install -d  $RPM_BUILD_ROOT%{_libexecdir}/glideinwms_pilot/PRE
install -d  $RPM_BUILD_ROOT%{_libexecdir}/glideinwms_pilot/POST

# install the ephemeral storage PRE script
install -m 0755 pre-scripts/mount_ephemeral $RPM_BUILD_ROOT%{_libexecdir}/glideinwms_pilot/PRE/mount_ephemeral

# install the check spot termination script
install -m 0755 pre-scripts/check-preempt-wrap.sh $RPM_BUILD_ROOT%{_libexecdir}/glideinwms_pilot/PRE/check-preempt-wrap.sh

%clean
[ ${RPM_BUILD_ROOT} != "/" ] && rm -rf ${RPM_BUILD_ROOT}


###############################################################################
## post section(s)
###############################################################################
%post core
# $1 = 1 - Installation
# $1 = 2 - Upgrade
# Source: http://www.ibm.com/developerworks/library/l-rpm2/

/sbin/chkconfig --add glideinwms-pilot
/sbin/chkconfig glideinwms-pilot on
mkdir -p %{_localstatedir}/log/glideinwms-pilot
touch %{_localstatedir}/log/glideinwms-pilot/pilot_launcher.log
chown -R glidein_pilot.glidein_pilot %{_localstatedir}/log/glideinwms-pilot

%post ec2

# create a symbolic link to the file using a common name
ln -s %{_sysconfdir}/glideinwms/glidein-pilot-ec2.ini %{_sysconfdir}/glideinwms/glidein-pilot.ini

%post one

# create a symbolic link to the file using a common name
ln -s %{_sysconfdir}/glideinwms/glidein-pilot-one.ini %{_sysconfdir}/glideinwms/glidein-pilot.ini

#%post nimbus

# install the ini
#ln -s %{_sysconfdir}/glideinwms/glidein-pilot-nimbus.ini %{_sysconfdir}/glideinwms/glidein-pilot.ini

%post gce

# install the ini
ln -s %{_sysconfdir}/glideinwms/glidein-pilot-gce.ini %{_sysconfdir}/glideinwms/glidein-pilot.ini


###############################################################################
## preun section(s)
###############################################################################
%preun core
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    /sbin/chkconfig --del glideinwms-pilot
    /usr/sbin/userdel -f glidein_pilot

    rm -rf %{_sbindir}/pilot-launcher
    rm -rf %{_initrddir}/glideinwms-pilot
    rm -rf %{python_sitelib}/glideinwms-pilot
fi

%preun ec2
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    unlink %{_sysconfdir}/glideinwms/glidein-pilot.ini
    rm -rf %{_sysconfdir}/glideinwms/glidein-pilot-ec2.ini
fi

%preun one
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    unlink %{_sysconfdir}/glideinwms/glidein-pilot.ini
    rm -rf %{_sysconfdir}/glideinwms/glidein-pilot-one.ini
fi

#%preun nimbus
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

#if [ "$1" = "0" ] ; then
#    unlink %{_sysconfdir}/glideinwms/glidein-pilot.ini
#    rm -rf %{_sysconfdir}/glideinwms/glidein-pilot-nimbus.ini
#fi

%preun gce
# $1 = 0 - Action is uninstall
# $1 = 1 - Action is upgrade

if [ "$1" = "0" ] ; then
    unlink %{_sysconfdir}/glideinwms/glidein-pilot.ini
    rm -rf %{_sysconfdir}/glideinwms/glidein-pilot-gce.ini
fi


###############################################################################
## files section(s)
###############################################################################
%files core
%defattr(-,root,root,-)
%attr(755,root,root) %{_sbindir}/pilot-launcher
%attr(755,root,root) %{_initrddir}/glideinwms-pilot
%attr(755,root,root) %{python_sitelib}/glideinwms_pilot
%attr(755,root,root) %{_libexecdir}/glideinwms_pilot/PRE/mount_ephemeral

# For the moment there are no post scripts but we want to include the post directory anyway
%dir %{_libexecdir}/glideinwms_pilot/POST


%files ec2
%defattr(-,root,root,-)
%attr(755,root,root) %{_sysconfdir}/glideinwms/glidein-pilot-ec2.ini
%attr(755,root,root) %{_libexecdir}/glideinwms_pilot/PRE/check-preempt-wrap.sh

#%files nimbus
#%defattr(-,root,root,-)
#%attr(755,root,root) %{_sysconfdir}/glideinwms/glidein-pilot-nimbus.ini

%files one
%defattr(-,root,root,-)
%attr(755,root,root) %{_sysconfdir}/glideinwms/glidein-pilot-one.ini

%files gce
%defattr(-,root,root,-)
%attr(755,root,root) %{_sysconfdir}/glideinwms/glidein-pilot-gce.ini

%changelog
* Fri Aug 12 2016 Parag Mhashilkar <parag@fnal.gov> 2-0.1.rc1
- Add support for Google Compute Engine
- Changed the format of userdata. Works with GlideinWMS v3.3+
- Unified the config attribute names used across different cloud types

* Thu Jun 09 2016 Parag Mhashilkar <parag@fnal.gov> 1.0.10-1
- Bug Fix: Correctly extract proxy as last element
- Add a new file check-preempt-wrap.sh in glideinwms-vm-ec2 package under /usr/libexec/glideinwms/PRE/ directory

* Wed Mar 23 2016 Parag Mhashilkar <parag@fnal.gov> 1.0.9-1
- Read the proxy file from user data as last field rather than positional argument
- Bug Fix: Fixed typo in variable name

* Fri Jan 29 2016 Hyunwoo Kim  1.0.8-1
- mount_ephemeral will first look for LVM, if found, it will replace /dev/xvdb

* Thu Dec 17 2015 Hyunwoo Kim  1.0.7-1
- mount_ephemeral will try to format /dev/xvdb with ext4 filesystem when xvdb is EBS in case of c4.* instances
- Tony Tiradani updated user_data.py to deal with gzip

* Thu Oct 15 2015 Hyunwoo Kim  1.0.6-1
- Introduce /home/scratchgwms. mount_ephemeral will try to mount an ephemeral store in this new location.
- If no ephmeral store available, /home/scratchgwms is still used where glidein_startup.sh will run
- /home/glidein_pilot is still used as the initial space where pilot-launcher does some initializations
- This changelog did not show 1.0.5-1 but web1.fnal.gov:/var/www/html/files/glideinwms/prod/6/x86_64/ already had 1.0.5-1
- and yum install installed 1.0.5-1, so I jump to 1.0.6-1

* Wed Aug 20 2014 Parag Mhashilkar  1.0.4-1
- Bug Fix: Start glidein_startup.sh in glidein_pilot's HOME

* Wed Aug 20 2014 Parag Mhashilkar  1.0.3-1
- Bug Fix: Fixed issues preventing execution of PRE and POST scripts

* Tue Aug 19 2014 Parag Mhashilkar  1.0.2-1
- Add vda3 new mount points for ephemeral storage
- Tee the output of mount_ephemeral script to /tmp directory

* Mon Aug 18 2014 Parag Mhashilkar  1.0.1-1
- Add new mount points for ephemeral storage in ec2

* Wed Aug 6 2014 Parag Mhashilkar  1.0-2
- Make glideinwms-vm-core dependency for other rpms

* Thu Jul 31 2014 Parag Mhashilkar  1.0-1
- First stable release

* Mon Sep 09 2013 Parag Mhashilkar  0.4.0
- Added support for OpenNebula style context

* Fri Jul 12 2013 Anthony Tiradani  0.3.2
- Changed the format of expected user data

* Mon Jul 01 2013 Anthony Tiradani  0.3.1
- Fixed typos
- Fixed get_custom_env function

* Thu Feb 28 2013 Anthony Tiradani  0.2.1
- Added PRE and POST scripts

* Tue Sep 04 2012 Anthony Tiradani  0.1.1
- Initial Version

