###############################################################################

%define rhel6_minor       %(%{__grep} -o "6.[0-9]*" /etc/redhat-release |%{__sed} -s 's/6.//')
%define rhel7_minor       %(%{__grep} -o "7.[0-9]*" /etc/redhat-release |%{__sed} -s 's/7.//')

%if 0%{?rhel} && 0%{?rhel} <= 6
%{!?__python2: %define __python2 /usr/bin/python2}
%{!?python2_sitelib: %define python2_sitelib %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python2_sitearch: %define python2_sitearch %(%{__python2} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}
%endif

%define __provides_exclude_from %{python2_sitearch}/.*\.so$
%define __provides_exclude_from %{python3_sitearch}/.*\.so$
%define _empty_manifest_terminate_build 0

%if (0%{?fedora} || 0%{?rhel} >= 7)
  %define use_systemd 1
%endif

%if (0%{?fedora} || 0%{?rhel} >= 7)
  %define install_pcscd_polkit_rule 1
%else
  %define enable_polkit_rules_option --disable-polkit-rules-path
%endif

%if (0%{?use_systemd} == 1)
  %define with_initscript --with-initscript=systemd --with-systemdunitdir=%{_unitdir}
  %define with_syslog --with-syslog=journald
%else
  %define with_initscript --with-initscript=sysv
%endif

%define enable_experimental 1

%if (0%{?enable_experimental} == 1)
  %define experimental --enable-all-experimental-features
%endif

%define ldb_modulesdir %(pkg-config --variable=modulesdir ldb)

%if (0%{?fedora} || 0%{?rhel} >= 7)
%define _hardened_build 1
%endif

%if (0%{?fedora} || 0%{?rhel} >= 7)
  %define with_cifs_utils_plugin 1
%else
  %define with_cifs_utils_plugin_option --disable-cifs-idmap-plugin
%endif

%if (0%{?fedora} || (0%{?rhel} == 7 &&  0%{?rhel7_minor} >= 1) || (0%{?rhel} == 6 &&  0%{?rhel6_minor} >= 7))
  %define with_krb5_localauth_plugin 1
%endif

%if (0%{?fedora})
  %define with_python3 1
%else
  %define with_python3_option --without-python3-bindings
%endif

%define alt_add /usr/sbin/alternatives --install
%define alt_rm  /usr/sbin/alternatives --remove

###############################################################################

%define _posixroot        /
%define _root             /root
%define _bin              /bin
%define _sbin             /sbin
%define _srv              /srv
%define _home             /home
%define _lib32            %{_posixroot}lib
%define _lib64            %{_posixroot}lib64
%define _libdir32         %{_prefix}%{_lib32}
%define _libdir64         %{_prefix}%{_lib64}
%define _logdir           %{_localstatedir}/log
%define _rundir           %{_localstatedir}/run
%define _lockdir          %{_localstatedir}/lock/subsys
%define _cachedir         %{_localstatedir}/cache
%define _spooldir         %{_localstatedir}/spool
%define _crondir          %{_sysconfdir}/cron.d
%define _loc_prefix       %{_prefix}/local
%define _loc_exec_prefix  %{_loc_prefix}
%define _loc_bindir       %{_loc_exec_prefix}/bin
%define _loc_libdir       %{_loc_exec_prefix}/%{_lib}
%define _loc_libdir32     %{_loc_exec_prefix}/%{_lib32}
%define _loc_libdir64     %{_loc_exec_prefix}/%{_lib64}
%define _loc_libexecdir   %{_loc_exec_prefix}/libexec
%define _loc_sbindir      %{_loc_exec_prefix}/sbin
%define _loc_bindir       %{_loc_exec_prefix}/bin
%define _loc_datarootdir  %{_loc_prefix}/share
%define _loc_includedir   %{_loc_prefix}/include
%define _rpmstatedir      %{_sharedstatedir}/rpm-state
%define _pkgconfigdir     %{_libdir}/pkgconfig

%define __service         %{_sbin}/service
%define __chkconfig       %{_sbin}/chkconfig
%define __ldconfig        %{_sbin}/ldconfig
%define __useradd         %{_sbindir}/useradd
%define __groupadd        %{_sbindir}/groupadd
%define __getent          %{_bindir}/getent

###############################################################################

%define service_user      root
%define service_group     root
%define service_name      %{name}
%define service_home      /

%define sssdstatedir      %{_localstatedir}/lib/sss
%define dbpath            %{sssdstatedir}/db
%define keytabdir         %{sssdstatedir}/keytabs
%define pipepath          %{sssdstatedir}/pipes
%define mcpath            %{sssdstatedir}/mc
%define pubconfpath       %{sssdstatedir}/pubconf
%define gpocachepath      %{sssdstatedir}/gpo_cache

###############################################################################

Summary:            System Security Services Daemon 
Name:               sssd
Version:            1.14.2
Release:            0%{?dist}
License:            GPLv3+
Group:              Applications/System
URL:                http://fedorahosted.org/sssd

Source0:            https://fedorahosted.org/released/%{name}/%{name}-%{version}.tar.gz
Source1:            %{name}.init
Source2:            %{name}.conf

BuildRoot:          %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:           %{name}-ad = %{version}-%{release}
Requires:           %{name}-common = %{version}-%{release}
Requires:           %{name}-common-pac = %{version}-%{release}
Requires:           %{name}-ipa = %{version}-%{release}
Requires:           %{name}-krb5 = %{version}-%{release}
Requires:           %{name}-ldap = %{version}-%{release}
Requires:           %{name}-proxy = %{version}-%{release}
Requires:           kaosv >= 2.12

%if (0%{?with_python3} == 1)
Requires:           python3-sssdconfig = %{version}-%{release}
%else
Requires:           python-sssdconfig = %{version}-%{release}
%endif

BuildRequires:      autoconf automake libtool m4 popt-devel libtalloc-devel libtevent-devel 
BuildRequires:      libtdb-devel libldb-devel libdhash-devel >= 0.4.2 libcollection-devel
BuildRequires:      libini_config-devel >= 1.1 dbus-devel dbus-libs openldap-devel
BuildRequires:      pam-devel nss-devel nspr-devel pcre-devel libxslt libxml2
BuildRequires:      docbook-style-xsl krb5-devel c-ares-devel python-devel check-devel
BuildRequires:      doxygen libselinux-devel libsemanage-devel bind-utils 
BuildRequires:      keyutils-libs-devel gettext-devel pkgconfig findutils glib2-devel
BuildRequires:      selinux-policy-targeted samba4-devel libsmbclient-devel
BuildRequires:      libnl3-devel http-parser-devel jansson-devel

%if 0%{?fedora}
BuildRequires:      libcmocka-devel >= 1.0.0
%endif

%if (0%{?fedora} >= 20)
BuildRequires:      uid_wrapper
BuildRequires:      nss_wrapper
%endif

%if (0%{?use_systemd} == 1)
BuildRequires:      systemd-devel
%endif

%if (0%{?with_cifs_utils_plugin} == 1)
BuildRequires:      cifs-utils-devel
%endif

%if (0%{?fedora} || (0%{?rhel} >= 7))
BuildRequires:      libnfsidmap-devel
%else
BuildRequires:      nfs-utils-lib-devel
%endif

%if (0%{?with_python3} == 1)
BuildRequires:      python3-devel
%endif

###############################################################################

%description
Provides a set of daemons to manage access to remote directories and
authentication mechanisms. It provides an NSS and PAM interface toward
the system and a pluggable backend system to connect to multiple different
account sources. It is also the basis to provide client auditing and policy
services for projects like FreeIPA.

The sssd subpackage is a meta-package that contains the deamon as well as all
the existing back ends.

###############################################################################

%package common
Summary:            Common files for the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           libldb >= 0.9.3
Requires:           libtdb >= 1.1.3
Requires:           sssd-client%{?_isa} = %{version}-%{release}
Requires:           libsss_idmap = %{version}-%{release}

Conflicts:          sssd < %{version}-%{release}

%if (0%{?use_systemd} == 1)
Requires(post):     systemd-units systemd-sysv
Requires(preun):    systemd-units
Requires(postun):   systemd-units
%else
Requires(post):     initscripts chkconfig
Requires(preun):    initscripts chkconfig
Requires(postun):   initscripts chkconfig
%endif

Provides:           libsss_sudo = %{version}-%{release}
Provides:           libsss_sudo-devel = %{version}-%{release}
Provides:           libsss_autofs = %{version}-%{release}

Obsoletes:          libsss_sudo <= 1.9.93
Obsoletes:          libsss_sudo-devel <= 1.9.93
Obsoletes:          libsss_autofs <= 1.9.93

###############################################################################

%description common
Common files for the SSSD. The common package includes all the files needed
to run a particular back end, however, the back ends are packaged in separate
subpackages such as sssd-ldap.

###############################################################################

%package client
Summary:            SSSD Client libraries for NSS and PAM
Group:              Applications/System
License:            LGPLv3+

Requires(post):     %{__ldconfig} 
Requires(postun):   %{__ldconfig}

%description client
Provides the libraries needed by the PAM and NSS stacks to connect to the SSSD
service.

###############################################################################

%package tools
Summary:            Userspace tools for use with the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}

