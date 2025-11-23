
jpg="$1"

if [ -z "$jpg" ] ; then
    jpg=$(ls -rt1 ~/screen*.jpg | tail -1)
fi

echo "take file: $jpg"
ls -l "$jpg"

txt=$(echo "$jpg" | sed "s/\.jpg$//")

# tesseract $jpg stdout
tesseract $jpg $txt

echo "=========================================================================================="
cat "$txt.txt"
echo "=========================================================================================="

tag=$(date '+%Y-%m-%d_%H%M%S')

dest_jpg=/tmp/$(echo "$jpg" | sed "s/.*\///").$tag

mv $jpg $dest_jpg

echo "generated file: $txt.txt"
ls -l "$dest_jpg"
