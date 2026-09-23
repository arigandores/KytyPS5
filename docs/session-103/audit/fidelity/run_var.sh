B=/c/VulkanSDK/1.4.357.0/Bin
cd /c/kyty/s103/audit103/fidelity
for spec in "S3_3d705c1b57adec00_p0 ps" "S4_2e2ae33a4d374e8f_p0 ps" "S5_b96c2898f05637df_p0 ps" "S8_7a46be05e11e081b_p0 ps" "S2_746c68bba46b2b49_p0 ps" "S6_173677e49330bd65_100166fe_p0 cs" "S7_3276e23cce1be33c_p0 cs" "S10_c924afb0821b68c8_p0 ps"; do
 set -- $spec; it=$1; st=$2; flag=""; [ $st = ps ] && flag="--ps"; ex="CS"; [ $st = ps ] && ex="FS"
 for mode in rt noslow nodword nobounds noslow,nodword noslow,nodword,nobounds; do
  tag=$(echo $mode | tr ',' '+')
  if [ $mode = rt ]; then cp dis/${it}_V2p.dis var/${it}_rt.dis; else python surgery.py dis/${it}_V2p.dis var/${it}_$tag.dis $mode >/dev/null; fi
  $B/spirv-as.exe --preserve-numeric-ids --target-env spv1.3 var/${it}_$tag.dis -o var/${it}_$tag.spv || { echo "ASFAIL $it $tag"; continue; }
  $B/spirv-val.exe --target-env vulkan1.3 --uniform-buffer-standard-layout var/${it}_$tag.spv >/dev/null 2>&1 || echo "VALFAIL $it $tag"
  r=$(/c/kyty/tools/pipestat/pipestat.exe $flag var/${it}_$tag.spv | grep "\"$ex\"" | sed -E 's/.*Register Count=([0-9]+) Binary Size=([0-9]+).*Local Memory Size=([0-9]+).*/rc=\1 bin=\2 lm=\3/')
  echo "$it $tag $r"
 done
 for arm in A V1; do
  r=$(/c/kyty/tools/pipestat/pipestat.exe $flag /c/kyty/s103/m5p/spv/${it}_$arm.spv | grep "\"$ex\"" | sed -E 's/.*Register Count=([0-9]+) Binary Size=([0-9]+).*Local Memory Size=([0-9]+).*/rc=\1 bin=\2 lm=\3/')
  echo "$it $arm $r"
 done
done