%if (0%{?with_python3} == 1)
Requires:           python3-sss = %{version}-%{release}
Requires:           python3-sssdconfig = %{version}-%{release}
%else
Requires:           python-sss = %{version}-%{release}
Requires:           python-sssdconfig = %{version}-%{release}
%endif

%description tools
Provides userspace tools for manipulating users, groups, and nested groups in
SSSD when using id_provider = local in /etc/sssd/sssd.conf.

Also provides several other administrative tools:
    * sss_debuglevel to change the debug level on the fly
    * sss_seed which pre-creates a user entry for use in kickstarts
    * sss_obfuscate for generating an obfuscated LDAP password

###############################################################################

%package -n python-sssdconfig
Summary:            SSSD and IPA configuration file manipulation classes and functions
Group:              Applications/System
License:            GPLv3+

BuildArch:          noarch

%description -n python-sssdconfig
Provides python2 files for manipulation SSSD and IPA configuration files.

###############################################################################

%if (0%{?with_python3} == 1)
%package -n python3-sssdconfig
Summary:            SSSD and IPA configuration file manipulation classes and functions
Group:              Applications/System
License:            GPLv3+

BuildArch:          noarch

%description -n python3-sssdconfig
Provides python3 files for manipulation SSSD and IPA configuration files.
%endif

###############################################################################

%package -n python-sss
Summary:            Python2 bindings for sssd
Group:              Development/Libraries
License:            LGPLv3+

Requires:           sssd-common = %{version}-%{release}

%description -n python-sss
Provides python2 module for manipulating users, groups, and nested groups in
SSSD when using id_provider = local in /etc/sssd/sssd.conf.

Also provides several other useful python2 bindings:
    * function for retrieving list of groups user belongs to.
    * class for obfuscation of passwords

###############################################################################

