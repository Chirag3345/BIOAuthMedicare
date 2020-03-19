cd Images
MINDTCT_BIN_PATH="$HOME/nbis/bin/mindtct"

for directory in */; do
	work_dir=${PWD}
	cd "$directory"
	for filename in *.png; do
		oroot=${filename%.*}
	    $MINDTCT_BIN_PATH "$filename" "$oroot"
	done
	cd "$work_dir"
done
