################################################################################

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
%define _loc_mandir       %{_loc_datarootdir}/man
%define _rpmstatedir      %{_sharedstatedir}/rpm-state
%define _pkgconfigdir     %{_libdir}/pkgconfig

%define __ln              %{_bin}/ln
%define __touch           %{_bin}/touch
%define __service         %{_sbin}/service
%define __chkconfig       %{_sbin}/chkconfig
%define __ldconfig        %{_sbin}/ldconfig
%define __groupadd        %{_sbindir}/groupadd
%define __useradd         %{_sbindir}/useradd
%define __install_info    %{_sbindir}/install-info

################################################################################

Summary:              A GNU general-purpose parser generator
Name:                 bison
Version:              3.2.1
Release:              0%{?dist}
License:              GPLv3+
Group:                Development/Tools
URL:                  http://www.gnu.org/software/bison/

Source:               http://ftp.gnu.org/pub/gnu/bison/bison-%{version}.tar.xz

BuildRoot:            %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:        autoconf m4 >= 1.4 make gcc

Requires:             m4 >= 1.4

Requires(post):       /sbin/install-info
Requires(preun):      /sbin/install-info

Provides:             bundled(gnulib) = %{name}-%{version}

################################################################################

%description
Bison is a general purpose parser generator that converts a grammar
description for an LALR(1) context-free grammar into a C program to
parse that grammar. Bison can be used to develop a wide range of
language parsers, from ones used in simple desk calculators to complex
programming languages. Bison is upwardly compatible with Yacc, so any
correctly written Yacc grammar should work with Bison without any
changes. If you know Yacc, you should not have any trouble using
Bison. You do need to be very proficient in C programming to be able
to use Bison. Bison is only needed on systems that are used for
development.

If your system will be used for C development, you should install
Bison.

################################################################################

%package devel

Summary: -ly library for development using Bison-generated parsers
Group:    Development/Libraries

Provides: bison-static = %{version}-%{release}

%description devel
The bison-devel package contains the -ly library sometimes used by
programs using Bison-generated parsers.  If you are developing programs
using Bison, you might want to link with this library.  This library
is not required by all Bison-generated parsers, but may be employed by
simple programs to supply minimal support for the generated parsers.

################################################################################

%package runtime

Summary: Runtime support files used by Bison-generated parsers
Group:   Development/Libraries

%description runtime
The bison-runtime package contains files used at runtime by parsers
that Bison generates.  Packages whose binaries contain parsers
generated by Bison should depend on bison-runtime to ensure that
these files are available.  See the Internationalization in the
Bison manual section for more information.

################################################################################

%prep
%setup -q

%build
%configure
%{__make} %{?_smp_mflags}

%install
rm -rf %{buildroot}
%{make_install}

rm -f %{buildroot}%{_bindir}/yacc
rm -f %{buildroot}%{_infodir}/dir
rm -f %{buildroot}%{_mandir}/man1/yacc*
rm -rf %{buildroot}%{_docdir}/%{name}/examples

%find_lang %{name}
%find_lang %{name}-runtime

gzip -9nf %{buildroot}%{_infodir}/%{name}.info*

%clean
rm -rf %{buildroot}

################################################################################

%files -f %{name}.lang
%defattr(-,root,root)
%doc AUTHORS ChangeLog NEWS README THANKS TODO COPYING
%{_docdir}/%{name}
%{_mandir}/*/%{name}*
%{_datadir}/%{name}
%{_infodir}/%{name}.info*
%{_bindir}/%{name}
%{_datadir}/aclocal/%{name}*.m4

%files -f %{name}-runtime.lang runtime
%defattr(-,root,root)
%doc COPYING
%{_datarootdir}/locale/*/LC_MESSAGES/%{name}-runtime.mo

%files devel
%defattr(-,root,root)
%doc COPYING
%{_libdir}/liby.a

################################################################################

%changelog
* Thu Nov 15 2018 Anton Novojilov <andy@essentialkaos.com> - 3.2.1-0
- Updated to latest stable release

* Thu Nov 15 2018 Anton Novojilov <andy@essentialkaos.com> - 3.1-0
- Updated to latest stable release

* Sat Jun 09 2018 Anton Novojilov <andy@essentialkaos.com> - 3.0.5-0
- Updated to latest stable release

* Wed Feb 24 2016 Gleb Goncharov <yum@gongled.ru> - 3.0.4-0
- Initial build
