cd /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/
git stash
git pull
#Edit file CMakeLists.txt
sed -i -e 's|/Users/ballanty/.local|/opt/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt
cmake .
make
ln -sf /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor
/opt/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor --help