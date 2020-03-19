no_args="true"
init_delete="false"
reg_delete="false"

while getopts :ri opt; do
   case $opt in
     i ) init_delete="true"                   ;;
     r ) reg_delete="true"                    ;;
    \? ) echo "${0##*/} [ -erw ]" >&2; exit 1 ;;
  esac
  no_args="false"
done

if [[ $no_args == "true" ]]; then
    init_delete="true"
    reg_delete="true"
fi

if [[ $reg_delete == "true" ]]; then
    rm -r ./UserData/*
    rm -r ./Pickle/*
fi

if [[ $init_delete == "true" ]]; then
    cd Images
    for directory in */; do
        find "$directory" -type f ! -name '*.png' -delete
    done
fi