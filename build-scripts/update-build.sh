#!/bin/sh

cd /home/build/awx-rpm-build/awx

git pull --quiet

RELEASE=`git describe --long --first-parent |cut -f1-2 -d- |sed 's/-/./'`

if [[ ! -f /home/build/awx-rpm-build/awx/dist/awx-$RELEASE.tar.gz ]] ; then
	echo "Building new release: $RELEASE"

docker run -v `pwd`:/awx --rm -i centos:7 /bin/bash <<EOF
yum install -y epel-release 
yum install -y https://centos7.iuscommunity.org/ius-release.rpm
yum install -y bzip2 gcc-c++ git2u gettext make python-pip
curl --silent --location https://rpm.nodesource.com/setup_6.x | bash -
yum install -y nodejs
cd /awx/
make sdist
EOF

cd /home/build/awx-rpm-build

TIMESTAMP=`date +%a" "%b" "%d" "%Y" "%H:%M:%S" "%z" Martin Juhl <mj@casalogic.dk>"`
CHANGE="\* $TIMESTAMP $RELEASE\n- New Git version build\n"
echo $CHANGE

sed -i 's/.*%changelog.*/&\n'"$CHANGE"'/' awx-rpm/awx.spec
sed 's/¤VERSION¤/'$RELEASE'/g' awx-rpm/awx.spec > awx-rpm/awx-build.spec
sed -i 's/¤SOURCE¤/awx-'$RELEASE'.tar.gz/g' awx-rpm/awx-build.spec

cd /home/build/awx-rpm-build/awx-rpm

cp /home/build/awx-rpm-build/awx/dist/awx-$RELEASE.tar.gz /home/build/awx-rpm-build/awx-rpm

./build.sh centos-7

cd /home/build/awx-rpm-build/

if [[ ! -f /home/build/awx-rpm-build/awx-rpm/result/awx-$RELEASE-1.el7.centos.src.rpm ]]; then

mail -s "AWX RPM Auto Build FAILED!! Version $RELEASE" "m@rtinjuhl.dk" <<EOF
New version build of AWX failed for:

Release Version: $RELEASE

EOF

	exit 1
fi

./send-build awx-$RELEASE-1.el7.centos.src.rpm /home/build/awx-rpm-build/awx-rpm/result/awx-$RELEASE-1.el7.centos.src.rpm

mail -s "AWX RPM Auto Build Version $RELEASE" "m@rtinjuhl.dk" <<EOF
New version of AWX has been build and pushed to COPR

Release Version: $RELEASE

EOF

else

	echo "Version: $RELEASE, Already built"
	
fi
