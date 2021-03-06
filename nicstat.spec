###############################################################################

Summary:           Network traffic statics utility
Name:              nicstat
Version:           1.95
Release:           0%{?dist}
License:           Artistic 2.0
Group:             Applications/System
URL:               http://sourceforge.net/projects/nicstat

Source:            http://downloads.sourceforge.net/%{name}/%{name}-src-%{version}.tar.gz

BuildRoot:         %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:     gcc

###############################################################################

%description
nicstat is a Solaris and Linux command-line that prints out network statistics 
for all network interface cards (NICs), including packets, kilobytes per second,
average packet sizes and more.

###############################################################################

%prep
%setup -qn %{name}-src-%{version}

%build
%ifarch %ix86
  gcc %{optflags} -O3 -m32 %{name}.c -o %{name}
%else
  gcc %{optflags} -O3 -m64 %{name}.c -o %{name}
%endif

%install
rm -rf %{buildroot}

install -dm 755 %{buildroot}%{_bindir}
install -dm 755 %{buildroot}%{_mandir}/man1/

install -pm 755 %{name} %{buildroot}%{_bindir}/
install -pm 644 %{name}.1 %{buildroot}%{_mandir}/man1/

%clean
rm -rf %{buildroot}

###############################################################################

%files
%defattr(-,root,root,-)
%doc README.txt LICENSE.txt ChangeLog.txt
%{_bindir}/%{name}
%{_mandir}/man1/*

###############################################################################

%changelog
* Sun Mar 22 2015 Anton Novojilov <andy@essentialkaos.com> - 1.95-0
- Initial build
