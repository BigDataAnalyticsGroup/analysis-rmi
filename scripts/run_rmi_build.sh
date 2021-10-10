#!bash
# set -x
trap "exit" SIGINT

EXPERIMENT="rmi build"

DIR_DATA="data"
DIR_RESULTS="results"
FILE_RESULTS="${DIR_RESULTS}/rmi_build.csv"

BIN="build/bin/rmi_build"

# Set number of repetitions and samples
N_REPS="3"
PARAMS="--n_reps ${N_REPS}"
TIMEOUT=$((${N_REPS}*3000))

DATASETS="books_200M_uint64 fb_200M_uint64 osm_cellids_200M_uint64 wiki_ts_200M_uint64"
LAYER1="cubic_spline linear_spline linear_regression radix"
LAYER2="linear_spline linear_regression"
BOUNDS="none gabs gind labs lind"

run() {
    DATASET=$1
    L1=$2
    L2=$3
    N_MODELS=$4
    BOUND=$5
    DATA_FILE="${DIR_DATA}/${DATASET}"
    timeout ${TIMEOUT} ${BIN} ${DATA_FILE} ${L1} ${L2} ${N_MODELS} ${BOUND} ${PARAMS} >> ${FILE_RESULTS}
}

# Create results directory
if [ ! -d "${DIR_RESULTS}" ];
then
    mkdir -p "${DIR_RESULTS}";
fi

# Check data downloaded
if [ ! -d "${DIR_DATA}" ];
then
    >&2 echo "Please download datasets first."
    return 1
fi

# Write csv header
echo "dataset,n_keys,layer1,layer2,n_models,bounds,size_in_bytes,rep,build_time,checksum" > ${FILE_RESULTS} # Write csv header

# Run layer1 model type experiment
for dataset in ${DATASETS};
do
    echo "Performing ${EXPERIMENT}: layer1 on '${dataset}'..."
    for ((i=6; i<=25; i += 1));
    do
        n_models=$((2**$i))
        for l1 in ${LAYER1};
        do
            run ${dataset} ${l1} linear_spline ${n_models} none
        done
    done
done

# Run layer2 model type experiment
for dataset in ${DATASETS};
do
    echo "Performing ${EXPERIMENT}: layer2 on '${dataset}'..."
    for ((i=6; i<=25; i += 1));
    do
        n_models=$((2**$i))
        for l2 in ${LAYER2};
        do
            run ${dataset} cubic_spline ${l2} ${n_models} none
            run ${dataset} linear_spline ${l2} ${n_models} none
        done
    done
done

# Run bound type experiment
for dataset in ${DATASETS};
do
    echo "Performing ${EXPERIMENT}: bounds on '${dataset}'..."
    for ((i=6; i<=25; i += 1));
    do
        n_models=$((2**$i))
        for bound in ${BOUNDS};
        do
            run ${dataset} linear_spline linear_regression ${n_models} ${bound}
        done
    done
done