%if (0%{?with_python3} == 1)
%package -n python3-sss
Summary:            Python3 bindings for sssd
Group:              Development/Libraries
License:            LGPLv3+

Requires:           sssd-common = %{version}-%{release}

%description -n python3-sss
Provides python3 module for manipulating users, groups, and nested groups in
SSSD when using id_provider = local in /etc/sssd/sssd.conf.

Also provides several other useful python3 bindings:
    * function for retrieving list of groups user belongs to.
    * class for obfuscation of passwords
%endif

###############################################################################

%package -n python-sss-murmur
Summary:            Python2 bindings for murmur hash function
Group:              Development/Libraries
License:            LGPLv3+

%description -n python-sss-murmur
Provides python2 module for calculating the murmur hash version 3

###############################################################################

%if (0%{?with_python3} == 1)
%package -n python3-sss-murmur
Summary:            Python3 bindings for murmur hash function
Group:              Development/Libraries
License:            LGPLv3+

%description -n python3-sss-murmur
Provides python3 module for calculating the murmur hash version 3
%endif

###############################################################################

%package ldap
Summary:            The LDAP back end of the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}
Requires:           sssd-krb5-common = %{version}-%{release}

Conflicts:          sssd < %{version}-%{release}

%description ldap
Provides the LDAP back end that the SSSD can utilize to fetch identity data
from and authenticate against an LDAP server.

###############################################################################

%package krb5-common
Summary:            SSSD helpers needed for Kerberos and GSSAPI authentication
Group:              Applications/System
License:            GPLv3+

Requires:           cyrus-sasl-gssapi
Requires:           sssd-common = %{version}-%{release}

Conflicts:          sssd < %{version}-%{release}

%description krb5-common
Provides helper processes that the LDAP and Kerberos back ends can use for
Kerberos user or host authentication.

###############################################################################

%package krb5
Summary:            The Kerberos authentication back end for the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}
Requires:           sssd-krb5-common = %{version}-%{release}

Conflicts:          sssd < %{version}-%{release}

%description krb5
Provides the Kerberos back end that the SSSD can utilize authenticate
against a Kerberos server.

###############################################################################

%package common-pac
Summary:            Common files needed for supporting PAC processing
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}

%description common-pac
Provides common files needed by SSSD providers such as IPA and Active Directory
for handling Kerberos PACs.

###############################################################################

%package ipa
Summary:            The IPA back end of the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}
Requires:           sssd-krb5-common = %{version}-%{release}
Requires:           libipa_hbac = %{version}-%{release}
Requires:           bind-utils
Requires:           sssd-common-pac = %{version}-%{release}

Conflicts:          sssd < %{version}-%{release}

%description ipa
Provides the IPA back end that the SSSD can utilize to fetch identity data
from and authenticate against an IPA server.

###############################################################################

%package ad
Summary:            The AD back end of the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}
Requires:           sssd-krb5-common = %{version}-%{release}
Requires:           bind-utils
Requires:           sssd-common-pac = %{version}-%{release}

Conflicts: sssd < %{version}-%{release}

%description ad
Provides the Active Directory back end that the SSSD can utilize to fetch
identity data from and authenticate against an Active Directory server.

###############################################################################

%package proxy
Summary:            The proxy back end of the SSSD
Group:              Applications/System
License:            GPLv3+

Conflicts:          sssd < %{version}-%{release}
Requires:           sssd-common = %{version}-%{release}

%description proxy
Provides the proxy back end which can be used to wrap an existing NSS and/or
PAM modules to leverage SSSD caching.

###############################################################################

%package -n libsss_idmap
Summary:            FreeIPA Idmap library
Group:              Development/Libraries
License:            LGPLv3+

Requires(post):     %{__ldconfig}
Requires(postun):   %{__ldconfig}

%description -n libsss_idmap
Utility library to convert SIDs to Unix uids and gids

###############################################################################

%package -n libsss_idmap-devel
Summary:            FreeIPA Idmap library
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libsss_idmap = %{version}-%{release}

%description -n libsss_idmap-devel
Utility library to SIDs to Unix uids and gids

###############################################################################

%package -n libipa_hbac
Summary:            FreeIPA HBAC Evaluator library
Group:              Development/Libraries
License:            LGPLv3+

Requires(post):     %{__ldconfig}
Requires(postun):   %{__ldconfig}

%description -n libipa_hbac
Utility library to validate FreeIPA HBAC rules for authorization requests

###############################################################################

%package -n libipa_hbac-devel
Summary:            FreeIPA HBAC Evaluator library
Group:              Development/Libraries
License:            LGPLv3+ 

Requires:           libipa_hbac = %{version}-%{release}

%description -n libipa_hbac-devel
Utility library to validate FreeIPA HBAC rules for authorization requests

###############################################################################

%package -n python-libipa_hbac
Summary:            Python2 bindings for the FreeIPA HBAC Evaluator library
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libipa_hbac = %{version}-%{release}
Provides:           libipa_hbac-python = %{version}-%{release}

Obsoletes:          libipa_hbac-python < 1.12.90

%description -n python-libipa_hbac
The python-libipa_hbac contains the bindings so that libipa_hbac can be
used by Python applications.

###############################################################################

%if (0%{?with_python3} == 1)
%package -n python3-libipa_hbac
Summary:            Python3 bindings for the FreeIPA HBAC Evaluator library
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libipa_hbac = %{version}-%{release}

%description -n python3-libipa_hbac
The python3-libipa_hbac contains the bindings so that libipa_hbac can be
used by Python applications.
%endif

###############################################################################

