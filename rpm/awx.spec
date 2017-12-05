%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')
%global __arch_install_post  %{nil}

Name:           awx
Version:        1.0.1.234
Release:        1%{?dist}
Summary:        Package source version control system

Group:          Utilities/Management

License:        MIT and GPLv1 and GPLv2+
#URL:            https://github.com/release-engineering/dist-git
Source0:        %{name}-%{version}.tar.gz
Source1:	awx.conf
Source2:	supervisor.conf
Source3:	supervisor_task.conf
Source4:	launch_awx.sh
Source5:	launch_awx_task.sh
Source6:	settings.py
Source7:	env.sh
Source8:	awx-web.service
Source9:	awx-task.service
Patch1:		uninstall-fix.patch

AutoReqProv: 0

BuildRequires:   git libffi-devel python-pip gcc postgresql-devel libxml2-devel libxslt-devel cyrus-sasl-devel openldap-devel xmlsec1-devel krb5-devel xmlsec1-openssl-devel libtool-ltdl-devel gcc-c++ python-devel python-virtualenv
Requires:  ansible git mercurial subversion curl python-psycopg2 python-pip python-setuptools libselinux-python setools-libs yum-utils sudo acl make nginx python-psutil libstdc++.so.6 cyrus-sasl libffi-devel python-pip swig xmlsec1-openssl xmlsec1 bubblewrap krb5-workstation krb5-libs supervisor memcached

%description
AWX is the Community version of Ansible Tower

%prep
%setup -q
%patch1 -p0

%install
mkdir -p %{buildroot}/var/lib/awx/public/static
#pip install virtualenv supervisor
#virtualenv --system-site-packages "%{buildroot}/var/lib/awx/venv"
#PIP_OPTIONS="$PIP_OPTIONS --root \"%{buildroot}\"" make requirements_ansible
#PIP_OPTIONS="$PIP_OPTIONS --root \"%{buildroot}\"" make requirements_awx
#VENV_BASE=%{buildroot}/var/lib/awx/venv PIP_OPTIONS="$PIP_OPTIONS --root \"%{buildroot}\"" make requirements_ansible
#VENV_BASE=%{buildroot}/var/lib/awx/venv PIP_OPTIONS="$PIP_OPTIONS --root \"%{buildroot}\"" make requirements_awx
VENV_BASE=%{buildroot}/var/lib/awx/venv make requirements_ansible
VENV_BASE=%{buildroot}/var/lib/awx/venv make requirements_awx


mkdir -p %{buildroot}/var/log/tower
mkdir -p %{buildroot}/etc/tower
#OFFICIAL=yes pip install --target=%{buildroot}/var/lib/awx/venv/awx/lib/python2.7/site-packages/ %{SOURCE0}
#VENV_BASE=%{buildroot}/var/lib/awx/venv OFFICIAL=yes pip install --root "%{buildroot}" %{SOURCE0}
VENV_BASE=%{buildroot}/var/lib/awx/venv OFFICIAL=yes pip install --root %{buildroot} %{SOURCE0}

virtualenv --relocatable "%{buildroot}/var/lib/awx/venv/awx"
virtualenv --relocatable "%{buildroot}/var/lib/awx/venv/ansible"

echo "%{version}" > %{buildroot}/var/lib/awx/.tower_version
mkdir -p %{buildroot}/etc/nginx/conf.d
mkdir -p %{buildroot}/usr/bin/
cp %{SOURCE1} %{buildroot}/etc/nginx/conf.d/awx.conf
cp %{SOURCE2} %{buildroot}/etc/tower/supervisor.conf
cp %{SOURCE3} %{buildroot}/etc/tower/supervisor_task.conf
cp %{SOURCE4} %{buildroot}/usr/bin/launch_awx.sh
cp %{SOURCE5} %{buildroot}/usr/bin/launch_awx_task.sh
chmod +rx %{buildroot}/usr/bin/launch_awx.sh && chmod +rx %{buildroot}/usr/bin/launch_awx_task.sh
cp %{SOURCE6} %{buildroot}/etc/tower/settings.py
cp %{SOURCE7} %{buildroot}/etc/tower/env.sh
mkdir -p %{buildroot}/etc/systemd/system/
cp %{SOURCE8} %{buildroot}/etc/systemd/system/awx-web.service
cp %{SOURCE9} %{buildroot}/etc/systemd/system/awx-task.service
SAVEIFS=$IFS
IFS=$(echo -en "\n\b")
for i in `find %{buildroot}/var/lib/awx/venv/awx/bin -type f`;do
	sed -i "s&%{buildroot}&&g" "$i"
done
for i in `find %{buildroot}/var/lib/awx/venv/ansible/bin -type f`;do
        sed -i "s&%{buildroot}&&g" "$i"
done
IFS=$SAVEIFS

%pre
/usr/bin/getent group awx > /dev/null || /usr/sbin/groupadd -r awx
/usr/bin/getent passwd awx > /dev/null || /usr/sbin/useradd -r -d /var/lib/awx -s /sbin/nologin -g awx awx

%postun
/usr/sbin/userdel awx
/usr/sbin/groupdel awx


%files
%defattr(-,awx,awx,0755)
/var/lib/awx
/var/log/tower
%config /etc/nginx/conf.d/awx.conf
%config /etc/tower/supervisor.conf
%config /etc/tower/supervisor_task.conf
%config /etc/tower/env.sh
%config /etc/tower/settings.py
/usr/bin/launch_awx.sh
/usr/bin/launch_awx_task.sh
/usr/bin/ansible-tower-service
/usr/bin/awx-manage
/usr/bin/awx-python
/usr/bin/failure-event-handler
/usr/lib/python2.7/site-packages/awx*
/usr/share/awx
/usr/share/doc/awx
/etc/systemd/system/awx-task.service
/etc/systemd/system/awx-web.service
/usr/share/sosreport/sos/plugins/tower.py


%changelog
* Fri Dec 01 2017 Martin Juhl <mj@casalogic.dk> 1.0.1.234
- Initial Release (mj@casalogic.dk)


