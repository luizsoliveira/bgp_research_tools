cd /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/
git switch dev-2.0 -f
# git checkout c100c21 -f
git stash
git pull
sed -i -e 's|$ENV{HOME}/.local|/opt/bgp_research_tools/src/feature_extraction/mrtprocessor|g' ./CMakeLists.txt
cmake .
make
ln -sf /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/repo/src/mrtprocessor/mrtprocessor /opt/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor
export DYLD_LIBRARY_PATH=/opt/bgp_research_tools/src/feature_extraction/mrtprocessor/lib
/opt/bgp_research_tools/src/feature_extraction/mrtprocessor/bin/mrtprocessor --help