%package -n libsss_nss_idmap
Summary:            Library for SID based lookups
Group:              Development/Libraries
License:            LGPLv3+

Requires(post):     %{__ldconfig}
Requires(postun):   %{__ldconfig}

%description -n libsss_nss_idmap
Utility library for SID based lookups

###############################################################################

%package -n libsss_nss_idmap-devel
Summary:            Library for SID based lookups
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libsss_nss_idmap = %{version}-%{release}

%description -n libsss_nss_idmap-devel
Utility library for SID based lookups

###############################################################################

%package -n python-libsss_nss_idmap
Summary:            Python2 bindings for libsss_nss_idmap
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libsss_nss_idmap = %{version}-%{release}
Provides:           libsss_nss_idmap-python = %{version}-%{release}

Obsoletes:          libsss_nss_idmap-python < 1.12.90

%description -n python-libsss_nss_idmap
The python-libsss_nss_idmap contains the bindings so that libsss_nss_idmap can
be used by Python applications.

###############################################################################

%if (0%{?with_python3} == 1)
%package -n python3-libsss_nss_idmap
Summary:            Python3 bindings for libsss_nss_idmap
Group:              Development/Libraries
License:            LGPLv3+

Requires:           libsss_nss_idmap = %{version}-%{release}

%description -n python3-libsss_nss_idmap
The python3-libsss_nss_idmap contains the bindings so that libsss_nss_idmap can
be used by Python applications.
%endif

###############################################################################

%package dbus
Summary:            The D-Bus responder of the SSSD
Group:              Applications/System
License:            GPLv3+

Requires:           sssd-common = %{version}-%{release}

BuildRequires:      augeas-devel

%description dbus
Provides the D-Bus responder of the SSSD, called the InfoPipe, that allows
the information from the SSSD to be transmitted over the system bus.

###############################################################################

%package -n libsss_simpleifp
Summary:            The SSSD D-Bus responder helper library
Group:              Development/Libraries
License:            GPLv3+

Requires:           dbus-libs
Requires:           sssd-dbus = %{version}-%{release}

Requires(post):     %{__ldconfig}
Requires(postun):   %{__ldconfig}

%description -n libsss_simpleifp
Provides library that simplifies D-Bus API for the SSSD InfoPipe responder.

###############################################################################

%package -n libsss_simpleifp-devel
Summary:            The SSSD D-Bus responder helper library
Group:              Development/Libraries
License:            GPLv3+

Requires:           dbus-devel
Requires:           libsss_simpleifp = %{version}-%{release}

%description -n libsss_simpleifp-devel
Provides library that simplifies D-Bus API for the SSSD InfoPipe responder.

###############################################################################

%package libwbclient
Summary:            The SSSD libwbclient implementation
Group:              Applications/System
License:            GPLv3+ and LGPLv3+

%description libwbclient
The SSSD libwbclient implementation.

###############################################################################

%package libwbclient-devel
Summary:            Development libraries for the SSSD libwbclient implementation
Group:              Development/Libraries
License:            GPLv3+ and LGPLv3+

%description libwbclient-devel
Development libraries for the SSSD libwbclient implementation.

###############################################################################

%package winbind-idmap
Summary:            SSSD's idmap_sss Backend for Winbind
Group:              Applications/System
License:            GPLv3+ and LGPLv3+

%description winbind-idmap
The idmap_sss module provides a way for Winbind to call SSSD to map UIDs/GIDs
and SIDs.

###############################################################################

%prep
%setup -qn %{name}-%{version}

%build
%ifarch i386
export CFLAGS="$CFLAGS -march=i686"
%endif

autoreconf -ivf

%{configure} \
    --with-test-dir=/dev/shm \
    --with-db-path=%{dbpath} \
    --with-mcache-path=%{mcpath} \
    --with-pipe-path=%{pipepath} \
    --with-pubconf-path=%{pubconfpath} \
    --with-gpo-cache-path=%{gpocachepath} \
    --with-init-dir=%{_initrddir} \
    --with-krb5-rcache-dir=%{_localstatedir}/cache/krb5rcache \
    --enable-nsslibdir=/%{_lib} \
    --enable-pammoddir=/%{_lib}/security \
    --enable-nfsidmaplibdir=%{_libdir}/libnfsidmap \
    --disable-static \
    --disable-rpath \
    --with-sssd-user=%{service_user} \
    %{with_initscript} \
    %{?with_syslog} \
    %{?with_cifs_utils_plugin_option} \
    %{?with_python3_option} \
    %{?enable_polkit_rules_option} \
    %{?experimental}

%{__make} %{?_smp_mflags} all
%{__make} %{?_smp_mflags} docs

%install
rm -rf %{buildroot}

%if (0%{?with_python3} == 1)
sed -i -e 's:/usr/bin/python:/usr/bin/python3:' src/tools/sss_obfuscate
%endif

%{make_install} DESTDIR=%{buildroot}

/usr/lib/rpm/find-lang.sh %{buildroot} %{name}

install -dm 755 %{buildroot}%{_initrddir}
install -dm 755 %{buildroot}%{_sysconfdir}/%{name}
install -dm 755 %{buildroot}%{_sysconfdir}/logrotate.d
install -dm 755 %{buildroot}%{_sysconfdir}/rwtab.d
install -dm 750 %{buildroot}%{_logdir}/%{name}

install -pm 644 src/examples/rwtab %{buildroot}%{_sysconfdir}/rwtab.d/sssd
install -pm 644 src/examples/logrotate %{buildroot}%{_sysconfdir}/logrotate.d/sssd

