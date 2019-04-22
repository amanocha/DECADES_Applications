

awk ' NR < 3 {$0; print; next;} { $3 = rand(); print; }' $1 | sort -k1n -k2n
