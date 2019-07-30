if [ ${#} -ne 2 ]; then
	echo This programme needs 2 arguments:
	echo ""
	echo ./prefilter_images \"Folder_images\" \"num _of_slides\"
	exit;
fi
for FOLDER in $(find "$1" -maxdepth 1 -mindepth 1 -type d); do
	MAX=0
	for SESSION in $(find "$FOLDER" -mindepth 2 -maxdepth 2 -type d); do
		NUMBER=$(find "$SESSION" -iname "*.DCM" | wc -l)
		if (( NUMBER > MAX )); then MAX=$NUMBER; fi
	done
	if (( MAX > "$2" )); then
		echo "$FOLDER"
	fi
done
