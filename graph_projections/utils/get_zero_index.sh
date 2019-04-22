awk ' NR < 3 {$0; print; next;} { $1 = $1 - 1; $2 = $2 - 1; print; }' $1 
