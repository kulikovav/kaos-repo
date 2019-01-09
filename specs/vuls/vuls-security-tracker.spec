################################################################################

# rpmbuilder:gopack    github.com/knqyf263/gost

################################################################################

%define  debug_package %{nil}

################################################################################

%define _posixroot        /
%define _root             /root
%define _bin              /bin
%define _sbin             /sbin
%define _srv              /srv
%define _home             /home
%define _opt              /opt
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
%define _loc_mandir       %{_loc_datarootdir}/man
%define _rpmstatedir      %{_sharedstatedir}/rpm-state
%define _pkgconfigdir     %{_libdir}/pkgconfig

%define __ldconfig        %{_sbin}/ldconfig
%define __service         %{_sbin}/service
%define __touch           %{_bin}/touch
%define __chkconfig       %{_sbin}/chkconfig
%define __updalt          %{_sbindir}/update-alternatives
%define __useradd         %{_sbindir}/useradd
%define __groupadd        %{_sbindir}/groupadd
%define __getent          %{_bindir}/getent
%define __systemctl       %{_bindir}/systemctl

################################################################################

%define username          vuls
%define groupname         vuls

%define service_name      sectd-server
%define short_name        security-tracker
%define service_logdir    %{_logdir}/vuls/%{short_name}
%define install_dir       %{_opt}/vuls/%{short_name}

################################################################################

Summary:         Security Tracker data fetcher and server for VULS
Name:            vuls-%{short_name}
Version:         0.1.0
Release:         0%{?dist}
Group:           Applications/System
License:         MIT
URL:             https://github.com/knqyf263/gost

Source0:         %{name}-%{version}.tar.bz2
Source1:         %{service_name}.init
Source2:         %{service_name}.sysconfig
Source3:         %{service_name}.service
Source4:         %{short_name}-fetch
Source5:         %{short_name}-fetch.cron

BuildRequires:   golang >= 1.11

BuildRoot:       %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:        sqlite kaosv >= 2.15

Provides:        %{name} = %{version}-%{release}

################################################################################

%description
This tool builds a local copy of Security Tracker(Redhat/Debian/Microsoft).

################################################################################

%prep
%setup -q

mkdir -p .src ; cp -r * .src/ ; rm -rf * ; mv .src src

%build
export GOPATH=$(pwd)
export LD_FLAGS="-X main.version=%{version} -X main.revision=000000"

sed -i "s#/var/log/gost#%{service_logdir}#" \
       src/github.com/knqyf263/gost/util/util.go

go build -ldflags "$LD_FLAGS" -o %{short_name} src/github.com/knqyf263/gost/main.go

%install
rm -rf %{buildroot}

install -dm 755 %{buildroot}%{_bindir}
install -dm 755 %{buildroot}%{install_dir}
install -dm 755 %{buildroot}%{service_logdir}

install -pm 755 %{short_name} %{buildroot}%{_bindir}/
install -pm 755 %{SOURCE4} %{buildroot}%{_bindir}/

install -pDm 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{service_name}
install -pDm 755 %{SOURCE1} %{buildroot}%{_initddir}/%{service_name}

%if 0%{?rhel} >= 7
install -pDm 644 %{SOURCE3} %{buildroot}%{_unitdir}/%{service_name}.service
%endif

install -pDm 644 %{SOURCE5} %{buildroot}%{_crondir}/%{short_name}-fetch

%clean
rm -rf %{buildroot}

################################################################################

%pre
if [[ $1 -eq 1 ]] ; then
  %{__getent} group %{groupname} &>/dev/null || %{__groupadd} -r %{groupname}
  %{__getent} passwd %{username} &>/dev/null || %{__useradd} -r -g %{groupname} -d %{_rundir}/%{name} -s /sbin/nologin %{username}
fi

%post
if [[ $1 -eq 1 ]] ; then
%if 0%{?rhel} >= 7
  %{__systemctl} daemon-reload %{service_name}.service &>/dev/null || :
  %{__systemctl} preset %{service_name}.service &>/dev/null || :
%else
  %{__chkconfig} --add %{service_name} &>/dev/null || :
%endif
fi

%postun
if [[ $1 -eq 0 ]] ; then
%if 0%{?rhel} >= 7
  %{__systemctl} --no-reload disable %{service_name}.service &>/dev/null || :
  %{__systemctl} stop %{service_name}.service &>/dev/null || :
%else
  %{__service} stop %{service_name} &>/dev/null || :
%endif
fi

################################################################################

%files
%defattr(-,root,root,-)
%attr(0755,%{username},%{groupname}) %dir %{service_logdir}
%attr(0755,%{username},%{groupname}) %{install_dir}
%config(noreplace) %{_sysconfdir}/%{service_name}
%config(noreplace) %{_crondir}/%{short_name}-fetch
%{_initddir}/%{service_name}
%if 0%{?rhel} >= 7
%{_unitdir}/%{service_name}.service
%endif
%{_bindir}/%{short_name}
%{_bindir}/%{short_name}-fetch

################################################################################

%changelog
* Wed Dec 12 2018 Anton Novojilov <andy@essentialkaos.com> - 0.1.0-0
- Initial build for kaos repository
