import argparse

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-L', '--Logfile',
                        help='Path to logfile which needs cleaning.')
    args = parser.parse_args()
    logfile = args.Logfile
    print(f'Cleaning TensorFlow logfile: {logfile}')
    with open(logfile, 'r') as f:
        lines = f.readlines()
    lines_cleaned = []
    for line in lines:
        lines_cleaned.append(line.replace('\x08', ''))
    with open(logfile, 'w') as f:
        f.writelines(lines_cleaned)
    print('Done.')
