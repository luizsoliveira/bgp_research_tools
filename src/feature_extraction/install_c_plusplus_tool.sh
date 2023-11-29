echo "This script was designed to be exected in their same path."
echo "Execute using ./install_c_plusplus_tool.sh"
echo "This script was designed to run jut on MacOS Darwin and Ubuntu 22.04"

unameOut="$(uname -s)"
case "${unameOut}" in
    Linux*)     machine=Linux;;
    Darwin*)    machine=Mac;;
    CYGWIN*)    machine=Cygwin;;
    MINGW*)     machine=MinGw;;
    MSYS_NT*)   machine=Git;;
    *)          machine="UNKNOWN:${unameOut}"
esac
echo ${machine} = "operation system detected."

if ["$machine" == "Mac"]
then
    echo "Installing dependencies using brew"
    brew install cmake zlib bzip2
fi

if ["$machine" == "Linux"]
then
    echo "Installing dependencies using apt"
    # sudo apt install -y cmake zlib1g bzip2
    sudo apt install -y zlib1g bzip2
    #zlib1g-dev
fi

# Installing required version of cmake
sudo apt remove --purge --auto-remove cmake
sudo apt update && \
sudo apt install -y software-properties-common lsb-release && \
sudo apt clean all
wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
sudo apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"
sudo apt update
sudo apt install kitware-archive-keyring
sudo rm /etc/apt/trusted.gpg.d/kitware.gpg
sudo apt update
sudo apt install cmake
cmake --version

# Creating dir for mrtprocessor
mkdir -p /opt/bgp_research_tools/src/feature_extraction/mrtprocessor
cd /opt/bgp_research_tools/src/feature_extraction/mrtprocessor

# Installing library bgpdump
echo "Installing library bgpdump"
git clone https://github.com/RIPE-NCC/bgpdump tmp_bgpdump
cd tmp_bgpdump
autoheader
autoconf
./configure --prefix /opt/bgp_research_tools/src/feature_extraction/mrtprocessor
make
make install
cd ..
rm -fr tmp_bgpdump

# Installing MRT Processor last version
git clone https://github.com/zhida-li/CyberDefense mrtprocessor/repo
cd mrtprocessor/repo
git checkout dev-2.0
cd src/mrtprocessor/

#Edit file CMakeLists.txt
sed -i -e 's|/Users/ballanty/.local|/opt/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt

#Edit file main.cpp
sed -i -e 's|__u6_addr\.|__in6_u.|g' ./main.cpp

cmake .
make
ln -sf /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor






