from functools import reduce
import sys
import git
import glob
from astropy.table import Table
from tqdm import tqdm

def analyse_file(filename):

    commits = repo.iter_commits(paths=filename)

    allcommits = [c for c in commits]
    if len(allcommits) == 0:
        return None
    authors = set()
    for commit in allcommits:
        authors.add(commit.author.name)
        if len(authors) > 1:
            return None
    commits_number = len(allcommits)
    return [str(authors.pop()), commits_number, "{:%Y-%m-%d}".format(allcommits[0].authored_datetime)]

if __name__ == '__main__':
    repo = git.Repo()
    files = reduce(lambda l1, l2: l1 + l2, [glob.glob(sys.argv[1] + "/**/*." + e, recursive=True) for e in ['py', 'f', 'c', 'h', 'pyx']])
    t = Table([[], [], [], []],
              names=('filename', 'author', 'commits', 'last date'),
              dtype=('S100','S100', 'i4', 'S10' ))
    t.convert_bytestring_to_unicode()
    for file_i in tqdm(files):
        row = analyse_file(file_i)
        if row:
            t.add_row([file_i] + row)
    t.write('{}_critic.txt'.format(sys.argv[1]), format='ascii.fixed_width', overwrite=True)

# What else I want to do?

