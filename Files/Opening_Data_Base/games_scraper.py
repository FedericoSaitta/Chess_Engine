import re
import pandas as pd

FILE = 'games_pgn.txt'
FILE_2 = 'game_moves.txt'
FILE_3 = 'opening_moves.txt'

with open(FILE, 'r') as file, open(FILE_2, 'w') as file_2:
    for line in file:
        if line[0] != '1':
            line = line.strip('\n')
        if (line != '') and (line[0] != '['):
            file_2.write(line)
file.close()


with open(FILE_2, 'r') as file, open(FILE_3, 'w') as file_3:
    for line in file:
        try:
            opening_end_point = line.index('10')
            line = line[:opening_end_point]
            line = re.sub(r'\d+\.', '', line)
            line = line.replace('+', '').replace('#', '')

            line = line + '\n'
            file_3.write(line)
        except ValueError:
            continue


df = pd.read_csv(FILE_3, delim_whitespace=True, header=None)


#filtered_df = df[df['0'] == 'e4']

# Display the filtered DataFrame
print(df[0])




