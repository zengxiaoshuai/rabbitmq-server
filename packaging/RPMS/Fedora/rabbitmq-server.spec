Name: rabbitmq-server
Version: %%VERSION%%
Release: 1
License: MPLv1.1
Group: Development/Libraries
Source: http://www.rabbitmq.com/releases/rabbitmq-server/v%{version}/%{name}-%{version}.tar.gz
Source1: rabbitmq-server.init
Source2: rabbitmq-server.wrapper
Source3: rabbitmq-server.logrotate
Source4: rabbitmq-server-preserve-db.sh
URL: http://www.rabbitmq.com/
Vendor: LShift Ltd., Cohesive Financial Technologies LLC., Rabbit Technlogies Ltd.
%if 0%{?debian}
%else
BuildRequires: erlang, python-simplejson
%endif
Requires: erlang, logrotate
Packager: Hubert Plociniczak <hubert@lshift.net>
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-%{_arch}-root
Summary: The RabbitMQ server
Requires(post): chkconfig
Requires(pre): chkconfig initscripts

%description
RabbitMQ is an implementation of AMQP, the emerging standard for high
performance enterprise messaging. The RabbitMQ server is a robust and
scalable implementation of an AMQP broker.

%ifarch x86_64
  %define _defaultlibdir /usr/lib64
%else
  %define _defaultlibdir /usr/lib
%endif

%define _erllibdir %{_defaultlibdir}/erlang/lib
%define _rabbitbindir %{_defaultlibdir}/rabbitmq/bin

%define _maindir %{buildroot}%{_erllibdir}/rabbitmq_server-%{version}

%pre
if [ $1 -gt 1 ]; then
  #Upgrade - stop and remove previous instance of rabbitmq-server init.d script
  /sbin/service rabbitmq-server stop
  /sbin/chkconfig --del rabbitmq-server
fi

%prep
%setup -n %{name}-%{version}

%build
make

%install
rm -rf %{buildroot}

make install TARGET_DIR=%{_maindir} \
             SBIN_DIR=%{buildroot}%{_rabbitbindir} \
             MAN_DIR=%{buildroot}%{_mandir}

mkdir -p %{buildroot}/var/lib/rabbitmq/mnesia
mkdir -p %{buildroot}/var/log/rabbitmq
mkdir -p %{buildroot}/etc/rc.d/init.d/

#Copy all necessary lib files etc.
install -m 0755 %SOURCE1 %{buildroot}/etc/rc.d/init.d/rabbitmq-server
chmod 0755 %{buildroot}/etc/rc.d/init.d/rabbitmq-server

mkdir -p %{buildroot}%{_sbindir}
install -m 0755 %SOURCE2 %{buildroot}%{_sbindir}/rabbitmqctl

mkdir -p %{buildroot}/etc/logrotate.d
install %SOURCE3 %{buildroot}/etc/logrotate.d/rabbitmq-server

rm %{_maindir}/LICENSE %{_maindir}/LICENSE-MPL-RabbitMQ %{_maindir}/INSTALL

%post
# create rabbitmq group
if ! getent group rabbitmq >/dev/null; then
        groupadd -r rabbitmq
fi

# create rabbitmq user
if ! getent passwd rabbitmq >/dev/null; then
        useradd -r -g rabbitmq --home /var/lib/rabbitmq  rabbitmq
        usermod -c "Rabbit AMQP Messaging Server" rabbitmq
fi

chown -R rabbitmq:rabbitmq /var/lib/rabbitmq
chown -R rabbitmq:rabbitmq /var/log/rabbitmq

su rabbitmq -s /bin/sh -c %{_rabbitbindir}/rabbitmq-mnesia-current
if [ $? = 1 ]; then
	/bin/sh %SOURCE4 /var/lib/rabbitmq/mnesia
fi

/sbin/chkconfig --add %{name}
/sbin/service rabbitmq-server start

%preun
if [ $1 = 0 ]; then
  #Complete uninstall
  /sbin/service rabbitmq-server stop
  /sbin/chkconfig --del rabbitmq-server
  
  # We do not remove /var/log and /var/lib directories
  # Leave rabbitmq user and group
fi

%files
%defattr(-,root,root,-)
%{_erllibdir}/rabbitmq_server-%{version}/
%{_rabbitbindir}/
%{_mandir}/man1/rabbitmq-multi.1.gz
%{_mandir}/man1/rabbitmq-server.1.gz
%{_mandir}/man1/rabbitmqctl.1.gz
%{_sbindir}/rabbitmqctl
%dir /var/lib/rabbitmq
%dir /var/log/rabbitmq
/etc/rc.d/init.d/rabbitmq-server
%config(noreplace) /etc/logrotate.d/rabbitmq-server
%doc LICENSE LICENSE-MPL-RabbitMQ INSTALL

%clean
rm -rf %{buildroot}

%changelog
* Thu Jul 24 2008 Tony Garnock-Jones <tonyg@lshift.net> 1.4.0-1
- New upstream release

* Mon Mar 3 2008 Adrien Pierard <adrian@lshift.net> 1.3.0-1
- New upstream release

* Wed Sep 26 2007 Simon MacMullen <simon@lshift.net> 1.2.0-1
- New upstream release

* Wed Aug 29 2007 Simon MacMullen <simon@lshift.net> 1.1.1-1
- New upstream release

* Mon Jul 30 2007 Simon MacMullen <simon@lshift.net> 1.1.0-1.alpha
- New upstream release

* Tue Jun 12 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.20070607
- Building from source tarball, added starting script, stopping

* Mon May 21 2007 Hubert Plociniczak <hubert@lshift.net> 1.0.0-1.alpha
- Initial build of server library of RabbitMQ package