install -pm 600 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}/%{name}.conf

%if (0%{?use_systemd} == 0)
install -pm 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%endif

find %{buildroot} -name "*.la" -exec rm -f {} \;

rm -Rf %{buildroot}%{_docdir}/%{name}

for file in `ls %{buildroot}%{python2_sitelib}/*.egg-info 2> /dev/null` ; do
  echo %{python2_sitelib}/`basename $file` >> python2_sssdconfig.lang
done

%if (0%{?with_python3} == 1)
for file in `ls %{buildroot}%{python3_sitelib}/*.egg-info 2> /dev/null` ; do
  echo %{python3_sitelib}/`basename $file` >> python3_sssdconfig.lang
done
%endif

touch %{name}.lang
touch %{name}_tools.lang
touch %{name}_client.lang

for provider in ldap krb5 ipa ad proxy ; do
  touch %{name}_$provider.lang
done

for man in `find %{buildroot}%{_mandir}/??/man?/ -type f | sed -e "s#%{buildroot}%{_mandir}/##"` ; do
  lang=`echo $man | cut -c 1-2`
  case `basename $man` in
    sss_cache*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}.lang
      ;;
    sss_*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_tools.lang
      ;;
    sssd_krb5_*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_client.lang
      ;;
    pam_sss*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_client.lang
      ;;
    sssd-ldap*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_ldap.lang
      ;;
    sssd-krb5*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_krb5.lang
      ;;
    sssd-ipa*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_ipa.lang
      ;;
    sssd-ad*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_ad.lang
      ;;
    sssd-proxy*)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}_proxy.lang
      ;;
    *)
      echo \%lang\(${lang}\) \%{_mandir}/${man}\* >> %{name}.lang
      ;;
  esac
done

%clean
rm -rf %{buildroot}

###############################################################################

%if (0%{?use_systemd} == 1)

%post common
%service_add_post %{service_name}.service

%preun common
%service_del_preun %{service_name}.service

%postun
%service_del_postun %{service_name}.service

%else

%post common
if [[ $1 -eq 1 ]] ; then
  %{__chkconfig} --add %{service_name}
fi

%preun common
if [[ $1 -eq 0 ]] ; then
  %{__service} %{service_name} stop 2>&1 > /dev/null
  %{__chkconfig} --del %{service_name}
fi

%endif

%if (0%{?with_cifs_utils_plugin} == 1)

%post client
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
  
  %{alt_add} %{_sysconfdir}/cifs-utils/idmap-plugin \
             cifs-idmap-plugin \
             %{_libdir}/cifs-utils/cifs_idmap_sss.so 20
fi

%preun client
if [[ $1 -eq 0 ]] ; then
  %{alt_rm} cifs-idmap-plugin %{_libdir}/cifs-utils/cifs_idmap_sss.so
fi

%else

%post client
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%endif

%postun client
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%post -n libipa_hbac
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%postun -n libipa_hbac
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%post -n libsss_idmap
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%postun -n libsss_idmap
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%post -n libsss_nss_idmap
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

%postun -n libsss_nss_idmap
if [[ $1 -eq 1 ]] ; then
  %{__ldconfig}
fi

###############################################################################

%files
%defattr(-,root,root,-)
%doc COPYING

%files common -f %{name}.lang
%defattr(-,root,root,-)
%doc COPYING
%doc src/examples/%{name}-example.conf
%{_sbindir}/%{name}
%if (0%{?use_systemd} == 1)
%{_unitdir}/%{name}.service
%{_unitdir}/%{name}-secrets.service
%{_unitdir}/%{name}-secrets.socket
%else
%{_initrddir}/%{name}
%endif

%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/sssd_be
%{_libexecdir}/%{name}/sssd_nss
%{_libexecdir}/%{name}/sssd_pam
%{_libexecdir}/%{name}/sssd_autofs
%{_libexecdir}/%{name}/sssd_secrets
%{_libexecdir}/%{name}/sssd_ssh
%{_libexecdir}/%{name}/sssd_sudo
%{_libexecdir}/%{name}/p11_child

