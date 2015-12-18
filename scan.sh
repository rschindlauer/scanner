#!/bin/bash

TIME=$(date +%Y_%m_%d-%H_%M_%S)
DESTINATION=/var/local/share
TMPDIR=/var/local/share/tmp

function scan_photo {
    echo "calling scanimage..."
    scanimage -B --mode Color --page-height 0 --format tiff > ${TMPDIR}/${TIME}.tiff 

    echo "converting scanned pages to jpg..."
    gm convert ${TMPDIR}/${TIME}.tiff -compress jpeg -quality 80  "${DESTINATION}/${TIME}.jpg" &
}

function scan_doc {
    local SOURCE="ADF Front"
    if [ "$1" = "duplex" ]
    then
        SOURCE="ADF Duplex"
    fi

    echo "calling scanimage..."
    scanimage -B --mode Color --page-height 0 --format tiff \
         --batch=${TMPDIR}/${TIME}_%d.tiff --source "$SOURCE" 

    echo "converting scanned pages to pdf..."
    #gm convert +dither -colors 8 -normalize -fuzz 15% -trim \
    #     ${TMPDIR}/${TIME}_*cleaned.tiff "${DESTINATION}/${TIME}.pdf" &
    gm convert -fuzz 15% -trim +repage -level 10%,1,74% ${TMPDIR}/${TIME}_*.tiff "${DESTINATION}/${TIME}.pdf" &
}

function print_usage {
cat << EOF

Usage: 0 [--help] --type {photo|front|duplex}

Scans and post-processes a document according to the specified type into a fixed folder.

--help  Print this message
--type	Type of scan:
        photo: single-sided color scan, jpeg output
        front: single-sided document scan, pdf output
        duplex: double-sided document scan, pdf output   

EOF

exit -1;
}

if [ $# -lt 1 ]; then
    print_usage;
fi

while [ $# -gt 0 ]; do
    arg=$1

    shift;

    if [ $arg == "--help" ]; then
        print_usage;
    fi

    if [ $arg == "--type" ]; then
        type=$1

        case $type in
            photo) scan_photo ;;
            front) scan_doc "front" ;;
            duplex) scan_doc "duplex" ;;
        esac
    fi
done

