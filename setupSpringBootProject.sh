#!/bin/bash

echo "This scripts generates quickstart spring boot projects that can be easily customized.\nDefault dependencies added are web, data-jpa, h2, actuator, lombok & devtools.\nAlso added, Java version 8 and Spring Boot version 2.3.0"
echo "Please follow below instructions ..."

read -p " Enter packageName ( default value : com.pankiba ) : " packageName
packageName="${packageName:-com.pankiba}"
echo "you entered : $packageName"

read -p " Enter groupId ( default value : com.pankiba ) : " groupId
groupId="${groupId:-com.pankiba}"
echo "you entered : $groupId"

read -p " Enter artifactId : " artifactId
echo "you entered : $artifactId"

read -p " Enter name ( default value : $artifactId ) : " name
name="${name:-$artifactId}"
echo "you entered : $name"

read -p " Enter description ( default value : $artifactId ) : " description
description="${description:-$artifactId}"
echo "you entered : $description"

read -p " Enter packaging type ( default value : jar ) : " packaging
packaging="${packaging:-jar}"
echo "you entered : $packaging"

read -p " Enter javaVersion ( default value : 1.8 ) : " javaVersion
javaVersion="${javaVersion:-1.8}"
echo "you entered : $javaVersion"

read -p " Enter bootVersion ( default value : 2.3.0.RELEASE ) : " bootVersion
bootVersion="${bootVersion:-2.3.0.RELEASE}"
echo "you entered : $bootVersion"

read -p " Enter dependencies ( comma separated values like web,devtools,actuator ) : " dependencies
echo "you entered : $dependencies"

curl https://start.spring.io/starter.zip \
     -d packageName=$packageName \
     -d groupId=$groupId \
     -d artifactId=$artifactId \
     -d name=$name \
     -d description=$description \
     -d packaging=$packaging \
     -d javaVersion=$javaVersion \
     -d bootVersion=$bootVersion \
     -d dependencies=$dependencies \
     -o $artifactId.zip
echo "Unzipping "$artifactId".zip file..."
unzip $artifactId.zip -d $artifactId