%if (0%{?install_pcscd_polkit_rule} == 1)
%{_datadir}/polkit-1/rules.d/*
%endif

%dir %{_libdir}/%{name}
%{_libdir}/%{name}/libsss_simple.so

%{_libdir}/%{name}/libsss_child.so
%{_libdir}/%{name}/libsss_crypt.so
%{_libdir}/%{name}/libsss_cert.so
%{_libdir}/%{name}/libsss_debug.so
%{_libdir}/%{name}/libsss_krb5_common.so
%{_libdir}/%{name}/libsss_ldap_common.so
%{_libdir}/%{name}/libsss_util.so
%{_libdir}/%{name}/libsss_semanage.so

%{_libdir}/sssd/modules/libsss_autofs.so
%{_libdir}/libsss_sudo.so
%{_libdir}/libnfsidmap/sss.so

%{ldb_modulesdir}/memberof.so
%{_bindir}/sss_ssh_authorizedkeys
%{_bindir}/sss_ssh_knownhostsproxy
%{_sbindir}/sss_cache
%{_libexecdir}/%{name}/sss_signal

%dir %{sssdstatedir}
%dir %{_localstatedir}/cache/krb5rcache
%attr(700,%{service_user},%{service_group}) %dir %{dbpath}
%attr(755,%{service_user},%{service_group}) %dir %{mcpath}
%ghost %attr(0644,%{service_user},%{service_group}) %verify(not md5 size mtime) %{mcpath}/passwd
%ghost %attr(0644,%{service_user},%{service_group}) %verify(not md5 size mtime) %{mcpath}/group
%ghost %attr(0644,%{service_user},%{service_group}) %verify(not md5 size mtime) %{mcpath}/initgroups
%attr(755,%{service_user},%{service_group}) %dir %{pipepath}
%attr(755,%{service_user},%{service_group}) %dir %{pubconfpath}
%attr(755,%{service_user},%{service_group}) %dir %{gpocachepath}
%attr(700,%{service_user},%{service_group}) %dir %{pipepath}/private
%attr(750,%{service_user},%{service_group}) %dir %{_logdir}/%{name}
%attr(711,%{service_user},%{service_group}) %dir %{_sysconfdir}/%{name}
%if (0%{?use_systemd} == 1)
%attr(755,root,root) %dir %{_sysconfdir}/systemd/system/%{name}.service.d
%config(noreplace) %{_sysconfdir}/systemd/system/%{name}.service.d/journal.conf
%endif
%attr(0600,%{service_user},%{service_group}) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/sssd
%config(noreplace) %{_sysconfdir}/rwtab.d/sssd
%dir %{_datadir}/sssd
%{_sysconfdir}/pam.d/sssd-shadowutils
%{_libdir}/%{name}/conf/sssd.conf
%{_datadir}/sssd/cfg_rules.ini
%{_datadir}/sssd/sssd.api.conf
%{_datadir}/sssd/sssd.api.d
%{_mandir}/man1/sss_ssh_authorizedkeys.1*
%{_mandir}/man1/sss_ssh_knownhostsproxy.1*
%{_mandir}/man5/sssd.conf.5*
%{_mandir}/man5/sssd-secrets.5*
%{_mandir}/man5/sssd-simple.5*
%{_mandir}/man5/sssd-sudo.5*
%{_mandir}/man5/sss_rpcidmapd.5*
%{_mandir}/man8/sssd.8*
%{_mandir}/man8/sss_cache.8*

%files ldap -f sssd_ldap.lang
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/%{name}/libsss_ldap.so
%{_mandir}/man5/sssd-ldap.5*

%files krb5-common
%defattr(-,root,root,-)
%doc COPYING
%attr(755,%{service_user},%{service_group}) %dir %{pubconfpath}/krb5.include.d
%attr(4750,root,%{service_group}) %{_libexecdir}/%{name}/ldap_child
%attr(4750,root,%{service_group}) %{_libexecdir}/%{name}/krb5_child

%files krb5 -f sssd_krb5.lang
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/%{name}/libsss_krb5.so
%{_mandir}/man5/sssd-krb5.5*

%files common-pac
%defattr(-,root,root,-)
%doc COPYING
%{_libexecdir}/%{name}/%{name}_pac

%files ipa -f %{name}_ipa.lang
%defattr(-,root,root,-)
%doc COPYING
%attr(700,%{service_user},%{service_group}) %dir %{keytabdir}
%{_libdir}/%{name}/libsss_ipa.so
%attr(4750,root,%{service_user}) %{_libexecdir}/%{name}/selinux_child
%{_mandir}/man5/%{name}-ipa.5*

%files ad -f sssd_ad.lang
%defattr(-,root,root,-)
%doc COPYING
%{_libdir}/%{name}/libsss_ad.so
%{_libexecdir}/%{name}/gpo_child
%{_mandir}/man5/%{name}-ad.5*

%files proxy
%defattr(-,root,root,-)
%doc COPYING
%attr(4750,root,sssd) %{_libexecdir}/%{name}/proxy_child
%{_libdir}/%{name}/libsss_proxy.so

%files dbus
%defattr(-,root,root,-)
%doc COPYING
%{_libexecdir}/%{name}/sssd_ifp
%{_mandir}/man5/sssd-ifp.5*
%{_sysconfdir}/dbus-1/system.d/org.freedesktop.sssd.infopipe.conf
%{_datadir}/dbus-1/system-services/org.freedesktop.sssd.infopipe.service
%{_libdir}/%{name}/libsss_config.so

%files -n libsss_simpleifp
%defattr(-,root,root,-)
%{_libdir}/libsss_simpleifp.so.*

%files -n libsss_simpleifp-devel
%defattr(-,root,root,-)
%doc sss_simpleifp_doc/html
%{_includedir}/sss_sifp.h
%{_includedir}/sss_sifp_dbus.h
%{_libdir}/libsss_simpleifp.so
%{_libdir}/pkgconfig/sss_simpleifp.pc

%files client -f sssd_client.lang
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
/%{_lib}/libnss_sss.so.2
/%{_lib}/security/pam_sss.so
%{_libdir}/krb5/plugins/libkrb5/sssd_krb5_locator_plugin.so
%{_libdir}/krb5/plugins/authdata/sssd_pac_plugin.so
%if (0%{?with_cifs_utils_plugin} == 1)
%{_libdir}/cifs-utils/cifs_idmap_sss.so
%ghost %{_sysconfdir}/cifs-utils/idmap-plugin
%endif
%if (0%{?with_krb5_localauth_plugin} == 1)
%{_libdir}/%{name}/modules/sssd_krb5_localauth_plugin.so
%endif
%{_mandir}/man8/pam_sss.8*
%{_mandir}/man8/sssd_krb5_locator_plugin.8*

%files tools -f sssd_tools.lang
%defattr(-,root,root,-)
%doc COPYING
%{_sbindir}/sss_useradd
%{_sbindir}/sss_userdel
%{_sbindir}/sss_usermod
%{_sbindir}/sss_groupadd
%{_sbindir}/sss_groupdel
%{_sbindir}/sss_groupmod
%{_sbindir}/sss_groupshow
%{_sbindir}/sss_obfuscate
%{_sbindir}/sss_override
%{_sbindir}/sss_debuglevel
%{_sbindir}/sss_seed
%{_sbindir}/sssctl
%{_mandir}/man8/sss_groupadd.8*
%{_mandir}/man8/sss_groupdel.8*
%{_mandir}/man8/sss_groupmod.8*
%{_mandir}/man8/sss_groupshow.8*
%{_mandir}/man8/sss_useradd.8*
%{_mandir}/man8/sss_userdel.8*
%{_mandir}/man8/sss_usermod.8*
%{_mandir}/man8/sss_obfuscate.8*
%{_mandir}/man8/sss_override.8*
%{_mandir}/man8/sss_debuglevel.8*
%{_mandir}/man8/sss_seed.8*
%{_mandir}/man8/sssctl.8*

%files -n python-sssdconfig -f python2_sssdconfig.lang
%defattr(-,root,root,-)
%dir %{python2_sitelib}/SSSDConfig
%{python2_sitelib}/SSSDConfig/*.py*

%if (0%{?with_python3} == 1)
%files -n python3-sssdconfig -f python3_sssdconfig.lang
%defattr(-,root,root,-)
%dir %{python3_sitelib}/SSSDConfig
%{python3_sitelib}/SSSDConfig/*.py*
%{python3_sitelib}/SSSDConfig/__pycache__/*.py*
%endif

%files -n python-sss
%defattr(-,root,root,-)
%{python2_sitearch}/pysss.so

%if (0%{?with_python3} == 1)
%files -n python3-sss
%defattr(-,root,root,-)
%{python3_sitearch}/pysss.so
%endif

%files -n python-sss-murmur
%defattr(-,root,root,-)
%{python2_sitearch}/pysss_murmur.so

%if (0%{?with_python3} == 1)
%files -n python3-sss-murmur
%defattr(-,root,root,-)
%{python3_sitearch}/pysss_murmur.so
%endif

%files -n libsss_idmap
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libsss_idmap.so.*

%files -n libsss_idmap-devel
%defattr(-,root,root,-)
%doc idmap_doc/html
%{_includedir}/sss_idmap.h
%{_libdir}/libsss_idmap.so
%{_libdir}/pkgconfig/sss_idmap.pc

%files -n libipa_hbac
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libipa_hbac.so.*

%files -n libipa_hbac-devel
%defattr(-,root,root,-)
%doc hbac_doc/html
%{_includedir}/ipa_hbac.h
%{_libdir}/libipa_hbac.so
%{_libdir}/pkgconfig/ipa_hbac.pc

%files -n libsss_nss_idmap
%defattr(-,root,root,-)
%doc src/sss_client/COPYING src/sss_client/COPYING.LESSER
%{_libdir}/libsss_nss_idmap.so.*

%files -n libsss_nss_idmap-devel
%defattr(-,root,root,-)
%doc nss_idmap_doc/html
%{_includedir}/sss_nss_idmap.h
%{_libdir}/libsss_nss_idmap.so
%{_libdir}/pkgconfig/sss_nss_idmap.pc

%files -n python-libsss_nss_idmap
%defattr(-,root,root,-)
%{python2_sitearch}/pysss_nss_idmap.so

%if (0%{?with_python3} == 1)
%files -n python3-libsss_nss_idmap
%defattr(-,root,root,-)
%{python3_sitearch}/pysss_nss_idmap.so
%endif

%files -n python-libipa_hbac
%defattr(-,root,root,-)
%{python2_sitearch}/pyhbac.so

%if (0%{?with_python3} == 1)
%files -n python3-libipa_hbac
%defattr(-,root,root,-)
%{python3_sitearch}/pyhbac.so
%endif

%files libwbclient
%defattr(-,root,root,-)
%{_libdir}/%{name}/modules/libwbclient.so.*

%files libwbclient-devel
%defattr(-,root,root,-)
%{_includedir}/wbclient_sssd.h
%{_libdir}/%{name}/modules/libwbclient.so
%{_libdir}/pkgconfig/wbclient_sssd.pc

%files winbind-idmap
%defattr(-,root,root,-)
%dir %{_libdir}/samba/idmap
%{_libdir}/samba/idmap/sss.so
%{_mandir}/man8/idmap_sss.8*

###############################################################################

%changelog
* Wed Nov 09 2016 Anton Novojilov <andy@essentialkaos.com> - 1.14.2-0
- Several more regressions caused by cache refactoring to use qualified names
  internally were fixed, including a regression that prevented the krb5_map_user
  option from working correctly.
- A regression when logging in with a smart card using the GDM login manager
  was fixed
- SSSD now removes the internal timestamp on startup cache when the persistent
  cache is removed. This enables admins to follow their existing workflow of
  just removing the persistent cache and start from a fresh slate
- Several fixes to the sssd-secrets responder are present in this release
- A bug in the autofs responder that prevented automounter maps from being
  returned when sssd_be was offline was fixed
- A similar bug in the NSS responder that prevented netgroups from being
  returned when sssd_be was offline was fixed
- Disabling the netlink integration can now be done with a new option
  disable_netlink. Previously, the netlink integration could be disabled
  with a sssd command line switch, which is being deprecated in this release.
- The internal watchdog no longer kills sssd processes in case time shifts
  during sssd runtime
- The fail over code is able to cope with concurrent SRV resolution requests
  better in this release
- The proxy provider gained a new option proxy_max_children that allows
  the administrator to control the maximum number of child helper processes
  that authenticate users with auth_provider=proxy
- The InfoPipe D-Bus responder exports the UUIDs of user and group objects
  through a uniqueID property
- The private pipe directory permissions were changed from 0700 to 0750.
  The restrictive permissions we causing SELinux dac_override denials
- The Python packages for python2 were renamed from python-package to
  python2-package with backwards-compatible Provides and Obsoletes
- The sssd-common subpackage contains a new manual page sssd-secrets(5)
- The sssd-tools subpackage explicitly Requires /sbin/service on platforms
  that don't support systemd in order to be able to restart sssd from
  the sssctl tool
- The kill_service option that was no longer useful after we moved from
  in-process pings to watchdog was removed
- The --disable-netlink sssd(8) command-line option was removed in favor
  of [sssd] section option disable_netlink
- The proxy_max_children option was added. Please see the highlights
  section for more details.
- The sssd-secrets responder gained a man page in this release.
- Two new options containers_nest_level and max_secrets options
  were added to the sssd-secrets responder. The former allows the
  administrator to configure the maximum nesting level of secrets
  containers, the latter allows the administrator to configure the
  maximum number of secrets that can be stored. Please note that both
  option apply to the local secrets provider only.
- The sssd-ldap man page didn't specify different default for user and
  group name LDAP attribute default for the AD provider. This documentation
  bug was fixed.

* Mon Oct 17 2016 Anton Novojilov <andy@essentialkaos.com> - 1.14.1-0
- The IPA provider now supports logins with enterprise principals (also known
  as additional UPN suffixes). This functionality also enabled Active Directory
  users from trusted AD domains who use an additional UPN suffix to log in.
  Please note that this feature requires a recent IPA server.
- When a user name is overriden in an IPA domain, resolving a group these users
  are a member of now returns the overriden user names
- Users can be looked up by and log in with their e-mail address as
  an identifier. In order to do so, an attribute that represents the user's
  e-mail address is fetched by default. This attribute can by customized by
  setting the ldap_user_email configuration option.
- A new ad_enabled_domains option was added. This option lets the administrator
  select domains that SSSD should attempt to reach in the AD forest SSSD is
  joined to. This option is useful for deployments where not all domains are
  reachable on the network level, yet the administrator needs to access some
  trusted domains and therefore disabling the subdomains provider completely
  is not desirable.
- The sssctl tool has two new commands active-server and servers that allow
  the administrator to observe the server that SSSD is bound to and the
  servers that SSSD autodiscovered
- SSSD used to fail to start when an attribute name is present in both the
  default SSSD attribute map and the custom ldap_user_extra_attrs map
- GPO policy procesing no longer fails if the gPCMachineExtensionNames attribute
  only contains whitespaces
- Several commits fix regressions related to switching all user and group names
  to fully qualified format, such as running initgroups for a user who is only
  a member of a primary group
- Several patches fix regressions caused by splitting the database into two ldb
  files, such as when user attributes change without increasing the
  modifyTimestamp attribute value
- systemd unit files are now shipped for the sssd-secrets responder, allowing
  the responder to be socket-activated. To do so, administrators should enable
  the sssd-secrets.socket and sssd-secrets.service systemd units.
- The sssd binary has a new switch --disable-netlink that lets sssd skip
  messages from the kernel's netlink interface.
- A crash when entries with special characters such as '(' were requested was
  fixed
- The ldap_rfc_2307_fallback_to_local_users option was broken in the previous
  version. This release fixes the functionality.

* Sun Jun 19 2016 Anton Novojilov <andy@essentialkaos.com> - 1.13.4-0
- The IPA sudo provider was reimplemented. The new version reads the data 
  from IPA's LDAP tree (as opposed to the compat tree populated by the 
  slapi-nis plugin that was used previously). The benefit is that deployments 
  which don't require the compat tree for other purposes, such as support for 
  non-SSSD clients can disable those autogenerated LDAP trees to conserve 
  resources that slapi-nis otherwise requires. There should be no visible 
  changes to the end user.
- SSSD now has the ability to renew the machine credentials (keytabs) when 
  the ad provider is used. Please note that a recent version of the adcli 
  (0.8 or newer) package is required for this feature to work.
- The automatic ID mapping feature was improved so that the administrator is 
  no longer required to manually set the range size in case a RID in the AD 
  domain is larger than the default range size
- A potential infinite loop in the NFS ID mapping plugin that was resulting 
  in an excessive memory usage was fixed
- Clients that are pinned to a particular AD site using the ad_site option 
  no longer communicate with DCs outside that site during service discovery.
- The IPA identity provider is now able to resolve external (typically coming 
  from a trusted AD forest) group members during get-group-information 
  requests. Please note that resolving external group memberships for AD users 
  during the initgroup requests used to work even prior to this update. This 
  feature is mostly useful for cases where an IPA client is using the compat 
  tree to resolve AD trust users.
- The IPA ID views feature now works correctly even for deployments without 
  a trust relationship. Previously, the subdomains IPA provider failed to 
  read the views data if no master domain record was created on the IPA 
  server during trust establishment.
- A race condition in the client libraries between the SSSD closing the 
  socket as idle and the client application using the socket was fixed. This 
  bug manifested with a Broken Pipe error message on the client.
- SSSD is now able to resolve users with the same usernames in different 
  OUs of an AD domain
- The smartcard authentication now works properly with gnome-screensaver

* Tue Mar 22 2016 Gleb Goncharov <yum@gongled.ru> - 1.13.3-1
- Initial build 
