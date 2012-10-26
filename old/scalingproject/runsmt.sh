# This script allows us to save the parameter file without any changes in the
# directory where the computation results are stored. Additionally it saves the
# standard output of the scaling script in that same directory, which is neat.
# This allows us to access all that from the sumatra web interface.

TIMESTAMP=`date +%Y%m%d-%H%M%S`
echo $TIMESTAMP
mkdir ./Results/$TIMESTAMP
cp current.param ./Results/$TIMESTAMP
#smt run current.param --label=$TIMESTAMP | tee ./Results/$TIMESTAMP/stdout.txt
if [ -n "$1" ]; then
    smt run current.param --label=$TIMESTAMP --reason="$1" | tee ./Results/$TIMESTAMP/stdout.txt
else
    smt run current.param --label=$TIMESTAMP | tee ./Results/$TIMESTAMP/stdout.txt
fi
#python scaling_control_script.py current.param $TIMESTAMP

