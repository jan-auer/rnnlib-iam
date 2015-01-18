EMPTY='""'
case $1 in
	"train")
		TRAIN_F="trainset.nc"
		VAL_F=$EMPTY
		TEST_F=$EMPTY
		DATASET=train
		CONFIG=trainset.config
		;;
	"val1")
		TRAIN_F=$EMPTY
		VAL_F="testset_v.nc"
		TEST_F=$EMPTY
		DATASET=val
		CONFIG=`ls trainset\@*ctcError.save | tail -1`
		;;
	"val2")
		TRAIN_F=$EMPTY
		VAL_F="testset_t.nc"
		TEST_F=$EMPTY
		DATASET=val
		CONFIG=`ls testset_v\@*ctcError.save | tail -1`
		;;
	"test")
		TRAIN_F=$EMPTY
		VAL_F=$EMPTY
		TEST_F="testset_f.nc"
		DATASET="test"
		CONFIG=`ls testset_t\@*ctcError.save | tail -1`
		;;
	*)
		echo "ERROR: Parameter must be one of train, val1, val2 or test."
		exit
esac

set -x
/Users/jauer/Coding/puli/rnnlib/bin/rnnlib \
  --trainFile=$TRAIN_F \
  --valFile=$VAL_F     \
  --testFile=$TEST_F   \
  --dataset=$DATASET   \
  --autosave=true      \
  $CONFIG
