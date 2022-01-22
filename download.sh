cd data/download

# Emerson et al CMV Dataset
FILE=emerson-2017-natgen.zip
if test -f "$FILE"; then
    echo "$FILE already exists. Skipped downloading."
else
    # https://clients.adaptivebiotech.com/pub/emerson-2017-natgen
    wget -O $FILE https://s3-us-west-2.amazonaws.com/publishedproject-supplements/emerson-2017-natgen/emerson-2017-natgen.zip 
    mkdir -p ../interim/emerson-2017-natgen/
    unzip $FILE -d ../interim/emerson-2017-natgen/
fi

# Heather et al HIV Dataset

FILE=heather-2016-frontimmunol.zip
if test -f "$FILE"; then
    echo "$FILE already exists. Skipped downloading."
else
    # https://figshare.com/articles/dataset/Human_TCRs_and_CDR3s_sequenced_from_healthy_volunteers_and_HIV_infected_patients_before_and_after_14_weeks_of_therapy/1153921/1
    wget -O $FILE https://figshare.com/ndownloader/articles/1153921/versions/1 
    mkdir -p ../interim/heather-2016-frontimmunol/
    unzip $FILE -d ../interim/heather-2016-frontimmunol/
fi

# Huth et al CMV Dataset

FILE=huth-2018-jimmunol.zip
if test -f "$FILE"; then
    echo "$FILE already exists. Skipped downloadings."
else
    # https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE114931
    wget -O $FILE ftp://ftp.ncbi.nlm.nih.gov/geo/series/GSE114nnn/GSE114931/suppl/GSE114931_RAW.tar
    mkdir -p ../interim/huth-2018-jimmunol/
    tar -xvf $FILE -C ../interim/huth-2018-jimmunol/
fi
