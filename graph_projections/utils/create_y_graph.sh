
awk ' NR==1 {$0; print; next} NR==2 {t = $3; $3 = $4; $4=t; print; next} { t = $1; $1 = $2; $2 = t; print; } ' $1 | sort -k1n -k2n 
