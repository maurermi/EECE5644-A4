echo "Starting..."
python Q1.py --learning_rate=0.001 --weight_decay=0.0001 --hidden_linear=120 --hidden_channel=16 --mode=train --print_model=True &> c1_out.txt
echo "done 1"
python Q1.py --learning_rate=0.0001 --weight_decay=0.0001 --hidden_linear=120 --hidden_channel=16 --mode=train --print_model=True &> c2_out.txt
echo "done 2"
python Q1.py --learning_rate=0.001 --weight_decay=0.00001 --hidden_linear=120 --hidden_channel=16 --mode=train --print_model=True &> c3_out.txt
echo "done 3"

python Q1.py --learning_rate=0.0001 --weight_decay=0.00001 --hidden_linear=120 --hidden_channel=16 --mode=train --print_model=True &> c4_out.txt

echo "done 4"
python Q1.py --learning_rate=0.001 --weight_decay=0.0001 --hidden_linear=100 --hidden_channel=12 --mode=train --print_model=True &> c5_out.txt

echo "done 5"
python Q1.py --learning_rate=0.0001 --weight_decay=0.0001 --hidden_linear=100 --hidden_channel=12 --mode=train --print_model=True &> c6_out.txt

echo "done 6"
python Q1.py --learning_rate=0.001 --weight_decay=0.00001 --hidden_linear=100 --hidden_channel=12 --mode=train --print_model=True &> c7_out.txt

echo "done 7"
python Q1.py --learning_rate=0.0001 --weight_decay=0.00001 --hidden_linear=100 --hidden_channel=12 --mode=train --print_model=True &> c8_out.txt
echo "done!"
