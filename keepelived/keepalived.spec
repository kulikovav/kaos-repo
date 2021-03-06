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
%define _lockdir          %{_localstatedir}/lock
%define _cachedir         %{_localstatedir}/cache
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

%define __ln              %{_bin}/ln
%define __touch           %{_bin}/touch
%define __service         %{_sbin}/service
%define __chkconfig       %{_sbin}/chkconfig

###############################################################################

%bcond_without snmp
%bcond_without vrrp
%bcond_with profile
%bcond_with debug

###############################################################################

Name:              keepalived
Summary:           High Availability monitor built upon LVS, VRRP and service pollers
Version:           1.2.24
Release:           0%{?dist}
License:           GPLv2+
URL:               http://www.keepalived.org
Group:             System Environment/Daemons

Source0:           http://www.keepalived.org/software/%{name}-%{version}.tar.gz
Source1:           %{name}.init

Requires(post):    %{__chkconfig}
Requires(preun):   %{__chkconfig}
Requires(preun):   %{__service}
Requires(postun):  %{__service}

BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%if %{with snmp}
BuildRequires:     net-snmp-devel
%endif

BuildRequires:     gcc make openssl-devel libnl-devel kernel-devel popt-devel
BuildRequires:     libnfnetlink-devel

%if 0%{?rhel} >= 7
Requires:          systemd
%else
Requires:          kaosv >= 2.8
%endif

Provides:          %{name} = %{version}-%{release}

###############################################################################

%description
Keepalived provides simple and robust facilities for load balancing
and high availability to Linux system and Linux based infrastructures.
The load balancing framework relies on well-known and widely used
Linux Virtual Server (IPVS) kernel module providing Layer4 load
balancing. Keepalived implements a set of checkers to dynamically and
adaptively maintain and manage load-balanced server pool according
their health. High availability is achieved by VRRP protocol. VRRP is
a fundamental brick for router failover. In addition, keepalived
implements a set of hooks to the VRRP finite state machine providing
low-level and high-speed protocol interactions. Keepalived frameworks
can be used independently or all together to provide resilient
infrastructures.

###############################################################################

%prep
%setup -q

%build
%configure \
    %{?with_debug:--enable-debug} \
    %{?with_profile:--enable-profile} \
    %{!?with_vrrp:--disable-vrrp} \
    %{?with_snmp:--enable-snmp}
%{__make} %{?_smp_mflags} STRIP=/bin/true

%install
%{__rm} -rf %{buildroot}

%{make_install}

%{__rm} -rf %{buildroot}%{_sysconfdir}/%{name}/samples/

%if 0%{?rhel} <= 7
rm -rf %{buildroot}%{_libdir32}/systemd
install -dm 755 %{buildroot}%{_initrddir}
install -pm 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%endif

