mkdir /home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor
cd /home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor 

git clone https://github.com/RIPE-NCC/bgpdump tmp_bgpdump
cd tmp_bgpdump
autoheader
autoconf
./configure --prefix /home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor
make
make install
cd ..
rm -fr tmp_bgpdump
ls -l

# Installing MRT Processor last version
git clone https://github.com/zhida-li/CyberDefense repo
cd repo
git checkout dev-2.0
cd src/mrtprocessor/

#Edit file CMakeLists.txt
sed -i -e 's|$ENV{HOME}/.local|/home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt

cmake .
make

ln -sf /home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor /home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor
export DYLD_LIBRARY_PATH=/home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor/lib
/home/loa10/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor --help