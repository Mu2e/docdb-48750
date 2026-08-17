import os
import subprocess

def make_dirtree_no_files(src, dst):
    src = os.path.abspath(src)
    src_prefix = len(src) + len(os.path.sep)

    for root, dirs, files in os.walk(src):
        for dirname in dirs:
            dirpath = os.path.join(dst, root[src_prefix:], dirname)
            os.makedirs(dirpath, exist_ok=True)

def make_stamped_file(filename, start_dir, end_dir, stampfile):
    if ".png" in filename.lower():
        #filename_old = filename.replace('.png', '.pdf')
        #filename_old = start_dir+'hold.png'
        filename_old = filename.replace(filename[filename.rfind('/')+1:], 'hold.pdf')
        filename_new = filename.replace('.png', '.pdf').replace(start_dir, end_dir)
        # convert to pdf
        run_cmd = f'convert {filename} {filename_old}'
        print(run_cmd)
        _ = subprocess.run(run_cmd, shell=True, capture_output=False)
        del_old = True
    else:
        filename_old = filename
        filename_new = filename_old.replace(start_dir, end_dir)
        del_old = False
    # add stamp
    run_cmd = f'pdftk {filename_old} multistamp {stampfile} output {filename_new}'
    print(run_cmd)
    _ = subprocess.run(run_cmd, shell=True, capture_output=False)
    # delete hold file?
    if del_old:
        run_cmd = f'rm {filename_old}'
        print(run_cmd)
        _ = subprocess.run(run_cmd, shell=True, capture_output=False)


if __name__=='__main__':
    start_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '')
    end_dir = os.path.join(os.path.abspath(os.path.join(start_dir, '..', 'plots_preapproval')), '')
    stampfile = os.path.join(start_dir, 'forapproval_stamp.pdf')
    # make sure directory structure in preapproval matches
    make_dirtree_no_files(start_dir, end_dir)
    # gather a list of files to stamp
    files = [os.path.join(root, f) for root, _, fn in os.walk(start_dir) for f in fn]
    files_to_stamp = []
    for f in files:
        if (".pdf" == f[-4:].lower()) or (".png" == f[-4:].lower()):
            if ("forapproval_stamp" in f) or ("hold.pdf" in f):
                continue
            # check for duplicates -- prefer original PDFs to avoid conversion losses
            if ".png" == f[-4:].lower():
                if f.replace(".png", ".pdf") in files:
                    continue
            files_to_stamp.append(f)
    # loop through files and stamp
    for f in files_to_stamp:
        make_stamped_file(f, start_dir, end_dir, stampfile)