%if %{with snmp}
  %{__mkdir_p} %{buildroot}%{_datadir}/snmp/mibs/
  %{__install} -pm 644 doc/KEEPALIVED-MIB %{buildroot}%{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
%endif

%clean
%{__rm} -rf %{buildroot}

%post
%{__chkconfig} --add %{name}

%preun
if [[ $1 -eq 0 ]] ; then
  %{__service} %{name} stop >/dev/null 2>&1
  %{__chkconfig} --del %{name}
fi

%postun
if [[ $1 -eq 1 ]] ; then
  %{__service} %{name} restart >/dev/null 2>&1 || :
fi

###############################################################################

%files
%defattr(-,root,root,-)
%doc AUTHOR ChangeLog CONTRIBUTORS COPYING README TODO
%doc doc/%{name}.conf.SYNOPSIS doc/samples/%{name}.conf.*
%dir %{_sysconfdir}/%{name}/
%config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
%{_bindir}/genhash
%{_sbindir}/%{name}
%{_mandir}/man1/genhash.1*
%{_mandir}/man5/%{name}.conf.5*
%{_mandir}/man8/%{name}.8*

%if 0%{?rhel} >= 7
%{_unitdir}/%{name}.service
%else
%{_initrddir}/%{name}
%endif

%if %{with_snmp}
  %{_datadir}/snmp/mibs/KEEPALIVED-MIB.txt
  %{_datadir}/snmp/mibs/KEEPALIVED-MIB
%endif

###############################################################################

%changelog
* Sun Oct 16 2016 Anton Novojilov <andy@essentialkaos.com> - 1.2.24-0
- Declare and use default value for garp_refresh.
- Update documentation for default setting of snmp_server.
- Ensure old VIPs removed after reload.
- Add internet network control support for IPv6.
- Log startup and "already running" messages to console with --log-console.
- Remove VIPs on reload if no longer in configuration.
- Add internet network control support for IPv6.
- Add more lvs syncd options, and various minor fixes.
- Don't attempt to set packet priority for wrong IP protocol.
  if_setsockopt_priority() was setting SO_PRIORITY socket option regardless
  of whether the socket was IPv4 or IPv6. Although the setsockopt() call doesn't
  fail for IPv6, it doesn't do anything.
  Commit fc7ea83 added setting IPV6_TCLASS, again for both IPv4 and IPv6, but
  the setsockopt() call fails on an IPv4 socket.
  This commit makes keepalived only set the appropriate socket option, depending
  on whether it is an IPv4 or IPv6 socket.
  The commit also changes from using the SO_PRIORITY option for IPv4 to using the
  more specific IP_TOS option.
- Avoid compiler warning of duplicate definition.
- Add function attributes to malloc functions.
- KEEPALIVED-MIB vrrpRuleIndex should be unsigned.
- Allow all ip rule/route options for rules and routes.
  This commit adds support for all ip rule/route supported options for
  rules and routes (and also tunnel-id rule option not yet supported
  by ip rule).
- Make ip rules/routes a configuration option.
- Add all ip rules/routes options, and minor fixes.
- Corrections for rule suppress_ifgroup.
- Stop respawning children repeatedly after permanent error.
  Keepalived was respawning very rapidly after a permanent error, which
  was not useful.
  This commit allows the detection of certain errors and if one occurs
  keepalived won't respawn the child processes, but will terminate with
  an error message.
- Remove all remaining vestiges of Linux 2.4 (and earlier) support.
  There was code remaining for supporting ip_vs for Linux 2.4, but
  the remainder of the keepalived code requires Linux >= 2.6.
- Make some libipvs functions static.
- Move ipvs source and include files into check/include directories.
- Don't duplicate kernel definitions for IPVS code.
- Remove unused code from libipvs.c.
- Remove ip_vs_nl_policy.c, contents now in libipvs.c.
- Add ipvs 64 bit stats.
- Remove linux 2.4 code, add 64bit ipvs snmp stats, and some minor fixes.
- Fix compiling without SNMP checker support.
  The patchset removing support for Linux 2.4 introduced a problem
  compiling libipvs.c when SNMP checker support wasn't enabled.
- Remove those annoying "unknown keyword" messages.
  A slight reworking of the parsing code manages to get rid of those
  annoying "unknown keyword" messages which we all know are't true.
- Remove IP_VS_TEMPLATE_TIMEOUT. It was removed from ipvsadm in
  version 1.0.4.
- Remove check for MSG_TRUNC being defined.
  It has been defined since glibc 2.2.
- Remove conditionals based on libc5. libc5 predated glibc 2.0.
- Remove conditional compilation checks for defines in Linux 2.6.
  ETHTOOOL_GLINK, RTAX_FEATURES, RTAX_INITRWND, SIOCETHTOOL and SIOCGMIIPHY
  are all defined in Linux 2.6, so no longer need to be wrapped in
  conditional compilation checks.
- Sort out checks for O_CLOEXEC.
- Remove check for SA_RESTART. It existed pre Linux 2.6.
- Change reporting of default snmp socket.
- More updates for removing pre-Linux 2.6 code, and stop "unknown keyword"
  messages.
- Fix adding iptables entries on Linux 4.6.3 onwards.
  ip[46]tables_add_rules() were allocating space for an additional
  struct xt_entry_match. kernel commit 13631bfc6041 added validation
  that all offsets and sizes are sane, and the extra
  struct entry_match failed that test.
- Fix adding iptables entries on Linux 4.6.3 onwards.
- Fix size parameter for keepalived_malloc/realloc.
  lib/memory.h specified the size parameter to keepalived_malloc/realloc
  as size_t, whereas lib/memory.c specified unsigned long.
  The inconsistency was complained about by the compiler on 32-bit systems.
  Fix memory.c to make the parameter a size_t.
  Change lib/memory.c and lib/memory.h to use type size_t for size
  variables.
  Use printf format specified zu for size parameters.
- Fix building without LVS or without VRRP.
- Convert build system to automake.
  The INSTALL file gives instructions for setting up the build system
  using automake etc.
  For those without automake (and autoconf), just running configure
  works as before.
- Convert build system to automake.
- Add network namespace support.
  This allows multiple instances of keepalived to be run on a single
  system. The instances can communicate with each other as though they
  are running in separate systems, but they are also isolated from
  each other for all other purposes.
  See keepalived/core/namespaces.c for some example configurations and
  use cases.
- Use atexit() for reporting malloc/free checks on termination.
- Add + and git commit in -v output if uncommited changes.
- Add network namespace support.
- Remove some superfluous conditional compilation tests.
- Poll for reflection netlink messages after adding each interface.
  If a large number of interfaces are added, the kernel reflection
  netlink socket can run out of buffers. This commit adds a poll of
  the kernel netlink reflection channel after adding each interface,
  thereby ensuring that a large queue of messages isn't built up.
- Stop Netlink: Received message overrun (No buffer space available) messages.
- Fix debug build since automake conversion.
- Fix configuration testing for ipset support prior to Linux 3.4.
- Add polling of netlink messages when entering master state.
  If a large number of vrrp instances enter master state simultaneously
  the netlink socket can run out of buffers, since the netlink socket
  isn't read sufficiently frequently. Adding a poll of the netlink socket
  after the VIPs/eVIPs are added ensures that the netlink messages are read
  when the become available.
- Add some missing '\n's when printing the vrrp configuration.
- Fix generating git-commit.h.
- Ensure xmit_base not set with strict mode.
- Fix detection of code changes not commited to git in git-commit.h.
- Change true/false variables in global_data to bools.
- Fix timer_cmp handling large differences between the two times.
  In a struct timeval, tv_sec is a time_t which is a long. Assigning
  a.tv_sec - b.tv_sec to an int caused it to overflow if the time
  differences were large.
- Add a TIMER_NEVER value.
  This allows a thread to specify that it never wants to be woken on a
  timed basis.
- Add global default_interface keyword.
  default_interfaces sets the default interface to use for static
  ipaddresses. If the system does not have an eth0, or one wants to
  use a different interface for several static ipaddresses, this makes
  the configuration simpler. It also has the potential to reduces
  changes required if transferring the configuration to another system.
- Fix skew time for VRRPv3 with low priority and long advert interval.
  With a low priority and a long advert interval, the calculation of the
  skew time was overflowing a uint32_t. For example, with a priority of
  1 and an advertisment interval of 10 seconds, the skew time was being
  calculated as 4288 seconds, rather than 9.96 seconds. This had the
  impact that the backup instance would take over an hour to transition
  to master.
- Don't set master_adver_int from an invalid packet.
- Make timeout_persistence a uint32 rather than a string.
- Fix some configuration tests and compiling on old Linux version.
- Improve persistence handling.
  Properly support persistence_granularity for IPv6.
  Set persistence_timeout default if granularity specified.
  Only support persistence engine if supported by the kernel.
  This commit also changes variables timeout_persistence and
  granularity_persistence to persistence_timeout and
  granularity_timeout.
- Simplify a bit of indentation.
- Add (commented out) code for writing stack backtrace to a file.
- Free syslog_ident string after logging the free.
  When writing mem check entries to the log, the syslog_ident needs to be
  freed after the log has been written to.
- Allow FREE_PTR mem check to log the proper function.
  Having FREE_PTR as a function meant that whenever any memory was freed by
  FREE_PTR() the function that was logged as freeing it was FREE_PTR itself.
  Changing FREE_PTR() to be a #define means that the calling function name
  is logged.
- Fix tests of HAVE_DECL_CLONE_NEWNET.
- Fix a conditional compilation test re namespaces and rename a variable.
- Fix when some FREE() calls are made.
- Only parse net_namespace in parent process.
- Add VRRP/LVS conditional compilation around PID files.
- Improve removing zombie PID files.
- Add more VRRP/LVS conditional compilation.
- Don't check if instance is a rotuer every time an NA is sent.
  keepalived was calling sysctl to check if the interface was configured as
  router before sending each gratuitous Neighbour Discovery advertisement. This
  patch now checks if the interface is routing when the instance transitions to
  master, and uses that for all the NA messages.
- Improve mem check initialisation.
- Add support for running multiple instances of keepalived.
  Using network namespaces allows multiple instances of keepalived to run
  concurrently, in different namespaces, without any collision of the pid
  files.
  This patch adds the concept of a keepalived instance name, which is then
  use in the pidfile name, so that multiple instances of keepalived can run
  in the same namespace without pid file name collisions.
- Add option to write pid files to /var/run/keepalived.
  When using namespaces or instances, pid files are written to /var/run/keepalived.
  The commit adds an option for the standard pid files to use that directory.
- Add keywords instance and use_pid_dir, plus sundry fixes/improvements.
- Add configure option to enable stacktrace support.
- Fix adding and deleting iptables rules for addresses.
  When keepalived was built not using ipsets, the adding and deleting
  of rules for addresses was including an extra xt_entry_match struct
  that meant that the rules could only be deleted by ithe iptables
  command by entry number and not be specifying the parameters.
- Fix compiling without libiptc (iptables) support.
- Don't log error message when trying to remove leftover iptables config.
  At startup keepalived attempts to remove any iptables configuration that
  may have been left over from a previous run. Of course the entries won't
  normally be there, so don't report an error if they are not found.
- Fix iptables entries for accept mode, other iptables fixes, and make
  write_stacktrace a configure option.
- Add script to setup interfaces in a network namespace.
  The scripts mirrors the running network interfaces that are needed
  for a given keepalived configuration into a network namespace
  (default test), so that keepalived can be run in that namespace in
  order to test the configuration.
- Correct comments re location of network namespace pid files.
- Add -s option for overriding net_namespace configuration option.
- Change test/netns-test.sh -c option to -f to match keepalived.
- Make netns-test.sh report interfaces that don't exist.
- Remove leftover debug message.
- Fix address comparison for equal priority adverts.
- Streamline the specification of libraries to the linker.
  Most of the dynamic libraries and static libraries were being specified
  twice. This commit removes the duplication of all of the dynamic libraries
  and only duplicates core/libcore.a of the static libraries.
- Fix automake files for building on Ubuntu 14.04 LTS.
- Enable building with Net-SNMP on Ubuntu.
- Stop compiler warning on Ubuntu.
- Fix compilation with libipset on Debian wheezy.
- Fix various build problems on Ubuntu 14.04 and Debian.

* Mon Sep 05 2016 Anton Novojilov <andy@essentialkaos.com> - 1.2.23-0
- Make malloc/free diagnostics a separate configure option.
  The commit adds the configure --enable-mem-check option which
  allows the MALLOC/FREE diagnostics to be enabled without
  the --enable-debug option. This means that the mem-check
  diagnostics can be used when running keepalived in it's normal mode
  with forking children for vrrp and checkers.
  The mem-check diagnostics are written to
  /tmp/Keepalived_{,vrrp,healthcheckers}_mem.PID.log
  The --mem-check-log configure option enables command line option
  -L which also writes zalloc/free details to the syslog.
- Fix compilation error on 32-bit systems with mem-check enabled.
- Replace one zalloc() and one free() call with MALLOC() and FREE().
  This ensures that the mem-check diagnostics cover all mallocs/frees.
-  Fix report of malloc'd memory not being freed.
- Streamline read_line().
- Resolve a segfault when reloading with vmacs.
  The vrrp_t entries on the vrrp_data list have pointers to an
  interface_t for each vrrp instance. When reloading, the
  interface_t items where freed, but a pointer to the old list
  of vrrp_t items is held in old_vrrp_data. After the new
  configuration is processed, clear_diff_vrrp() is called. clear_diff_vrrp()
  uses the interface_t pointers from the old vrrp_t entries, but the
  memory pointed to by the interface_t pointers has already been freed,
  and probably reallocated for a different use.
  This commit delays freeing the old interface_t items until after
  clear_diff_vrrp() has completed, so the interface_t pointers remain valid.
- Check valid interface pointer before calling reset_interface_parameters().
  Before resetting the settings on the base interface of a vmac, check that
  the interface_t pointer is valid.
- Fix new --mem-check-log option.
- Don't write parent's memory logging into children's log file.
  When running with mem-check output to files, the buffer from the
  parent process was also being written into the children's log
  files. The commit sets the CLOEXEC flag on the log files, and
  also sets the log files to be line buffered.
- Fix segfault or infinite loop in thread_child_handler() after reloading.
  When the checker and vrrp child processes start up, memory for a
  thread_master_t is malloc'd and saved in master. Subsequently,
  launch_scheduler() is called, and that sets the parameter to be passed
  to the SIGCHLD handler - thread_child_handler() to the value of master,
  pointing to a thread_master_t.
  If keepalived is signalled to reload, the child processes free all
  malloc'd memory, and a new thread_master_t is malloc'd and saved in
  master. If this is not the same address as the previous thread_master_t,
  then the value being passed to the SIGCHLD handler is a pointer to the
  old thread_master_t, whereas everything else is using the new thread_master_t.
  If the memory used for the old thread_master_t is then returned in a subsequent
  malloc() call, a subsequent SIGCHLD will invoke thread_child_handler() with
  a pointer to memory that has now been overwritten for some other purpose, hence
  causing either a segfault or an infinite loop.
  A further consequence is that new child processes will be added to the new
  thread_master_t, but when thread_child_hander() is called after a child
  terminates, it won't find the child since it is still looking at the old
  thread_master_t.
  This commit modifies the behaviour of a reload by not releasing the old
  thread_master_t and then malloc'ing a new one, but rather it just reinitialises
  the original thread_master_t and continues using it.
- Remove base_iface from struct _vrrp_ - it wasn't used.
- Add configuration option to flush LVS configuration.
  This commit adds a global configuration option lvs_flush to flush
  the LVS configuration, and if not set, the configuration won't be
  flushed.
- Add back real server when return from failure with HTTP_CHECK.
  If status_code wasn't specified for a url entry in the configuration
  then a real server would never be returned to service following a
  failure.
  The commit makes keepalived return a real server to service if no
  status_code is specified if the HTTP status code returned from the
  service is a success code (i.e. 2xx).
- Avoid duplication of keyword installation in check_http.c.
- Fix adding new static ip addresses after reload.
  Commit f23ab52, when stopping duplicate static ip routes and rules
  being added after a reload also stopped new static ip addresses being
  added. The commit reinstates adding new static ip addresses.
- Fix adding static iprule/routes after a reload.
- Stop segfault when configure a route with no destination address.
- Fix unused global vrrp_garp_master_refresh.
- fix healthchecker reload when some healthchecks are failed.

* Sat Jun 18 2016 Anton Novojilov <andy@essentialkaos.com> - 1.2.22-0
- vrrp: Fix build without VRRP VMAC.
- Fix compilation with RFC SNMP without Keepalived SNMP.
- vrrp: Update master_adver_int when receive higher priority advert
  when master.
  If VRRPv3 is being used, and a higher priority advert is received when
  in master mode, the master_adver_int needs to be updated when transitioning
  backup mode. If this isn't done, and our advert interval is less than a third
  of the new masters, we will time out and re-enter master mode, send an advert
  to which the other master will resond with a higher priority advert, causing
  us to go back into backup mode, until our timer expires again, and this will
  continue indefinitely.
- vrrp: Don't send advert after receiving higher priority advert.
  If a master receives a higher priority advert, there is no need
  to send another advert, since the sender of the higher priority
  advert is already a master. Further, any other instance in backup
  mode will process our subsequent advert, and then consider the
  wrong system to be master, until it receives another advert from
  the real master.
  With VRRPv3, if the other master has an advert interval more than
  three times our advert interval, backup routers will be using our
  advert interval after we've sent our subsequent advert, and will
  then timeout before the new master sends another advert, prompting
  (one of) the backup routers to become a master, which will prompt
  the higher priority master to send an advert, the ex-backup router
  will then send another advert and we could end up in an endless cycle.
- vrrp: Fix receiving advert from address owner when in fault state.
- vrrp: When transitioning from fault state, log state change.
- vrrp: Fix preempt delay when transitioning from fault state.
  There were two ways of leaving fault state, either by receiving a packet
  on the instance, or by a netlink message indication that the interface is
  up again. In neither case was preempt_delay considered in the code.
  This commit changes the way vrrp->preempt_time is used. preempt_time is now
  only used once a higher priority advert is received, rather than being updated
  every time a lower priority advert is received. vrrp->preempt_time is now also
  set when transitioning out of fault state. vrrp->preempt_time.tv_sec == 0 now
  indicates the timer is not running.
- vrrp: Detect and report duplicate address owners.
  If more than one system is configured as an address owner (priority
  == 255), this would be a configuration error, and could cause
  unexpected behaviour. This commit ensures that the problem is
  reported, and sets the local instance not to be the addess owner,
  as a temporary workaround for the problem.
- vrrp: Fix maximum number of VIPs allowe.
- ipvs: Fix IPVS with IPv6 addresses.
- ipvs: Don't overwrite errno by another syscall before checking errno.
- ipvs: ipvswrapper.c: fix comparison.
- Enable compilation with development net-snmp headers.
- vrrp: Fix IPv4 vIP removal when addr matches pre-existing interface addr.
  For IPv4 vIPs keepalived adds a /32 to the underlying interface. If
  this address matches an address already configured, e.g. a /24, when
  this vIP is eventually removed due to a configuration change or
  keepalived shutdown, the original address matching the vIP, outside
  of keepalived's control, is removed instead. This behaviour is
  incorrect. The /32 added by keepalived should be the address being
  removed. Keepalived should not be touching any addresses it does not
  create.
- vrrp: Check for errors when opening VRRP data and stats files.
  This fixes crashes when running keepalived under SELinux enforcing mode,
  which does not allow keepalived proccess to write to /tmp by default.
- vrrp: Don't assume IPADDRESS_DEL == 0 and IPADDRESS_ADD != 0.
- vrrp: Fix compilation failure.
- vrrp: Fix transition to backup when receive equal priority advert from
  higher address.
  When a vrrp instance in master mode received an advert from another master
  that had equal priority, it wasn't comparing the addresses to determine
  whether it should treat the advert as higher priority, and hence the
  instance should fall back into backup state.
  When checking whether the advert is from a lower priority master, it now
  checks if the priorities are equal and then compares the addresses.
- vrrp: Optimise address comparision when receive advert in master mode.
- Optimise inet_inaddr_cmp.

* Sat Jun 18 2016 Anton Novojilov <andy@essentialkaos.com> - 1.2.21-0
- Install VRRP-MIB when applicable.
  It appears that the condition in Makefile.in for installing VRRP-MIB
  was using a non-existent macro, SNMP_RFC2_SUPPORT. This patch removes
  two conditions from Makefile.in that use undefined macros and adds a
  condition to install VRRP-MIB when SNMP_RFCV2_SUPPORT is set
  appropriately.
- Check virtual route has an interface before returning ifindex to SNMP
- Force git-commit.h to be updated when needed
- INSTALL: Keepalived doesn't need popt anymore
- INSTALL: support for 2.2 kernels is long gone.
- INSTALL: fix a few typos
- keepalived.conf(5) some minor improvements
- man keepalived(8): some minor improvements
- Add printing of smtp server port when printing global config
- timeout_epilog: mark argument const.
- parser: mark some function arguments as const.
- terminate argv with NULL.
  man execvp says: "The array of pointers must be terminated by a null
  pointer."
- ipvswrapper.c: fix comparison.
- mark pidfile strings as const.
- utils.c: mark some arguments a const.
  I left inet_stosockaddr alone for now, since it modifies the string.
  We should fix that, since we pass in strings which might be const and in
  readonly memory.
- netlink_scope_n2a: mark return type as const.
- vector->allocated is unsigned.
- notify_script_exec: mark a few arguments as const.
- vscript_print: mark string as const.
- vector->allocted is unsigned.
- dump_vscript: mark str as const.
- Updated range for virtual_router_id and priority.
- Stop segfaulting with mixed IPv4/IPv6 configuration
  After reporting that an ip address was of the wrong family, when
  the invalid address was removed from the configuration, keepalived
  was segfaulting, which was due to the wrong address being passed to
  free_list_element().
- Updated range for virtual_router_id and priority in
  doc/keepalived.conf.SYNOPSIS
- Allow '-' characters in smtp_server hostname.
- Allow smtp_server domain names with '-' characters to be parsed
  correctly.
- Report and exit if configuration file(s) not found/readable.
  The configuration file is treated as a pattern, and processed
  using glob(). If there is no matching file, then it wasn't reading
  any file, and keepalived was running with no configuration.
  This patch adds a specific check that there is at least one matching
  file, and also checks that all the configuration files are readable,
  otherwise it reports an error and terminates.
- Fix building with Linux < 3.4 when ipset development libraries
  installed.
  Prior to Linux 3.4 the ipset header files could not be included in
  userspace. This patch adds checking that the ipset headers files can
  be included, otherwise it disables using ipsets.
- configure: fix macvlan detection with musl libc.
- Fix compiling without macvlan support.
- Bind read sockets to particular interface.
  Otherwise, since we use RAW sockets, we will receive IPPROTO_VRRP
  packets that come in on any interface.
- vrrp: read_to() -> read_timeout(). Make function name less confusing.
- vrrp: open_vrrp_socket() -> open_vrrp_read_socket().
  An equivalent open_vrrp_send_socket() exists, therefore make
  the read version follow the same naming convention.
- vrrp: fix uninitialized input parameter to setsockopt().
- Make most functions in vrrp_print.c static.
- Enable compilation on Linux 4.5.x.
  Including  causes a compilation failure on Linux 4.5
  due to both  and  being included, and they have
  a namespace collision.
  As a workaround, this commit defines _LINUX_IF_H before including
  , to stop  being included. Ugly, yes,
  but without editting kernel header files I can't see any other way
  of resolving the problem.
- Fix segmentation fault when no VIPs configured.
  When checking the VIPs in a received packet, it wasn't correctly
  handling the situation when there were no VIPs configured on the
  VRRP instance.
- Improve checking of existance and readability of config files.
  There was no check of the return value from glob() in read_conf_file()
  and check_conf_file(), so that if there were no matching files, they
  attempted to use the uninitialised globbuf, with globbuf.gl_pathc taking
  a random value. A further check has been added that the files returned
  are regular files.
  Finally, if no config file name is specified check_conf_file() is now
  passed the default config file name rather than null.
- vrrp: update struct msghdr.
  The vrrp netlink code assumes an order for the members of struct msghdr.
  This breaks recvmsg and sendmsg with musl libc on mips64. Fix this by
  using designated initializers instead.
- Initialise structures by field names.
- Detection of priority == 0 seems to be shaded.
- More verbose logging on (effective) priorities.
- Log changes to effective priority made via SNMP.
- vrrp: use proper interface index while handling routes.
  It appears current code has a small typos while handling routes trying
  to access route->oif where it should be route->index.
- vrrp: make vrrp_set_effective_priority() accessible from snmp code.
  just include proper file in order to avoid compilation error.
- monotonic_gettimeofday: make static.
- Disable unused extract_content_length function.
- utils: disable more unused functions.
- utils: make inet_sockaddrtos2 static.
- signal: remove unused functions.
- Disable unused signal_ending() consistently with other unused code.
- parser: make a bunch of stuff static.
- scheduler: make a bunch of stuff static.
- scheduler: disable unused thread_cancel_event().
- vector: disable unused functions.
- vector: make 2 functions static.
- list: disable unused function.
- genhash: make some functions static.
- Remove unused variable.
- core: make a few functions static.
- checkers: make some functions static.
- vrrp_arp: make some global variables file-scope.
- vrrp_ndisk.c: make 2 global variables file-scope.
- vrrp: make some functions and globals static.
- In get_modprobe(), close file descriptor if MALLOC fails.
  The sequencing of the code wasn't quite right, and so if the MALLOC
  had failed, the file descriptor would be left open.
- Fix compilation without SOCK_CLOEXEC and SOCK_NONBLOCK.
  SOCK_CLOEXEC and SOCK_NONBLOCK weren't introduced until
  Linux 2.6.23, so for earlier kernels explicitly call fcntl().
- Don't include FIB rule/route support if kernel doesn't support it.
- Enable genhash to build without SOCK_CLOEXEC.
- Ignore O_CLOEXEC if not defined when opening and immediately closing file.
- Allow building without --disable-fwmark if SO_MARK not defined.
  configure complained "No SO_MARK declaration in headers" if that
  was the case, but --disable-fwmark was not specified. The commit
  stops the error message, and just defines _WITHOUT_SO_MARK_ if
  SO_MARK is not defined.
- Update documentation for debug option.
- Add options -m and -M for producing core dumps.
  Many systems won't produce core dumps by default. The -m option
  sets the hard and soft RLIMIT_CORE values to unlimited, thereby
  allowing core dumps to be produced.
  Some systems set /proc/sys/kernel/core_pattern so that a core file
  is not produced, but the core image is passed to another process.
  The -M option overrides this so that a core file is produced, and
  it restores the previous setting on termination of the parent process,
  unless it was the parent process that abnormally terminated.
- Add option to specify port of smtp_-server.
- Add comment re when linux/if.h and net/if.h issue resolved upstream.
- Enable building with SNMP with FIB routing support.
- Exclude extraneous code when building with --disable-lvs.
- Update description of location of core files.
- Add support for throttling gratuitous ARPs and NAs.
  The commit supersedes pull request #111, and extends its functionality
  to also allow throttling of gratuitous NA messages (IPv6), and allows
  specifying the delay parameters per interface, since interfaces from
  the host may be connected to different switches, which require
  different throttling rates.
- Add snmpServerPort to Keepalived MIB.
- Add printing of smtp server port when printing global config.
- Add aggregation of interfaces for throttling ARPs/NAs.
  This commit adds support for aggregating interfaces together, so
  that if multiple interfaces are connected to the same physical switch
  and the switch is limited as a whole on the rate of gratuitous ARPs/
  unsolicited NAs it can process, the interfaces can be grouped together
  so that the limit specified is applied across them as a whole.
- In free_interface_queue, don't check LIST_ISEMPTY before freeing.
- Clear pointer freed by free_list().
- Make FREE_PTR() clear the pointer after freeing the memory.
- Make FREE() clear pointer after memory released.
  Since a pointer to allocated memory mustn't be used after the memory is
  freed, it is safer to clear the pointer. It also means that if the pointer
  is subsequently used, it shoud segfault immediately rather than potentially
  trampling over random memory, which might be very difficult to debug.
- vrrp: Improve validation of advert_int.

* Fri Apr 08 2016 Anton Novojilov <andy@essentialkaos.com> - 1.2.20-0
- Updated to latest release

* Thu Aug 06 2015 Anton Novojilov <andy@essentialkaos.com> - 1.2.19-0
- Updated to latest release

* Wed Jul 01 2015 Anton Novojilov <andy@essentialkaos.com> - 1.2.18-0
- Updated to latest release

* Wed Apr 15 2015 Anton Novojilov <andy@essentialkaos.com> - 1.2.16-0
- Updated to latest release

* Tue Jan 27 2015 Anton Novojilov <andy@essentialkaos.com> - 1.2.15-0
- Updated to latest release

* Sat Dec 20 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.14-0
- Updated to latest release

* Tue Oct 28 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.13-1
- Init script migrated to kaosv2

* Sat Aug 09 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.13-0
- Updated to latest release
- Init script now use kaosv

* Tue Apr 01 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.12-0
- Updated to latest release

* Tue Apr 01 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.11-0
- Updated to latest release

* Tue Jan 14 2014 Anton Novojilov <andy@essentialkaos.com> - 1.2.10-0
- Updated to latest release

* Mon Dec 23 2013 Anton Novojilov <andy@essentialkaos.com> - 1.2.9-0
- Updated to latest release

* Tue Oct 22 2013 Anton Novojilov <andy@essentialkaos.com> - 1.2.8-0
- Initial build
