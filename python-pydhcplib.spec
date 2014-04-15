%define __python python2.6
%define __pyver 2.6
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print (get_python_lib())")}

Name:           python-pydhcplib
Version:        0.6.2
Release:        1%{?dist}
Summary:        Python dhcp library
Group:          Network

License:        ASL 2.0
URL:            http://code.locaweb.com.br/iaas/motoko
Source0:        pydhcplib-%{version}.tar.gz
Buildroot:      %{_tmppath}/%{name}-%{version}-%{release}-root

BuildArch:      noarch
BuildRequires:  python

Requires:       python

%description
Pydhcplib is a python library to read/write and encode/decode dhcp packet on network.

%prep
%setup -q -n pydhcplib

%build
echo -n

%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --root $RPM_BUILD_ROOT


%files
%defattr(-,root,root,-)
%{_bindir}/pydhcp
/usr/lib/python%{__pyver}/site-packages/pydhcplib-%{version}-py%{__pyver}.egg-info
/usr/lib/python%{__pyver}/site-packages/pydhcplib/*
%{_mandir}/fr/man3/pydhcplib.3.gz
%{_mandir}/fr/man3/pydhcplib.DhcpBasicPacket.3.gz
%{_mandir}/fr/man3/pydhcplib.DhcpPacket.3.gz
%{_mandir}/fr/man3/pydhcplib.hwmac.3.gz
%{_mandir}/fr/man3/pydhcplib.ipv4.3.gz
%{_mandir}/fr/man3/pydhcplib.strlist.3.gz
%{_mandir}/man3/pydhcplib.3.gz
%{_mandir}/man3/pydhcplib.ipv4.3.gz
%{_mandir}/man3/pydhcplib.strlist.3.gz
%{_mandir}/man8/pydhcp.8.gz


%changelog
* Sat Mar 15 2014 Andre Ferraz <andre.ferraz@locaweb.com.br> - 0.6.2-1
- Initial release
