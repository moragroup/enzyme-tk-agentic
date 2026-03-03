from enzymetk import Chai
from enzymetk import Save
import pandas as pd

output_dir = './'
num_threads = 1
id_col = 'Entry'
seq_col = 'Sequence'
substrate_col = 'Substrate'
rows = [['P0DP23', 'MALWMRLLPLLALLALWGPDPAAAMALWMRLLPLLALLALWGPDPAAAMALWMRLLPLLALLALWGPDPAAA', 'CCCCC(CC)COC(=O)C1=CC=CC=C1C(=O)OCC(CC)CCCC', ''], 
        ['P0DP24', 'MALWMRLLPLLALLALWGPDPAAAMALWMRLLPLLALLALWGPDPAAAMALWMRLLPLLALLALWGPDPAAA', 'CCCCC(CC)COC(=O)C1=CC=CC=C1C(=O)OCC(CC)CCCC', '']]
df = pd.DataFrame(rows, columns=[id_col, seq_col, substrate_col, 'cofactor'])
print(df)
 # id_col: str, seq_col: str, substrate_col: str, cofactor_col: str, output_dir: str, 
df = df << (Chai(id_col, seq_col, substrate_col, 'cofactor', f'{output_dir}', num_threads) >> Save(f'{output_dir}test.pkl'))
print(df)